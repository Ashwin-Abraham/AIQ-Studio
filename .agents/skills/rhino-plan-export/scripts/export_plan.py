"""Read model source plans and build a scaled, layered drawing scene."""
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import math
from pathlib import Path

import rhino3dm as r3d
from shapely.geometry import LineString, Point, Polygon, box


def source_key(obj, layer):
    a = obj.Attributes
    return (layer, a.GetUserString("source_feature_id") or a.GetUserString("overture_id")
            or a.Name.removesuffix(" hole"),
            a.GetUserString("clipped_part_index") or a.GetUserString("geometry_part_index") or "0")


def read_features(path, root=None):
    model = r3d.File3dm.Read(str(path))
    if model is None:
        raise ValueError("Cannot read the Rhino model")
    roots = sorted({l.FullPath.split("::2D")[0] + "::2D" for l in model.Layers
                    if "::2D::" in l.FullPath})
    if root is None:
        if len(roots) != 1:
            raise ValueError(f"Select --root from these 2D branches: {roots}")
        root = roots[0]
    if root not in roots:
        raise ValueError(f"Unknown 2D root: {root}")
    if model.Settings.ModelUnitSystem in (getattr(r3d.UnitSystem, "None"), r3d.UnitSystem.Unset,
                                          r3d.UnitSystem.CustomUnits):
        raise ValueError("The model needs defined length units")
    metres = r3d.UnitSystem.UnitScale(model.Settings.ModelUnitSystem, r3d.UnitSystem.Meters)
    features, holes, counts = [], defaultdict(list), Counter()
    for obj in model.Objects:
        layer = model.Layers.FindIndex(obj.Attributes.LayerIndex).FullPath
        if not layer.startswith(root + "::"):
            continue
        counts[layer] += 1
        role = obj.Attributes.GetUserString("geometry_role") or ""
        geo = obj.Geometry
        if isinstance(geo, r3d.Point):
            pts = [geo.Location]
            shape = Point(pts[0].X * metres, pts[0].Y * metres)
        elif isinstance(geo, r3d.Curve):
            pts = geo.TryGetPolyline()
            if pts is None:
                raise ValueError(f"Curve {obj.Attributes.Id} is not a polyline. Use Rhino to approximate it at a stated tolerance.")
            xy = [(p.X * metres, p.Y * metres) for p in pts]
            shape = Polygon(xy) if geo.IsClosed else LineString(xy)
        else:
            raise ValueError(f"Unsupported source geometry: {type(geo).__name__} on {layer}")
        if any(abs(p.Z * metres) > 0.001 for p in pts):
            raise ValueError(f"Source plan is not at Z = 0: {obj.Attributes.Id}")
        if not shape.is_valid or shape.is_empty:
            raise ValueError(f"Invalid source geometry: {obj.Attributes.Id}")
        key = source_key(obj, layer)
        if role.endswith("hole"):
            if not isinstance(shape, Polygon):
                raise ValueError("A polygon hole must be a closed ring")
            holes[key].append(shape)
            continue
        features.append({"geometry": shape, "layer": layer[len(root) + 2:],
                         "id": str(obj.Attributes.Id), "name": obj.Attributes.Name or "",
                         "key": key, "metadata": dict(obj.Attributes.GetUserStrings())})
    for key, rings in holes.items():
        parents = [f for f in features if f["key"] == key and isinstance(f["geometry"], Polygon)]
        if len(parents) != 1:
            raise ValueError(f"Cannot identify one parent for hole: {key}")
        parent = parents[0]
        if not all(parent["geometry"].contains(ring) for ring in rings):
            raise ValueError(f"Hole lies outside its parent: {key}")
        parent["geometry"] = Polygon(parent["geometry"].exterior.coords,
                                     [ring.exterior.coords for ring in rings])
        if not parent["geometry"].is_valid:
            raise ValueError(f"Invalid polygon with holes: {key}")
    if not features:
        raise ValueError("No source plan geometry found")
    return features, {"root": root, "model_units": str(model.Settings.ModelUnitSystem),
                      "metres_per_unit": metres, "source_layer_counts": dict(counts),
                      "polygon_holes": sum(map(len, holes.values())),
                      "document_metadata": dict(model.Strings)}


