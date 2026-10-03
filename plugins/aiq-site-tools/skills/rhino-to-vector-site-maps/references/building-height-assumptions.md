# Building height assumptions

Policy: `aiq-building-height-2026-10-03`, version 1.

Use this reference to resolve building heights from source values, floor counts, or building types. These values are AIQ starting assumptions for site analysis. They are not Overture measurements, statistical averages, or design requirements. Review them for the project location and record any overrides.

## Selection and provenance

Apply this order to each building:

1. Valid positive source `height`.
2. Valid positive integer `num_floors` multiplied by **3.5 m**. Add a valid non-negative source `roof_height` only to this floor-derived height.
3. The exact source `class` default below. When class is absent, use the source `subtype` default. An unsupported nonempty class remains Unknown until reviewed.
4. Unknown when neither a valid height, floor count, nor supported type is available.

The tables give the assumed full height, including a nominal roof allowance. Add no separate roof term to a type default or an explicit source height. For raised features, add valid `min_height`; otherwise use valid `min_floor` multiplied by 3.5 m. If both offset fields are absent, assume a zero bottom offset. Invalid supplied offsets remain unresolved.

Retain source properties unchanged. Record the selected value, input fields, method, policy version, table key, and any project override in the derived data. Use method values `source`, `floors`, `type`, and `unknown`. A floor-derived offset makes a source-height result `floors`. A type-derived height remains `type` even when its offset uses floors.

Building parts use their own height and floor fields first. Overture parts do not have the parent building's use classification. A part without sufficient fields can inherit the parent's resolved top and method; record this as inheritance, not independent evidence. Apply neither a whole-building type height to each stacked part nor a default height taken from a 3D volume.

The table includes a value for every published class in schema v1.18.0 and v2.0.0. The latter adds `shelter`. Compare the class set when adopting a later schema. `townhouse` is not a class in these versions. Use the actual source value, commonly `terrace` or `house`; do not invent an alias from appearance.

## Detailed class defaults

These are explicit starting models. A floor-based explanation in this table does not make a value a floor-count estimate: it remains a **type assumption**, because the source supplies no floor count. Taller local examples do not change the default unless the project records an override.

