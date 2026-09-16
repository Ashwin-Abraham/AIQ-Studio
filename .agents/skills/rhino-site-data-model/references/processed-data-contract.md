# Processed data contract

Use `scripts/site_model/contract.py` for source, terrain, and checkpoint checks. It uses only the Python standard library. Read the [staged workflow](staged-workflow.md) for commands and stage order.

## Shared sources

One UTF-8 JSON object contains shared source geometry. Coordinates use local projected metres, with every source point at Z = 0.

```json
{
  "run": {},
  "site": {"parts": []},
  "context": {"parts": []},
  "features": []
}
```

Terrain belongs in a separate file. An empty legacy `terrain: {}` is accepted; populated terrain is rejected. An empty feature list is valid, but both site and context need polygon parts.

The `run` object requires nonempty strings for `site_name`, `generated_utc`, `semantic_source`, `source_release`, `projected_crs`, `vertical_datum`, `source_manifest_path`, and `report_path`. Use `"not set"` for the source vertical datum when no terrain datum applies. It also requires `origin_wgs84: [longitude, latitude]` and `origin_projected: [easting, northing]`.

Context should retain `selection_method`, `bounds_wgs84`, and `bounds_local` for reporting. Do not change the coordinate frame between stages.

## Features and parts

```json
{
  "id": "source feature ID",
  "feature_type": "building",
  "version": 1,
  "name": "Optional name",
  "category_path": ["Buildings", "Footprints", "Residential"],
  "properties": {},
  "sources": [],
  "parts": [{
    "kind": "Polygon",
    "points": [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 0, 0]],
    "holes": []
  }]
}
```

Each feature needs a nonempty string ID and type, at least one category name, properties, source records, and geometry parts. The pair `(feature_type, id)` must be unique. Category names cannot contain the Rhino layer separator `::`. Retain exact source properties, including height fields; do not replace them with generic categories.

Parts use these formats:

- `Point`: `points` contains exactly one `[x, y, 0]` coordinate.
- `LineString`: `points` contains at least two coordinates.
- `Polygon`: `points` contains a closed exterior ring. `holes` contains closed interior rings.

Each ring needs at least three distinct vertices and nonzero signed area. Keep the repeated closing point. Flatten multipolygons into polygon parts. Keep `source_part_index` and `clipped_part_index` where available. Contract checks cover structure; geometry preparation must also check polygon topology.

## Terrain

Terrain is needed only for a 3D run that selects terrain placement. It must declare the exact source coordinate frame and a nonempty vertical datum:

```json
{
  "provider": "Provider name",
  "dataset": "Dataset name",
  "projected_crs": "EPSG:27700",
  "origin_projected": [500000, 180000],
  "vertical_datum": "ODN",
  "rows": [
    [[0, 0, 4.2], [5, 0, 4.3]],
    [[0, 5, 4.1], [5, 5, 4.2]]
  ]
}
```

Rows must have equal lengths and contain at least two rows and two columns. XY coordinates must form a regular affine grid with independent axes. All coordinates and heights must be finite. Height sampling uses bilinear interpolation. Keep terrain beneath mapped water. A 3D run without terrain requires an explicit flat elevation; absent terrain is not an instruction to assume zero.

## Saved checkpoint

The coordinator writes a checkpoint after it saves, reopens, and checks the 2D model:

```json
{
  "schema": "rhino-site-model-checkpoint",
  "version": 1,
  "source_digest": "SHA-256 of shared source content",
  "model_sha256": "SHA-256 of saved model bytes",
  "checked_and_saved": true,
  "audit_path": "path to the saved audit",
  "audit_sha256": "SHA-256 of audit bytes"
}
```

`checked_and_saved` records completion of the check and save; it does not mean every geometry check passed. Read the audit failures. A 3D run verifies the source digest and saved model hash before preparation. If an audit reference is present, its path and hash must both be present and its bytes must match.

The source digest excludes `generated_utc`, `report_path`, `source_manifest_path`, and `vertical_datum` from run metadata. It includes source geometry, properties, release, and coordinate frame. Empty legacy terrain is excluded. The coordinator updates the saved model hash after a completed 3D run so later 3D runs can replace that stage without a false stale-file error.

## File integrity

Use `load_json` to reject duplicate keys and nonfinite values. Use `atomic_json` for complete, same-directory file replacement. Resolve project paths with `confined_path`; paths and symlinks must remain inside the project root. Do not share mutable output filenames between workers.
