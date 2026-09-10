# Coordinate-to-Rhino base site model workflow

Research checked on 8 September 2026.

## Research question

How can a user select any point on Earth, define an Area of Interest (AOI), get useful global site data, and make a layered 3D Rhino Site Model? The workflow must keep coordinates, sources, licences, checks, and reruns clear. It must also give a fast Site Data Report when a layer cannot become reliable geometry at a reasonable cost.

## Answer

Use a two-coordinate workflow. Keep the AOI and source data in real-world coordinates. Process the data in a suitable local projected coordinate reference system (CRS). Move the final geometry to a local Rhino origin. Store the full inverse transform and the Rhino Earth Anchor Point with the model.

Use these tools as the first implementation:

- Use GeoJSON in WGS 84 longitude and latitude for the portable AOI.
- Use QGIS for drawing, inspection, and manual correction.
- Use pinned GDAL and PROJ commands for repeatable conversion, clipping, and coordinate operations.
- Use Overture Maps for the first global vector baseline. Use its buildings, transportation, water, land, and land-cover data only as context.
- Use Copernicus DEM for the first global terrain baseline, subject to current access rights and attribution duties.
- Use a selected Copernicus Sentinel-2 product for optional image context. Do not copy Google base-map content into the model.
- Use `rhino3dm` to write the main `.3dm` output without an active Rhino session.
- Keep a tested DXF import route and the Heron Grasshopper add-on as optional review paths. Do not make either path the only workflow.
- Produce a cited Site Data Report entry when a source has unclear rights, weak accuracy, missing height, failed conversion, excessive geometry, or a high manual or AI cost.

This is a base workflow. A separate location-specific enhancement workflow must find better local data after the user gives an AOI. Neither global coverage nor a successful import makes data survey-grade, current, complete, or legally authoritative.

## Verified facts

### AOI capture and exchange

