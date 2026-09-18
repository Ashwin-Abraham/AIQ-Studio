# Overture coverage recommendations

Reviewed against Overture Maps schema v2.0.0 on 18 September 2026.

## Current coverage

The site-model downloader supports these Overture feature types:

- `building`
- `building_part`
- `segment`
- `water`
- `land`
- `land_use`
- `place`

See [download_overture.py](../scripts/download_overture.py) and [process_overture.py](../scripts/process_overture.py).

## Feature types that are not handled

| Overture type | Current status | Recommendation |
| --- | --- | --- |
| `land_cover` | Not downloaded. The cartographic reference has Land Cover styles, but the model has no matching source data. | Add this type first. Keep it separate from `land` and `land_use`. |
| `infrastructure` | Not downloaded. This omits bridges, airports, runways, transit stops, platforms, power lines, barriers, piers, utilities, and similar objects. | Add this type after `land_cover`. Use broad presentation groups instead of one style for each class. |
| `bathymetry` | Not downloaded. | Add only for coastal, river, lake, or marine projects. |
| `connector` | Deliberately rejected by the processed-data contract. | Keep it excluded from normal plans. Add it only when network routing or topology is in scope. |
| `address` | Not downloaded. | Keep it out of the base site model. Add it only when address labels or geocoding are required. |
| `division` | Not downloaded. | Add only when settlement labels or administrative context are required. |
| `division_area` | Not downloaded. | Add only when administrative areas are required. |
| `division_boundary` | Not downloaded. | Add only when administrative boundary lines are required. |

## Cartographic coverage status

### Land and land cover

`land` and `land_cover` are different Overture feature types. The cartographic reference now has a complete subtype table for each type. The skill downloads `land`. It does not download `land_cover`.

Keep these groups separate:

- `land`: physical land features such as forest, rock, sand, scrub, trees, and wetland;
- `land_cover`: dominant surface cover from ESA WorldCover;
- `land_use`: the human use of an area.

Do not use the Land Cover table as an automatic replacement for `land`.

### Buildings

The cartographic reference now covers every current Overture building subtype. It also maps every current building class to a subtype style when source subtype data is absent. Keep the exact Overture subtype and class in metadata.

### Transport

Road segments can include classes that do not have an explicit style mapping. Examples include:

- bridleway;
- cycleway;
- footway;
- living street;
- path;
- pedestrian;
- residential road;
- steps;
- track;
- unclassified;
- unknown.

Rail segments can include:

- funicular;
- light rail;
- monorail;
- narrow gauge;
- standard gauge;
- subway;
- tram;
- unknown.

Map these source classes into a small set of presentation classes. Do not create a separate colour for every source class.

### Places

The skill imports `place` points, but the cartographic reference has no symbol or label styles for them. Overture has a large place taxonomy. Use the top-level taxonomy group or `basic_category` to select a small symbol family.

### Water

The skill imports water polygons and water transport segments. The cartographic reference now covers every current Overture water subtype. Detailed water classes inherit their subtype style.

Add class-specific overrides only when the drawing needs them.

### Infrastructure and bathymetry

The cartographic reference now covers every current Overture infrastructure subtype. Infrastructure classes inherit their subtype style. Bathymetry uses one colour for all depth bands. Acquisition and Rhino geometry for these feature types remain deferred.

## Implementation gaps

The current Rhino writer creates polygon features as outline curves. It does not create filled meshes for land, land use, land cover, water, or 2D building footprints. See [geometry.py](../scripts/site_model/geometry.py).

The writer also does not apply the cartographic reference automatically. It does not currently set:

- layer colours;
- print widths;
- filled region meshes;
- display order;
- styles from Overture cartographic hints;
- detailed 2D order from transport `level` values.

Source properties are retained as metadata, so the source information is available for later styling.

## Recommended priority

1. Add `land_cover` acquisition and processing.
2. Add `infrastructure` acquisition and broad presentation groups.
3. Add optional `bathymetry` acquisition for coastal and marine sites.
4. Create filled planar meshes for polygon features.
5. Apply the cartographic colour and print-width tables in the Rhino writer.
6. Complete road and rail class mappings.
7. Add a small symbol and label system for places.
8. Use Overture transport `level` and cartographic sort hints for 2D drawing order where they are reliable.
9. Keep addresses, divisions, and connectors optional.

## Overture references

- [Overture schema](https://docs.overturemaps.org/schema/)
- [Base theme](https://docs.overturemaps.org/guides/base/)
- [Buildings theme](https://docs.overturemaps.org/guides/buildings/)
- [Transportation theme](https://docs.overturemaps.org/guides/transportation/)
- [Places theme](https://docs.overturemaps.org/guides/places/)
- [Addresses theme](https://docs.overturemaps.org/guides/addresses/)
- [Divisions theme](https://docs.overturemaps.org/guides/divisions/)
