# Water Flow and Watersheds

Show flow lines and watershed areas on one board. First complete the [terrain check](terrain-analysis.md). Use the full available terrain for calculation; clip only the artwork to the map frame. Record where source coverage limits the result.

## Calculate

1. Read the [Python guidance](../../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). Use a managed runtime with the packages in [requirements.txt](../scripts/requirements.txt). Check the source mesh, units, CRS, and resolution. Use one ground surface, including terrain on hidden layers.
2. Run [analyze_water_flow.py](../scripts/analyze_water_flow.py) with `--product both`. Use the [script contract](water-flow-script.md) for inputs and outputs. Flow tracing and watershed creation use separate modules but share one mesh and drainage graph.
3. Check `run.json`. Continue only when its status is `complete`. A `skipped` run has no terrain. A failed run has no final output directory. Retain the source hash and settings with the map record.

```text
python -B scripts/analyze_water_flow.py --input SITE.3dm --output RUN_DIRECTORY --product both --min-area-m2 100 --min-length-m 30 --max-fill-area-m2 5000 --max-fill-depth-m 0.3
```

Run this command from the skill directory. Select a new run directory under `artifacts/vector-site-maps/terrain/`.

Flow follows the steepest downhill mesh edge. At equal slopes, the lower vertex ID wins. This approximates flow on the surface; mesh edges and resolution affect the route. Exact flat areas route to lower exits by shortest edge distance. Flat routes are assumptions. Flat areas without a lower exit remain unresolved. For a less fragmented map, fill small depressions on an analysis copy before routing. Start with a 5,000 m² combined catchment limit and a 0.30 m depth limit; record these assumptions. A one-pass priority flood finds spill levels from terrain edges and protected large catchments. Accept a connected fill only when both limits pass. Retain larger, deeper, and rejected depressions. The source terrain stays unchanged.

Each watershed groups land that reaches the same terminal. Terminals can be model-edge exits, sinks, or unresolved flats. Edges include terrain holes and data gaps. These are catchments within the supplied terrain, not proof of complete natural watersheds. The model does not calculate rainfall volume, infiltration, pipe drainage, or flood depth.

## Create and check Rhino results

Follow the shared document editing rules. Prepare results offline, then add them to the open target document in batches. Preserve the source terrain.

- `AIQ Site::Analysis::Water Flow`: create downstream polylines from `flow-paths.json` XYZ points. Keep path IDs, contributing areas, terminal IDs, flat-step indices, and filled-step indices. Flow coordinates use the analysis surface; watershed cells retain the source terrain elevations.
- `AIQ Site::Analysis::Watersheds`: create mesh cells from `watersheds.json` XYZ points. Group cells by terminal ID and colour. Keep source face and vertex IDs. Cells lie on the terrain; each vertex owns one third of each incident triangle's plan area.
- `AIQ Site::Analysis::Drainage Terminals`: mark terminal points with their ID and type. An unresolved flat's point is an ID marker, not a known outlet.

Check that flow segments follow mesh edges without going uphill on the analysis surface, cells cover the terrain once, and each basin's area matches its terminal's contributing area. Save and check the Rhino results before SVG export. Keep a result-to-object ID record when cells are combined into meshes.

## Draw the SVG

Use dissolved basin polygons from `watersheds.json`; preserve holes. Use the returned pale cool colours, fine `#64788A` boundaries at 0.15 mm, and basin ID labels. Adjacent basins use different colours. Mark unresolved flat catchments with a grey hatch and an **Unresolved flat** key.

Draw flow lines above the watershed fills in dark blue `#08306B`, 0.35 mm wide, with downstream arrows. Use dashed lines for recorded flat or filled steps and label them **Assumed route across flat or filled terrain**. The default line filter is 100 m² contributing area; record any change. Also hide branches shorter than 30 m in plan, but retain short downstream links needed to connect longer branches to their outlets. Both display filters leave watershed boundaries and area totals unchanged. Fill first, recalculate drainage, then filter the lines. If it removes every line, state that no paths meet the threshold.

Use groups `Area / Watersheds / <basin ID>`, `Line / Water Flow`, and `Point / Drainage Terminals`. Show edge exits as circles, sinks as squares, and unresolved flats as triangles. Keep the site boundary and labels above them. Use labels as well as colour where the palette repeats.

Label the board **Water Flow and Watersheds**. Include the terrain source, mesh resolution, line threshold, and **Terrain-based flow estimate**. Keep the shared base, scale, and north arrow. Save `Water_Flow_and_Watersheds.svg` and add it to the review PDF.

Check line direction, basin IDs, fill contrast, holes, and alignment at print size. Keep full-terrain statistics separate from visible and site-boundary areas. Link `run.json` and the result files from `map-config.json`; record missing coverage and failed checks in the validation report.

Method background: [steepest-link routing on irregular grids](https://landlab.readthedocs.io/en/latest/tutorials/flow_direction_and_accumulation/the_FlowDirectors.html), [priority-flood filling](https://rbarnes.org/sci/2014_depressions.pdf), and [watersheds from flow direction](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/how-watershed-works.htm). The area/depth limits and protected catchments are this workflow's conservative policy.
