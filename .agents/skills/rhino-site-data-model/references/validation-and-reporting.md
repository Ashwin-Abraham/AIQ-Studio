# Validation and reporting

Validation records failures. It does not stop model creation by itself.

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
- All building masses extend in world `+Z`.
- No main building mass starts below its reference ground elevation.
- Building-part bottom and top elevations follow the placement rules.
- Parent envelopes with visible part volumes are hidden by default.
- Terrain skirts are separate from building-height geometry.
- Unresolved bridges, tunnels, water levels, and underground parts are clearly marked.
- The file has document-level release, CRS, origin, terrain, and assumption data.

## Visual checks

When Rhino control is available:

1. Inspect a plan view with 2D and 3D branches alternately visible.
2. Inspect a perspective view with terrain, masses, skirts, and building parts visible.
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

The report must distinguish source facts, derived values, estimates, and unresolved conditions. Include all failed checks with affected object IDs. Deliver a partial model when useful, but do not describe a failed check as successful.

## Run annotation

Add a small annotation group under `AIQ Site::QA::Annotations::Run Info`. Include:

- site name;
- generation time;
- Overture release;
- context rule and bounds;
- projected CRS and local origin;
- terrain source and vertical datum;
- height fallback rules;
- report and manifest filenames.

Do not copy the run annotation onto every object.
