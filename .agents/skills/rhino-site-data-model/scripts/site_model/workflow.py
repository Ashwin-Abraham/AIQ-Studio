"""Coordinate immutable inputs, bounded preparation, one writer, and checkpoints."""

from collections import defaultdict
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from .contract import (CHECKPOINT_SCHEMA, CONTRACT_VERSION, atomic_json, check_checkpoint,
                       confined_path, file_sha256, load_json, source_digest,
                       validate_sources, validate_terrain)


def migrate(input_path, sources_path, terrain_path=None):
    """Split old combined JSON without changing the original input file."""
    data = load_json(input_path)
    terrain = data.pop("terrain", None)
    validate_sources(data)
    if terrain:
        if terrain_path is None:
            raise ValueError("A terrain output path is required for embedded terrain")
        terrain = dict(terrain)
        for key in ("projected_crs", "origin_projected"):
            terrain.setdefault(key, data["run"][key])
        validate_terrain(terrain, data)
    atomic_json(sources_path, data)
    if terrain:
        atomic_json(terrain_path, terrain)
    return {"sources": str(sources_path), "terrain": str(terrain_path) if terrain else None}


def _partitions(data, size, stage):
    base = {key: value for key, value in data.items() if key != "features"}
    # Parent/part relationships cross theme partitions. Do not hide a parent
    # merely because the source claims parts exist outside the selected context.
    parents = set()
    for record in data["features"] if stage == "3d" else []:
        props = record.get("properties") or {}
        try:
            height = float(props["height"]) if props.get("height") is not None else float(props.get("num_floors") or 1) * 3.5
        except (ValueError, TypeError):
            continue
        if (record["feature_type"] == "building_part" and not props.get("is_underground")
                and props.get("building_id") and any(p["kind"] == "Polygon" for p in record["parts"])
                and isinstance(height, (float, int)) and math.isfinite(height) and height > 0):
            parents.add(str(props["building_id"]))
    base["_valid_part_parents"] = sorted(parents)
    yield {**base, "features": []}
    groups = defaultdict(list)
    for feature in data["features"]:
        groups[feature["feature_type"]].append(feature)
    for theme in sorted(groups):
        features = groups[theme]
        for start in range(0, len(features), size):
            yield {**base, "site": {"parts": []},
                   "context": {**data["context"], "parts": []},
                   "_include_context": False, "features": features[start:start + size]}


def prepare_worker(job_path, result_path):
    """Internal subprocess entry point; outputs are task-local temporary files."""
    from .geometry import prepare_stage
    job = load_json(job_path)
    terrain = load_json(job["terrain_path"]) if job.get("terrain_path") else None
    model = prepare_stage(job["sources"], job["stage"], terrain, job.get("flat_elevation"))
    if not model.Write(str(result_path), 8):
        raise RuntimeError("Cannot write prepared worker result")


def _preflight_preparation(workers, worker_python):
    """Validate preparation dependencies before a writer transaction starts."""
    if not worker_python and workers == 1:
        try:
            from . import geometry  # noqa: F401
        except ImportError as error:
            raise RuntimeError("In-process geometry preparation dependencies are unavailable: " + str(error)) from error
        return None

    executable = str(worker_python or sys.executable)
    if not worker_python and Path(executable).name.lower() not in ("python.exe", "python", "python3", "python3.exe"):
        raise ValueError("Set --worker-python to a managed Python executable for parallel work inside Rhino")
    if worker_python and not Path(executable).is_file():
        raise ValueError("The managed Python executable is not visible from the current Rhino process: " + executable)

    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    command = [executable, "-B", "-c", "import rhino3dm, shapely; print('site-model-worker-ok')"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), env=environment)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError("Geometry worker preflight failed: " + str(error)) from error
    if result.returncode or "site-model-worker-ok" not in result.stdout:
        details = (result.stderr or result.stdout or "no worker output")[-4000:]
        raise RuntimeError("Geometry worker preflight failed: " + details)
    return executable


