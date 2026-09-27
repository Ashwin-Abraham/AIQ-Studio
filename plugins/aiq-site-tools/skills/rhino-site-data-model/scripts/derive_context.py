#!/usr/bin/env python3
"""Select a projected CRS and derive a site-centred model context."""

import argparse
import json
import math
from pathlib import Path

from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import box, shape
from shapely.ops import transform


DEFAULT_CONTEXT_MARGIN_METRES = 100.0


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


def estimated_context(site_projected, margin_metres=DEFAULT_CONTEXT_MARGIN_METRES):
    """Return the site envelope with a small projected safety margin."""
    if (
        not isinstance(margin_metres, (int, float))
        or not math.isfinite(margin_metres)
        or margin_metres <= 0
    ):
        raise ValueError("Context margin must be a positive finite number of metres")
    min_x, min_y, max_x, max_y = site_projected.bounds
    return box(
        min_x - margin_metres,
        min_y - margin_metres,
        max_x + margin_metres,
        max_y + margin_metres,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="GeoJSON site polygon in WGS84")
    parser.add_argument("--output", required=True)
    parser.add_argument("--viewport", help="Reliable west,south,east,north bounds in WGS84")
    parser.add_argument(
        "--context-margin-metres",
        type=float,
        default=DEFAULT_CONTEXT_MARGIN_METRES,
        help="Safety margin around the site envelope when --viewport is omitted (default: 100)",
    )
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
        context_margin_metres = None
    else:
        context_projected = estimated_context(site_projected, args.context_margin_metres)
        context_margin_metres = args.context_margin_metres
        method = f"site envelope plus {context_margin_metres:g} m safety margin"

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
        "context_margin_metres": context_margin_metres,
        "site_longest_edge_m": max(site_projected.bounds[2] - site_projected.bounds[0], site_projected.bounds[3] - site_projected.bounds[1]),
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
