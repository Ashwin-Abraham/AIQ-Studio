# Processed data contract

The build script accepts one UTF-8 JSON file. Coordinates are local projected metres.

## Top level

```json
{
  "run": {},
  "site": {},
  "context": {},
  "terrain": {},
  "features": []
}
```

## Run

Required fields:

- `site_name`
- `generated_utc`
- `semantic_source`
- `source_release`
- `projected_crs`
- `origin_wgs84`: `[longitude, latitude]`
- `origin_projected`: `[easting, northing]`
- `vertical_datum`
- `source_manifest_path`
- `report_path`

## Site and context

`site.parts` and `context.parts` use the polygon-part format below. Context also records `selection_method`, `bounds_wgs84`, and `bounds_local`.

## Terrain

Terrain can be absent. When present:

```json
{
  "provider": "Provider name",
  "dataset": "Dataset name",
  "vertical_datum": "Datum name",
  "rows": [
    [[0.0, 0.0, 4.2], [5.0, 0.0, 4.3]],
    [[0.0, 5.0, 4.1], [5.0, 5.0, 4.2]]
  ]
}
```

Rows must form a regular or affine grid. The build script uses bilinear height sampling.

## Feature

```json
{
  "id": "source feature ID",
  "feature_type": "building",
  "version": 1,
  "name": "Optional name",
  "category_path": ["Buildings", "Footprints", "Residential"],
  "properties": {},
  "sources": [],
  "parts": []
}
```

Retain exact source properties and sources. Do not replace them with the generic category.

## Geometry parts

Point:

```json
{"kind": "Point", "points": [[10.0, 20.0, 0.0]]}
```

Line:

```json
{"kind": "LineString", "points": [[0.0, 0.0, 0.0], [10.0, 10.0, 0.0]]}
```

Polygon:

```json
{
  "kind": "Polygon",
  "points": [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 10.0, 0.0], [0.0, 0.0, 0.0]],
  "holes": []
}
```

Flatten multipolygons into several polygon parts. Keep `source_part_index` and `clipped_part_index` when one source feature creates several working parts.

For buildings and building parts, keep source height fields in `properties`. The build script applies the placement rules in `building-placement.md`.
