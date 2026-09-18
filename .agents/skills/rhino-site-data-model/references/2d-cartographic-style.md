# 2D cartographic style reference

Use object colour and print width `ByLayer`. All line weights are in millimetres.

Use the Overture `subtype` value to select the base style. A `class` or `subclass` inherits the style of its subtype unless this document gives an override. Use the Unclassified style when the subtype is absent or unsupported.

## Draw order

Use this order from bottom to top. The order controls the drawing display. It does not show elevation.

| Order | Section |
| ---: | --- |
| 1 | Bathymetry fills |
| 2 | Land fills |
| 3 | Land-cover fills |
| 4 | Land-use fills |
| 5 | Water areas |
| 6 | Building fills and outlines |
| 7 | Transport networks |
| 8 | Infrastructure |
| 9 | Context boundary |
| 10 | Site boundary |
| 11 | Unresolved items and QA annotations |

Use this order within transport networks. More important routes draw above less important routes. A primary road draws above a secondary road.

## Building use

### Building subtype styles

| Overture subtype | Colour | RGB | Hex | Line weight |
| --- | --- | ---: | --- | ---: |
| `agricultural` | Muted olive | 168, 165, 106 | `#A8A56A` | 0.18 |
| `civic` | Warm brown | 209, 170, 127 | `#D1AA7F` | 0.20 |
| `commercial` | Warm sand | 227, 191, 139 | `#E3BF8B` | 0.18 |
| `education` | Muted violet | 177, 160, 198 | `#B1A0C6` | 0.20 |
| `entertainment` | Muted pink | 197, 154, 181 | `#C59AB5` | 0.20 |
| `industrial` | Warm grey | 154, 149, 135 | `#9A9587` | 0.20 |
| `medical` | Muted rose | 208, 160, 170 | `#D0A0AA` | 0.20 |
| `military` | Khaki grey | 143, 146, 112 | `#8F9270` | 0.25 |
| `outbuilding` | Light brown grey | 184, 177, 163 | `#B8B1A3` | 0.13 |
| `religious` | Pale violet | 188, 163, 198 | `#BCA3C6` | 0.20 |
| `residential` | Muted ochre | 201, 188, 111 | `#C9BC6F` | 0.18 |
| `service` | Light grey | 185, 185, 178 | `#B9B9B2` | 0.13 |
| `transportation` | Slate blue | 134, 160, 181 | `#86A0B5` | 0.25 |
| Unclassified | Dark grey | 135, 135, 132 | `#878784` | 0.18 |

### Building class fallback mapping

Use this table only when the building subtype is absent. Each class uses the style of the mapped subtype.

| Style subtype | Overture building classes |
| --- | --- |
| `agricultural` | `agricultural`, `barn`, `cowshed`, `digester`, `farm`, `farm_auxiliary`, `glasshouse`, `greenhouse`, `silo`, `slurry_tank`, `stable`, `sty` |
| `civic` | `civic`, `fire_station`, `government`, `library`, `post_office`, `public`, `toilets` |
| `commercial` | `commercial`, `hotel`, `kiosk`, `office`, `parking`, `retail`, `supermarket` |
| `education` | `college`, `dormitory`, `kindergarten`, `school`, `university` |
| `entertainment` | `grandstand`, `pavilion`, `sports_centre`, `sports_hall`, `stadium` |
| `industrial` | `factory`, `industrial`, `manufacture`, `storage_tank`, `warehouse` |
| `medical` | `hospital` |
| `military` | `bunker`, `guardhouse`, `military` |
| `outbuilding` | `allotment_house`, `beach_hut`, `boathouse`, `carport`, `garage`, `garages`, `hut`, `outbuilding`, `roof`, `shed`, `shelter` |
| `religious` | `cathedral`, `chapel`, `church`, `monastery`, `mosque`, `presbytery`, `religious`, `shrine`, `synagogue`, `temple`, `wayside_shrine` |
| `residential` | `apartments`, `bungalow`, `cabin`, `detached`, `dwelling_house`, `ger`, `house`, `houseboat`, `residential`, `semi`, `semidetached_house`, `static_caravan`, `stilt_house`, `terrace`, `trullo` |
| `service` | `bridge_structure`, `service`, `transformer_tower` |
| `transportation` | `hangar`, `train_station`, `transportation` |

