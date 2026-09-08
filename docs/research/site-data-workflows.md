# Reusable site-data workflows for architects

Research checked on 8 September 2026.

## Question

Which existing tools, data sources, standards, and workflow formats can support a repeatable site-data-gathering workflow for a real vacant parcel in Bangalore? The residential project is hypothetical. The workflow must also be useful to practising architects on other sites.

## Recommendation

Build a small, source-neutral pipeline. Do not build a new GIS system.

1. Use a GeoPackage as the main case-specific spatial file. Use normal files for source documents, rasters, and reports.
2. Keep one machine-readable source manifest. Use STAC fields where they fit. Add fields for the issuing body, access date, effective date, licence, extraction method, checksum, coordinate reference system, confidence, and privacy class.
3. Use QGIS for review and manual correction. Use GDAL, PROJ, GeoPandas, and OSMnx for tested and repeatable processing.
4. Put each external source behind a replaceable adapter. Do not make the workflow depend on one public endpoint, web viewer, or commercial service.
5. Use official Karnataka and Bangalore records for legal and parcel facts. Use open global data for context only. Do not infer a legal boundary, title, zoning status, or road right-of-way from OpenStreetMap, imagery, or an AI model.
6. Export clean layers and metadata to Rhino. Use `rhino3dm` first. Add Grasshopper or Compute only when later maps need live parametric processing.
7. Package the procedure as a thin Agent Skill over a tested command-line workflow. The skill must explain the human checks. It must not contain the only copy of the logic.

This approach gives the project a reusable workflow and a clear learning artifact. It also keeps each source, licence, and manual decision traceable.

## Verified candidates

The facts in this table come from primary sources. “Maturity” is a practical description based on the official project status, releases, or service state. The last column is the project recommendation, not a fact stated by the source owner.

