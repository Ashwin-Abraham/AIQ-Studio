# Water flow script contract

Use [analyze_water_flow.py](../scripts/analyze_water_flow.py) from external Python. It reads a saved model or exported mesh, writes JSON, and leaves the Rhino model unchanged. Read [the map workflow](water-flow-and-watersheds.md) to add and draw its results in Rhino and SVG.

## Inputs

- `--input`: a metre-unit `.3dm` file or terrain JSON. For a live model with unsaved changes, export the selected terrain and metadata to JSON; do not use an older saved file.
- `--layer`: exact `.3dm` layer path; default `AIQ Site::3D::Terrain`. Hidden and locked objects are included. Every object on the selected layer must be a mesh. Join surfaces only when they share the same coordinate frame and ground source.
- `--output`: a new run directory. Existing directories are rejected to protect earlier results.
- `--product`: `both` (default), `flow`, or `watersheds`. Both products share the same routing method.
- `--min-area-m2`: minimum contributing area for displayed flow lines; default 100. Use zero to retain every routed edge before the length filter.

- `--min-length-m`: minimum visible branch length in plan; default zero. Short downstream links stay when a longer branch needs them.
- `--max-fill-area-m2` and `--max-fill-depth-m`: combined original catchment area and maximum elevation rise for an accepted fill. Both default to zero, which disables filling. Map starting values are 5000 m² and 0.30 m. Large catchments anchor the flood; connected fill components that exceed either limit remain unchanged. The method makes one pass and does not guarantee that every small catchment will merge.

JSON example:

```json
{
  "units": "metres",
  "metadata": {
    "crs": "EPSG:27700",
    "origin_projected": [540214.1, 180110.7],
    "vertical_datum": "ODN",
    "terrain_source": "Record source and resolution here"
  },
  "vertices": [[0, 0, 2], [10, 0, 1], [0, 10, 0]],
  "faces": [[0, 1, 2]],
  "source_faces": [{"object_id": "terrain-object-id", "face": 0}]
}
```

Use zero-based vertex indices. Faces can be triangles or quads; quads split along A-C. `source_faces` is optional but must match the face count when supplied. Keep vertex order stable to retain IDs and tie choices.

The `.3dm` reader joins identical XYZ vertices and reads `site.projected_crs`, `site.origin_projected`, `site.vertical_datum`, and `site.terrain` document text. JSON vertices must already be joined. Near-coincident seams need an explicit repair before calculation. A missing datum is acceptable for relative flow but must be reported as unknown.

The script rejects nonfinite coordinates, invalid indices, unused vertices, zero-plan-area faces, overlapping surfaces, duplicate XY vertices, and non-manifold connectivity. Holes remain open. Coordinates must use the same metre scale in XY and Z. Empty terrain produces a `skipped` run with reason `no terrain`.

## Outputs

| File | Contents |
| --- | --- |
| `run.json` | Status, source and geometry hashes, method, settings, checks, counts, and limitations. |
| `drainage.json` | Shared vertices, triangles, source faces, receivers, terminals, and contributing areas. Analysis vertices can be raised; `source_vertices` preserves the original coordinates. A null receiver stops flow. |
| `flow-paths.json` | XYZ lines between junctions, vertex IDs, area at each vertex, terminal ID, plan length, and flat/filled-step indices. Each selected edge occurs once. |
| `watersheds.json` | XYZ cells for Rhino and dissolved XY basin polygons for SVG, with holes, IDs, colours, terminal types, and areas. |

Flow and watershed files have the same geometry hash. A skipped run writes only `run.json`. Calculation or file errors return exit code 1 and create no final run directory; earlier results stay unchanged. Invalid command syntax returns 2. Successful and skipped runs return 0; always read the status.

Contributing area is horizontal area in m², assuming equal rainfall per unit area. It is not discharge. Filling changes only the analysis elevations used for routing. Record accepted fills, rejected component count, and before/after basin counts. Check downhill flow against the analysis surface, not the source elevations. One third of each triangle's area belongs to each vertex. Basin boundaries follow these cells and depend on mesh resolution. Flat routing uses exactly equal Z values; the script neither rounds heights nor smooths noise.

The implementation separates [mesh checks](../scripts/terrain_water/mesh.py), [bounded filling](../scripts/terrain_water/depressions.py), [shared routing](../scripts/terrain_water/routing.py), [flow tracing](../scripts/terrain_water/flow.py), [watersheds](../scripts/terrain_water/watersheds.py), and [file handling](../scripts/terrain_water/files.py). Keep these responsibilities separate when extending the script.

From the repository root, run `python -B -m unittest discover -s tests/terrain-water -v`. Tests use small terrains and saved Rhino fixtures; live Rhino display and SVG layout still need project review.
