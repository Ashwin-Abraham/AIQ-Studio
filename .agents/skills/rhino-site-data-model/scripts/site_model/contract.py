"""Shared, standard-library-only contracts for source, terrain, and 2D handoffs.

These checks validate structure and coordinate frames. Geometry preparation must
also check polygon topology with its geometry library before it writes objects.
"""

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

CHECKPOINT_SCHEMA = "rhino-site-model-checkpoint"
CONTRACT_VERSION = 1
_RUN_TEXT = ("site_name", "generated_utc", "semantic_source", "source_release",
             "projected_crs", "vertical_datum", "source_manifest_path", "report_path")


def _number(value, label):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(label + " must be a finite number")


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be a nonempty string")


def _vector(value, count, label, flat=False):
    if not isinstance(value, (list, tuple)) or len(value) != count:
        raise ValueError(label + " has the wrong coordinate count")
    for component in value:
        _number(component, label)
    if flat and value[2] != 0:
        raise ValueError(label + " must have Z=0")


def _ring(points, label):
    if not isinstance(points, list) or len(points) < 4:
        raise ValueError(label + " must be a closed ring with at least four points")
    for point in points:
        _vector(point, 3, label, flat=True)
    if points[0] != points[-1]:
        raise ValueError(label + " must be closed")
    if len({tuple(p[:2]) for p in points[:-1]}) < 3:
        raise ValueError(label + " needs three distinct vertices")
    origin = points[0]
    area = sum((a[0] - origin[0]) * (b[1] - origin[1]) -
               (b[0] - origin[0]) * (a[1] - origin[1]) for a, b in zip(points, points[1:]))
    if not math.isfinite(area) or area == 0:
        raise ValueError(label + " has zero or invalid area")


def _parts(parts, label, polygons_only=False):
    if not isinstance(parts, list) or not parts:
        raise ValueError(label + " must contain geometry parts")
    for index, part in enumerate(parts):
        name = "{}[{}]".format(label, index)
        if not isinstance(part, dict):
            raise ValueError(name + " must be an object")
        kind = part.get("kind")
        points = part.get("points")
        if kind == "Polygon":
            _ring(points, name)
            holes = part.get("holes", [])
            if not isinstance(holes, list):
                raise ValueError(name + ".holes must be a list")
            for hole in holes:
                _ring(hole, name + ".hole")
        elif kind in ("Point", "LineString") and not polygons_only:
            if not isinstance(points, list) or (kind == "Point" and len(points) != 1) or (kind == "LineString" and len(points) < 2):
                raise ValueError(name + " has the wrong number of points")
            for point in points:
                _vector(point, 3, name, flat=True)
            if part.get("holes"):
                raise ValueError(name + " cannot contain holes")
        else:
            raise ValueError(name + " has an unsupported geometry kind")


def _canonical(data):
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Data must contain valid finite JSON values") from error


def validate_sources(data):
    """Return the source object after structural checks; do not change it."""
    if not isinstance(data, dict):
        raise ValueError("Sources must be an object")
    if "terrain" in data and data["terrain"] != {}:
        raise ValueError("Sources cannot contain terrain; use a separate terrain file")
    run = data.get("run")
    if not isinstance(run, dict):
        raise ValueError("Sources require run metadata")
    for name in _RUN_TEXT:
        _text(run.get(name), "run." + name)
    for name in ("origin_wgs84", "origin_projected"):
        _vector(run.get(name), 2, "run." + name)
    lon, lat = run["origin_wgs84"]
    if not -180 <= lon <= 180 or not -90 <= lat <= 90:
        raise ValueError("run.origin_wgs84 is outside longitude/latitude bounds")
    for name in ("site", "context"):
        section = data.get(name)
        if not isinstance(section, dict):
            raise ValueError(name + " must be an object")
        _parts(section.get("parts"), name + ".parts", polygons_only=True)
    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("features must be a list")
    identities = set()
    for feature in features:
        if not isinstance(feature, dict):
            raise ValueError("Each feature must be an object")
        for name in ("id", "feature_type"):
            _text(feature.get(name), "feature." + name)
        identity = (feature["feature_type"], feature["id"])
        if identity in identities:
            raise ValueError("Duplicate source feature: " + repr(identity))
        identities.add(identity)
        category = feature.get("category_path")
        if not isinstance(category, list) or not category:
            raise ValueError("feature.category_path must contain names")
        for name in category:
            _text(name, "category name")
            if "::" in name:
                raise ValueError("Category names cannot contain the layer separator ::")
        if not isinstance(feature.get("properties"), dict) or not isinstance(feature.get("sources"), list):
            raise ValueError("Features require properties and sources")
        _parts(feature.get("parts"), "feature.parts")
    _canonical(data)
    return data


