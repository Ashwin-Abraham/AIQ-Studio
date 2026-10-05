# Map specification

The board template is authoritative. Preserve its artboard size, `viewBox`, map-frame rectangle, legend area, title block, margins, and static geometry. Replace placeholder text and map-frame content without moving or resizing template elements.

Fill the complete map-frame rectangle with map content and use the rectangle as the clipping boundary. Fit the selected context with **cover**, not contain: preserve its aspect ratio, crop overflow, and leave no blank margin inside the frame. Use the largest frame-shaped view available from the context, with the site near the centre.

After framing the context, check the site boundary. If the crop cuts it, zoom out only enough to include the complete boundary and its stroke. Extend source coverage when necessary so the frame remains filled. Do not resize the frame or introduce an internal margin.

Store the selected centre, extent, scale, margin, offset, rotation, and frame size in the `rhino-to-vector-site-maps` workflow entry in `project.json`. This is the persistent framing definition. Copy it into the generated `map-config.json` with the source and style record.

The source uses local projected metres; north is `+Y`. Use one transform for the base, themes, and feature labels:

```text
page_x_mm = map_left_mm + (x_m - min_x_m) * 1000 / scale_denominator
page_y_mm = map_top_mm + (max_y_m - y_m) * 1000 / scale_denominator
```

Fit the extent in the map frame at the stated scale. A ground distance of `d` metres occupies `d * 1000 / scale_denominator` mm on the page. Use the [sample scale bar](../assets/scale-bar.svg) as a style reference; recalculate its segment lengths and labels for the selected scale. Align the north arrow with the map orientation.

Transform geometry to page millimetres before styling. Treat stroke widths and point-symbol sizes as paper-space values. Place the linked base at 100%; regenerate it when the frame or scale changes. Use `vector-effect="non-scaling-stroke"` in SVG where a later transform remains.

Save `map-config.json` with source path and hash, release, CRS, origin, persistent framing values, ordered boards, and style choices. Preserve polygon holes and clipped parts.

## Maps to create

Read only the drawing specifications needed for the selected boards, plus the shared base map specification. Map detailed Overture and Rhino classes to their stable categories. Show only layers present in the drawing.

Use the listed RGB hex colours as stable category defaults across projects. Record explicit project overrides in `map-config.json`.

### Data coverage check

Before drawing, compare the selected source with the fields required by each board. Resolve the Overture schema for the recorded release. Read the [Overture coverage review](../../rhino-site-data-model/references/overture-coverage-recommendations.md) when comparing workflow support with the dataset or diagnosing missing themes.

Count unique `(feature_type, id)` records in the selected map extent. Count building parts separately from buildings. Deduplicate Rhino fills, outlines, and clipped pieces by source identity. Read properties from the processed source or retained 2D metadata, not from layer colours or derived 3D volumes.

Record these results in `reports/validation.json` for each board:

- Source, processed, and displayed feature counts where available; state the extent and denominator.
- Required fields present, missing, invalid, or in conflict; separate source-height, floor-estimate, type-assumption, and unknown-height counts; classified and unknown building-use counts.
- Required themes that were not acquired, were empty in the source, were rejected during processing, or have no display mapping. State `unverified` when the cache cannot establish the cause.
- Unsupported classes and IDs, intentional exclusions, overlap decisions, and evidence needed to close each gap.

The check is complete when each required theme and field has a status and each gap has a stated effect on the map. Keep a short coverage note on affected boards. Missing data does not mean that a physical feature or use is absent.

### Shared drawing rules

Use the layer hierarchy `Geometry / Category / Source class`. For example, `Area / Managed green` contains separate `Garden`, `Flowerbed`, `Allotment`, and `Managed grass` layers with the same colour. Preserve this hierarchy when saving to `.ai`.

Geometry controls the mark and primary paint order. Category controls the style. Source class controls the editable layer name.

- Draw points as unfilled circles at a fixed print size.
- Draw open curves as strokes in the colour used to fill the same class.
- Fill closed curves and polygons unless a theme specifies a transparent hatch or outline. Preserve polygon holes in fills and hatches.

Assign and sort by explicit paint order before writing:

1. Base underlay.
2. Areas.
3. Lines.
4. Points.
5. Protected-area overlays.
6. Site and context boundaries.
7. Labels.
8. Map furniture.

Within one geometry band, use the theme's overlap rule. Where none is specified, the first listed category has the highest priority. Legend order does not override a theme's overlap rule. In SVG, write frontmost objects last. In Illustrator, place frontmost layers higher in the Layers panel. Do not use source iteration order as paint order.

Do not merge overlapping `land`, `land_cover`, and `land_use` features automatically. Prefer detailed physical geometry over broad land cover, and draw designations as overlays. Use Places points for labels or symbols, not physical extent.

### Base map

Read the [base map specification](base-map.md) when building the shared underlay.

### Figure-ground

For a Figure-ground drawing, read its [specification](figure-ground.md).

### Vegetation and Open Space

For a Vegetation and Open Space drawing, read its [specification](vegetation-and-open-space.md).

### Water Features

For a Water Features drawing, read its [specification](water-features.md).

### Building Height

For a Building Height drawing, read its [specification](building-height.md).

### Terrain Height

For a Terrain Height drawing, read the [terrain workflow](terrain-analysis.md), then the [Rhino and SVG specification](terrain-height.md).

### Terrain Slope

For a Terrain Slope drawing, read the [terrain workflow](terrain-analysis.md), then the [Rhino and SVG specification](terrain-slope.md).

### Water Flow and Watersheds

For one drawing with terrain flow lines and coloured watershed areas, read the [terrain workflow](terrain-analysis.md), then the [calculation and drawing specification](water-flow-and-watersheds.md).

### Building Use

For a Building Use drawing, read its [specification](building-use.md).

### Detailed Building Use

For a Detailed Building Use drawing, read its [specification](detailed-building-use.md).

### Land Use

For a Land Use drawing, read its [specification](land-use.md).

### Natural Features

For a Natural Features drawing, read its [specification](natural-features.md).

### Radiation

For a Radiation drawing, read the [calculation and drawing workflow](radiation.md). It defines the coloured cells and continuous gradient legend.

### Isovist

For an Isovist drawing, read the [calculation and drawing workflow](isovist.md). It defines observation markers, heights, and visible-area polygons.

### Seasonal Shadows

For seasonal shadow drawings, read the [drawing specification](shadow.md). It defines sunlit and shaded areas and date/time labels.

## Output structure

```text
Projects/<project>/
├── project.json
├── artifacts/vector-site-maps/
│   ├── map-config.json
│   └── reports/validation.json
└── exports/site-maps/
    ├── Base_Map.ai
    ├── Site_Analysis.ai
    └── Site_Analysis.pdf
```

`Base_Map.ai` contains editable reference layers shared by every board. A placed `.ai` is one linked object; its source layers cannot have separate visibility on each board.

`Site_Analysis.ai` has one unchanged template artboard and one top-level group per concern. Each group contains the linked base underlay, editable theme artwork, shared boundary overlay, labels, and map furniture. Clip map artwork to the template frame. Keep the relative link paths within the project.

The validation report records the source hash and release, extent, scale, board sizes, link status, data gaps, and failed checks. Check that the output uses the template artboard and map-frame bounds, the linked map covers the frame, the site boundary is visible, and QA layers are hidden. Check the saved `.ai` files and PDF in the authoring application.
