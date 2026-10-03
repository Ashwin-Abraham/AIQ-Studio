# Building Height

Show building height in metres with a sequential light-to-dark palette. Keep streets and other context in the muted base map.

## Values and geometry

Use retained `building` and `building_part` properties. Join parts to parents with `building_id`. Exclude wholly underground features from the height bands and report their count.

Use valid positive source `height` values first. Label them as source values, not surveyed values. For raised or stacked parts, the mapped value is the top above the reference ground: `min_height + height`. With neither a minimum height nor a minimum floor, use a zero bottom offset and record this assumption. Keep sea-level elevation, terrain skirts, and roof material out of the mapped height. An explicit total height already includes the roof.

Use the [building height assumptions](building-height-assumptions.md) for the default source-height, floor-count, then building-type selection policy. Read its detailed class table before assigning a type default. Record any source-only project override. Derive estimates from retained source fields and this reference, rather than taking fallback heights from 3D volumes. The reference defines height selection and unresolved cases.

Where parts have usable values, draw their footprints above the parent. Resolve part overlaps by the highest mapped top, with source ID as a stable tie-breaker. Use the parent value on the remaining footprint. Parts with no usable value retain the parent value where available, with that inheritance recorded; otherwise show Unknown. Report missing parent references. Count each visible area once for area statistics and keep source counts separate.

## Project height bands

1. Inspect the valid values within the final map extent, including estimates only when enabled. Check extremes before selecting breaks.
2. Aim for about ten height bands. Start with rounded equal intervals for a compact range. For a long upper tail, use narrower lower intervals and wider upper intervals so low buildings remain distinct. Keep verified tall buildings in the range.
3. Use fewer bands when there are too few distinct values. Keep equal values in the same band. Record the reason for a reduced band count; Unknown is outside the numeric bands.
4. Use increasing breaks with no gaps or overlaps. Use lower-inclusive, upper-exclusive intervals, with the maximum included in the final interval. Labels must state metres and make the interval boundaries clear.
5. Save the breaks, method, value range, counts, estimate policy, and colours in `map-config.json`. Reuse them for revisions unless the extent or data changes enough to require a new distribution check. Bands are project-specific; colours alone cannot compare heights between projects.

Use this ten-colour sequence from low to high: `#F7FCFD`, `#E5F5F9`, `#CCECE6`, `#A8DDB5`, `#7BCCC4`, `#4EB3D3`, `#2B8CBE`, `#0868AC`, `#084081`, `#041F4A`. For fewer bands, sample this sequence in order. Keep a fine building outline so the lightest band remains visible.

## Display and validation

Use height-band colour for every resolved value. Source values have no hatch. Floor-count estimates have a single diagonal hatch. Type assumptions have parallel wavy lines and the legend label **Assumed based on building type**. Unknown values keep the grey cross hatch with no thematic fill. Inherited values retain the parent's method mark.

Use paper-space hatch strokes of 0.15 mm, spacing of 1.5 mm, and grey `#8C8C8C`. Clip hatches to each footprint and its holes. Show both estimate legend keys with hatch only and no fill. On the map, keep each estimate hatch over the applicable height-band colour. Recheck project height bands after enabling estimates.

For type assumptions, use a smooth repeating wave with a 2.4 mm wavelength and 0.3 mm amplitude. Keep wave rows 1.5 mm apart. Use the same wave dimensions in the map and legend.

Validate the complete published class/subtype sets against the tables. Check source priority, floor multiplication, offset rules, part inheritance, and unresolved exceptions. Record feature counts and visible areas for each method separately. Keep both the source-only coverage and the resolved coverage in the report.

Keep method counts separate from numeric bands.

Label selected landmarks or tall buildings only. Include `m` and an estimate mark where applicable. If all heights are unknown, keep the board with its coverage note and Unknown key; omit numeric bands.

Check that each displayed building area has a band or Unknown style, all valid values fit the breaks, inherited and estimated values are reported, and parent/part overlap does not distort counts. Inspect the hatch and legend at final print size.
