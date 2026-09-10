#!/usr/bin/env python3
"""Convert cached Overture GeoJSON files to the skill's local processed-data contract."""

import argparse
import datetime as dt
import json
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import transform

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
    value = str(value or "Other Unclassified").replace("-", " ").replace("_", " ")
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
        points = [[x, y, 0.0] for x, y in geometry.coords]
        return [{"kind": "LineString", "points": points}] if len(points) >= 2 else []
    if isinstance(geometry, Polygon):
        return [
            {
                "kind": "Polygon",
                "points": [[x, y, 0.0] for x, y in geometry.exterior.coords],
                "holes": [[[x, y, 0.0] for x, y in ring.coords] for ring in geometry.interiors],
            }
        ]
    if isinstance(geometry, (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)):
        parts = []
        for item in geometry.geoms:
            parts.extend(flatten(item))
        return parts
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--site", required=True, help="WGS84 site Polygon or MultiPolygon GeoJSON")
    parser.add_argument("--context", required=True, help="JSON from derive_context.py")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--site-name", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--terrain", help="Optional terrain JSON containing provider, dataset, vertical_datum, and rows")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    context_data = json.loads(Path(args.context).read_text(encoding="utf-8"))
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    target_crs = CRS.from_user_input(context_data["projected_crs"])
    forward = Transformer.from_crs(4326, target_crs, always_xy=True)
    origin_x, origin_y = context_data["origin_projected"]

    def to_local(x, y, z=None):
        projected_x, projected_y = forward.transform(x, y)
        return projected_x - origin_x, projected_y - origin_y

    site_local = transform(to_local, read_geojson_geometry(args.site))
    context_bounds = context_data["context_bounds_local"]
    context_geometry = box(*context_bounds)
    records = []

    for feature_type in FEATURE_TYPES:
        path = input_dir / (feature_type + ".geojson")
        if not path.exists():
            continue
        collection = json.loads(path.read_text(encoding="utf-8"))
        for feature in collection.get("features", []):
            source_geometry = transform(to_local, shape(feature["geometry"]))
            if not source_geometry.is_valid:
                source_geometry = source_geometry.buffer(0)
            clipped = source_geometry.intersection(context_geometry)
            parts = flatten(clipped)
            if not parts:
                continue
            properties = feature.get("properties") or {}
            for index, part in enumerate(parts):
                part["clipped_part_index"] = index
            records.append(
                {
                    "id": feature.get("id"),
                    "feature_type": feature_type,
                    "version": properties.get("version"),
                    "name": name_of(properties),
                    "category_path": category(feature_type, properties),
                    "properties": properties,
                    "sources": properties.get("sources") or [],
                    "source_bounds_local": list(source_geometry.bounds),
                    "parts": parts,
                }
            )

    context_part = flatten(context_geometry)[0]
    terrain = json.loads(Path(args.terrain).read_text(encoding="utf-8")) if args.terrain else {}
    output = {
        "run": {
            "site_name": args.site_name,
            "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "semantic_source": "Overture Maps",
            "source_release": manifest.get("release") or "unknown",
            "projected_crs": context_data["projected_crs"],
            "origin_wgs84": context_data["origin_wgs84"],
            "origin_projected": context_data["origin_projected"],
            "vertical_datum": terrain.get("vertical_datum") or "not set",
            "source_manifest_path": str(Path(args.manifest).resolve()),
            "report_path": args.report_path,
        },
        "site": {"parts": flatten(site_local)},
        "context": {
            "parts": [context_part],
            "bounds_local": context_bounds,
            "bounds_wgs84": context_data["context_bounds_wgs84"],
            "selection_method": context_data["context_selection_method"],
        },
        "terrain": terrain,
        "features": records,
    }
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output_path), "feature_count": len(records), "geometry_part_count": sum(len(record["parts"]) for record in records)}, indent=2))


if __name__ == "__main__":
    main()