def style(layer):
    """Paper widths are symbols. They never imply measured road widths."""
    key = layer.lower().replace("_", " ")
    if "boundary" in key:
        return (90, "#b34d37", None, 0.50)
    if "buildings" in key:
        return (60 if "parts" not in key else 61, "#555d61", "#d3d7d7", 0.16)
    if "water" in key:
        return (30, "#80a8b3", "#d8e9ed", 0.18)
    if "transport" in key:
        return (70, "#8a776f" if "railway" in key else "#969a98", None,
                0.18 if any(v in key for v in ("footway", "steps", "cycleway")) else 0.28)
    if any(v in key for v in ("wood", "tree", "shrub", "scrub")):
        return (45, "#9aaa91", "#d1ddc8", 0.15)
    if any(v in key for v in ("park", "grass", "garden", "recreation", "cemetery")):
        return (20, "#b2c1a4", "#e1e9d8", 0.15)
    if "land use" in key:
        return (10, "#d9d8d0", "#efeee8", 0.12)
    return (5, "#deded5", "#f6f5ef", 0.12)


def parts(geometry):
    if geometry.is_empty:
        return
    if hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            yield from parts(part)
    else:
        yield geometry


def build_scene(features, source, config):
    scale = float(config["scale"])
    bounds = [float(v) for v in config["bounds_m"]]
    if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds + [scale]):
        raise ValueError("Bounds and scale must be finite numbers")
    xmin, ymin, xmax, ymax = bounds
    if scale <= 0 or xmax <= xmin or ymax <= ymin:
        raise ValueError("Use positive scale and ordered, non-empty bounds")
    factor = 1000 / scale
    w, h = (xmax - xmin) * factor, (ymax - ymin) * factor
    if w > 267 or h > 237:
        raise ValueError("The extent does not fit the A3 map frame at this scale")
    left, top = 16 + (267 - w) / 2, 42 + (237 - h) / 2
    def xy(point):
        return [left + (point[0] - xmin) * factor, top + (ymax - point[1]) * factor]
    scene = {"width_mm": 420, "height_mm": 297, "items": [], "scale": scale,
             "bounds_m": bounds, "title": config["title"], "north": config["north"],
             "map_frame_mm": [left, top, w, h]}
    items = scene["items"]
    def path(layer, rings, stroke, fill, width):
        items.append({"kind": "path", "layer": layer, "rings": rings,
                      "stroke": stroke, "fill": fill, "width": width})
    def text(x, y, label, size=3, color="#303c40"):
        items.append({"kind": "text", "layer": "95 Sheet text", "x": x, "y": y,
                      "text": label, "size": size, "color": color})
    def rect(x, y, rw, rh, stroke, fill, width=.15, layer="00 Paper"):
        path(layer, [[[x, y], [x+rw, y], [x+rw, y+rh], [x, y+rh], [x, y]]], stroke, fill, width)
    rect(0, 0, 420, 297, None, "#ffffff")
    rect(left, top, w, h, None, "#fbfaf6", layer="01 Map background")
    clip = box(*bounds)
    excluded, drawn = Counter(), Counter()
    exported = []
    for f in sorted(features, key=lambda f: (style(f["layer"])[0], f["layer"], f["id"])):
        layer = f["layer"]
        key = layer.lower()
        if "connectors" in key or "places" in key or ("boundary" in key and "context" in key):
            excluded[layer] += 1
            continue
        order, stroke, fill, width = style(layer)
        clipped = f["geometry"].intersection(clip)
        if clipped.is_empty:
            excluded["outside extent"] += 1
            continue
        drawn[layer] += 1
        exported.append({k: f[k] for k in ("id", "layer", "name", "metadata")})
        for geo in parts(clipped):
            rings = []
            if isinstance(geo, Polygon):
                rings = [[xy(p) for p in ring.coords] for ring in [geo.exterior, *geo.interiors]]
            elif isinstance(geo, LineString):
                rings = [[xy(p) for p in geo.coords]]
            elif isinstance(geo, Point):
                # A fixed symbol marks the source point; it is not a measured tree canopy.
                x, y = xy(geo.coords[0])
                rings = [[[x + .50 * math.cos(i * math.tau / 16),
                           y + .50 * math.sin(i * math.tau / 16)] for i in range(17)]]
                rings[0][-1] = rings[0][0]
            if rings:
                path(f"{order:02d} {layer}", rings, stroke,
                     fill if isinstance(geo, (Polygon, Point)) else None, width)
    if not drawn:
        raise ValueError("No geometry in the selected extent")
    rect(left, top, w, h, "#c9ccc6", None, .15, "91 Frame")
    text(16, 16, "AIQ STUDIO  /  SITE DRAWINGS", 3.0)
    text(16, 29, config["title"], 7.0)
    text(16, 36, config["subtitle"], 3.0, "#697477")
    path("91 Frame", [[[298, 43], [298, 279]]], "#d5d9d6", None, .2)
    text(310, 51, config["sheet_id"] + "  /  " + config["drawing_name"], 3.6)
    text(310, 60, f"1:{scale:g}  |  A3  |  Print at 100%", 3.0)
    text(310, 78, config["north_label"], 2.8)
    if config["north"] != "+Y":
        raise ValueError("This sheet template requires confirmed north along +Y")
    path("92 North and scale", [[[318, 103], [318, 84], [315, 91], [318, 89], [321, 91], [318, 84]]],
         "#303c40", None, .35)
    text(324, 88, "N", 3.8)
    text(310, 120, "DRAWING KEY", 3.0)
    legend = [("Building footprint", "#d3d7d7", "#555d61"),
              ("Green space / land use", "#e1e9d8", "#b2c1a4"),
              ("Water", "#d8e9ed", "#80a8b3"),
              ("Transport centre line", None, "#969a98"),
              ("Mapped site boundary", None, "#b34d37")]
    for index, (label, fill, stroke) in enumerate(legend):
        y = 128 + index * 9
        if fill:
            rect(310, y-3, 6, 3, stroke, fill, layer="93 Legend")
        else:
            path("93 Legend", [[[310, y-1.5], [316, y-1.5]]], stroke, None, .35)
        text(320, y, label, 2.8)
    text(310, 185, "SOURCE AND METHOD", 3.0)
    for i, line in enumerate(config["notes"]):
        if len(line) > 49 or i >= 9:
            raise ValueError("Use at most 9 short sidebar notes (49 characters each)")
        text(310, 193 + i*5, line, 2.6, "#697477")
    length = float(config["scale_bar_m"])
    bw = length * factor
    if not 0 < bw <= 80:
        raise ValueError("Scale bar must fit the sidebar")
    for i in range(4):
        rect(310+i*bw/4, 257, bw/4, 2, "#303c40", "#303c40" if i%2==0 else "#ffffff",
             layer="92 North and scale")
    text(310, 265, "0", 2.6)
    text(310+bw/2-2, 265, f"{length/2:g}", 2.6)
    text(310+bw-4, 265, f"{length:g} m", 2.6)
    text(310, 277, "Vector plan  /  Editable layers", 2.7)
    text(16, 289, "Source geometry from Rhino  |  Footprint plan  |  Not a surveyed or construction drawing", 2.5, "#697477")
    text(356, 289, config["date"], 2.5, "#697477")
    scene["report"] = {**source, "drawn_features": dict(drawn), "excluded_features": dict(excluded),
                       "exported_objects": exported,
                       "method": "Source 2D geometry; XY plan; polygon clipping in model metres",
                       "scale_bar_m": length, "scale_bar_paper_mm": bw,
                       "north_basis": config["north_label"],
                       "limitations": ["No hidden-line or section calculation", "Roads are centre lines",
                                       "Tree point symbols do not show canopy extent",
                                       "Hidden 2D source branch is included by design"]}
    return scene


