# Source and context rules

## Boundary

Use this priority:

1. Geometry supplied by the user.
2. An exact mapped site feature selected by the user.
3. An inferred boundary that the user approves.
4. A context boundary without a separate site polygon.

A map image is a visual reference unless it has geographic control points or a reliable scale and the user asks for image measurement.

If there is no exact mapped feature, show or describe the candidate before model generation. Get user approval.

## Context

Use the map viewport when its geographic bounds are directly available and reliable. Otherwise, estimate the context boundary and add a small margin of safety.
Clip working model geometry to the context boundary. Keep the complete downloaded source files unchanged in the cache. Record both the download bounds and model context bounds.

## Semantic sources

Use Overture Maps by default for:

- buildings and building parts;
- transport segments;
- water;
- land and land use;
- places.

Use the latest Overture release unless the user pins a release. Record the release ID, retrieval time, download bounds, file hashes, and tool versions.

Use `scripts/download_overture.py` with `--types` to select themes and `--workers 1` through `--workers 4` to select acquisition concurrency. Parallel acquisition requires an explicit `--release` so every worker uses the same release. A sequential download can resolve the first release and pin it for later themes. Give separate download invocations separate output directories; each invocation publishes one manifest after its downloads succeed.

Use `scripts/process_overture.py` to normalize the cache without terrain. It requires `--input-dir`, `--site`, `--context`, `--manifest`, `--site-name`, `--output`, and `--report-path`. Use `--types` for a selected subset; otherwise it reads available supported theme files. Each selected file must have a matching SHA-256 entry in the source manifest. A missing or changed manifest entry stops normalization. Do not modify the raw files or hashes to bypass the check.

Independent normalization workers can write separate theme outputs. Before a model run, combine their feature lists under one unchanged run/site/context frame and validate the complete source set, including duplicate identities. The staged runner accepts one combined source JSON; it does not merge theme files automatically. Terrain acquisition can continue independently while these 2D sources are processed.

Do not repeat the release ID on every object. Put it in Rhino document user text, the run-information annotation, the report, and the final response.

Each source object must keep:

- feature ID and feature type;
- feature version;
- exact source properties;
- exact source records and licences;
- selected generic classification;
- original source classification.

## Other sources

Prefer an authoritative national or local terrain model over a global terrain model. Record its horizontal CRS, vertical datum, resolution, survey period, accuracy statement, licence, and file hash.

If no suitable authoritative terrain exists, ask the user to select a global DEM or a flat model. Do not silently use a lower-quality terrain source.

When an authoritative dataset conflicts with Overture, keep each source in a separate layer branch. Mark the selected modelling source. Do not silently merge or delete either dataset.

Use OSM only when Overture lacks a needed feature or property, or when the user asks for it. Label it as fallback or enrichment data.