## Water

Water classes inherit the style of the water subtype.

| Overture subtype | Colour | RGB | Hex | Line or outline weight |
| --- | --- | ---: | --- | ---: |
| `canal` | Canal blue | 120, 172, 206 | `#78ACCE` | 0.25 |
| `human_made` | Muted blue | 150, 188, 213 | `#96BCD5` | 0.18 |
| `lake` | Pale blue | 177, 205, 226 | `#B1CDE2` | 0.18 |
| `ocean` | Ocean blue | 159, 197, 223 | `#9FC5DF` | 0.18 |
| `physical` | Soft blue | 168, 201, 221 | `#A8C9DD` | 0.18 |
| `pond` | Light blue | 190, 216, 232 | `#BED8E8` | 0.13 |
| `reservoir` | Reservoir blue | 167, 200, 222 | `#A7C8DE` | 0.18 |
| `river` | River blue | 111, 168, 207 | `#6FA8CF` | 0.25 |
| `spring` | Strong blue | 95, 159, 200 | `#5F9FC8` | 0.18 |
| `stream` | Stream blue | 118, 175, 209 | `#76AFD1` | 0.18 |
| `wastewater` | Blue grey | 143, 170, 178 | `#8FAAB2` | 0.18 |
| `water` | General water blue | 177, 205, 226 | `#B1CDE2` | 0.18 |
| Unclassified | Pale blue grey | 190, 205, 213 | `#BECDD5` | 0.18 |

## Land

Land classes inherit the style of the land subtype.

| Overture subtype | Colour | RGB | Hex | Line or outline weight |
| --- | --- | ---: | --- | ---: |
| `crater` | Muted brown | 184, 165, 143 | `#B8A58F` | 0.13 |
| `desert` | Pale desert sand | 228, 210, 162 | `#E4D2A2` | 0.13 |
| `forest` | Mid green | 117, 169, 116 | `#75A974` | 0.13 |
| `glacier` | Ice blue | 220, 236, 241 | `#DCECF1` | 0.13 |
| `grass` | Light green | 181, 211, 170 | `#B5D3AA` | 0.13 |
| `land` | Pale neutral | 229, 225, 212 | `#E5E1D4` | 0.13 |
| `physical` | Warm light grey | 200, 195, 182 | `#C8C3B6` | 0.13 |
| `reef` | Pale blue green | 183, 209, 200 | `#B7D1C8` | 0.13 |
| `rock` | Stone grey | 168, 163, 154 | `#A8A39A` | 0.13 |
| `sand` | Sand | 226, 211, 170 | `#E2D3AA` | 0.13 |
| `shrub` | Muted green | 157, 190, 143 | `#9DBE8F` | 0.13 |
| `tree` | Dark green | 95, 150, 95 | `#5F965F` | 0.18 |
| `wetland` | Blue green | 161, 199, 189 | `#A1C7BD` | 0.13 |
| Unclassified | Very light grey | 232, 232, 228 | `#E8E8E4` | 0.13 |

## Land use

Land-use classes inherit the style of the land-use subtype.

