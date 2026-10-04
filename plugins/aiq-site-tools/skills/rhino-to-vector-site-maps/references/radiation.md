# Radiation

Use [Ladybug analysis](../../ladybug-analysis/SKILL.md) for ground surfaces within the site boundary, excluding building footprints. Include buildings inside the site and nearby buildings as obstructions. Reuse recorded results only when geometry and settings match. Follow the shared [map specification](map-specification.md) for framing and export.

Draw ground result cells as editable polygons, preserving holes and sample values. Use a plan projection. Show building footprints in solid dark grey `#404040` at 100% opacity, matching the solid–void diagram. Apply the radiation colour scale only to the analysed ground. Keep the site boundary visible.

Use the low-to-high gradient `#4575B4`, `#91BFDB`, `#FFFFBF`, `#FDAE61`, `#D73027`. Use the same linear range for cells and a continuous legend labelled **Incident solar radiation (kWh/m²)**. Show numeric ticks, the period, weather station, and grid size; omit spot labels. Use one value for constant results, and distinguish missing results from zero. Comparison boards use a common range.

Check sample-to-cell matching, units, legend, and alignment. State the analysed surface scope and that reflected energy from surrounding geometry is excluded. Link the analysis record and CSV; retain full-result statistics when clipping artwork. Inspect the exported PDF at print size.
