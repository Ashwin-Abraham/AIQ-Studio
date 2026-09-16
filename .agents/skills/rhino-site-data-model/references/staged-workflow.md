# Staged workflow

The shared sources are independent of terrain. Both 2D and 3D preparation read them. The 3D stage also needs a saved checkpoint and either checked terrain or an explicit flat elevation. It does not reconstruct source data from Rhino curves.

## Modules and ownership

- `contract.py` checks source data, terrain frames, file hashes, and checkpoint identity.
- `geometry.py` prepares geometry and metadata without changing the target document.
- `writer.py` is the only module that changes the target document.
- `workflow.py` controls stage order, preparation workers, saves, and checkpoints.
- `audit.py` checks saved geometry for the selected stage.

Independent source acquisition, terrain downloads, and geometry preparation can use workers or sub-agents. Give each sub-agent a separate output path and a bounded theme or partition. Use the same release, CRS, and origin. Keep document changes, saves, and checkpoint updates under one writer. `--workers` selects preparation workers; it does not start Codex sub-agents.

Geometry preparation accepts 1 to 8 workers. For parallel preparation inside Rhino, set `--worker-python` to the managed external Python executable selected under [Python scripting guidance](../../../PYTHON-SCRIPTING-GUIDANCE.md). That environment must have the script dependencies. Do not use Rhino's host executable as a Python worker. Use `--partition-size` to bound the number of source features in each preparation job; it is separate from the writer's object `--batch-size`.

## Live document

Use the default `live` backend inside Rhino Python. Before the run, create and open the target file if needed. Capture the open target and check its path, serial number, saved state, units, and frame as required by [Rhino document editing guidance](../../../RHINO-DOCUMENT-EDITING-GUIDANCE.md). The command does not replace this setup.

The writer applies bounded batches on Rhino's main interface thread, updates progress, redraws, and checks cancellation. Set `--batch-size` to suit the document. Preparation can continue while the writer applies ready batches. A failed or cancelled stage must not leave its incomplete edits; completed saved stages remain available.

Use `--backend file` only for an explicitly selected offline workflow or tests. It cannot show progressive changes in the open Rhino document. Do not use it as an automatic fallback when a live operation fails.

## Commands

The examples below show arguments for `scripts/run_site_model.py`. Resolve the script path from the skill directory. Run live commands inside Rhino Python, not in an external Python process. All input and output paths must resolve inside `--project-root`.

Create the 2D model without terrain:

```text
run_site_model.py --project-root PROJECT --input processed/sources.json --output Models/site.3dm --stage 2d --workers 4 --worker-python "MANAGED_PYTHON" --batch-size 500
```

After the complete 2D model is checked and saved, add or replace 3D with terrain:

```text
run_site_model.py --project-root PROJECT --input processed/sources.json --output Models/site.3dm --stage 3d --terrain processed/terrain.json --workers 4 --worker-python "MANAGED_PYTHON" --batch-size 500
```

For a documented flat base, replace `--terrain processed/terrain.json` with `--flat-elevation 0`. Choose one placement mode. Use `--stage all` to run 2D and then 3D with the same checkpoint boundary. It does not prepare 3D before the 2D save and check.

Use `--checkpoint PATH` to change the checkpoint location. By default, the checkpoint is `Models/site.3dm.checkpoint.json`; stage audits use `Models/site.3dm.2d.audit.json` and `Models/site.3dm.3d.audit.json`.

The generated report is `Models/site.3dm.report.md`. The source `run.report_path` remains provenance metadata; set it to this output location during normalization so the run annotation points to the report.

Check a saved model without changing its geometry:

```text
run_site_model.py --project-root PROJECT --output Models/site.3dm --stage 2d --audit-only
```

Use `--stage 3d` to check a completed 3D model, including its retained 2D sources. Review audits use `Models/site.3dm.2d.review.audit.json` or `Models/site.3dm.3d.review.audit.json`; they do not replace the audit referenced by the checkpoint. Add `--visual-inspection passed|failed|not-possible` and `--visual-notes` to record an actual visual review. The programmatic audit does not perform visual inspection.

## Repeat runs and recovery

Generated objects carry `site_owner`, `site_stage`, and a stable `site_key`. Repeat runs replace owned outputs for the selected stage. They preserve user objects. A fresh 2D stage removes old owned 3D outputs because those outputs can refer to changed sources. A 3D stage keeps the checked 2D objects.

Do not remove existing objects solely because their layer starts with `AIQ Site`. Legacy models without ownership metadata need an explicit migration decision before replacement.

A 3D run stops before preparation if the checkpoint source digest, saved model hash, or referenced audit hash differs. Resolve the changed input or repeat the 2D stage; do not edit hashes by hand. Geometry audit failures are recorded in the report. Contract, frame, and file-integrity errors block a run because the inputs cannot be applied consistently.

## Legacy data

Use this entry point instead of the old combined builder and validator. The old builder remains only because saved project scripts import its functions. The unused validator is removed. Preserve original source files when migrating a JSON file that contains both features and terrain:

```text
run_site_model.py --project-root PROJECT --migrate-input processed/legacy.json --input processed/sources.json --terrain-output processed/terrain.json
```

This command only migrates data. It does not change the Rhino document. Add or check missing source-frame metadata before the normal staged run. `--terrain-output` is needed when the legacy input contains terrain that must be retained.
