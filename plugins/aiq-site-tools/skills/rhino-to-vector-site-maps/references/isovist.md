# Isovist

Show the horizontal visible region from a selected point and eye height over the shared base map. Apply the common framing and output rules in [map specification](map-specification.md). A percentage visibility surface or a 3D visible volume requires a separate defined method; neither is the default point isovist.

## Calculate or reuse results

1. For a new calculation, follow [Ladybug analysis](../../ladybug-analysis/SKILL.md). Select `isovist`. Resolve observation points, height per point, height reference, obstruction geometry, maximum distance, and angular step. Use supplied inputs; ask for missing inputs before calculation. Ground-relative heights require the named ground surface. Weather data is not required.
2. Follow the [Ladybug isovist method](../../ladybug-analysis/references/isovist.md) for eye positions, ray intersections, unresolved points, and metrics. Use actual obstruction geometry at the selected height. A building footprint alone does not establish whether a ray at that height is blocked. Record assumed obstruction heights.
3. Before creating scripts, read [Python scripting guidance](../../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). The skill currently supplies method instructions, not a ready-to-run isovist script. Reuse a checked project script when appropriate; otherwise create the project scripts described below during the analysis run.
4. Reuse saved polygons only when the run record identifies the observation coordinates, height reference, obstruction geometry, coordinate transform, maximum distance, and angular step. Compare these with the requested drawing. Recalculate when they differ. Keep a missing or unresolved result separate from a valid small visible region.

## Project script workflow

These are script responsibilities and suggested names, not installed commands. Keep calculation scripts in `<project>/artifacts/ladybug-analysis/scripts/` and drawing scripts in `<project>/artifacts/vector-site-maps/scripts/`. Record the actual paths in the run record.

| Script | Inputs and work | Required output |
| --- | --- | --- |
| `calculate_isovist.py` | Run through the live Rhino connection with the selected points, height references, obstructions, range, and angular step. Follow the linked isovist method. | Eye coordinates, ordered ray endpoints and hit/range status, closed polygons, point IDs, source obstruction IDs, metrics CSV, and run record. |
| `draw_isovist.py` | Read checked results, project polygons and eye positions into the shared plan coordinates, then clip artwork to the map frame. | Editable vector overlay per point and height, legend, drawing configuration, and validation report for the site-map document. |

Complete the calculation stage when every requested point/height pair has a result or an explicit unresolved status. Retain the polygon at eye height in the analysis data; the drawing uses its plan projection. Preserve full polygons and metrics before clipping the artwork.

## Drawing and legend

Use a separate board for each point/height pair by default. A multi-height request can produce boards such as **Isovist - P01 - 1.5 m above ground**, **10 m**, and **30 m**. These sample heights are examples, not automatic analysis inputs. Use the same frame and scale for comparison boards.

Show the visible region with `#6FA8B8` fill at 35% opacity and a `#356B7A` boundary, 0.25 mm at print size. Show the eye position as a 2 mm white circle with a dark outline and its point ID. This filled marker is an exception to the shared unfilled point rule. Keep the map context muted and the shared site boundary visible above the result. Omit individual rays from the normal drawing; retain them in the analysis data.

Use a dashed stroke for polygon edges whose two endpoint rays both reached the maximum distance. Retain mixed hit/range edges as approximation boundaries and explain them in the result note. A range boundary is not a wall. Key the visible region, observation point, and range limit. If the map frame clips the isovist, state **View extends beyond map frame**.

State the observation height and its reference, maximum distance, angular step, and field of view. Report visible area in m² and the fraction of rays limited by range. Label metrics as applying to the full calculated polygon, not its clipped drawing. Put the remaining method metrics and obstruction assumptions in the run record. Describe the result as a horizontal view at eye height, not visibility of every ground surface within the polygon.

## Check and export

Check each point/height pairing, ground reference where used, closed polygon, and result status. Check that distances stay within the requested range and that hit/range flags survive export. Report invalid polygons or points inside/on obstructions as unresolved; a geometry repair must not silently change the visible area.

Verify that the observation marker and result use the base map's transform. Inspect the PDF at print size for visible context, correct labels, range marks, and clipping notes. Save the vector artwork and review PDF through the shared export workflow, with links to the calculation run and metrics CSV. Keep incomplete point/height pairs in the validation report.