def _prepared(data, stage, terrain, flat_elevation, workers, partition_size, worker_python, pump):
    jobs = iter(_partitions(data, partition_size, stage))
    if not worker_python:
        from .geometry import prepare_stage
        # Show boundaries before starting the larger jobs.
        pump()
        yield prepare_stage(next(jobs), stage, terrain, flat_elevation)
    if workers == 1 and not worker_python:
        for job in jobs:
            pump()
            yield prepare_stage(job, stage, terrain, flat_elevation)
        return
    import rhino3dm as r3d
    executable = str(worker_python or sys.executable)
    entry = Path(__file__).resolve().parents[1] / "run_site_model.py"
    with tempfile.TemporaryDirectory(prefix="site-preparation-") as temporary:
        directory = Path(temporary)
        terrain_path = directory / "terrain.json"
        if terrain is not None:
            atomic_json(terrain_path, terrain)
        pending, exhausted, sequence = [], False, 0
        first_job = bool(worker_python)
        try:
            while pending or not exhausted:
                pump()
                while len(pending) < (1 if first_job else workers) and not exhausted:
                    try:
                        data_part = next(jobs)
                    except StopIteration:
                        exhausted = True
                        break
                    sequence += 1
                    job_path, result_path = directory / (str(sequence) + ".json"), directory / (str(sequence) + ".3dm")
                    atomic_json(job_path, dict(sources=data_part, stage=stage, flat_elevation=flat_elevation,
                                              terrain_path=str(terrain_path) if terrain else None))
                    log = (directory / (str(sequence) + ".log")).open("w+b")
                    environment = os.environ.copy()
                    # Rhino's embedded Python home is incompatible with the
                    # selected external worker runtime.
                    environment.pop("PYTHONHOME", None)
                    try:
                        process = subprocess.Popen([executable, "-B", str(entry), "--worker-job", str(job_path),
                                                    "--worker-result", str(result_path)], stdout=log, stderr=log,
                                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), env=environment)
                    except BaseException:
                        log.close()
                        raise
                    pending.append((process, log, job_path, result_path))
                for item in list(pending):
                    process, log, job_path, result_path = item
                    if process.poll() is None:
                        continue
                    pending.remove(item)
                    log.seek(0)
                    details = log.read().decode("utf-8", errors="replace")
                    log.close()
                    if process.returncode:
                        raise RuntimeError("Geometry worker failed: " + details[-4000:])
                    model = r3d.File3dm.Read(str(result_path))
                    if model is None:
                        raise RuntimeError("Cannot read geometry worker result")
                    yield model
                    first_job = False
                    job_path.unlink()
                    result_path.unlink()
                if pending:
                    time.sleep(0.05)
        finally:
            for process, log, _, _ in pending:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                log.close()