| Overture subtype | Colour | RGB | Hex | Outline weight |
| --- | --- | ---: | --- | ---: |
| `agriculture` | Pale yellow green | 224, 222, 178 | `#E0DEB2` | 0.13 |
| `aquaculture` | Pale blue green | 184, 215, 208 | `#B8D7D0` | 0.13 |
| `campground` | Pale brown | 214, 200, 168 | `#D6C8A8` | 0.13 |
| `cemetery` | Grey green | 201, 212, 194 | `#C9D4C2` | 0.13 |
| `construction` | Pale construction brown | 224, 207, 185 | `#E0CFB9` | 0.13 |
| `developed` | Pale warm grey | 221, 216, 207 | `#DDD8CF` | 0.13 |
| `education` | Pale violet | 222, 214, 231 | `#DED6E7` | 0.13 |
| `entertainment` | Pale pink | 229, 199, 213 | `#E5C7D5` | 0.13 |
| `golf` | Golf green | 197, 221, 181 | `#C5DDB5` | 0.13 |
| `grass` | Pale grass green | 216, 230, 200 | `#D8E6C8` | 0.13 |
| `horticulture` | Horticulture yellow green | 215, 214, 159 | `#D7D69F` | 0.13 |
| `landfill` | Muted brown grey | 200, 183, 165 | `#C8B7A5` | 0.18 |
| `managed` | Pale olive grey | 214, 218, 196 | `#D6DAC4` | 0.13 |
| `medical` | Pale rose | 231, 205, 210 | `#E7CDD2` | 0.13 |
| `military` | Pale khaki | 196, 197, 170 | `#C4C5AA` | 0.18 |
| `park` | Pale park green | 207, 226, 198 | `#CFE2C6` | 0.13 |
| `pedestrian` | Pale paving grey | 225, 220, 203 | `#E1DCCB` | 0.13 |
| `protected` | Protected green | 184, 215, 190 | `#B8D7BE` | 0.18 |
| `recreation` | Recreation green | 199, 222, 189 | `#C7DEBD` | 0.13 |
| `religious` | Pale religious violet | 220, 207, 227 | `#DCCFE3` | 0.13 |
| `residential` | Pale cream | 238, 231, 205 | `#EEE7CD` | 0.13 |
| `resource_extraction` | Quarry brown | 201, 185, 163 | `#C9B9A3` | 0.18 |
| `transportation` | Cool grey | 216, 218, 218 | `#D8DADA` | 0.13 |
| `winter_sports` | Snow blue grey | 221, 232, 236 | `#DDE8EC` | 0.13 |
| Unclassified | Very light grey | 232, 232, 228 | `#E8E8E4` | 0.13 |

## Land cover

| Overture subtype | Colour | RGB | Hex | Outline weight |
| --- | --- | ---: | --- | ---: |
| `barren` | Bare ground | 218, 204, 171 | `#DACCAB` | 0.13 |
| `crop` | Crop yellow green | 218, 214, 155 | `#DAD69B` | 0.13 |
| `forest` | Mid green | 117, 169, 116 | `#75A974` | 0.13 |
| `grass` | Light green | 181, 211, 170 | `#B5D3AA` | 0.13 |
| `mangrove` | Dark blue green | 111, 159, 134 | `#6F9F86` | 0.13 |
| `moss` | Moss green | 169, 190, 139 | `#A9BE8B` | 0.13 |
| `shrub` | Muted green | 157, 190, 143 | `#9DBE8F` | 0.13 |
| `snow` | Snow white blue | 234, 240, 242 | `#EAF0F2` | 0.13 |
| `urban` | Light urban grey | 214, 214, 209 | `#D6D6D1` | 0.13 |
| `wetland` | Blue green | 161, 199, 189 | `#A1C7BD` | 0.13 |
| Unclassified | Very light grey | 232, 232, 228 | `#E8E8E4` | 0.13 |

## Infrastructure

Infrastructure classes inherit the style of the infrastructure subtype.