- Google My Maps can export a map as KML or KMZ. Google Earth can draw lines and polygons, and an Earth project can export KML. These products are valid manual AOI entry tools ([Google My Maps help](https://support.google.com/mymaps/answer/3109452?co=GENIE.Platform%3DDesktop&hl=en), [Google Earth help](https://support.google.com/earth/answer/148072?hl=en), [Google Earth project help](https://support.google.com/earth/answer/9394930?co=GENIE.Platform%3DDesktop&hl=en-SE)).
- KML polygon coordinates use longitude, latitude, and optional altitude. An altitude can also be clamped to the Google Earth ground surface. A KML altitude is therefore not safe evidence of surveyed height without a separate source record ([Google KML reference](https://developers.google.com/kml/documentation/kmlreference)).
- GeoJSON RFC 7946 uses WGS 84 longitude and latitude in decimal degrees. The optional third coordinate is ellipsoidal height in metres. The RFC does not support an alternate CRS member ([RFC 7946](https://www.rfc-editor.org/info/rfc7946/)).
- The open-source geojson.io editor can draw points, lines, and polygons and export GeoJSON and KML. QGIS can provide the same functions in a managed desktop GIS ([geojson.io repository](https://github.com/mapbox/geojson.io), [QGIS documentation](https://docs.qgis.org/latest/en/docs/user_manual/)).
- Google Maps Platform terms restrict extraction and copying of Google map content. The OpenStreetMap copyright page also tells contributors not to copy from Google Maps. A user-drawn AOI is different from traced Google roads, buildings, imagery, or labels ([Google Maps Platform terms](https://cloud.google.com/maps-platform/terms), [OpenStreetMap copyright](https://www.openstreetmap.org/copyright)).

### Global baseline data

- Overture Maps publishes global buildings, transportation, water, land, and land-cover features. Its Python client can download a feature type inside a longitude-latitude bounding box as GeoJSON, GeoJSON sequence, or GeoParquet. The tool uses the Overture STAC catalogue by default ([Overture Python client](https://docs.overturemaps.org/getting-data/overturemaps-py/)).
- Overture building coverage is global, but many footprints come from machine-learning sources. Overture states that footprint precision is lower in some areas, especially where machine-derived data has a large share. Building heights are present only when available ([Overture buildings guide](https://docs.overturemaps.org/guides/buildings/)).
- Overture transportation features model roads, rail, and water routes as centre-line segments. Its base theme supplies land, water, infrastructure, land use, and land cover. The accuracy and completeness of many base features match their upstream OpenStreetMap data ([Overture transportation guide](https://docs.overturemaps.org/guides/transportation/), [Overture base guide](https://docs.overturemaps.org/guides/base/)).
- The Overture base, buildings, divisions, and transportation themes use the Open Database Licence (ODbL). Overture publishes source-level attribution text. The workflow must keep the attribution for every used theme and release ([Overture attribution and licensing](https://docs.overturemaps.org/attribution/)).
- OpenStreetMap data uses ODbL. It requires credit. A distributed derivative database can also have share-alike duties. The public map-tile service is not a bulk data source ([OpenStreetMap copyright](https://www.openstreetmap.org/copyright), [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/)).
- ESA WorldCover supplies a global 10 m land-cover product under CC BY 4.0 and gives required acknowledgement text. Its class cells do not describe parcel boundaries or legal land use ([ESA WorldCover data access](https://esa-worldcover.org/en/data-access)).
- Copernicus DEM GLO-30 and GLO-90 have global coverage. The product is a digital surface model. It can include buildings, infrastructure, and vegetation. The documented horizontal CRS is WGS 84. The vertical reference is EGM2008, EPSG 3855. The GLO-30 grid spacing is one arc second, and its stated global absolute vertical accuracy is less than 4 m at 90% linear error. Local errors can be different ([Copernicus DEM collection](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM), [Copernicus DEM product handbook](https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf)).
- Copernicus changed access to the GLO-30 view service in 2026. A user must confirm the current account category, service, and licence before a run. GLO-90 is the present default in the Sentinel Hub DEM service when no DEM is set ([Copernicus notice, 25 August 2026](https://dataspace.copernicus.eu/news/2026-8-25-copernicus-dem-30m-view-service-update), [Copernicus DEM API documentation](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM.html)).
- Copernicus Sentinel data allows reproduction, distribution, adaptation, and combination, subject to its legal notice and source notice. The Copernicus Data Space STAC API can search Sentinel-2 Level-2A products by geometry, date, and cloud cover ([Copernicus Sentinel licence](https://cds.climate.copernicus.eu/licences/ec-sentinel), [Copernicus STAC API](https://documentation.dataspace.copernicus.eu/APIs/STAC.html)).

### Processing and Rhino exchange

- GDAL can clip vector data, make invalid geometry valid, change format, and reproject data. It can also clip raster data with a georeferenced polygon ([GDAL `ogr2ogr`](https://gdal.org/en/stable/programs/ogr2ogr.html), [GDAL raster clip](https://gdal.org/en/stable/programs/gdal_raster_clip.html)).
- PROJ selects coordinate operations from its CRS database and available transformation grids. A vertical transformation can fail or use a less suitable operation when a required grid is not available. Tool, database, grid, and operation versions can therefore affect a rerun ([PROJ operation selection](https://proj.org/en/stable/operations/operations_computation.html)).
- Rhino can import `.3dm`, DXF, DWG, OBJ, PLY, E57, and several point formats. Rhino does not list GeoJSON or GeoPackage as native import formats ([Rhino 8 import and export formats](https://docs.mcneel.com/rhino/8/help/en-us/fileio/_index_of_import_export_file_types.htm)).
- McNeel's `rhino3dm` library can create meshes, curves, surfaces, layers, object attributes, and other Rhino objects. It can read and write `.3dm` files without Rhino ([McNeel `rhino3dm` repository](https://github.com/mcneel/rhino3dm)).
- Rhino has an Earth Anchor Point for latitude, longitude, elevation, and related location data. Its linear model-to-Earth transform assumes that the model is small enough to ignore Earth curvature ([Rhino Earth Anchor Point API](https://developer.rhino3d.com/api/RhinoCommon/html/T_Rhino_DocObjects_EarthAnchorPoint.htm), [model-to-Earth transform](https://developer.rhino3d.com/api/RhinoCommon/html/M_Rhino_DocObjects_EarthAnchorPoint_GetModelToEarthTransform.htm)).
- McNeel warns that geometry far from the world origin can cause display and precision problems. Its units guidance says that Rhino works best when model size stays at or below 100,000 model units and the absolute tolerance is suitable for the smallest feature ([McNeel floating-point note](https://wiki.mcneel.com/rhino/floating_point_faq), [Rhino units and tolerances](https://docs.mcneel.com/rhino/mac/help/en-us/documentproperties/units.htm)).
- Heron is an MIT-licensed Grasshopper add-on. It uses GDAL and the Rhino Earth Anchor Point to import, locate, scale, and clip vector, raster, topographic, and OpenStreetMap data. Its published repository had a release in January 2026, but it remains an optional third-party dependency ([Heron repository](https://github.com/blueherongis/Heron)).

## Recommended workflow

The items in this section are design recommendations. They are not claims from the source owners.

### 1. Capture the point and boundary

Ask the user for one reference point. Accept a closed boundary polygon when the user supplies one. If the user supplies only a point, ask for a context distance or a named extent rule. Make a polygon from that declared rule. Do not select an arbitrary area silently. The point can be inside the polygon. Give the point a clear purpose, such as `site_reference_point` or `entrance_reference_point`.

Preferred path:

1. Draw the point and polygon in QGIS or geojson.io.
2. Save one RFC 7946 GeoJSON `FeatureCollection` as `aoi.geojson`.
3. Use only `Point`, `Polygon`, or `MultiPolygon` features.
4. Put `id`, `name`, `role`, `created_at`, and `created_by` in each feature.
5. Validate ring closure, geometry validity, coordinate order, longitude range, latitude range, and the point-to-polygon relation.

Google path:

1. Draw the boundary in Google My Maps or Google Earth.
2. Export KML or KMZ.
3. Convert only the user-created features to GeoJSON.
4. Do not trace or export Google imagery, roads, buildings, labels, or terrain.
5. Check the converted polygon in QGIS against its source drawing.

Use GeoJSON as the portable AOI because its CRS and coordinate order are explicit in RFC 7946. Keep the original KML when it is the user's input. The original file is evidence of what the user supplied.

### 2. Create a run record

Create a unique run folder. Do not overwrite an earlier run.

```text
runs/<run-id>/
  input/aoi.geojson
  raw/<source>/<unchanged files>
  work/<derived GIS files>
  output/site-model.3dm
  output/site-data-report.md
  manifest.json
  checks.json
  logs/
```

The run identifier must not depend only on the current date. Add a short random or content-derived value. Save the exact AOI checksum and configuration checksum.

### 3. Choose coordinate systems and model units

Use three coordinate frames:

| Frame | Purpose | Required record |
|---|---|---|
| WGS 84 longitude and latitude | AOI exchange and catalogue search | `OGC:CRS84` or the exact source CRS and axis order |
| Local projected CRS | clipping, distance, area, and geometry preparation | EPSG code or full WKT2, coordinate operation, PROJ version, and required grids |
| Rhino local Cartesian frame | stable modelling near `0,0,0` | units, local origin in projected coordinates, rotation, vertical offset, and inverse transform |

Choose a projected CRS whose official area of use contains the AOI. A suitable national grid is usually better than a generic global projection. A suitable UTM zone can be the default for a small AOI when no better official local grid exists. Do not use Web Mercator for measured model geometry.

Set Rhino model units to metres for the base workflow. Set an absolute tolerance that matches the useful precision of the best input. Do not use a tolerance that suggests millimetre accuracy when the terrain cell, building footprint, or coordinate transform is much less accurate.

Choose one projected point near the AOI centre as the local origin. Subtract its easting, northing, and chosen vertical origin from all output geometry. Keep the full values in the manifest. Do not round the stored transform. Set the Rhino Earth Anchor Point when the selected `rhino3dm` API supports all required fields. Also store the transform as document user text because an anchor point alone does not state the projected CRS or full processing operation.

### 4. Get the baseline data

Download by the AOI bounding box, then clip with the AOI polygon. A bounding-box request is an access optimization. It is not the final spatial filter.

| Model content | First baseline | Acquisition rule | Initial geometry rule |
|---|---|---|---|
| Terrain | Copernicus DEM GLO-30 when access permits; otherwise GLO-90 | Select and record product ID, release, resolution, vertical datum, access route, and terms | Clip raster, transform horizontal coordinates, handle the vertical datum, sample to a controlled grid, and triangulate a mesh |
| Buildings | Overture buildings | Pin an Overture release and query the bounding box | Keep footprints. Extrude only when a credible height or level value exists. Keep unknown-height buildings as footprints or clearly marked proxy masses |
| Roads and paths | Overture transportation | Query `segment`, then filter `subtype=road` and needed classes | Import centre-lines. Create road edges or surfaces only when width data is usable and the rule is recorded |
| Water | Overture base water | Query the water type | Keep water polygons or lines. Do not infer a flood level or depth |
| Land cover | Overture base land cover or direct ESA WorldCover | Pin release or product version | Use classified polygons or clipped raster cells. Do not turn a class into a legal land-use claim |
| Imagery | Copernicus Sentinel-2 Level-2A | Search the AOI and time range. Select a low-cloud product and record its product ID | Make a clipped, north-correct, georeferenced image plane only when the licence and pixel transform remain clear |

Do not add addresses, owner data, utilities, zoning, cadastral boundaries, or regulatory constraints to the global base model by inference. The location-specific workflow must find an issuing authority for those items.

### 5. Preserve raw inputs

Save each downloaded response unchanged when the terms permit local storage. If a source does not permit this, save the stable record ID, request, response headers that matter, and access instructions. Calculate SHA-256 for each stored file. Never treat an AI summary, screen capture, or rendered web tile as the source dataset.

### 6. Normalize and clip

Use a pinned command or script for each data type.

For vector data:

1. Confirm or assign the source CRS from source metadata. Do not guess silently.
2. Preserve the source feature ID and source attributes.
3. Repair geometry only through a named operation. Keep a count of changed or dropped features.
4. Reproject to the selected local projected CRS.
5. Clip to the AOI, or to a declared context buffer around it.
6. Normalize geometry type and field names.
7. Test for empty output, invalid geometry, duplicate IDs, and coordinates outside the expected extent.

For raster data:

1. Confirm horizontal CRS, vertical datum, pixel interpretation, unit, no-data value, resolution, and acquisition date.
2. Reproject to the local projected CRS at a declared target resolution.
3. Clip with the AOI or context buffer.
4. Keep no-data as no-data. Do not replace gaps without a named rule.
5. For terrain, transform vertical values only when a verified operation and its grids are available.
6. Record interpolation, resampling, grid spacing, and vertical offset.

Use GDAL and PROJ for these operations. Use QGIS to inspect the result and to make a saved manual correction layer. Do not edit an unchanged raw file.

### 7. Make Rhino geometry

Use `rhino3dm` as the main export path:

1. Create one `.3dm` file in metres.
2. Create the stable layer tree before objects.
3. Convert projected X, Y, and Z values to local Rhino coordinates with the recorded transform.
4. Create terrain as a mesh. Keep its source cell size and any mesh decimation rule in object user text.
5. Create buildings as closed planar curves, valid extrusions, or meshes. Record whether the height is observed, stated, derived from levels, or a proxy.
6. Create roads as curves. Add surfaces only when a width rule passes review.
7. Create water and land-cover polygons as curves or light meshes.
8. Put imagery on a separate reference layer. Keep the image file beside the model when the `.3dm` does not embed it reliably.
9. Add source IDs, confidence, dates, and manifest asset IDs as object user text where this does not make the file too large.
10. Write the Earth Anchor Point and document user text for CRS, local origin, vertical reference, run ID, manifest path, and generated time.

Use DXF as a simple manual exchange path when direct `.3dm` generation fails for vector curves. Rhino can import DXF and preserve layers. DXF does not carry the full GIS CRS and provenance contract, so the manifest remains required.

Use Heron only when a Grasshopper review or parametric import gives clear value. Pin the Rhino, Grasshopper, Heron, GDAL, and PROJ versions. Save the Grasshopper definition. The standalone `rhino3dm` path remains the default because it can run without Rhino and has a smaller operating boundary.

### 8. Use a stable layer contract

Use ASCII layer names with a numeric order. Do not put a source product name in the main semantic layer name.

```text
00_CONTROL
  AOI
  REFERENCE_POINT
  LOCAL_ORIGIN
  CHECKS
10_TERRAIN
  MESH
  CONTOURS
20_BUILDINGS
  FOOTPRINTS
  MASSES_VERIFIED
  MASSES_PROXY
30_TRANSPORT
  ROAD_CENTERLINES
  PATH_CENTERLINES
  RAIL_CENTERLINES
40_WATER
  AREAS
  LINES
50_LAND_COVER
  CLASSES
60_IMAGERY
  REFERENCE
90_REPORT_ONLY
```

Add `source_asset_id`, `source_feature_id`, `confidence`, and `status` to objects. Use `status` values such as `verified-source`, `derived`, `proxy`, and `review-required`. Keep legal or authoritative local layers out of these global baseline layers until the location-specific workflow supplies them.

### 9. Write the provenance manifest

Use one JSON manifest for the run. STAC is a useful source model because a STAC Item is a GeoJSON feature with time and asset links, and a STAC Collection records providers and licences. The stable STAC File Info extension defines a checksum field ([OGC STAC standard](https://www.ogc.org/standards/stac/), [STAC File Info extension](https://github.com/stac-extensions/file)). Adapt these fields. Do not claim that the project manifest is a STAC catalogue unless it passes the applicable schemas.

Record at least:

- run ID and workflow version;
- AOI geometry, AOI checksum, and reference point;
- source title, issuing body, stable URL, record or product ID, and release;
- query text or request body and access time in UTC;
- unchanged file name, byte size, media type, and SHA-256;
- licence identifier, licence URL, attribution text, and redistribution class;
- source horizontal CRS, axis order, vertical datum, unit, resolution, stated accuracy, and date;
- output CRS as EPSG or WKT2;
- chosen coordinate operation, PROJ version, database version, and grid files;
- clip geometry or buffer, geometry repair, resampling, simplification, height, and mesh rules;
- Rhino units, tolerance, local origin, rotation, vertical offset, and inverse transform;
- output layer, object count, bounds, and validation result;
- automated warnings, human reviewer, review date, decision, and notes;
- report fallback reason when no geometry was made.

### 10. Validate the model

Run automated checks before human review:

- The AOI is valid and not empty.
- Each output feature intersects the AOI or declared buffer.
- All output bounds are close to the Rhino origin and match the expected projected bounds after the inverse transform.
- The point count, face count, object count, and file size are below set limits.
- Each Rhino object is on an allowed layer.
- Each object or batch has a manifest asset link.
- The `.3dm` reopens with `rhino3dm` and passes the available file audit.
- Terrain has no unexpected no-data spikes, inverted faces, or extreme Z values.
- Building heights outside set limits are flagged. Proxy heights stay on the proxy layer.
- The model has no invalid objects after Rhino opens it.
- The exported control points return to expected longitude and latitude within the declared tolerance.

Then require a human to:

1. Compare the AOI and reference point with the user's selection.
2. View all layers together in QGIS and Rhino.
3. Check terrain against imagery and visible water.
4. Check a sample of building footprints and road centre-lines.
5. Check units with a known distance.
6. Check vertical alignment and the stated vertical datum.
7. accept, reject, or mark each layer for local enhancement.

The user must not use this model as a boundary survey, title record, utility search, flood certificate, planning decision, or construction set unless the responsible authority or qualified professional supplies and checks the required data.

### 11. Make reruns repeatable

Pin the workflow code, configuration, Overture release, selected Copernicus product IDs, container or package versions, PROJ database, and datum grids. Save all commands and human inputs. A rerun with the same stored inputs must make the same geometry, layer names, counts, and checksums where the file format permits deterministic output.

When the user asks for current data, make a new run. Do not change the old run. Compare manifests and feature IDs. Report added, changed, removed, and failed features.

## Decision points and stop rules

Use these rules before geometry enters Rhino:

| Question | Make geometry when | Make a Site Data Report entry when |
|---|---|---|
| Are reuse rights clear? | The source licence permits the planned storage, transformation, and output | Rights are absent, unclear, or restrict the planned derivative or redistribution |
| Is the source identifiable? | A stable provider and record, product, or release ID exist | Only a screen view, transient tile, or AI statement exists |
| Is the CRS known? | Horizontal CRS and axis order are explicit | Coordinates need an unsupported guess |
| Is height usable? | Vertical datum, unit, and height meaning are known, or the layer is explicitly 2D | Height mixes ellipsoidal, orthometric, surface, floor, or proxy values without a safe transform |
| Is geometry credible? | Validation passes and a human sample agrees with independent visual evidence | Geometry is empty, invalid after repair, badly displaced, or materially incomplete |
| Is conversion proportionate? | A tested deterministic adapter can finish within the run limits | Manual tracing, repeated AI extraction, or a fragile browser process is needed |
| Is the model usable? | Object and face counts stay within set file and review limits | Simplification would remove the meaning, or the result makes Rhino unstable |

A report entry must state the question, source, record ID, access date, licence, what the source says, why geometry was not made, confidence, and the next human action. A report entry is a valid workflow result. It is not a hidden failure.

## Automation and human review boundary

Automate file download from documented APIs, checksum creation, CRS inspection, reprojection, clipping, normalization, mesh creation, layer creation, manifest writing, and repeatable checks.

Require human review for:

- the final AOI;
- the selected local CRS and vertical datum when the choice is not clear;
- all licence exceptions;
- imagery date and cloud-cover choice;
- proxy building heights and road widths;
- conflicts between sources;
- legal, cadastral, planning, utility, flood, heritage, and safety claims;
- acceptance of the Rhino model.

AI can help find official sources, map fields, draft adapter code, and summarize checks. AI output is not source evidence. Do not use AI vision to trace a large layer when a downloadable dataset exists. Set a token and elapsed-time limit for each unsupported format. When the limit ends, write the report entry and continue with the other layers.

## What this workflow reuses

- It reuses GeoJSON, STAC concepts, GDAL, PROJ, QGIS, Overture, Copernicus, Rhino, and `rhino3dm`.
- It adapts Heron's Earth Anchor Point and clipping pattern as an optional Grasshopper path.
- It does not build a new GIS engine, map portal, coordinate database, or CAD file format.
- It keeps adapters small so a better local or global source can replace a baseline layer.

## Unknowns to test in the prototype

These items were not proved by this research:

- The minimum Rhino version and `.3dm` version for all required Earth Anchor Point and user-text fields.
- Reliable cross-platform embedding of a georeferenced image and its relative file path in a generated `.3dm`.
- The best terrain mesh density and contour interval for useful performance in the target Rhino hardware.
- The file-size and object-count limits that define reasonable model performance for this project.
- A stable direct AOI polygon option in the current Overture client. Its documented simple command uses a bounding box, so polygon clipping remains a local step.
- The current access category and automated download route for Copernicus GLO-30 for every user type.
- A valid vertical transformation for every AOI and every better local elevation source.
- Whether Heron works without correction in the exact Rhino, Grasshopper, GDAL, and PROJ versions selected for the prototype.
- Which global building-height fields are complete enough to use at the future reference site.

Test these items with a small synthetic AOI before the human selects the real reference site. The later Workflow Application must record elapsed time, failures, data quality, manual work, and fallback report entries.

## Research outcome

Adopt a Rhino-first base workflow. Keep `aoi.geojson` as the portable user input. Use Overture and Copernicus as replaceable global baselines. Process them with QGIS, GDAL, and PROJ. Generate a local-origin, metre-based, layered `.3dm` with `rhino3dm`. Keep a complete manifest that can return every object to real-world coordinates. Use a cited Site Data Report for data that does not pass the rights, coordinate, reliability, cost, or model-use checks.
