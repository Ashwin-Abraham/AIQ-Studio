#!/usr/bin/env python3
"""Select a projected CRS and derive a site-centred model context."""

import argparse
import json
from pathlib import Path

from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import box, shape
from shapely.ops import transform


def read_geometry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("type") == "FeatureCollection":
        if len(data.get("features", [])) != 1:
            raise ValueError("The site FeatureCollection must contain exactly one feature")
        data = data["features"][0]
    if data.get("type") == "Feature":
        data = data["geometry"]
    geometry = shape(data)
    if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("The site boundary must be a Polygon or MultiPolygon")
    return geometry


def projected_crs(geometry):
    centroid = geometry.centroid
    matches = query_utm_crs_info(
        datum_name="WGS 84",
        area_of_interest=AreaOfInterest(centroid.x, centroid.y, centroid.x, centroid.y),
    )
    if matches:
        return CRS.from_epsg(matches[0].code)
    return CRS.from_epsg(3857)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="GeoJSON site polygon in WGS84")
    parser.add_argument("--output", required=True)
    parser.add_argument("--viewport", help="Reliable west,south,east,north bounds in WGS84")
    args = parser.parse_args()

    site_wgs84 = read_geometry(args.site)
    target_crs = projected_crs(site_wgs84)
    forward = Transformer.from_crs(4326, target_crs, always_xy=True)
    inverse = Transformer.from_crs(target_crs, 4326, always_xy=True)
    site_projected = transform(forward.transform, site_wgs84)
    centre = site_projected.centroid

    if args.viewport:
        values = [float(value) for value in args.viewport.split(",")]
        if len(values) != 4 or values[0] >= values[2] or values[1] >= values[3]:
            raise ValueError("--viewport must be west,south,east,north")
        context_projected = transform(forward.transform, box(*values))
        method = "reliable map viewport"
    else:
        min_x, min_y, max_x, max_y = site_projected.bounds
        longest_edge = max(max_x - min_x, max_y - min_y)
        width = max(300.0, 5.0 * longest_edge)
        context_projected = box(centre.x - width / 2, centre.y - width / 2, centre.x + width / 2, centre.y + width / 2)
        method = "max(300 m, 5 x site longest edge) total width"

    def localize(x, y, z=None):
        return x - centre.x, y - centre.y

    site_local = transform(localize, site_projected)
    context_local = transform(localize, context_projected)
    context_wgs84 = transform(inverse.transform, context_projected)
    result = {
        "projected_crs": target_crs.to_string(),
        "origin_wgs84": list(inverse.transform(centre.x, centre.y)),
        "origin_projected": [centre.x, centre.y],
        "site_bounds_local": list(site_local.bounds),
        "context_bounds_local": list(context_local.bounds),
        "context_bounds_wgs84": list(context_wgs84.bounds),
        "context_selection_method": method,
        "site_longest_edge_m": max(site_projected.bounds[2] - site_projected.bounds[0], site_projected.bounds[3] - site_projected.bounds[1]),
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