| Overture subtype | Colour | RGB | Hex | Line or outline weight |
| --- | --- | ---: | --- | ---: |
| `aerialway` | Muted purple | 140, 122, 174 | `#8C7AAE` | 0.25 |
| `airport` | Airfield blue grey | 127, 156, 179 | `#7F9CB3` | 0.35 |
| `barrier` | Dark grey | 119, 117, 111 | `#77756F` | 0.25 |
| `bridge` | Dark brown | 125, 98, 77 | `#7D624D` | 0.35 |
| `communication` | Muted teal grey | 110, 144, 148 | `#6E9094` | 0.25 |
| `emergency` | Muted red | 180, 90, 90 | `#B45A5A` | 0.25 |
| `manhole` | Mid grey | 119, 119, 119 | `#777777` | 0.13 |
| `pedestrian` | Dark green | 91, 118, 89 | `#5B7659` | 0.18 |
| `pier` | Brown grey | 143, 123, 104 | `#8F7B68` | 0.25 |
| `power` | Muted orange brown | 178, 135, 82 | `#B28752` | 0.25 |
| `quay` | Blue grey | 126, 150, 163 | `#7E96A3` | 0.25 |
| `recreation` | Muted green | 127, 162, 115 | `#7FA273` | 0.18 |
| `tower` | Purple grey | 134, 124, 145 | `#867C91` | 0.25 |
| `transit` | Muted violet | 141, 114, 162 | `#8D72A2` | 0.25 |
| `transportation` | Slate blue | 111, 142, 166 | `#6F8EA6` | 0.25 |
| `utility` | Muted ochre | 154, 140, 92 | `#9A8C5C` | 0.20 |
| `waste_management` | Taupe | 140, 128, 114 | `#8C8072` | 0.20 |
| `water` | Strong blue | 94, 147, 181 | `#5E93B5` | 0.25 |
| Unclassified | Mid grey | 142, 142, 138 | `#8E8E8A` | 0.18 |

## Bathymetry

Use one colour for all bathymetry depth bands. Draw deeper bands before shallower bands.

| Overture type | Colour | RGB | Hex | Outline weight |
| --- | --- | ---: | --- | ---: |
| `bathymetry` | Muted depth blue | 141, 175, 200 | `#8DAFC8` | 0.13 |

## Transport

| Layer type | Colour | RGB | Hex | Line weight |
| --- | --- | ---: | --- | ---: |
| Motorway and trunk road | Dark brown | 69, 44, 32 | `#452C20` | 0.70 |
| Primary road | Brown | 104, 69, 47 | `#68452F` | 0.50 |
| Secondary road | Mid brown | 137, 103, 60 | `#89673C` | 0.35 |
| Tertiary road | Ochre | 153, 133, 76 | `#99854C` | 0.25 |
| Local road | Light ochre | 167, 155, 106 | `#A79B6A` | 0.18 |
| Service road | Pale brown | 184, 178, 151 | `#B8B297` | 0.13 |
| Major railway | Dark brown | 70, 48, 32 | `#463020` | 0.50 |
| Minor railway | Brown grey | 118, 92, 68 | `#765C44` | 0.25 |
| Cycle route | Dark green | 76, 112, 87 | `#4C7057` | 0.20 |
| Pedestrian route | Green grey | 91, 118, 89 | `#5B7659` | 0.18 |
| Other path | Light green grey | 111, 128, 105 | `#6F8069` | 0.13 |
| Ferry route | Blue | 65, 137, 180 | `#4189B4` | 0.25 |

## Boundaries and annotations

| Layer type | Colour | RGB | Hex | Line weight |
| --- | --- | ---: | --- | ---: |
| Site boundary | Dark red | 126, 53, 45 | `#7E352D` | 0.50 |
| Context boundary | Mid grey | 150, 150, 145 | `#969691` | 0.18 |
| Unresolved or QA | Magenta | 173, 43, 148 | `#AD2B94` | 0.35 |

## Overture schema references

- [Building subtypes](https://docs.overturemaps.org/schema/reference/buildings/types/building_subtype/)
- [Building classes](https://docs.overturemaps.org/schema/reference/buildings/types/building_class/)
- [Water subtypes](https://docs.overturemaps.org/schema/reference/base/types/water_subtype/)
- [Land subtypes](https://docs.overturemaps.org/schema/reference/base/types/land_subtype/)
- [Land-use subtypes](https://docs.overturemaps.org/schema/reference/base/types/land_use_subtype/)
- [Land-cover subtypes](https://docs.overturemaps.org/schema/reference/base/types/land_cover_subtype/)
- [Infrastructure subtypes](https://docs.overturemaps.org/schema/reference/base/types/infrastructure_subtype/)
- [Bathymetry](https://docs.overturemaps.org/schema/reference/base/bathymetry/)
