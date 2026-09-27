# 2D cartographic style reference

Use object colour, plot colour, and print width `ByLayer`. Keep all 2D geometry at Z = 0. Use object display order to control overlap.

Draw sections in this order from bottom to top: bathymetry, land, land cover, land use, water, buildings, transport, infrastructure, context boundary, site boundary, and QA. Within a section, draw the more important item above the less important item. For example, draw a primary road above a secondary road, and draw a deeper bathymetry threshold above a shallower threshold.

## Building use

| Layer type | RGB | Hex | Line weight (mm) |
| --- | ---: | --- | ---: |
| Residential | 201, 188, 111 | `#C9BC6F` | 0.18 |
| Commercial or retail | 227, 191, 139 | `#E3BF8B` | 0.18 |
| Office | 217, 199, 175 | `#D9C7AF` | 0.18 |
| Industrial or warehouse | 154, 149, 135 | `#9A9587` | 0.20 |
| Education | 177, 160, 198 | `#B1A0C6` | 0.20 |
| Healthcare | 208, 160, 170 | `#D0A0AA` | 0.20 |
| Civic or public | 209, 170, 127 | `#D1AA7F` | 0.20 |
| Religious | 188, 163, 198 | `#BCA3C6` | 0.20 |
| Transport building | 134, 160, 181 | `#86A0B5` | 0.25 |
| Service building | 185, 185, 178 | `#B9B9B2` | 0.13 |
| Unclassified | 135, 135, 132 | `#878784` | 0.18 |

## Land use

| Overture subtype | RGB | Hex | Outline weight (mm) |
| --- | ---: | --- | ---: |
| `residential` | 238, 231, 205 | `#EEE7CD` | 0.13 |
| `commercial` | 238, 215, 187 | `#EED7BB` | 0.13 |
| `industrial` | 211, 207, 197 | `#D3CFC5` | 0.13 |
| `institutional` | 222, 214, 231 | `#DED6E7` | 0.13 |
| `recreation` | 207, 226, 198 | `#CFE2C6` | 0.13 |
| `agriculture` | 224, 222, 178 | `#E0DEB2` | 0.13 |
| `transport` | 216, 218, 218 | `#D8DADA` | 0.13 |
| `construction` | 224, 207, 185 | `#E0CFB9` | 0.13 |
| Unclassified | 232, 232, 228 | `#E8E8E4` | 0.13 |

## Land cover

| Overture subtype | RGB | Hex | Outline weight (mm) |
| --- | ---: | --- | ---: |
| `barren` | 218, 204, 171 | `#DACCAB` | 0.13 |
| `crop` | 224, 222, 178 | `#E0DEB2` | 0.13 |
| `forest` | 117, 169, 116 | `#75A974` | 0.13 |
| `grass` | 181, 211, 170 | `#B5D3AA` | 0.13 |
| `mangrove` | 91, 151, 121 | `#5B9779` | 0.13 |
| `moss` | 190, 205, 170 | `#BECDAA` | 0.13 |
| `shrub` | 157, 190, 143 | `#9DBE8F` | 0.13 |
| `snow` | 232, 239, 242 | `#E8EFF2` | 0.13 |
| `urban` | 214, 214, 209 | `#D6D6D1` | 0.13 |
| `wetland` | 161, 199, 189 | `#A1C7BD` | 0.13 |

## Transport

| Layer type | RGB | Hex | Line weight (mm) |
| --- | ---: | --- | ---: |
| Motorway or trunk road | 69, 44, 32 | `#452C20` | 0.70 |
| Primary road | 104, 69, 47 | `#68452F` | 0.50 |
| Secondary road | 137, 103, 60 | `#89673C` | 0.35 |
| Tertiary road | 153, 133, 76 | `#99854C` | 0.25 |
| Local or residential road | 167, 155, 106 | `#A79B6A` | 0.18 |
| Service road | 184, 178, 151 | `#B8B297` | 0.13 |
| Major railway | 70, 48, 32 | `#463020` | 0.50 |
| Minor railway or path | 118, 92, 68 | `#765C44` | 0.25 |

## Other layers

| Layer type | RGB | Hex | Line weight (mm) |
| --- | ---: | --- | ---: |
| Land base | 232, 229, 218 | `#E8E5DA` | 0.13 |
| Water area | 177, 205, 226 | `#B1CDE2` | 0.18 |
| Infrastructure | 96, 105, 112 | `#606970` | 0.25 |
| Bathymetry | Sequential muted blue by depth | — | 0.13 |
| Context boundary | 150, 150, 145 | `#969691` | 0.18 |
| Site boundary | 126, 53, 45 | `#7E352D` | 0.50 |
| Unresolved or QA | 173, 43, 148 | `#AD2B94` | 0.35 |

Use the Unclassified style for a source value that has no listed mapping.
