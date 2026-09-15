---
name: rhino-site-data-model
description: Build or update a geospatial Rhino site data model from a user-defined site. Use for Overture-based buildings, transport, water, land use, places, terrain, classified Rhino layers, source metadata, and model validation. Do not use for ordinary Rhino modelling that has no geographic site data.
---

# Rhino Site Data Model

Create a reproducible `.3dm` site model with source geometry, optional 3D content, clear classifications, and a validation report.

## Essential rules

- Use `AIQ Site::` as the generated root layer.
- Always create and include the 2D source data. Put it at Z = 0. Hide its parent layer by default.
- Use Overture Maps as the default semantic source. Keep the exact Overture taxonomy and provenance as object metadata.
- Use authoritative national or local data when it is better for the requested theme. Keep conflicting sources in separate branches. Do not silently merge them.
- Use OSM only as a documented fallback or enrichment source.
- Clip model geometry to the selected context. Keep the complete downloaded files in the source cache.
- Do not infer water levels or unresolved bridge, tunnel, or underground positions.
- Generate every building volume along world `+Z`. Never let curve direction control the volume direction.
- Record validation failures. Do not stop model generation only because a validation check fails.
- Do not overwrite or modify an existing model unless the user has authorized that target and its state is safe.

## Project guidance

- Read [Python scripting guidance](../../PYTHON-SCRIPTING-GUIDANCE.md) before you create or adapt Python scripts, manage dependencies, or select a runtime environment.
- Read [project folder organisation](../../PROJECT-FOLDER-ORGANISATION.md) before you create project folders or place models, source data, processed data, reports, scripts, or exports.

## Workflow

1. Resolve the site and target Rhino model. Use this boundary priority: user geometry, selected mapped feature, user-approved inferred boundary, then context-only geometry.
2. Read [source and context rules](references/source-and-context.md). Select the source release and context.
3. Read [Rhino structure](references/rhino-structure.md). Resolve units, coordinates, layers, and the existing-model policy.
4. When 3D buildings are in scope, read [building placement](references/building-placement.md) before creating geometry.
5. Acquire and process the data. Use the scripts in `scripts/` when their input contract fits. Read [processed data contract](references/processed-data-contract.md) before adapting the build script.
6. Build the Rhino model. Preserve exact source IDs, properties, versions, and source records on objects.
7. Read [validation and reporting](references/validation-and-reporting.md). Reopen the output, run the checks, and inspect plan and perspective views when Rhino control is available.
8. Deliver the model, source cache, processed data, manifest, report, and audit. State the Overture release in the final response.

## Reusable scripts

- `scripts/download_overture.py`: download selected Overture feature types and write a source manifest.
- `scripts/derive_context.py`: select a projected CRS and calculate context bounds from a site boundary.
- `scripts/build_rhino_site_model.py`: build a `.3dm` from the processed data contract.
- `scripts/validate_site_model.py`: audit a saved `.3dm` and write JSON results.

Treat the scripts as maintained starting points. Adapt source-specific parsing outside `SKILL.md` when a site needs a different authoritative dataset.
