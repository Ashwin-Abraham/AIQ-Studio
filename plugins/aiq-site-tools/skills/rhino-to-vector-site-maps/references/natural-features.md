# Natural Features

Show physical vegetation, water, and landforms, including managed vegetation and water. Retain the separate Vegetation and Open Space and Water Features boards when a full set is requested.

Use `land` for detailed physical features, `land_cover` for broad surface cover, and `water` for water features. Use `land_use` only where its class or properties support a physical cover interpretation, such as managed grass or a planted garden. A park or recreation designation alone does not establish vegetation across its full area.

Read [Vegetation and Open Space](vegetation-and-open-space.md) and [Water Features](water-features.md) for these shared tokens: Canopy, Low vegetation, Productive vegetation, Managed green, Wetland, Open water, Watercourse, Drainage, Managed water, and Protected area. Keep the same colours across boards. Map mangrove to Canopy and moss to Low vegetation, with the source class retained.

Add these stable groups when present:

| Legend group | RGB hex | Source examples |
| --- | --- | --- |
| Sand and exposed ground | `#D8C49A` | Beach, sand, barren land cover |
| Rock and landforms | `#9B9186` | Rock, cliff, peak |
| Snow and ice | `#E6F0F4` | Snow or ice supported by the selected release |

Draw broad land cover first, then detailed physical surfaces. Draw water surfaces above broad land cover; keep wetland as its own class. Resolve conflicts with detailed vegetation from source evidence and record the chosen order. Keep generic land, islands, and urban land cover in context; their extent alone is not a vegetation type.

Show tree points as fixed-size symbols and tree rows as lines. Use canopy areas only when source geometry supports them. Show managed water separately from open water. Use dashed or lighter watercourse strokes for intermittent water. Keep water label points and landforms out of water fills. Draw protected boundaries above physical cover.

Contours are optional and require checked terrain with a stated interval and datum. Bathymetry remains an optional Water Features layer. It does not establish land elevation or water-surface height.

Check source geometry against each mark. Report missing tree, land-cover, or water data as coverage gaps. Check that broad cover does not hide detailed features and that managed features remain distinguishable.
