# Overture coverage recommendations

Reviewed against Overture Maps schema v2.0.0 on 18 September 2026.

## Current coverage

The downloader, normalizer, contract, Rhino representation policy, and audit use one shared type registry. They support:

- `building` and `building_part`;
- `segment`;
- `water`;
- `land`, `land_use`, and `land_cover`;
- `place`;
- `bathymetry`;
- `infrastructure`.

Land cover and bathymetry are 2D-only filled plan data. Bathymetry depth controls draw order, not Z. Infrastructure supports point, line, polygon, and multipolygon source geometry. Its 3D vertical position stays unresolved unless a reliable placement rule is added.

## Types outside the base model

| Overture type | Policy |
| --- | --- |
| `connector` | Keep it out of normal plans. Add it only for network routing or topology. |
| `address` | Add it only for address labels or geocoding. |
| `division` | Add it only for settlement labels or administrative context. |
| `division_area` | Add it only for administrative areas. |
| `division_boundary` | Add it only for administrative boundary lines. |

## Remaining presentation work

- Complete the road and rail class mappings when a project needs more classes.
- Add a small symbol and label system for places.
- Add a reviewed ground-placement whitelist for infrastructure when reliable source rules are available.
- Use extra Overture cartographic hints only after their direction and fallback rules are tested.

Keep `land`, `land_cover`, and `land_use` separate. They describe physical features, dominant surface cover, and human use respectively.

## Overture references

- [Overture schema](https://docs.overturemaps.org/schema/)
- [Base theme](https://docs.overturemaps.org/guides/base/)
- [Buildings theme](https://docs.overturemaps.org/guides/buildings/)
- [Transportation theme](https://docs.overturemaps.org/guides/transportation/)
- [Places theme](https://docs.overturemaps.org/guides/places/)
