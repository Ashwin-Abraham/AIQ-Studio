# Location-specific site-data enhancement

Research checked on 8 September 2026.

## Question

How can the workflow find, assess, and add location-specific data after a human selects an Area of Interest (AOI)? The method must work across jurisdictions. It must improve a Rhino Site Model when reliable geometry is available. It must create a cited Site Data Report entry when geometry is not reliable, practical, or economical to produce.

This document does not select a site. It defines the Location-Specific Enhancement Workflow that a later Workflow Application can use.

## Answer

Use an authority-first discovery method. First, identify every public body that can issue data for the AOI. Then search its catalog, services, and formal records. Test each candidate with the same evidence matrix. Add data through a source-specific adapter and keep the unchanged response in a cache. Do not merge a local layer with a global layer until a human accepts the source, rights, coordinate reference system (CRS), date, quality, and conflict rule.

The workflow must have two valid results for each data need:

1. Add a traceable layer to the Rhino Site Model.
2. Add a cited entry to the Site Data Report.

A report entry is a correct result when the source is authoritative but cannot supply dependable geometry, permits only viewing, needs a restricted account, has unclear rights, has a high extraction cost, or needs professional interpretation.

## Evidence classes

This document uses three evidence classes.

- **Verified fact**: A primary source states the fact.
- **Design recommendation**: This document proposes a rule for AIQ Studio.
- **Unknown**: The answer depends on the future AOI, current access, or a human decision.

## Verified facts

### Catalog and service standards

