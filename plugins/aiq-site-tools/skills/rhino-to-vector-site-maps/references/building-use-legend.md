# Building use legend

Policy: `aiq-building-use-2026-10-03`, version 2.

Use this reference for Building Use and Detailed Building Use. It defines a fixed reusable legend, rather than groups selected from site counts. Show present groups in table order. Keep absent groups in the style registry so their colour assignments remain fixed across sites.

## Shared source rules

Use parent footprints by default on both use boards. A part can inherit a known parent use, but it is not another building in coverage counts. Use the same footprint selection, extent, and exclusions for Building Use and Detailed Building Use.

Mixed use requires explicit evidence recorded with its method. A nearby Place or surrounding land-use area does not establish whole-building use. Places can supply optional labelled point symbols after checking their release-specific taxonomy, operating status, and confidence.

## Group colours and class assignments

The class lists are explicit AIQ display assignments, not an Overture subtype hierarchy. They cover the 88 classes in schema v2.0.0, including the 87 classes in v1.18.0. Preserve each exact source value. A class describes use or building form; add this note to both boards.

| Group | Fill | Classes |
| --- | --- | --- |
| Houses | `#D8BE66` | house, dwelling_house, bungalow, detached, semi, semidetached_house, terrace, cabin, stilt_house, trullo |
| Apartments and communal housing | `#B99D45` | apartments, dormitory |
| Other | `#F0E5BD` | residential, ger, houseboat, static_caravan |
| Retail | `#E78A52` | retail, supermarket, kiosk |
| Offices | `#96502D` | office |
| Other commercial | `#B66A3C` | commercial |
| Industrial | `#8C78A8` | industrial, factory, manufacture, digester |
| Storage | `#B2A3C6` | warehouse, storage_tank |
| Education | `#527CB8` | school, college, university, kindergarten |
| Healthcare | `#C85C80` | hospital |
| Civic and community | `#4B9B96` | civic, public, government, library, fire_station, post_office |
| Religion | `#A65A9E` | religious, cathedral, chapel, church, monastery, mosque, presbytery, shrine, synagogue, temple, wayside_shrine |
| Leisure and hospitality | `#C99AC6` | hotel, sports_centre, sports_hall, stadium, grandstand, pavilion |
| Transport | `#7D8993` | transportation, parking, train_station, hangar |
| Service and utilities | `#596A76` | service, transformer_tower, toilets |
| Outbuildings and ancillary structures | `#B2BAC0` | outbuilding, allotment_house, beach_hut, boathouse, carport, garage, garages, hut, shed, shelter |
| Agriculture | `#8C9E55` | agricultural, barn, cowshed, farm, farm_auxiliary, glasshouse, greenhouse, silo, slurry_tank, stable, sty |
| Military | `#727A4C` | military, bunker, guardhouse |
| Mixed use | `#A88A58` | Explicit project evidence of multiple uses; no assumed Overture class |
| Unknown | None | No supported group; grey cross hatch |

`roof` and `bridge_structure` are structural classes. Select their fill from a valid source subtype. With no subtype, use no thematic fill. Keep these classes visible on the detailed board with their own class colours. Their form alone does not establish occupied use.

For a mapped class, use the assigned group. Where class and subtype indicate conflicting uses, keep the class assignment and report both source values. A missing or unsupported class uses this subtype fallback:

| Source subtype | Group |
| --- | --- |
| residential | Other |
| commercial | Other commercial |
| industrial | Industrial |
| education | Education |
| medical | Healthcare |
| civic | Civic and community |
| religious | Religion |
| entertainment | Leisure and hospitality |
| transportation | Transport |
| service | Service and utilities |
| outbuilding | Outbuildings and ancillary structures |
| agricultural | Agriculture |
| military | Military |

Keep an unsupported nonempty class in the report and exact source layer. In Detailed Building Use, give it its own colour entry, even if its group uses a subtype fallback. Never fold a rare class into another class on that board.

## Housing groups

Use three groups across all sites. Houses combines general houses and named house forms. Apartments and communal housing combines apartments and dormitories. Other retains unusual dwelling forms and records that establish residential use without a specific form. These are AIQ display groups based on the full Overture class set, not site frequencies or dwelling counts. A house class does not establish tenure, occupancy, or the number of dwellings. Keep agricultural buildings and religious accommodation in their existing groups.

## Detailed colour registry

Read [building-use-colours.json](building-use-colours.json) for the fixed detailed colour registry. Each recorded class has one solid fill. Each supported subtype without a class has a separate `subtype:<value>` colour and a “Class not recorded” legend entry. Colours remain fixed when classes are absent. Group headings organise the detailed legend; the group fill applies only to the broad Building Use board.

Use solid colours for all recorded classes, including structural classes. A structural class colour identifies form, not occupied use. With no supported group, put its exact class under “Use not established”. Keep an unsupported nonempty class visible with a new distinct colour, record it in the registry, and retain it on revisions. Preserve existing assignments when extending the registry.

Use only the Unknown cross hatch on either use board: grey +45/-45 lines, 0.15 mm stroke, 1.5 mm spacing, clipped to footprints and holes, with no thematic fill in map or key. On Detailed Building Use, Unknown means no recorded class and no supported subtype. A recorded structural class still has its class colour when its use is not established. Apply no other hatches on this board. Height-method hatches on Building Height are unchanged.

## Legend layout and checks

Building Use shows one key per present group and no class hatches. Its Unknown group uses the grey cross hatch. Detailed Building Use shows group headings, then every present class under that group with its class colour swatch and count. Include subtype-only and unsupported-class entries where present. With no supported group, show the exact class and its colour under “Use not established”.

Keep the map frame, scale, and template unchanged. If the detailed legend exceeds the template legend area at its normal text size, add numbered A3 legend continuation sheets to the PDF and editable document. Place every legend continuation sheet immediately after its map, before the next map theme. Put the final sheet reference on the map. Check the exported page order, page numbers, and cross-references together. Include all keys across those sheets; retain rare classes and legible text. Legend-only sheets do not count as extra map themes.

Save group assignments, source class and subtype, fallback or conflict status, colours, colour registry version, and counts in `map-config.json` or its linked style data. Use source IDs to link the drawing to retained properties. “All available data” here means all recorded building-use and type classifications in the selected extent and release; retain other building attributes as source metadata, not extra use categories. Places categories, heights, and roof materials have separate meanings.

Check that every displayed building has exactly one group result and one detailed class or missing-class state. Reconcile totals between both use boards and the source coverage report. Check all legend entries against their map styles and inspect dense areas, small footprints, holes, and continuation sheets at print size. Retain small features even where a colour is hard to distinguish; use a source-ID label or linked detail inset when needed. Report unresolved source conflicts and missing fields.

Schema references: [Building fields](https://docs.overturemaps.org/schema/reference/buildings/building/), [Building classes](https://docs.overturemaps.org/schema/reference/buildings/types/building_class/), and [Building subtypes](https://docs.overturemaps.org/schema/reference/buildings/types/building_subtype/). Check the schema for the selected release when processing new data.
