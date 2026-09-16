#!/usr/bin/env python3
"""Convert cached Overture GeoJSON files to the skill's local processed-data contract."""

import argparse
import datetime as dt
import json
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import transform
from shapely import make_valid
from site_model.contract import atomic_json, file_sha256, load_json, validate_sources
from download_overture import validate_types

FEATURE_TYPES = ["building", "building_part", "segment", "connector", "water", "land", "land_use", "place"]


def read_geojson_geometry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("type") == "FeatureCollection":
        if len(data.get("features", [])) != 1:
            raise ValueError("The site FeatureCollection must contain exactly one feature")
        data = data["features"][0]
    if data.get("type") == "Feature":
        data = data["geometry"]
    return shape(data)


def clean(value):
    value = str(value or "Other Unclassified").replace("-", " ").replace("_", " ").replace("::", " ")
    return " ".join(part.capitalize() for part in value.split())


def name_of(properties):
    return (properties.get("names") or {}).get("primary")


def category(feature_type, properties):
    subtype = properties.get("subtype")
    class_name = properties.get("class")
    if feature_type == "building":
        return ["Buildings", "Footprints", clean(subtype)]
    if feature_type == "building_part":
        return ["Buildings", "Parts", clean(subtype or class_name)]
    if feature_type == "segment":
        if subtype == "road":
            return ["Transport", "Roads", clean(class_name)]
        if subtype == "rail":
            return ["Transport", "Railway", clean(class_name)]
        return ["Transport", "Water Routes", clean(class_name or subtype)]
    if feature_type == "connector":
        return ["Transport", "Connectors"]
    if feature_type == "water":
        return ["Water", clean(subtype), clean(class_name)]
    if feature_type == "land_use":
        return ["Land Use", clean(subtype), clean(class_name)]
    if feature_type == "land":
        return ["Base", "Land", clean(class_name or subtype)]
    if feature_type == "place":
        hierarchy = ((properties.get("taxonomy") or {}).get("hierarchy") or [])
        return ["Places", clean(hierarchy[0] if hierarchy else "Other")]
    return [clean(feature_type)]


def flatten(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Point):
        return [{"kind": "Point", "points": [[geometry.x, geometry.y, 0.0]]}]
    if isinstance(geometry, LineString):
        points = [[x, y, 0.0] for x, y, *_ in geometry.coords]
        return [{"kind": "LineString", "points": points}] if len(points) >= 2 else []
    if isinstance(geometry, Polygon):
        return [
            {
                "kind": "Polygon",
                "points": [[x, y, 0.0] for x, y, *_ in geometry.exterior.coords],
                "holes": [[[x, y, 0.0] for x, y, *_ in ring.coords] for ring in geometry.interiors],
            }
        ]
    if isinstance(geometry, (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)):
        parts = []
        for item in geometry.geoms:
            parts.extend(flatten(item))
        return parts
    return []


def leaf_geometries(geometry):
    if isinstance(geometry, (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)):
        for item in geometry.geoms:
            yield from leaf_geometries(item)
    elif not geometry.is_empty:
        yield geometry


def normalize_features(collections, to_local, context_geometry):
    """Normalize selected cached collections without terrain or file writes."""
    records = []
    for feature_type, collection in collections.items():
        validate_types([feature_type])
        if collection.get('type') != 'FeatureCollection' or not isinstance(collection.get('features'),list):
            raise ValueError('Source must be a GeoJSON FeatureCollection')
        for source_feature_index, feature in enumerate(collection['features']):
            if feature.get('geometry') is None:
                raise ValueError('Source feature has no geometry')
            source_geometry = transform(to_local, shape(feature['geometry']))
            parts = []
            repaired = not source_geometry.is_valid
            for source_part_index, source_part in enumerate(leaf_geometries(source_geometry)):
                valid = source_part if source_part.is_valid else make_valid(source_part)
                clipped = valid.intersection(context_geometry)
                for part in flatten(clipped):
                    part['source_part_index'] = source_part_index
                    part['clipped_part_index'] = len(parts)
                    parts.append(part)
            if not parts:
                continue
            properties = feature.get('properties') or {}
            records.append({'id':feature.get('id'), 'feature_type':feature_type, 'version':properties.get('version'), 'name':name_of(properties), 'category_path':category(feature_type,properties), 'properties':properties, 'sources':properties.get('sources') or [], 'source_feature_index':source_feature_index, 'source_bounds_local':list(source_geometry.bounds), 'geometry_repaired':repaired, 'parts':parts})
    return records