| Overture class | Default height (m) | Assumption basis |
| --- | ---: | --- |
| agricultural | 6 | General farm structure |
| allotment_house | 3 | Small garden hut |
| apartments | 17.5 | Five nominal residential floors |
| barn | 8 | Tall single agricultural volume |
| beach_hut | 3 | Small single-storey hut |
| boathouse | 5 | Single boat-storage volume |
| bridge_structure | 6 | Structural depth only; no inferred bridge clearance |
| bungalow | 4.5 | One residential floor with roof |
| bunker | 3 | Above-ground structure only |
| cabin | 4 | One compact floor with roof |
| carport | 3 | Low open-sided cover |
| cathedral | 25 | Main roof mass; towers and spires excluded |
| chapel | 8 | Small worship hall; spire excluded |
| church | 14 | Main worship hall; tower and spire excluded |
| civic | 10.5 | Three nominal floors |
| college | 14 | Four nominal floors |
| commercial | 10.5 | Three nominal floors |
| cowshed | 5 | Single livestock hall |
| detached | 8 | Two residential floors with roof |
| digester | 10 | Process vessel envelope |
| dormitory | 14 | Four nominal residential floors |
| dwelling_house | 8 | Two residential floors with roof |
| factory | 10 | Production hall envelope |
| farm | 8 | Farmhouse-sized building |
| farm_auxiliary | 5 | Single agricultural support volume |
| fire_station | 8 | Appliance hall and upper accommodation |
| garage | 3.5 | One vehicle-storage floor |
| garages | 3.5 | Single-storey garage block |
| ger | 3 | Low tent-shaped dwelling |
| glasshouse | 4.5 | Single growing enclosure |
| government | 14 | Four nominal floors |
| grandstand | 12 | Spectator stand and roof envelope |
| greenhouse | 4.5 | Single growing enclosure |
| guardhouse | 3.5 | One control-room floor |
| hangar | 15 | Aircraft enclosure |
| hospital | 17.5 | Five nominal floors |
| hotel | 17.5 | Five nominal accommodation floors |
| house | 8 | Two residential floors with roof |
| houseboat | 4 | Superstructure above its base; no water level inferred |
| hut | 3 | Small single-storey structure |
| industrial | 9 | General industrial hall |
| kindergarten | 4.5 | Single teaching floor with roof |
| kiosk | 3 | Small single-storey sales unit |
| library | 10.5 | Three nominal floors |
| manufacture | 10 | Production hall envelope |
| military | 7 | Two nominal accommodation floors |
| monastery | 10.5 | Three nominal floors; towers excluded |
| mosque | 12 | Main prayer hall; minarets excluded |
| office | 17.5 | Five nominal office floors |
| outbuilding | 3.5 | One support floor |
| parking | 10.5 | Three nominal parking levels; high uncertainty |
| pavilion | 5 | Single hall with roof |
| post_office | 7 | Two nominal floors |
| presbytery | 8 | Two residential floors with roof |
| public | 10.5 | Three nominal public-building floors |
| religious | 10 | Main worship volume; towers excluded |
| residential | 10.5 | Broad residential fallback only |
| retail | 5 | Single trading hall |
| roof | 3.5 | Freestanding cover only; stacked roof elevation unresolved |
| school | 7 | Two nominal teaching floors |
| semi | 8 | Two residential floors with roof |
| semidetached_house | 8 | Two residential floors with roof |
| service | 3.5 | One service floor |
| shed | 3 | Small single-storey store |
| shelter | 3 | Low open-sided shelter; v2.0.0 addition |
| shrine | 4 | Small worship structure |
| silo | 15 | Vertical storage envelope |
| slurry_tank | 4 | Low storage vessel |
| sports_centre | 10 | Sports hall envelope |
| sports_hall | 9 | Single tall sports volume |
| stable | 5 | Single livestock hall |
| stadium | 25 | Main spectator structure; masts excluded |
| static_caravan | 3.5 | One accommodation level |
| stilt_house | 5 | Dwelling height; explicit base offset applied separately |
| storage_tank | 8 | General storage vessel; high uncertainty |
| sty | 3.5 | Low livestock enclosure |
| supermarket | 6 | Single retail hall with service zone |
| synagogue | 10 | Main worship hall |
| temple | 12 | Main worship hall; towers excluded |
| terrace | 10.5 | Three nominal floors in a terraced house |
| toilets | 3.5 | One service floor |
| train_station | 10 | Main station hall; platforms excluded |
| transformer_tower | 10 | Small utility tower |
| transportation | 8 | General transport building |
| trullo | 4.5 | Single dwelling with conical roof |
| university | 14 | Four nominal teaching floors |
| warehouse | 10 | Single storage hall |
| wayside_shrine | 3 | Small roadside worship structure |

For `bridge_structure`, resolve a numeric height above ground only with a supported bottom offset; zero is supported only when explicitly supplied. For `roof`, use its type default only when a freestanding cover is established. A roof above an unknown building or a bridge with unknown clearance remains Unknown despite having a listed structural default. Record these exceptions in the report.

## Broad subtype defaults

Use these only when the detailed class is absent. Record `subtype:<value>` as the table key so later review can distinguish broad and detailed assumptions.

| Overture subtype | Default height (m) | Assumption basis |
| --- | ---: | --- |
| agricultural | 6 | General farm structure |
| civic | 10.5 | Three nominal floors |
| commercial | 10.5 | Three nominal floors |
| education | 10.5 | Three nominal teaching floors |
| entertainment | 10 | General assembly hall |
| industrial | 9 | General industrial hall |
| medical | 14 | Four nominal care floors |
| military | 7 | Two nominal accommodation floors |
| outbuilding | 3.5 | One support floor |
| religious | 10 | Main worship volume |
| residential | 10.5 | Broad residential fallback |
| service | 3.5 | One service floor |
| transportation | 8 | General transport building |

## Taxonomy sources

The Overture references define the class names and fields, not the numeric assumptions above. Checked on 3 October 2026:

- [Building classes, schema v1.18.0](https://docs.overturemaps.org/schema/v1.18.0/reference/buildings/types/building_class/).
- [Building classes, schema v2.0.0](https://docs.overturemaps.org/schema/reference/buildings/types/building_class/).
- [Building subtypes](https://docs.overturemaps.org/schema/reference/buildings/types/building_subtype/).
- [Height and floor fields](https://docs.overturemaps.org/schema/v1.18.0/reference/buildings/building/).