| Candidate | Role | Maturity | Licence or terms | Reuse constraints | Recommendation |
|---|---|---|---|---|---|
| [OGC GeoPackage](https://www.ogc.org/standards/geopackage/) | Store vector features, attributes, rasters, and tiles in one portable SQLite file | Adopted OGC standard with broad GIS support | Open OGC standard; implementations have their own licences | It does not record the complete acquisition history by itself | **Adopt** as the main spatial exchange file |
| [STAC](https://stacspec.org/en/about/stac-spec/) | Describe spatial assets, time, providers, licences, and links | Stable specification with many public catalogues and clients | The [specification repository](https://github.com/radiantearth/stac-spec) is Apache-2.0 | STAC is strongest for spatiotemporal assets. It does not replace project-specific legal and confidence fields | **Adapt** for the source manifest |
| [QGIS Processing Modeler](https://docs.qgis.org/latest/en/docs/user_manual/processing/modeler.html) | Visual review, correction, and repeatable desktop processing | Mature desktop GIS and processing framework | GPL-2.0-or-later; check licences for plug-ins | A saved model can hide environment and plug-in differences. Pin the QGIS version and keep test data | **Adopt** for human review and optional visual models |
| [GDAL](https://gdal.org/en/stable/) and [PROJ](https://proj.org/) | Read, transform, clip, reproject, and export geospatial data | Long-lived core geospatial libraries | MIT/X-style licences | Coordinate operations can change with grid files and database versions. Record the tool and CRS versions | **Depend** on pinned releases |
| [GeoPandas](https://geopandas.org/en/stable/about.html) | Script vector cleaning, joins, overlays, and validation | Mature community project under NumFOCUS | BSD-3-Clause | It depends on GEOS, GDAL, and PROJ. Installation and numeric results must be tested in the pinned environment | **Adopt** as the main Python vector layer |
| [OSMnx](https://github.com/gboeing/osmnx) | Get and analyse street networks and selected OpenStreetMap features | Active open-source Python project with releases and tests | MIT | Results inherit OpenStreetMap data duties and public API limits. Cache raw responses and record the query | **Adapt** for access and walkability context |
| [OpenStreetMap](https://osmfoundation.org/wiki/Licence_and_Legal_FAQ) | Roads, buildings, amenities, water, and other context | Global community database with continuous updates | ODbL 1.0; attribution is required | Completeness and dates vary. A public use of a derivative database can trigger share-alike duties. The [public tile service](https://operations.osmfoundation.org/policies/tiles/) forbids bulk download and has no service guarantee | **Depend** on the data for context, not on the public tile service |
| [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) | Query a small area of OpenStreetMap by tags | Established query interface with public and self-hosted instances | Returned OpenStreetMap data is ODbL | Public instances have limits and no production guarantee. Queries must be saved with the result | **Adapt** behind a cacheable source adapter |
| [Overture Maps data](https://docs.overturemaps.org/guides/data/) | Download buildings, transport, places, and base data as GeoParquet | Regular public releases with schemas and release versions | Licence is theme-specific; official releases identify ODbL and CDLA-Permissive-2.0 content | Keep theme-level notices. Some content is derived from other providers. It is not cadastral data | **Learn from** the schemas; **adapt** as an optional comparison source |
| [Google Open Buildings](https://sites.research.google/gr/open-buildings/) | Supply machine-derived building footprints where local coverage is useful | Published dataset with India coverage and versioned downloads | CC BY 4.0 | Footprints are predictions, not survey records. Record version and confidence. Confirm current coverage before use | **Adapt** as a cross-check, not an authority |
| [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/explore-data/data-collections) | Provide Sentinel imagery and Copernicus DEM access | Operational official European data service | Dataset terms vary; Copernicus data carries source notices under its legal notice | Account, quota, processing level, scene date, cloud cover, and product terms must be recorded | **Depend** for open imagery and terrain when the selected product permits the planned output |
| [NASA POWER API](https://power.larc.nasa.gov/docs/services/api/) | Supply repeatable regional solar and meteorological time series | Operational NASA API with documented endpoints | US Government data policy; cite NASA POWER and the source products as requested | Grid data is not a site weather station and is too coarse for local legal or microclimate claims | **Adapt** for early climate context |
| [Bhuvan OGC services](https://bhuvan.nrsc.gov.in/wiki/index.php/How_to_use_WMS_services) | View Indian satellite and thematic layers through WMS or WMTS | Operational official ISRO/NRSC service | Restrictive [Bhuvan terms](https://bhuvan.nrsc.gov.in/terms.php), not an open-data licence | Terms restrict copying, derivatives, redistribution, and mass download. WMS images do not give reusable feature geometry | **Learn from** and use for manual checks only unless a specific dataset has separate reuse terms |
| [rhino3dm](https://developer.rhino3d.com/en/guides/opennurbs/what-is-rhino3dmio/) | Read and write 3DM geometry from Python, JavaScript, or .NET without Rhino | Official cross-platform McNeel library | [MIT](https://developer.rhino3d.com/en/license/) | It is a file and geometry library, not a full Rhino or Grasshopper runtime | **Adopt** for the first Rhino export boundary |
| [Rhino Compute and Hops](https://developer.rhino3d.com/en/guides/compute/) | Run Rhino and Grasshopper functions through a stateless API | Official McNeel deployment route | SDK and API code is MIT; production use also has Rhino licensing and hosting costs | It adds a server, credentials, cost, version coupling, and operational work | **Learn from** now; **depend** only when live parametric processing is required |
| [COMPAS](https://compas.dev/) | Move geometry and computational methods between Python and CAD tools | Established open-source AEC framework | MIT | It is a larger framework than this first data package needs | **Learn from** its interfaces; adopt only if later modelling needs justify it |
| [Speckle](https://github.com/specklesystems/speckle-server) | Exchange, version, and inspect AEC objects across tools | Active server and connector ecosystem | Core server repository is Apache-2.0 unless a module states another licence | A hosted or self-hosted server adds identity, storage, and operating concerns. Module licences can differ | **Learn from** its object and provenance model; keep it optional |
| [Agent Skills specification](https://agentskills.io/specification) | Package instructions, scripts, references, and assets for compatible AI agents | Published open format with validation tools | Each skill and bundled asset needs its own stated licence | An instruction file cannot make an unreliable script reliable. Client support and allowed tools vary | **Adapt** as the human-facing workflow wrapper |
| [Data Version Control](https://dvc.org/doc) | Version data inputs, pipeline stages, metrics, and remote storage pointers | Mature open-source data workflow tool | Apache-2.0 | It adds a tool and remote storage setup. It does not grant rights to redistribute source data | **Learn from** first; adopt only when normal Git plus checksums is no longer enough |

## Bangalore and Karnataka source hierarchy

These sources do not have equal authority or reuse rights.

### 1. Authoritative records

- [Karnataka Bhoomi and SSLR services](https://landrecords.karnataka.gov.in/) provide RTC, mutation, revenue-map, survey, sketch, Akarband, and conversion-order services. Search needs land identifiers. Some records need payment, registration, OTP, or CAPTCHA. No public bulk API or open reuse licence was verified. **Depend for parcel facts after manual access. Do not publish owner data.**
- The [BDA master-plan page](https://eng.bdabangalore.org/masterplan.html) lists Revised Master Plan 2015, Draft Revised Master Plan 2031, and approved-plan material. The service is document and map based. No parcel API or open licence was verified. **Depend on the applicable approved plan, and record its legal status, sheet, and date. Do not treat the draft plan as operative.**
- [Bengaluru e-Aasthi](https://bbmpeaasthi.karnataka.gov.in/citizen_core/) supports municipal property checks by ward and property identifiers. Some access needs login, OTP, or CAPTCHA. No open reuse licence was verified. **Use for verification, and keep private owner data out of the public package.**

### 2. Reusable open government data

- The [Karnataka Open Government Data portal](https://karnataka.data.gov.in/) states that its published resources use the Government Open Data Licence–India. Its [Transport GIS Dataset](https://karnataka.data.gov.in/catalog/transport-gis-dataset) provides road and rail data through a download and catalogue API, but the listed data is from 2021. **Adopt with a freshness warning and local checks.**
- The portal also has [district rainfall](https://karnataka.data.gov.in/catalog/district-wise-annual-rainfall-karnataka) and [Bengaluru environment](https://karnataka.data.gov.in/catalog/environmentbengaluru) datasets. **Use for regional context, not site microclimate.**

### 3. Visual or contextual checks

- The [GBA GIS Viewer](https://bbmp.gov.in/gisviewer/) and [Know Your New Corporation](https://www.bbmp.gov.in/KnowYourNewCorporation/) service can check corporation, zone, ward, and location. No public download API or open output licence was verified. The viewer also shows third-party base maps with separate terms. **Use manually. Do not scrape it or copy Google imagery.**
- [BBMP Road History 2.0](https://rh.bbmpgov.in/) can confirm road names and some road records. No bulk API or open licence was verified. **Use as a manual corroborating source.**
- [BBMP lake records](https://site.bbmp.gov.in/departmentwebsites/Lakes/index.html) list lakes, villages, survey numbers, and stated areas. Pages can be old and no reusable GIS download was found. **Use to raise a review flag. Confirm a boundary or buffer with current records.**
- Official [K-GIS documents](https://ksrsac.in/web/sites/default/files/projects/2018-02/K-GIS%20Data%20Exchange%20Protocol.pdf) describe schemas, coordinate rules, metadata, services, imagery, DEMs, and city GIS. Stable public endpoints and open licences for the underlying layers were not verified. **Learn from its data exchange and quality rules. Do not make it a dependency until access and rights are confirmed.**
- The [Sujala Land Resource Inventory Geoportal](https://www.sujala3lri.karnataka.gov.in/) can return PDF, KML, or Shapefile material for a selected area. It can need registration. Urban coverage and reuse rights were not verified. **Test it after site selection and use only if the parcel is covered and the rights are clear.**

## Repeatable workflow shape

Use this order for the first prototype:

1. The architect enters a site boundary or the identifiers needed to obtain one.
2. The workflow makes a case folder and a source manifest.
3. Each adapter saves an unchanged raw response or a reference to a controlled record. It records time, query, provider, licence, and checksum.
4. Deterministic processing changes all reusable geometry to a declared local projected CRS. It keeps the original geometry and source ID.
5. Automated checks test geometry validity, empty layers, coordinate range, age, and missing provenance.
6. QGIS shows the result for manual boundary, jurisdiction, access, terrain, imagery, and context checks.
7. The architect records corrections and confidence. AI can help classify, summarize, and draft notes, but it cannot silently change an authoritative fact.
8. The workflow writes the Site Data Package, a source register, a quality report, and a Rhino-ready export.
9. A second clean run from the saved inputs must create the same outputs, except for declared time-sensitive sources.

## Minimum provenance record

Record these fields for each asset or assertion:

- stable source name and URL;
- issuing body and dataset or document title;
- source record, map sheet, query, or product identifier;
- access date and the source data or legal effective date;
- raw-file checksum or a controlled-record reference;
- licence, required attribution, and redistribution class;
- automated or manual extraction method and tool version;
- source and output coordinate reference systems;
- spatial resolution, scale, and stated accuracy when available;
- human reviewer, review date, confidence, and unresolved conflict;
- privacy class and whether the public package can contain the item.

## AI boundary

AI is useful for source discovery, document indexing, field mapping, anomaly flags, and draft summaries. AI output is not a source. Keep the source passage or dataset record that supports each extracted fact. Require human approval for parcel boundaries, jurisdiction, zoning references, road access, water constraints, and any fact that can affect legal or design feasibility.

## Gaps and tests after site selection

- No stable public Karnataka parcel-boundary API was verified.
- No official Bengaluru orthophoto with clear public redistribution rights was verified.
- No official site-scale DEM with a clear open licence was verified.
- Public zoning information is mainly map-document based, not parcel-query based.
- Many land and municipal services use interactive forms, OTP, CAPTCHA, payment, or login. This prevents unattended automation.
- The chosen parcel can fall outside BDA plan coverage or inside another planning authority. Confirm the competent authority before the bylaw map starts.
- Global building footprints, roads, terrain, imagery, and climate data need field or official-record checks at site scale.

## Decision outcome

Adopt existing standards and libraries for storage, processing, provenance, and Rhino exchange. Adapt data acquisition through small replaceable adapters. Depend on authoritative public records for legal facts and on well-licensed open datasets for context. Learn from closed services and larger AEC platforms, but do not put them on the critical path.

The next prototype should prove this structure on the manually selected parcel. It should not attempt full unattended automation. The existing tickets for the minimum Site Data Package, reuse and attribution policy, and Workflow Package prototype are sufficient; this research does not make a separate new decision ticket necessary.
