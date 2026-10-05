# Transport

Show the available road, walking, cycling, railway, and water transport segments on one board. Read the [shared transport standard](../../../standards/overture/transport.md) and its linked JSON before styling Rhino or SVG geometry.

## Check the source

Use checked 2D `segment` records and their retained source IDs, subtype, and class. Keep geometry at Z = 0. Count each source feature once within the map extent. Record missing themes, unmapped classes, and rejected geometry in the coverage report. Missing data is not proof that a route is absent.

Use centre lines from the source. Keep rail and road records separate at crossings. Use source level rules where available to resolve crossing order; record unresolved cases. Do not infer bridge or tunnel positions, public access, service frequency, or bus routes from line geometry. Omit connector points from the artwork.

## Draw

1. Resolve every segment through the shared JSON. Use `transport_style(properties)` in the [Rhino style module](../../rhino-site-data-model/scripts/site_model/cartography.py) when scripting; it returns the same tokens for SVG. Retain unknown classes with the fallback style and include their count in the report.
2. Follow the [Rhino layer structure](../../rhino-site-data-model/references/rhino-structure.md) for source model layers. Use the shared styles with ByLayer colour and print width. Preserve source metadata.
3. Use the shared base, template, extent, and scale. Transform the lines to page millimetres, then apply shared widths and colours. Sort by shared draw order, with supported crossing order applied locally. Keep editable groups `Line / <style label> / <source subtype and class>`.
4. Show only used categories in the legend. Use source names for labels where space permits. Keep the site boundary and labels above transport lines.
5. Title the board **Transport**. Save `Transport.svg` and add the board to the review PDF. Record the shared style version and hash, source release, class counts, and coverage gaps in `map-config.json` and the validation report.

## Check

Compare Rhino and SVG styles by source ID: category, colour, paper width, and line pattern must match. Check layer order, crossings, clipping, labels, and the legend at print size. Keep source feature counts separate from clipped line-piece counts. Review the PDF and record failed checks.