def svg_text(scene):
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">']
    for item in scene["items"]:
        if item["kind"] == "text":
            body.append(f'<text x="{item["x"]}" y="{item["y"]}" font-family="Arial" '
                        f'font-size="{item["size"]}" fill="{item["color"]}">{html.escape(item["text"])}</text>')
        else:
            commands = []
            for ring in item["rings"]:
                commands.append("M " + " L ".join(f"{x:.6f} {y:.6f}" for x, y in ring))
                if ring[0] == ring[-1]:
                    commands.append("Z")
            body.append(f'<path d="{" ".join(commands)}" stroke="{item["stroke"] or "none"}" '
                        f'fill="{item["fill"] or "none"}" stroke-width="{item["width"]}" '
                        'fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"/>')
    return "\n".join(body + ["</svg>"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True, help="New output directory")
    parser.add_argument("--root")
    args = parser.parse_args()
    model = Path(args.model).resolve()
    output = Path(args.output).resolve()
    features, source = read_features(model, args.root)
    source.update(model=str(model), sha256=hashlib.sha256(model.read_bytes()).hexdigest())
    sheets = json.loads(Path(args.config).read_text(encoding="utf-8"))["sheets"]
    output.mkdir(parents=True, exist_ok=False)
    for config in sheets:
        name = config["name"]
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
            raise ValueError("Sheet names must use lowercase letters, digits, hyphens or underscores")
        scene = build_scene(features, source, config)
        target = output / name
        if target.with_suffix(".scene.json").exists():
            raise ValueError("Duplicate sheet name")
        target.with_suffix(".scene.json").write_text(json.dumps(scene, indent=2), encoding="utf-8")
        target.with_suffix(".svg").write_text(svg_text(scene), encoding="utf-8")
        target.with_suffix(".report.json").write_text(json.dumps(scene["report"], indent=2), encoding="utf-8")
        print(f"{name}: {sum(scene['report']['drawn_features'].values())} source features")


if __name__ == "__main__":
    main()
