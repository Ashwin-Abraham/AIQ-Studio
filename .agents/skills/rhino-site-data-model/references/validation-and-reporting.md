# Validation and reporting

Validation records failures. It does not stop model creation by itself.

Use `scripts/run_site_model.py --audit-only` with the target output, project root, and selected stage. This writes a separate `.2d.review.audit.json` or `.3d.review.audit.json` file, preserving the checkpoint audit. The old separate validator is no longer used. Contract errors, changed checkpoint hashes, and frame conflicts stop the run before inconsistent data can be applied.

Check and save the complete 2D stage before 3D preparation. A 2D audit marks 3D placement checks as not applicable. A 3D audit also checks the retained 2D geometry. Read the audit results; `checked_and_saved` in a checkpoint does not mean all checks passed.

## Required checks

- The saved `.3dm` reopens.
- Model units and coordinate metadata match the selected system.
- All source-plan geometry is on its specified Z plane, normally Z = 0.
- The site and context boundaries exist.
- Expected themes and non-empty category layers exist.
- Source counts reconcile with processed counts and created-object counts.
- All source-derived objects have a source ID, version, exact properties, and source records.
- All geometry is valid.
- Polygon holes and multipolygon parts are accounted for.
- In 3D, all building masses extend in world `+Z`.
- In 3D, no main building mass starts below its reference ground elevation.
- In 3D, building-part bottom and top elevations follow the placement rules.
- In 3D, parent envelopes with visible part volumes are hidden by default.
- When terrain is present, terrain skirts are separate from building-height geometry.
- Unresolved bridges, tunnels, water levels, and underground parts are clearly marked.
- The file has document-level release, CRS, origin, terrain, and assumption data.
- Generated object keys are unique, ownership and stage metadata are present, and a 2D checkpoint has no old owned 3D objects.

The programmatic audit checks saved geometry and metadata. Source-to-output count reconciliation also needs the coordinator's source and batch records. Check hole preservation and unresolved conditions during preparation and visual review; a successful file audit alone does not prove every source interpretation is correct.

## Visual checks

When Rhino control is available:

1. Inspect the 2D stage in plan. For a completed 3D model, alternate the 2D and 3D branches.
2. For 3D, inspect a perspective view with the available terrain, masses, skirts, and building parts visible.
3. Check site edges, large crossing features, extreme heights, and vertical outliers.
4. Capture or record the reviewed views.

If visual inspection is not possible, create a preview when practical and state the limitation in the final report.

### Viewport setup in Rhino Python

Use the following code after you obtain the active Rhino document as `doc`:

```python
view = doc.Views.ActiveView
vp = view.ActiveViewport

vp.ConstructionGridVisible = False
vp.ConstructionAxesVisible = False

mode = Rhino.Display.DisplayModeDescription.FindByName("Shaded")
if mode is not None:
    vp.DisplayMode = mode

doc.Views.Redraw()
```

Do not assign `vp.WorldAxesIconVisible`. The Rhino 8 `RhinoViewport` used by this workflow does not support that property. The assignment raises an `AttributeError` and stops the script before view capture or model save. Leave the world-axis icon at its current setting. If the Shaded display mode is not available, keep the current display mode.

## Required outputs

- Rhino model.
- Unchanged raw source cache.
- Processed data.
- Source manifest with hashes, bounds, retrieval time, release, and tool versions.
- Human-readable model report.
- Machine-readable validation audit.
- Saved checkpoint for later 3D runs, with source, model, and audit hashes.

The report must distinguish source facts, derived values, estimates, and unresolved conditions. Include all failed checks with affected object IDs. Deliver a partial model when useful, but do not describe a failed check as successful.

## Run annotation

Add stage-specific run annotations under `AIQ Site::2D::QA::Annotations::Run Info` and, when present, `AIQ Site::3D::QA::Annotations::Run Info`. Include:

- site name;
- generation time;
- Overture release;
- context rule and bounds;
- projected CRS and local origin;
- terrain source and vertical datum;
- height fallback rules;
- report and manifest filenames.

Do not copy the run annotation onto every object.
