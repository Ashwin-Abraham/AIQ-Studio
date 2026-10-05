---
name: rhino-to-vector-site-maps
description: Create editable vector site analysis maps from a checked Rhino 2D site source, with a shared base map, thematic boards, and a review PDF.
---

# Vector site maps

1. Select one checked 2D source, CRS, and release. Use the [Rhino data contract](../rhino-site-data-model/references/processed-data-contract.md); use `AIQ Site::2D` if the processed source is missing.
2. Read the [map specification](references/map-specification.md) and [board template](assets/board-template.svg). Select the boards, read their linked drawing specifications, and complete the data coverage check before drawing. For Radiation, Isovist, or Seasonal Shadows, follow the drawing reference's analysis workflow before preparing its artwork. Determine one extent and scale for the map frame. Reuse saved framing only when it passes the template and site-fit checks.
3. For Terrain Height or Terrain Slope, read the [terrain workflow](references/terrain-analysis.md). Check terrain in the Rhino model before analysis. If terrain is absent, skip both maps. Offer terrain creation through the Rhino site model skill only with user agreement. Complete and check the Rhino analysis before creating SVG artwork.
4. Build every board from the unchanged template. Build `Base_Map.ai` first and add it as the linked bottom underlay on every artboard in `Site_Analysis.ai`; every instance must use the same transform. Use the [north arrow](assets/north-arrow.svg) where useful.
5. Save a review PDF and a validation report. Check every artboard, the scale bar, north direction, map alignment, and link status. Record each failed check.

Save native `.ai` files in an application that supports them. If one is unavailable, deliver prepared vector artwork and identify the `.ai` files as unfinished.