def process_sources(collections, site_geometry, context_data, manifest, site_name, manifest_path, report_path, generated_utc=None):
    """Return checked 2D source data. All geometry uses local metres at Z=0.

    Each invocation owns its output. Independent theme workers can pass separate
    collections and write separate files; they never change the source manifest.
    """
    target_crs = CRS.from_user_input(context_data['projected_crs'])
    if not target_crs.is_projected or any(axis.unit_conversion_factor != 1 for axis in target_crs.axis_info[:2]):
        raise ValueError('The projected CRS must use metres')
    forward = Transformer.from_crs(4326,target_crs,always_xy=True)
    origin_x,origin_y = context_data['origin_projected']
    def to_local(x,y,z=None):
        projected_x,projected_y = forward.transform(x,y,errcheck=True)
        return projected_x-origin_x,projected_y-origin_y
    site_local = transform(to_local,site_geometry)
    if not site_local.is_valid:
        site_local = make_valid(site_local)
    context_bounds = context_data['context_bounds_local']
    context_geometry = box(*context_bounds)
    release = manifest.get('release')
    if not isinstance(release,str) or not release.strip() or release in {'unknown','latest'}:
        raise ValueError('Source manifest must identify its resolved release')
    result = {'run':{'site_name':site_name,'generated_utc':generated_utc or dt.datetime.now(dt.timezone.utc).isoformat(),'semantic_source':'Overture Maps','source_release':release,'projected_crs':context_data['projected_crs'],'origin_wgs84':context_data['origin_wgs84'],'origin_projected':context_data['origin_projected'],'vertical_datum':'not set','source_manifest_path':str(manifest_path),'report_path':str(report_path)},'site':{'parts':flatten(site_local)},'context':{'parts':flatten(context_geometry),'bounds_local':context_bounds,'bounds_wgs84':context_data['context_bounds_wgs84'],'selection_method':context_data['context_selection_method']},'features':normalize_features(collections,to_local,context_geometry)}
    return validate_sources(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir',required=True)
    parser.add_argument('--site',required=True,help='WGS84 site Polygon or MultiPolygon GeoJSON')
    parser.add_argument('--context',required=True,help='JSON from derive_context.py')
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--site-name',required=True)
    parser.add_argument('--output',required=True,help='Unique normalized source output for this invocation')
    parser.add_argument('--report-path',required=True)
    parser.add_argument('--types',nargs='+',choices=FEATURE_TYPES,help='Only process these types; omitted means all available files')
    args = parser.parse_args()
    input_dir = Path(args.input_dir).resolve()
    manifest = load_json(args.manifest)
    selected = validate_types(args.types if args.types is not None else [kind for kind in FEATURE_TYPES if (input_dir/(kind+'.geojson')).exists()])
    manifest_records = {record['feature_type']:record for record in manifest.get('files',[])}
    collections = {}
    for kind in selected:
        path = input_dir/(kind+'.geojson')
        if kind not in manifest_records or manifest_records[kind].get('sha256') != file_sha256(path):
            raise ValueError('Source file does not match its manifest: '+kind)
        collections[kind] = load_json(path)
    result = process_sources(collections,read_geojson_geometry(args.site),load_json(args.context),manifest,args.site_name,str(Path(args.manifest).resolve()),args.report_path)
    output_path = Path(args.output).resolve()
    atomic_json(output_path,result)
    print(json.dumps({'output':str(output_path),'feature_count':len(result['features']),'geometry_part_count':sum(len(record['parts']) for record in result['features'])},indent=2))

if __name__ == '__main__':
    main()
