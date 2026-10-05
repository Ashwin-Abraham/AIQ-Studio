"""Create flow paths and watersheds from one checked terrain drainage graph."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True

try:
    import shapely
except ImportError as error:
    raise SystemExit("Terrain water analysis requires shapely >=2,<3 in the selected runtime.") from error

from terrain_water.files import publish, read_input
from terrain_water.depressions import fill_small_depressions
from terrain_water.flow import trace_paths
from terrain_water.mesh import prepare_mesh
from terrain_water.routing import route
from terrain_water.watersheds import delineate


def analyze(input_path, output, layer="AIQ Site::3D::Terrain", product="both", min_area_m2=100.0,
            min_length_m=0.0, max_fill_area_m2=0.0, max_fill_depth_m=0.0):
    """Return the run report; write only into a new output directory."""
    if product not in ("both", "flow", "watersheds"):
        raise ValueError("Product must be both, flow, or watersheds.")
    if not math.isfinite(min_area_m2) or min_area_m2 < 0:
        raise ValueError("Minimum contributing area must be finite and nonnegative.")
    if any(not math.isfinite(v) or v < 0 for v in (min_length_m, max_fill_area_m2, max_fill_depth_m)):
        raise ValueError("Length and fill limits must be finite and nonnegative.")
    if Path(output).exists():
        raise ValueError("Output already exists. Select a new run directory.")
    vertices, faces, sources, source = read_input(input_path, layer)
    report = {"schema": "terrain-water-v1", "source": source, "product": product,
              "units": "metres", "method": "steepest mesh edge; single receiver",
              "quad_diagonal": "A-C", "flat_rule": "exact Z; shortest edge distance to lower exit",
              "depressions": "bounded fill" if max_fill_area_m2 and max_fill_depth_m else "retained",
              "min_area_m2": min_area_m2, "min_length_m": min_length_m,
              "limitations": ["Mesh-edge paths approximate surface flow.",
                              "Flats with no lower exit have no resolved direction.",
                              "Boundary exits include holes and data edges.",
                              "Terrain only: no pipes, infiltration, or rainfall volumes."]}
    if not vertices and not faces:
        report.update(status="skipped", reason="no terrain")
        publish(output, {"run.json": report})
        return report
    terrain = prepare_mesh(vertices, faces)
    drainage = route(terrain)
    original_count = len(drainage.terminals)
    conditioned, conditioning = fill_small_depressions(terrain, drainage, max_fill_area_m2, max_fill_depth_m)
    if conditioning["changed_vertices"]:
        drainage = route(conditioned)
    geometry_hash = hashlib.sha256(json.dumps([vertices, faces], allow_nan=False).encode()).hexdigest()
    report.update(status="complete", geometry_sha256=geometry_hash,
                  vertices=len(vertices), triangles=len(terrain.triangles),
                  plan_area_m2=math.fsum(terrain.local_area),
                  terminal_counts=dict(Counter(t["kind"] for t in drainage.terminals.values())),
                  flat_link_count=len(drainage.flat_links),
                  original_watersheds=original_count,
                  conditioning=conditioning,
                  validation={"acyclic": True, "no_uphill_links_on_analysis_surface": True, "area_balance": True},
                  versions={"python": sys.version.split()[0]})
    report["versions"]["shapely"] = shapely.__version__
    graph = {"geometry_sha256": geometry_hash, "vertices": conditioned.vertices,
             "source_vertices": terrain.vertices,
             "triangles": terrain.triangles,
             "source_faces": [sources[i] for i in terrain.source_faces],
             "receiver": drainage.receiver, "terminal": drainage.terminal,
             "terminals": drainage.terminals, "area_m2": drainage.accumulation}
    documents = {"drainage.json": graph}
    if product in ("both", "flow"):
        paths = trace_paths(conditioned, drainage, min_area_m2, min_length_m)
        for path in paths:
            path["filled_steps"] = [i for i, (a, b) in enumerate(zip(path["vertex_ids"], path["vertex_ids"][1:]))
                                    if conditioned.vertices[a][2] != terrain.vertices[a][2]
                                    or conditioned.vertices[b][2] != terrain.vertices[b][2]]
        documents["flow-paths.json"] = {"geometry_sha256": geometry_hash, "paths": paths}
        report["flow_paths"] = len(paths)
        if not paths:
            report["flow_note"] = "No lines meet the area and length limits, or all terrain is unresolved."
    if product in ("both", "watersheds"):
        watersheds = delineate(terrain, drainage)
        for cell in watersheds["cells"]:
            cell["source_face"] = sources[cell["source_face"]]
        documents["watersheds.json"] = {"geometry_sha256": geometry_hash, **watersheds}
        report["watersheds"] = len(watersheds["basins"])
    report["outputs"] = list(documents) + ["run.json"]
    documents["run.json"] = report
    publish(output, documents)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Terrain JSON or saved metre-unit .3dm")
    parser.add_argument("--output", required=True, type=Path, help="New run directory")
    parser.add_argument("--layer", default="AIQ Site::3D::Terrain", help="Exact Rhino layer path")
    parser.add_argument("--product", choices=("both", "flow", "watersheds"), default="both")
    parser.add_argument("--min-area-m2", type=float, default=100.0, help="Flow display threshold only")
    parser.add_argument("--min-length-m", type=float, default=0.0, help="Minimum displayed branch length; preserve downstream tails")
    parser.add_argument("--max-fill-area-m2", type=float, default=0.0, help="Maximum combined original catchment area; zero disables fill")
    parser.add_argument("--max-fill-depth-m", type=float, default=0.0, help="Maximum analysis elevation change; zero disables fill")
    args = parser.parse_args(argv)
    try:
        report = analyze(args.input, args.output, args.layer, args.product, args.min_area_m2,
                         args.min_length_m, args.max_fill_area_m2, args.max_fill_depth_m)
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
        print(f"Terrain water analysis failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
