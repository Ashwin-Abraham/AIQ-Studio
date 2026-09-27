---
name: rhino-to-vector-site-maps
description: Create vector site maps from Rhino 2D site data, with a linked base map and thematic artboards.
---

# Vector site maps

1. Select one checked 2D source, CRS, and release. Use the [Rhino data contract](../rhino-site-data-model/references/processed-data-contract.md); use `AIQ Site::2D` if the processed source is missing.
2. Read the [board template](assets/board-template.svg). Determine one extent and scale for its existing map frame with the framing rule below. Reuse saved framing only when it still passes the template and site-fit checks.
3. Build every board from the unchanged template. Build `Base_Map.ai` first and add it as the linked bottom underlay on every artboard in `Site_Analysis.ai`; every instance must use the same transform. Use the [north arrow](assets/north-arrow.svg) where useful.
4. Save a review PDF and a validation report. Check every artboard, the scale bar, north direction, map alignment, and link status. Record each failed check.

Save native `.ai` files in an application that supports them. If one is unavailable, deliver prepared vector artwork and identify the `.ai` files as unfinished.

## Map specification

The board template is authoritative. Preserve its artboard size, `viewBox`, map-frame rectangle, legend area, title block, margins, and static geometry. Replace placeholder text and map-frame content without moving or resizing template elements.

Fill the complete map-frame rectangle with map content and use the rectangle as the clipping boundary. Fit the selected context with **cover**, not contain: preserve its aspect ratio, crop overflow, and leave no blank margin inside the frame. Use the largest frame-shaped view available from the context, with the site near the centre.

After framing the context, check the site boundary. If the crop cuts it, zoom out only enough to include the complete boundary and its stroke. Extend source coverage when necessary so the frame remains filled. Do not resize the frame or introduce an internal margin.

Store the selected centre, extent, scale, margin, offset, rotation, and frame size in the `rhino-to-vector-site-maps` workflow entry in `project.json`. This is the persistent framing definition. Copy it into the generated `map-config.json` with the source and style record.

The source uses local projected metres; north is `+Y`. Use one transform for the base, themes, and feature labels:

```text
page_x_mm = map_left_mm + (x_m - min_x_m) * 1000 / scale_denominator
page_y_mm = map_top_mm + (max_y_m - y_m) * 1000 / scale_denominator
```

Fit the extent in the map frame at the stated scale. A ground distance of `d` metres occupies `d * 1000 / scale_denominator` mm on the page. Use the [sample scale bar](assets/scale-bar.svg) as a style reference; recalculate its segment lengths and labels for the selected scale. Align the north arrow with the map orientation.

Transform geometry to page millimetres before styling. Treat stroke widths and point-symbol sizes as paper-space values. Place the linked base at 100%; regenerate it when the frame or scale changes. Use `vector-effect="non-scaling-stroke"` in SVG where a later transform remains.

Save `map-config.json` with source path and hash, release, CRS, origin, persistent framing values, ordered boards, and style choices. Preserve polygon holes and clipped parts.

## Maps to create

Map detailed Overture and Rhino classes to the stable categories below. Show only layers present in the drawing.

Use the listed RGB hex colours as defaults. Record any project-specific overrides in `map-config.json`.

Use the layer hierarchy `Geometry / Category / Source class`. For example, `Area / Managed green` contains separate `Garden`, `Flowerbed`, `Allotment`, and `Managed grass` layers with the same colour. Preserve this hierarchy when saving to `.ai`.

Geometry controls the mark and primary paint order. Category controls the style. Source class controls the editable layer name.

- Draw points as unfilled circles at a fixed print size.
- Draw open curves as strokes in the colour used to fill the same class.
- Fill closed curves and polygons. Preserve polygon holes.

Assign and sort by explicit paint order before writing:

1. Base underlay.
2. Areas.
3. Lines.
4. Points.
5. Protected-area overlays.
6. Site and context boundaries.
7. Labels.
8. Map furniture.

Within one geometry band, the first listed category has the highest priority. In SVG, write frontmost objects last. In Illustrator, place frontmost layers higher in the Layers panel. Do not use source iteration order as paint order.

Do not merge overlapping `land`, `land_cover`, and `land_use` features automatically. Prefer detailed physical geometry over broad land cover, and draw designations as overlays. Use Places points for labels or symbols, not physical extent.

### Base map

Create a light shared underlay. Keep theme emphasis in the analysis maps. Keep the linked base at full opacity; mute its internal colours instead.

- `Buildings` — `#E3E0DA`.
- `Transport` — `#D2CEC7`.
- `Water` — `#D8E3E5`.
- `Site boundary` — `#D95F4B`, 0.6 mm solid stroke at full opacity.
- `Context boundary` — `#B8B8B8`.

Use one source and style token for the site boundary. Repeat it above thematic artwork as a shared boundary overlay; do not restyle it per board.

### Figure-ground

Fill `building` footprints with dark grey `#404040` and leave holes open. Use `building_part` only where its parent footprint is absent. Treat the unfilled map area as visual void, not public space.

### Green structure

- `Canopy` — `#2F5D3A`: tree, tree row, wood, forest.
- `Low vegetation` — `#78A85A`: grass, grassland, shrub, scrub, heath, meadow.
- `Productive vegetation` — `#A5B85B`: farmland, crop, orchard, vineyard, plant nursery.
- `Managed green` — `#B8D98A`: garden, flowerbed, allotment, managed grass.
- `Recreation` — `#D3E6AF`: park, dog park, playground, pitch, recreation ground, golf green.
- `Wetland` — `#5AAE9B`: wetland.
- `Protected area` — `#5C7A4B`: nature reserve, national park, strict nature reserve, wilderness area, and other protected classes. Draw this as an outline or hatch over the physical cover.

### Blue structure

- `Open water` — `#6BAED6`: river, lake, pond, and water polygons.
- `Watercourse` — `#1D5F91`: stream, river, and canal lines.
- `Drainage` — `#56B4C2`: ditch and drain lines.
- `Managed water` — `#8C9FD1`: basin, reservoir, dock, and swimming pool.
- `Water infrastructure` — `#243B6B`: relevant dams, weirs, aqueducts, fountains, and water towers. Draw these as point or line symbols.
- `Wetland` — `#5AAE9B`: wetland. Use the Green structure colour.
- `Bathymetry` — `#DCEFF5`, `#A9D5E6`, `#6BAED6`, then `#1D5F91`: optional depth-threshold polygons from shallow to deep. Draw deeper thresholds above shallower ones; depth is not water-surface height.

Water labels, landforms, and utilities do not receive water fills. Use a dashed or lighter stroke for intermittent water.

Place each unknown class on a hidden `Unmapped/<theme>/<class>` layer and list it in the validation report. Keep it out of the final artwork and review PDF. Use `#FF00FF` only in a separate QA view when requested. Keep conflicting sources separate.

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
