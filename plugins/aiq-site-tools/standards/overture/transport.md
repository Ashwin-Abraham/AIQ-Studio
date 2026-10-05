# Transport styles

[transport.json](transport.json) is the single source for AIQ transport class mappings, colours, paper line widths, line patterns, labels, and draw order. These are AIQ display choices, not Overture graphic standards.

Use these styles for Rhino transport layers and the Transport map. Match a segment's `subtype` and `class` after conversion to lower case. A null `classes` value matches all classes within that subtype. Use `unknown` when no row matches. Keep the source class and ID in metadata; report every fallback class and count.

Legacy aliases `local`, `rail`, `main`, and `high_speed` support existing processed models. Check the schema for the source release before mapping new classes. The rail category is a display group, not a measure of service importance.

Read [Overture segments](https://docs.overturemaps.org/guides/transportation/segments-and-connectors/) and [rail classes](https://docs.overturemaps.org/schema/reference/transportation/types/rail_class/) when checking source fields. Segment lines represent network centre lines. Connectors are topology records; omit them from normal artwork.

Draw larger `draw_order` values last. All current patterns are solid. In Rhino, use Continuous lines and colour and print width ByLayer. In SVG, use the listed colour and width in page millimetres, with no fill. Keep the same class groups and legend labels in both outputs. Line width is a graphic value, not a road width.

The shared base map uses its own muted transport colour. Apply this standard to the thematic transport overlay. Record the standard path, version, file hash, and any user-requested overrides in the map config. Apply each override to both output styles.
