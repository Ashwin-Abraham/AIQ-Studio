# Radiation

Show cumulative incident solar radiation on the selected site surface over the shared base map. Use a continuous colour legend instead of spot-value labels. Apply the common framing and output rules in [map specification](map-specification.md).

## Calculate or reuse results

1. For a new calculation, follow [Ladybug analysis](../../ladybug-analysis/SKILL.md), including its required inputs. Select `radiation`. Resolve the target surfaces, obstruction geometry, EPW file, period, model north, and grid size before execution. A 2D base map alone is not sufficient obstruction geometry. Record assumed building heights in the analysis inputs.
2. Use the [Ladybug radiation method](../../ladybug-analysis/references/radiation.md) for geometry conversion, sky calculation, units, and limitations. Keep calculation logic there; this reference governs the vector drawing. The default quantity is cumulative incident radiation in kWh/m² for the selected period. A sample drawing labelled W does not establish the same quantity or period.
3. Before creating scripts, read [Python scripting guidance](../../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). The skill currently supplies method instructions, not a ready-to-run radiation script. Reuse a checked project script when its inputs and method match; otherwise create the project scripts described below during the analysis run. Follow the Ladybug skill's runtime and output-location rules.
4. A saved result can be used without a new calculation only when its run record identifies the geometry, units, coordinate transform, weather file, period, north, and grid. Compare these with the requested drawing. Resolve missing records or changed inputs before export. Never derive radiation values from colours in a sample image.

## Project script workflow

These are script responsibilities and suggested names, not installed commands. Keep calculation scripts in `<project>/artifacts/ladybug-analysis/scripts/` and drawing scripts in `<project>/artifacts/vector-site-maps/scripts/`. Record the actual script paths in the run record.

| Script | Inputs and work | Required output |
| --- | --- | --- |
| `prepare_radiation.py` | Run through the live Rhino connection. Read the selected targets and obstructions; convert units and prepare meshes through the Ladybug workflow. | Serialized geometry, source IDs, sample IDs, face vertices, sample positions, normals, face areas, and sample offset. |
| `calculate_radiation.py` | Run in the checked Ladybug radiation runtime with prepared geometry, EPW, period, and north. Follow the linked radiation method. | One result per sample ID, total radiation and available components, units, valid/missing status, and calculation run record. |
| `draw_radiation.py` | Join results to target faces by sample ID, transform them to the shared map frame, and apply the scale below. | Editable vector overlay, gradient legend, drawing configuration, and validation report for assembly into the site-map document. |

Complete the calculation stage when every target sample has a result or an explicit failure, the sample IDs match, and the run record identifies the inputs. Keep full numeric values in the result data and CSV even though the drawing omits spot labels.

## Surface and legend

Use a plan projection of the selected analysis surface. Keep its mesh cells as editable polygons with colour determined by the corresponding result. Preserve surface boundaries and holes. Colour interpolation is for the legend; retain the calculated cell values without inventing a smoother result surface. Show vertical faces or overlapping target levels on separate suitable drawings rather than averaging them into a ground plan.

Use this low-to-high gradient: `#4575B4`, `#91BFDB`, `#FFFFBF`, `#FDAE61`, `#D73027`. Interpolate between equally spaced stops. Use the same colour function for cells and legend. Set a linear scale from the valid minimum to maximum for the selected period; state both limits and units. Save the limits and stops in `map-config.json`. Comparison boards for the same quantity and period use a common range. For constant results, use one colour and one value instead of implying a range.

Place a continuous gradient bar with readable numeric ticks in the template legend area. Label it **Incident solar radiation (kWh/m²)** and state the analysis period. Omit individual sample markers and spot-value labels. Show uncalculated cells with no thematic fill and a light grey outline, keyed as **No result**; valid zero remains on the numeric scale. Keep surrounding buildings muted and the shared site boundary visible.

Include the weather station, grid size, and a short note that reflected solar energy from surrounding geometry is excluded. Put full settings and geometry assumptions in the run record. This map describes incident solar energy, not electrical yield.

## Check and export

Verify the result-to-face join, finite non-negative values, missing cells, surface coverage, units, and map alignment. Confirm the legend uses the same scale as the artwork and that the full period is labelled. Use actual face areas for calculation statistics; drawing clipping must not change the recorded analysis totals. State the statistics' extent.

Inspect the PDF at print size for legend clipping, visible cell boundaries, missing polygons, and base-map alignment. Save the editable vector artwork and review PDF through the shared export workflow, with links to the analysis run and its CSV. Report partial results explicitly.
