# Terrain analysis

Use this workflow for the selected Terrain Height and Terrain Slope maps. Use the shared [map specification](map-specification.md) for the frame, scale, and export.

## Check terrain

1. Find ground terrain in the target Rhino model, including hidden and locked objects. Start with `AIQ Site::3D::Terrain`; check geometry and source metadata, not only the layer name. Exclude buildings, terrain skirts, water surfaces, and flat placement geometry.
2. If terrain is absent, record both maps as skipped with reason `no terrain`. Continue other boards. You may offer to build terrain with the [Rhino site model skill](../../rhino-site-data-model/SKILL.md). Start that work only if the user agrees. Follow its [terrain source rules](../../rhino-site-data-model/references/source-and-context.md), [terrain data contract](../../rhino-site-data-model/references/processed-data-contract.md), and [staged workflow](../../rhino-site-data-model/references/staged-workflow.md). Check the saved terrain before resuming these maps.
3. Check terrain units, CRS, origin, vertical datum, source resolution, and coverage against the map extent. Resolve coordinate or unit conflicts before analysis. Keep missing coverage as No data; never replace it with zero or extend terrain across gaps.

## Analyse in Rhino

1. Read the [document editing rules](../../rhino-site-data-model/references/RHINO-DOCUMENT-EDITING-GUIDANCE.md) before changing the model. Keep the source terrain unchanged. Create a separate analysis mesh from its ground surface. Record meshing settings and the diagonal used to split quad faces. Exclude side walls, bottom faces, invalid faces, and faces with zero plan area; report them.
2. Use one ground surface for each XY location. Resolve overlapping terrain sources before calculation. Keep holes. Convert coordinates to metres, including Z, before computing values.
3. Follow [Terrain Height](terrain-height.md) or [Terrain Slope](terrain-slope.md). Save result geometry on `AIQ Site::Analysis::Terrain Height` or `AIQ Site::Analysis::Terrain Slope`. Give each result a stable ID, source object and face IDs, value or range, unit, and class.
4. Save the Rhino results and a result file with polygon coordinates and matching attributes under `artifacts/vector-site-maps/terrain/`. Record the source model and geometry hashes, settings, CRS, origin, datum, coverage, and result paths in `map-config.json`. Reuse results only when source geometry and settings match.
5. Check values, coverage, and class assignment in Rhino. Record failures in `reports/validation.json`. Export SVG only from results that pass these checks.

## Export checked results to SVG

Project result polygons to XY and use the shared map transform. Keep editable paths, holes, and result IDs. Use groups `Area / <band> / Terrain`. Put No data in a separate group with grey `#BDBDBD` diagonal hatching. Keep boundaries and labels above the terrain fill.

Save `Terrain_Height.svg` and `Terrain_Slope.svg` for the selected maps in `exports/site-maps/`. Add their artwork to the corresponding analysis boards. Save breaks, colours, units, and legend labels in `map-config.json`.

Check SVG-to-Rhino values by result ID, total plan area, holes, class colours, legend limits, and base-map alignment. Report coverage and band areas in square metres within the map frame. Report site-boundary statistics separately. Inspect the review PDF at print size. A skipped map has a report entry and no empty artboard.