def source_digest(data):
    """Hash source content, excluding output paths, time, and vertical datum."""
    validate_sources(data)
    payload = dict(data)
    payload.pop("terrain", None)
    payload["run"] = {key: value for key, value in data["run"].items()
                      if key not in ("generated_utc", "report_path", "source_manifest_path", "vertical_datum")}
    return hashlib.sha256(_canonical(payload)).hexdigest()


def validate_terrain(terrain, sources):
    """Check a finite affine sample grid in the exact source coordinate frame."""
    validate_sources(sources)
    if not isinstance(terrain, dict):
        raise ValueError("Terrain must be an object")
    _text(terrain.get("projected_crs"), "terrain.projected_crs")
    _vector(terrain.get("origin_projected"), 2, "terrain.origin_projected")
    for key in ("projected_crs", "origin_projected"):
        if terrain.get(key) != sources["run"][key]:
            raise ValueError("Terrain " + key + " does not match the sources")
    _text(terrain.get("vertical_datum"), "terrain.vertical_datum")
    rows = terrain.get("rows")
    if not isinstance(rows, list) or len(rows) < 2 or not isinstance(rows[0], list) or len(rows[0]) < 2:
        raise ValueError("Terrain needs at least two rows and two columns")
    width = len(rows[0])
    for row in rows:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError("Terrain rows must have equal lengths")
        for point in row:
            _vector(point, 3, "terrain point")
    origin, column, row = rows[0][0], rows[0][1], rows[1][0]
    ax, ay = column[0] - origin[0], column[1] - origin[1]
    bx, by = row[0] - origin[0], row[1] - origin[1]
    determinant = ax * by - ay * bx
    if not math.isfinite(determinant) or abs(determinant) < 1e-12:
        raise ValueError("Terrain grid axes are degenerate")
    tolerance = max(math.hypot(ax, ay), math.hypot(bx, by)) * 1e-7
    for r, points in enumerate(rows):
        for c, point in enumerate(points):
            for actual, expected in zip(point[:2], (origin[0] + c * ax + r * bx, origin[1] + c * ay + r * by)):
                if not math.isclose(actual, expected, rel_tol=0, abs_tol=tolerance):
                    raise ValueError("Terrain coordinates must form a regular affine grid")
    return terrain


def load_json(path):
    """Read a JSON object; reject duplicate keys and nonfinite constants."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise ValueError("Invalid JSON constant: " + value)

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeError) as error:
        raise ValueError("Cannot read JSON file: " + str(path)) from error
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain an object")
    _canonical(data)  # Also reject floating-point overflow such as 1e999.
    return data


def atomic_json(path, data):
    """Replace a JSON file atomically after a complete same-directory write."""
    encoded = _canonical(data)
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as error:
        raise ValueError("Cannot write JSON file: " + str(path)) from error
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def confined_path(root, path):
    """Resolve a project path and reject traversal or symlinks outside its root."""
    try:
        root = Path(root).resolve()
        candidate = Path(path)
        candidate = (candidate if candidate.is_absolute() else root / candidate).resolve()
        candidate.relative_to(root)
        return candidate
    except (ValueError, OSError, RuntimeError) as error:
        raise ValueError("Path must remain inside the project root: " + str(path)) from error


def file_sha256(path):
    digest = hashlib.sha256()
    try:
        with Path(path).open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise ValueError("Cannot hash file: " + str(path)) from error
    return digest.hexdigest()


def check_checkpoint(checkpoint, sources, model_path):
    """Reject changed sources or model bytes before preparing a 3D stage."""
    if not isinstance(checkpoint, dict) or checkpoint.get("schema") != CHECKPOINT_SCHEMA or type(checkpoint.get("version")) is not int or checkpoint["version"] != CONTRACT_VERSION:
        raise ValueError("Unsupported 2D checkpoint schema or version")
    if checkpoint.get("checked_and_saved") is not True:
        raise ValueError("The 2D model must be checked and saved before 3D preparation")
    if checkpoint.get("source_digest") != source_digest(sources):
        raise ValueError("The 2D checkpoint refers to different source data")
    if checkpoint.get("model_sha256") != file_sha256(model_path):
        raise ValueError("The saved 2D model differs from its checkpoint")
    if "audit_path" in checkpoint or "audit_sha256" in checkpoint:
        _text(checkpoint.get("audit_path"), "checkpoint.audit_path")
        _text(checkpoint.get("audit_sha256"), "checkpoint.audit_sha256")
        audit = Path(checkpoint["audit_path"])
        audit = audit if audit.is_absolute() else Path(model_path).resolve().parent / audit
        if checkpoint["audit_sha256"] != file_sha256(audit):
            raise ValueError("The 2D audit differs from its checkpoint")
    return checkpoint