- The W3C Data Catalog Vocabulary (DCAT) defines metadata for datasets, distributions, and data services. It includes identifiers, publishers, spatial and temporal coverage, resolution, access and download URLs, access rights, licences, formats, and checksums. DCAT also warns that licence, access-right, and other rights statements are different things. [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/)
- OGC API - Features gives resource-based access to geographic features. The OGC also lists WFS, WMS, WMTS, and WCS as older web-service standards. WFS returns geographic features. WMS returns georeferenced map images. WMTS returns prepared map tiles. WCS provides coverages such as raster values. The OGC advises new implementations to consider the newer OGC APIs. [OGC API standards](https://ogcapi.ogc.org/) and [OGC Web Services](https://developer.ogc.org/ows.html)
- A WMS response is a map image, such as PNG or JPEG. It is not the source feature geometry. [OGC Web Map Service](https://www.ogc.org/standards/wms/)
- A STAC Catalog links STAC Items so that a client can browse them. A STAC Item is a GeoJSON feature that links to assets and can include date, geometry, bounding box, collection, and property data. [STAC specification](https://stacspec.org/en/about/stac-spec/)
- ArcGIS Hub has a Search API for catalog content. ArcGIS Feature Services have a query operation for attribute and spatial queries. A service can limit the number of returned records, so a client can need pagination or object-ID batches. [ArcGIS Hub Search API](https://developers.arcgis.com/hub/services/search/) and [ArcGIS Feature Service query](https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/)
- QGIS can connect to WMS, WMTS, WCS, WFS, OGC API - Features, ArcGIS REST services, vector tiles, and STAC. This makes it a suitable human review tool for many discovery surfaces. [QGIS Browser panel](https://documentation.qgis.org/3.44/en/docs/user_manual/introduction/browser.html) and [QGIS OGC client support](https://doc.qgis.org/3.44/en/docs/user_manual/working_with_ogc/ogc_client_support.html)

### Official portals have different scope and access rules

- England's Planning Data API provides more than 100 planning and housing datasets through one interface. It supports coordinate, boundary, and dataset queries. The service tells users that missing results do not prove that no constraint exists. It also states that the API is in beta and can change. [Planning Data documentation](https://www.planning.data.gov.uk/docs)
- HM Land Registry publishes INSPIRE Index Polygons for England and Wales. These polygons show the indicative position and extent of registered freehold property. They do not show an exact legal boundary. The files are grouped by local authority and are in GML. [HM Land Registry INSPIRE guidance](https://www.gov.uk/guidance/inspire-index-polygons-spatial-data) and [National Polygon technical specification](https://use-land-property-data.service.gov.uk/datasets/nps/tech-spec/1?back=true)
- The Environment Agency's English LiDAR catalog can provide downloads and OGC services. Its 1 m composite surface model has a stated CRS, vertical reference, acquisition range, resolution, licence, and accuracy. Its metadata index identifies which survey contributed at a location. [Defra Data Services Platform: 1 m composite DSM](https://dsp.environment.data.gov.uk/dataset/9ba4d5ac-d596-445a-9056-dae3ddec0178)
- Historic England publishes National Heritage List spatial data in several formats and through APIs. It states that this is the official, current register of nationally protected historic buildings and sites in England. [Historic England Open Data Hub](https://historicengland.org.uk/listing/the-list/data-downloads/)
- The United Kingdom National Underground Asset Register is not open to the public. Access has defined eligible users and legally controlled use. [NUAR service assessment](https://www.gov.uk/service-standard-reports/national-underground-asset-register-alpha-reassessment) and [NUAR access description](https://www.gov.uk/government/publications/nuar-minimum-viable-product-mvp/nuar-minimum-viable-product-mvp)
- The United States Geological Survey LidarExplorer lets users search, view, and download 3DEP LiDAR and derived products. 3DEP products have different resolutions and collection dates. USGS tells users to inspect quality information for the selected product. [USGS LidarExplorer](https://www.usgs.gov/tools/lidarexplorer) and [USGS 3DEP products and services](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services)
- The FEMA Map Service Center is the official source for United States flood-hazard products. The National Flood Hazard Layer is available through downloads and GIS services. [FEMA flood-hazard product access](https://msc.fema.gov/msccontent/FEMA_Hazard_Products_Direct_Download.pdf) and [FEMA public GIS feeds](https://gis.fema.gov/)
- Land Information New Zealand provides official open access to imagery, elevation, topographic, hydrographic, property, boundary, address, and road data. It also provides APIs and web services. API keys, rate limits, and the licence can apply to a selected service. [LINZ Data Service](https://www.linz.govt.nz/products-services/data/linz-data-service), [LINZ web services](https://www.linz.govt.nz/guidance/data-service/linz-data-service-guide/web-services), and [LINZ Basemaps documentation](https://www.linz.govt.nz/guidance/data-service/linz-basemaps-guide/linz-basemaps-documentation)
- New South Wales Spatial Services provides cadastral, imagery, elevation, transport, water, administrative boundary, and survey-control data. Supply methods differ by product. They include files, web services, viewers, account access, and manual delivery. Survey-control records can use GDA94 or GDA2020 horizontal datums and the Australian Height Datum or ellipsoidal heights. [NSW spatial data](https://www.spatial.nsw.gov.au/products_and_services/spatial_data) and [NSW SCIMS Online](https://www.spatial.nsw.gov.au/surveying/scims_online)
- The Netherlands PDOK cadastral map has OGC API - Features, vector tiles, and a Download API. The Download API supports full and change downloads, and it can apply area and feature-type filters. [PDOK cadastral APIs](https://www.pdok.nl/ogc-apis/-/article/kadastrale-kaart) and [PDOK cadastral Download API](https://api.pdok.nl/kadaster/kadastralekaart/download/v5_0/ui/)
- The NSW Planning Portal shows why the formal source still matters. Its viewer gives access to some planning-map datasets, but the official maps adopted with the legal instrument remain available separately. [NSW Planning Portal Spatial Viewer](https://www.planningportal.nsw.gov.au/spatialviewer/)
- The United Kingdom NaPTAN and NPTG API supplies national public-transport stop, gazetteer, and locality data as XML or CSV. It supports downloads by transport area or for the full national dataset. [UK Government API Catalogue: NaPTAN and NPTG](https://www.api.gov.uk/dft/national-public-transport-access-nodes-naptan-and-national-public-transport-gazetteer-nptg-api/)

These examples show the method. They are not a source list for a selected site.

## Design recommendations

### 1. Fix the discovery input

Start only when the Workflow Application has these inputs:

- the AOI polygon in WGS 84 longitude and latitude;
- one point that is known to be inside the AOI;
- the selection date;
- the requested use, such as internal design study, client issue, or public issue;
- the required data themes;
- the target horizontal CRS, vertical datum, model units, and local Rhino origin, if these are already known.

The point supports search tools that do not accept a polygon. The polygon supports boundary intersection and spatial filters. Keep both. Do not replace the AOI with a postal address.

### 2. Identify the jurisdiction and issuing authorities

Run this procedure for the AOI:

1. Intersect the AOI point and polygon with an official administrative-boundary dataset.
2. Record every intersected country, state or province, county or region, municipality, and local government area.
3. Identify special authorities that do not follow the normal boundary hierarchy. Check the planning authority, cadastral or land-registration body, flood or water authority, heritage body, transport body, environmental regulator, mapping agency, and utility-record service.
4. Open each authority's official page. Confirm its name, legal remit, geographic coverage, and contact route.
5. Record the boundary dataset, boundary version, source feature ID, and intersection result.
6. If the AOI crosses a boundary, search both authorities. Do not choose one silently.

Use geocoding or a web map only as a discovery aid. Use an official boundary or a written statement from the issuing body for the final authority record. A national catalog can aggregate local data, but the dataset metadata must still identify the issuing or custodial body.

The authority record must distinguish these roles:

| Role | Meaning |
|---|---|
| Issuing authority | The body that creates or legally issues the record. |
| Custodian | The body that maintains the dataset. |
| Portal operator | The body or vendor that publishes the catalog or service. |
| Rights holder | The body that grants the reuse rights. |
| Legal decision maker | The body or instrument that controls the legal status. |

One organization can have more than one role. A portal operator is not automatically the issuing authority.

### 3. Search in a fixed order

Search each data theme through these surfaces. Stop when the authoritative source and its usable distribution are clear.

1. **Official dataset page or download catalog.** Search the issuing authority's site before a general web search. Record the stable dataset ID and metadata page.
2. **Government open-data portal.** Search national, state or province, regional, and municipal portals. Inspect the publisher, custodian, update date, coverage, licence, and each distribution.
3. **ArcGIS Hub or ArcGIS REST catalog.** Search the Hub catalog. Open the item and its service metadata. Test the layer query, spatial reference, fields, `maxRecordCount`, pagination, access level, and last edit date. Do not use a rendered web map when the Feature Service is available.
4. **OGC API - Features or WFS.** Read the landing page or `GetCapabilities`. List collections or feature types. Test a small bounding-box request before the AOI request. Preserve the service version and request.
5. **WCS.** Use it for source raster or coverage values when the licence and native resolution are clear.
6. **WMS or WMTS.** Use these for visual review and map evidence. Do not infer reusable feature geometry from pixels. Do not use tiles as a model texture unless the terms permit that use.
7. **STAC catalog.** Search by AOI, date, collection, cloud or quality fields, and asset role. Save the Catalog, Collection, Item, and Asset identifiers.
8. **Planning portal.** Search the current plan, zoning, overlays, development controls, planning applications, and adopted map instruments. Verify whether the downloadable GIS layer or the adopted document is legally controlling.
9. **Cadastral or land-registration portal.** Find parcel geometry, survey plans, title references, easements, covenants, and boundary-status notes. Treat an index polygon as an index unless the source says it is a legal boundary.
10. **LiDAR and orthophoto catalog.** Search the exact footprint. Inspect acquisition date, point density or ground sample distance, classification, horizontal accuracy, vertical accuracy, horizontal CRS, height reference, geoid model, processing level, and gaps.
11. **Topic authority.** Search the official environmental, flood, coastal, geology, heritage, ecology, transport, and utility authority. Search national and local sources because responsibility can be split.
12. **Formal request or human contact.** If the source is not public, record the request route, fee, account, licence, expected response, and named human action.

Use keyword variants that match local language. Examples include parcel, cadastre, title index, zoning, land-use plan, development plan, flood extent, LiDAR, orthophoto, heritage register, road reserve, right of way, utility plan, and survey control. Record each useful query. A failed query is evidence and must be reproducible.

### 4. Use a source evaluation matrix

Create one row for each candidate dataset and each distribution. Do not score only the catalog page.

| Field | Required record | Acceptance question |
|---|---|---|
| Authority | Issuer, custodian, portal operator, and rights holder | Does the responsible body have the remit for this theme and place? |
| Identity | Dataset title, stable ID, version, layer ID, and record URL | Can a later user find the same source? |
| Date | Acquisition, effective, publication, update, and access dates | Is the relevant date known and suitable for the use? |
| Legal status | Adopted, draft, superseded, indicative, advisory, or unknown | Does the model and report state the correct status? |
| Licence and rights | Licence URL, copyright, attribution, access rights, derived-work terms, and redistribution terms | Can the project download, transform, put in a `.3dm`, and issue the result for the stated use? |
| Scale or resolution | Map scale, ground sample distance, grid size, point density, and stated accuracy | Can it support the required model detail? |
| Horizontal reference | CRS identifier, coordinate epoch when relevant, and stated accuracy | Can it be transformed without an undeclared assumption? |
| Vertical reference | Height type, vertical datum, geoid model, units, and stated accuracy | Can its heights align with terrain and survey control? |
| Completeness | Coverage footprint, missing areas, null rate, class coverage, and known omissions | Does the AOI have enough data? |
| Data structure | Geometry or raster type, attributes, IDs, topology, and schema | Can the required Rhino layer be made without guessing? |
| Access method | File, API, OGC service, portal export, viewer, request, fee, or account | Is there a lawful and repeatable acquisition path? |
| Automation limits | Authentication, CAPTCHA, quota, pagination, maximum area, robots rules, session expiry, and service-level statement | Can a script rerun the access safely? |
| Privacy and security | Personal data, sensitive sites, critical infrastructure, account terms, and public-issue limits | Can the raw and derived data be stored and shared? |
| Cross-check | Independent source, sample visual check, and discrepancy | Did a human test plausible position and content? |
| Confidence | High, medium, low, or rejected, with a reason | Is the rating supported by the fields above? |
| Output | Rhino layer, reference-only layer, report entry, or reject | Is the result explicit? |

Use gates before confidence:

- **Rights gate:** Reject model use when transformation or distribution rights are absent or unclear.
- **Coordinate gate:** Reject 3D integration when the horizontal CRS or required vertical reference cannot be established.
- **Geometry gate:** Reject geometry when the data type, topology, or accuracy cannot support the intended layer.
- **Coverage gate:** Reject or qualify geometry when important AOI areas are missing.
- **Cost gate:** Use the report when extraction and correction need unreasonable human, compute, or AI-token effort for the decision value.

Do not turn the matrix into one numeric quality score. A high authority score cannot correct an incompatible licence or an unknown vertical datum.

### 5. Define adapters and cache boundaries

Use one adapter for one source distribution or service contract. Do not make one adapter for a final Rhino layer. Several sources can contribute to one layer, and one source can contribute to several layers.

An adapter can do these tasks:

- catalog search and item selection;
- authentication without putting credentials in logs;
- capability and schema discovery;
- bounding-box or polygon query;
- pagination, retry, quota, and rate-limit handling;
- unchanged download or response capture;
- source metadata and rights capture;
- checksum calculation;
- validation of transport, file type, schema, and declared CRS.

Keep clipping, reprojection, height conversion, geometry repair, classification, simplification, and Rhino generation outside the source adapter. These are processing steps. This boundary makes a source change easier to test and keeps transformations visible.

Use three cache levels:

| Cache | Contents | Rule |
|---|---|---|
| Discovery cache | Catalog responses, capability documents, item metadata, and search queries | Keep the unchanged response and access time. Refresh by declared expiry or before a formal issue. |
| Raw-data cache | Original files or API pages | Make it immutable. Address it by checksum. Do not overwrite a prior acquisition. |
| Processed cache | Clipped and transformed intermediate files | Key it by raw checksum, processing recipe, tool versions, AOI checksum, and output CRS. |

Never cache passwords, access tokens, session cookies, or personal owner records in the project package. Store only a reference to the approved secret or controlled record. If terms prohibit local storage, store the stable record ID, request, access date, and human review note instead of the data.

For a live service without a release number, record the exact request and response checksum. Add the server time or response date when available. A later run must create a new acquisition, not replace the old one.

### 6. Decide how local and global layers interact

Use one of four explicit relations for each local candidate:

| Relation | Use |
|---|---|
| Override | The accepted local source replaces the global geometry for the same theme and footprint. |
| Supplement | The local source adds attributes, detail, or features that the global source does not have. |
| Conflict | The sources disagree and the workflow keeps both until a human decides. |
| Reference only | The source helps review but does not create Rhino geometry. |

Apply these rules:

1. Prefer the competent issuing authority for legal status. Do not use a global dataset to override an official local record.
2. Prefer the source that fits the needed date, scale, accuracy, licence, and data type for physical context. Local does not always mean newer or more accurate.
3. Clip an override to its verified coverage footprint. Do not delete the global layer outside that footprint.
4. Preserve the source ID on every derived object. Keep separate source layers until the conflict check is complete.
5. Compare position, count, attribute, and date. Set tolerances by theme and stated accuracy. Do not invent one tolerance for all layers.
6. Record the accepted relation, decision maker, decision date, reason, and any rejected source IDs.
7. In Rhino, show unresolved conflicts on a review layer. Do not hide them in one clean-looking layer.

### 7. Record a complete acquisition and transformation trail

Each accepted layer or report entry must have this record:

- AOI ID and AOI geometry checksum;
- data need and target Rhino layer;
- issuer, custodian, rights holder, and portal;
- dataset, collection, item, layer, map sheet, title, application, or record IDs;
- catalog query, service URL, request parameters, and page sequence;
- access, acquisition, effective, publication, and update dates where available;
- original filenames, byte counts, media types, and SHA-256 checksums;
- licence URL, captured rights text, attribution, and issue limits;
- source CRS, coordinate epoch, vertical datum, geoid model, and units where applicable;
- coverage, scale, resolution, stated accuracy, and completeness notes;
- adapter name and version;
- each transformation in order, with parameters and tool versions;
- processed-file checksums and derived Rhino object or layer IDs;
- automated check results;
- human reviewer, review date, confidence, conflict decision, and unresolved limits;
- public, internal, restricted, or reference-only classification.

DCAT fields are a useful base for this record, but they are not enough for the full transformation and human-review trail. Keep the project fields in a simple machine-readable manifest.

### 8. Validate before Rhino integration

Run automated checks first:

- response status, size, format, and checksum;
- expected schema and feature count;
- non-empty AOI intersection;
- geometry validity and geometry type;
- duplicate and stable IDs;
- CRS range and unit checks;
- raster cell size, nodata, band, and coverage checks;
- LiDAR class, point density, bounds, and height-range checks;
- licence and attribution presence;
- date and legal-status presence;
- difference from the current global layer.

Then require human review in GIS:

- overlay the local source, global source, AOI, and a permitted reference base;
- inspect edges, gaps, duplicates, shifts, and implausible heights;
- check the formal document when a map layer represents a legal instrument;
- confirm the selected source version and its date;
- confirm the override, supplement, conflict, or reference-only relation;
- approve the Rhino layer name and the Site Data Report text.

AI can find catalog leads, map fields, run deterministic checks, and draft notes. AI output is not source evidence. A human must approve legal, cadastral, utility, planning, flood, heritage, and vertical-datum interpretations.

### 9. Stop geometry work at a clear threshold

Stop and create a sourced Site Data Report entry when one or more of these conditions apply:

- only a WMS, WMTS, PDF, or interactive viewer is available and vector extraction is not permitted or dependable;
- access needs a CAPTCHA, one-time code, payment, professional account, or invitation that prevents an approved repeatable run;
- the licence does not clearly permit the required download, transformation, model embedding, or issue;
- the source CRS is unknown or cannot be established;
- elevations have an unknown height reference or cannot align within the required tolerance;
- geometry is indicative, generalized, incomplete, obsolete, or materially inconsistent with the required use;
- topology repair, georeferencing, transcription, or AI extraction cost is high compared with the layer's design value;
- the source contains personal or security-sensitive data that must not enter the package;
- a competent professional must interpret the record;
- authoritative sources conflict and a human cannot resolve the conflict in this run.

The report entry must state:

- the question or constraint;
- the issuing authority and source title;
- the stable record, map sheet, or service link;
- the relevant date and status;
- the AOI query or lookup method;
- the factual result, or that the result is unknown;
- why geometry was not made;
- the licence, access, privacy, and issue limits;
- the confidence and required human follow-up;
- the access date and reviewer.

Do not trace a viewer or screenshot to make the Rhino model look complete. A clear report gap is safer than unsupported geometry.

## Repeatable Workflow Application

For a future selected site, run this sequence:

1. Validate the AOI point and polygon.
2. Identify intersecting jurisdictions and special authorities.
3. Create the theme search list.
4. Search official sources in the fixed order.
5. Save discovery evidence and failed queries.
6. Evaluate each distribution with the matrix and gates.
7. Claim the source relation to the global layer: override, supplement, conflict, or reference only.
8. Acquire through an adapter or record a manual access action.
9. Save the immutable raw response and manifest.
10. Clip and transform through the separate processing pipeline.
11. Run automated checks.
12. Review the result in GIS.
13. Add approved geometry to stable Rhino layers. Add all other useful evidence to the Site Data Report.
14. Save the review decision, provenance, and checksums.
15. Run again from the saved AOI and configuration. Compare source versions, output checksums, report changes, effort, failures, and human interventions.

## Unknowns to resolve after site selection

- Which jurisdictions and special authorities intersect the AOI?
- Which authority has legal control for planning, parcels, roads, water, heritage, environment, and utilities?
- Which sources have usable distributions and suitable rights on the access date?
- Which coordinate epoch and vertical datum apply?
- Are local parcel lines legal boundaries, survey indexes, or only map references?
- Are current LiDAR and orthophotos available for the full AOI?
- Do planning layers match the current adopted instruments?
- Which utility data can the project team lawfully access and issue?
- Which local sources override global layers, and what tolerances apply?
- Which records need a surveyor, planner, engineer, heritage specialist, or other professional?
- What human, compute, service, and AI-token cost is reasonable for each data theme?

These unknowns must stay open until the human selects a test site. They are Workflow Application questions, not reasons to select a site during this research.

## Decision outcome

Adopt an authority-first Location-Specific Enhancement Workflow. Use standard catalog and service interfaces when they are present, but evaluate the actual distribution and its rights. Keep source adapters separate from spatial processing. Keep immutable raw evidence and a machine-readable provenance trail. Make local-versus-global conflicts visible. Add only approved, coordinate-safe, and licensed geometry to the Rhino Site Model. Put all other useful facts in a cited Site Data Report.