def run(project_root, input_path, output_path, stage="all", backend="live", terrain_path=None,
        flat_elevation=None, workers=1, batch_size=500, partition_size=1000, checkpoint_path=None,
        worker_python=None, cancel=None, progress=None, writer_factory=None):
    """Run requested stages. Failed stages keep the last completed saved model.

    File output is explicit. Live output requires the selected document to be
    open and saved. Validation findings are reported, not treated as exceptions.
    Contract, geometry construction, and write failures abort the current stage.
    """
    if stage not in ("2d", "3d", "all") or backend not in ("live", "file"):
        raise ValueError("Invalid stage or backend")
    if not 1 <= workers <= 8 or batch_size < 1 or partition_size < 1:
        raise ValueError("Use 1 to 8 workers and positive batch and partition sizes")
    root = Path(project_root).resolve()
    source_path = confined_path(root, input_path)
    target = confined_path(root, output_path)
    checkpoint_path = confined_path(root, checkpoint_path or str(target) + ".checkpoint.json")
    terrain_file = confined_path(root, terrain_path) if terrain_path else None
    output_files = [target, checkpoint_path, Path(str(target) + ".report.md")]
    output_files += [Path(str(target) + "." + s + ".audit.json") for s in ("2d", "3d")]
    if len(set(output_files)) != len(output_files) or any(p in (source_path, terrain_file) for p in output_files):
        raise ValueError("Input, model, checkpoint, and report paths must be separate")
    data = validate_sources(load_json(source_path))
    if stage == "2d" and (terrain_path is not None or flat_elevation is not None):
        raise ValueError("2D does not take terrain or a flat elevation")
    if stage != "2d":
        if (terrain_path is None) == (flat_elevation is None):
            raise ValueError("3D requires either terrain or an explicit flat elevation")
        if flat_elevation is not None and (isinstance(flat_elevation, bool) or not math.isfinite(flat_elevation)):
            raise ValueError("Flat elevation must be finite")
    worker_python = _preflight_preparation(workers, worker_python)
    from .writer import FileWriter, RhinoWriter
    from .audit import audit_file
    writer_type = writer_factory or (FileWriter if backend == "file" else RhinoWriter)
    writer = writer_type(target, data, cancel=cancel, progress=progress)
    results = []
    try:
        for current in (("2d", "3d") if stage == "all" else (stage,)):
            terrain = None
            if current == "3d":
                check_checkpoint(load_json(checkpoint_path), data, target)
                # No terrain parsing or 3D preparation before the saved 2D checkpoint.
                if terrain_file:
                    terrain = validate_terrain(load_json(terrain_file), data)
            current_data = deepcopy(data)
            if terrain:
                current_data["run"]["vertical_datum"] = terrain["vertical_datum"]
            prepared = None
            try:
                writer.begin(current)
                warnings = []
                prepared = _prepared(current_data, current, terrain, flat_elevation if current == "3d" else None,
                                     workers, partition_size, worker_python, writer.pump)
                for model in prepared:
                    warnings.extend(json.loads(model.Strings["site.warnings"] or "[]"))
                    objects = list(model.Objects)
                    for offset in range(0, len(objects), batch_size):
                        writer.apply(model, objects[offset:offset + batch_size])
                writer.finish()
                writer.save()
            except BaseException:
                if prepared is not None:
                    prepared.close()
                if getattr(writer, "transaction_open", True):
                    writer.rollback()
                raise
            audit_path = Path(str(target) + "." + current + ".audit.json")
            audit = audit_file(target, current)
            audit["preparation_warnings"] = warnings
            audit["writer_counts"] = writer.counts
            audit["source_feature_count"] = len(data["features"])
            audit["source_digest"] = source_digest(data)
            expected_plan_count = sum(1 + len(part.get("holes") or [])
                                      for section in (data["site"], data["context"], *data["features"])
                                      for part in section["parts"])
            audit["expected_source_plan_object_count"] = expected_plan_count
            if audit.get("source_plan_object_count") != expected_plan_count:
                audit["failures"].append({"check": "source_count_reconciliation", "expected": expected_plan_count,
                                          "actual": audit.get("source_plan_object_count")})
                audit["passed"] = False
            atomic_json(audit_path, audit)
            if not audit.get("model_sha256"):
                raise RuntimeError("Saved model read-back failed; no checkpoint was published")
            checkpoint = dict(schema=CHECKPOINT_SCHEMA, version=CONTRACT_VERSION,
                              source_digest=source_digest(data), model_sha256=file_sha256(target),
                              checked_and_saved=True, completed_stage=current,
                              audit_path=os.path.relpath(audit_path, target.parent), audit_sha256=file_sha256(audit_path))
            atomic_json(checkpoint_path, checkpoint)
            results.append(audit)
            _report(target, results, stage)
    finally:
        writer.close()
    return {"model": str(target), "checkpoint": str(checkpoint_path), "stages": results}


def _report(target, audits, requested_stage):
    lines = ["# Site model report", "", "Requested stage: " + requested_stage, ""]
    for audit in audits:
        lines.extend(["## " + audit.get("stage", "Stage"), "",
                      "Programmatic checks: " + ("passed" if audit["passed"] else "failed"),
                      "", "Visual inspection: " + audit.get("visual_inspection", "not-possible"), "",
                      "Source facts and property provenance are retained on source-derived objects.",
                      "Building height estimates and placement methods are recorded on each volume.", ""])
        for finding in audit.get("failures", []) + audit.get("warnings", []) + audit.get("preparation_warnings", []):
            lines.append("- " + json.dumps(finding, ensure_ascii=False))
        lines.append("")
    path = Path(str(target) + ".report.md")
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write("\n".join(lines))
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
