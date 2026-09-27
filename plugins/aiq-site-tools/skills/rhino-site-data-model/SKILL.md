---
name: rhino-site-data-model
description: Build or update a geospatial Rhino site model from a site boundary, with checked 2D source layers, optional 3D content, and a validation report.
---

# Rhino Site Data Model

Create a reproducible `.3dm` site model with source geometry, optional 3D content, clear classifications, and a validation report.

## Essential rules

- Use `AIQ Site::` as the generated root layer.
- Always create and include the 2D source data at Z = 0. Show it during the 2D stage. Hide its parent layer when the 3D stage is complete.
- Use Overture Maps as the default semantic source. Keep the exact Overture taxonomy and provenance as object metadata.
- Use authoritative national or local data when it is better for the requested theme. Keep conflicting sources in separate branches. Do not silently merge them.
- Use OSM only as a documented fallback or enrichment source.
- Clip model geometry to the selected context. Keep the complete downloaded files in the source cache.
- Do not infer water levels or unresolved bridge, tunnel, or underground positions.
- Generate every building volume along world `+Z`. Never let curve direction control the volume direction.
- Record validation failures. Do not stop model generation only because a validation check fails.

## Project guidance

- Read [subagent delegation guidance](references/SUBAGENT-DELEGATION-GUIDANCE.md) before you delegate work.
- Read [Rhino document editing guidance](references/RHINO-DOCUMENT-EDITING-GUIDANCE.md) before you select an editing method or change a Rhino document. Follow its rules for progressive edits, document identity, progress display, cancellation, undo, and saving.
- Read [Python scripting guidance](references/PYTHON-SCRIPTING-GUIDANCE.md) before you create or adapt Python scripts, manage dependencies, or select a runtime environment.
- Read [project folder organisation](references/PROJECT-FOLDER-ORGANISATION.md) before you create project folders or place models, source data, processed data, reports, scripts, or exports.

## Workflow

Run independent preparation steps in parallel when workers are available. Start the single Rhino writer when the first ordered batch is ready. Prepare later batches while it writes.

1. Resolve the target Rhino model. Create a model if there is no existing model at the specified location.
2. Resolve the site boundary. Use this boundary priority: user geometry, selected mapped feature, user-approved inferred boundary, then context-only geometry.
3. Run `scripts/preflight.py` with the selected external Python. If it reports missing packages, provision a managed environment under [Python scripting guidance](references/PYTHON-SCRIPTING-GUIDANCE.md) and run the check again. Continue when every package is available. Confirm Rhino 8 before live document editing.
4. Read [source and context rules](references/source-and-context.md). Select the source release and context.
5. Read [Rhino structure](references/rhino-structure.md) and the [2D cartographic style reference](references/2d-cartographic-style.md). Resolve units, coordinates, layers, draw order, and the existing-model policy.
6. Find the best available source for terrain and ask the user if a 3D model with terrain and projected objects is required (alongside a flat 2D model).
7. When 3D buildings are in scope, read [building placement](references/building-placement.md) before creating geometry.
8. Acquire independent source themes in parallel where useful. Give each worker separate outputs. Read the [processed data contract](references/processed-data-contract.md) and [staged workflow](references/staged-workflow.md). Process shared source geometry without terrain. Terrain downloads can run during 2D work.
9. Use `scripts/run_site_model.py` to prepare geometry in parallel and apply ready batches with one writer. Use the live backend for visible edits in the open target document. Import, check, and save all 2D geometry before preparing 3D geometry. Resume 3D from the checked source data and saved checkpoint, with separate terrain or an explicit flat elevation.
10. Read [validation and reporting](references/validation-and-reporting.md). Check each saved stage and record failures. Inspect a plan view for 2D and plan and perspective views for 3D when Rhino control is available.
11. Deliver the model, source cache, processed data, manifest, report, and audit. State the Overture release in the final response.

## Reusable scripts

- `scripts/download_overture.py`: download selected Overture feature types and write a source manifest.
- `scripts/derive_context.py`: select a projected CRS and calculate context bounds from a site boundary.
- `scripts/process_overture.py`: convert cached source features to shared, local 2D source data.
- `scripts/run_site_model.py`: run a 2D stage, a 3D stage, both stages in order, an audit, or legacy-data migration.
- `scripts/site_model/`: shared contract checks, geometry preparation, one document writer, stage coordination, and audits.
- `scripts/disable_backface_culling.py`: set the Rhino application display option when needed.

Treat the scripts as maintained starting points. Adapt source-specific parsing outside `SKILL.md` when a site needs a different authoritative dataset.
