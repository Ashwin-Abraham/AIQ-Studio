#!/usr/bin/env python3
"""Build a Rhino 3DM from the rhino-site-data-model processed JSON contract."""

import argparse
import json
import math
import uuid
from collections import Counter
from pathlib import Path

import rhino3dm as r3d
from shapely.geometry import Polygon
from shapely.ops import triangulate

FLOOR_HEIGHT = 3.5
ROOT = "AIQ Site"


def safe_name(value):
    return str(value or "Other Unclassified").replace("::", "-")


def polyline_curve(points, z_function=None, z_override=None):
    polyline = r3d.Polyline()
    for x, y, z in points:
        value = z_override if z_override is not None else z_function(x, y) if z_function else z
        polyline.Add(x, y, value)
    return polyline.ToPolylineCurve()


class TerrainSampler:
    def __init__(self, terrain):
        self.rows = (terrain or {}).get("rows") or []
        self.row_count = len(self.rows)
        self.column_count = len(self.rows[0]) if self.rows else 0
        self.available = self.row_count >= 2 and self.column_count >= 2
        if self.available:
            p00, p01, p10 = self.rows[0][0], self.rows[0][1], self.rows[1][0]
            self.p00 = p00
            self.ax, self.ay = p01[0] - p00[0], p01[1] - p00[1]
            self.bx, self.by = p10[0] - p00[0], p10[1] - p00[1]
            self.determinant = self.ax * self.by - self.ay * self.bx
            if abs(self.determinant) < 1e-12:
                raise ValueError("Terrain grid axes are degenerate")

    def z(self, x, y):
        if not self.available:
            return 0.0
        dx, dy = x - self.p00[0], y - self.p00[1]
        column_value = (dx * self.by - dy * self.bx) / self.determinant
        row_value = (self.ax * dy - self.ay * dx) / self.determinant
        c0 = max(0, min(self.column_count - 2, math.floor(column_value)))
        r0 = max(0, min(self.row_count - 2, math.floor(row_value)))
        u = max(0.0, min(1.0, column_value - c0))
        v = max(0.0, min(1.0, row_value - r0))
        z00, z01 = self.rows[r0][c0][2], self.rows[r0][c0 + 1][2]
        z10, z11 = self.rows[r0 + 1][c0][2], self.rows[r0 + 1][c0 + 1][2]
        return (1 - u) * (1 - v) * z00 + u * (1 - v) * z01 + (1 - u) * v * z10 + u * v * z11

    def mesh(self):
        if not self.available:
            return None
        mesh = r3d.Mesh()
        for row in self.rows:
            for x, y, z in row:
                mesh.Vertices.Add(x, y, z)
        for row_index in range(self.row_count - 1):
            for column_index in range(self.column_count - 1):
                a = row_index * self.column_count + column_index
                mesh.Faces.AddFace(a, a + 1, a + 1 + self.column_count, a + self.column_count)
        mesh.Compact()
        return mesh


def polygon_from_part(part):
    outer = [(point[0], point[1]) for point in part["points"]]
    holes = [[(point[0], point[1]) for point in ring] for ring in part.get("holes", [])]
    polygon = Polygon(outer, holes)
    return polygon if polygon.is_valid else polygon.buffer(0)


def reference_ground(part, sampler):
    polygon = polygon_from_part(part)
    samples = [(point[0], point[1]) for point in part["points"]]
    samples.extend((point[0], point[1]) for ring in part.get("holes", []) for point in ring)
    for triangle in triangulate(polygon):
        if polygon.covers(triangle.representative_point()):
            point = triangle.representative_point()
            samples.append((point.x, point.y))
    values = [sampler.z(x, y) for x, y in samples]
    return max(values) if values else 0.0, len(values)


def height_rule(record):
    properties = record.get("properties") or {}
    feature_type = record.get("feature_type")
    if feature_type == "building_part":
        if properties.get("is_underground"):
            return None, "underground vertical position unresolved", False
        if properties.get("height") is not None:
            return float(properties["height"]), "explicit height", False
        if properties.get("num_floors") is not None:
            return float(properties["num_floors"]) * FLOOR_HEIGHT, "num_floors x 3.5 m", True
        return FLOOR_HEIGHT, "one-floor building-part fallback", True

    if properties.get("height") is not None:
        return float(properties["height"]), "explicit height", False
    if properties.get("num_floors") is not None:
        value = float(properties["num_floors"]) * FLOOR_HEIGHT
        if properties.get("roof_height") is not None:
            value += float(properties["roof_height"])
            return value, "num_floors x 3.5 m plus explicit roof_height", True
        return value, "num_floors x 3.5 m", True
    class_name = str(properties.get("class") or "").lower()
    subtype = str(properties.get("subtype") or "").lower()
    if class_name in {"roof", "carport", "shelter"}:
        return None, "default volume excluded for class", False
    if class_name in {"garage", "garages", "shed", "service", "outbuilding"} or subtype in {"service", "outbuilding"}:
        return FLOOR_HEIGHT, "one-floor small-building fallback", True
    return 3.0 * FLOOR_HEIGHT, "three-floor occupied-building fallback", True


def part_bottom_rule(record):
    properties = record.get("properties") or {}
    if record.get("feature_type") != "building_part":
        return 0.0, "ground", False
    if properties.get("min_height") is not None:
        conflict = False
        if properties.get("min_floor") is not None:
            conflict = abs(float(properties["min_height"]) - float(properties["min_floor"]) * FLOOR_HEIGHT) > 0.01
        return float(properties["min_height"]), "explicit min_height", conflict
    if properties.get("min_floor") is not None:
        return float(properties["min_floor"]) * FLOOR_HEIGHT, "min_floor x 3.5 m", False
    return 0.0, "zero bottom offset", False


def flat_mass(part, bottom_z, top_z):
    polygon = polygon_from_part(part)
    rings = [[(point[0], point[1]) for point in part["points"]]]
    rings.extend([[(point[0], point[1]) for point in ring] for ring in part.get("holes", [])])
    mesh = r3d.Mesh()
    for ring in rings:
        for index in range(len(ring) - 1):
            x0, y0 = ring[index]
            x1, y1 = ring[index + 1]
            start = len(mesh.Vertices)
            mesh.Vertices.Add(x0, y0, bottom_z)
            mesh.Vertices.Add(x1, y1, bottom_z)
            mesh.Vertices.Add(x1, y1, top_z)
            mesh.Vertices.Add(x0, y0, top_z)
            mesh.Faces.AddFace(start, start + 1, start + 2, start + 3)
    for triangle in triangulate(polygon):
        if not polygon.covers(triangle.representative_point()):
            continue
        points = list(triangle.exterior.coords)[:3]
        top = len(mesh.Vertices)
        for x, y in points:
            mesh.Vertices.Add(x, y, top_z)
        mesh.Faces.AddFace(top, top + 1, top + 2)
        bottom = len(mesh.Vertices)
        for x, y in points:
            mesh.Vertices.Add(x, y, bottom_z)
        mesh.Faces.AddFace(bottom + 2, bottom + 1, bottom)
    mesh.Compact()
    return mesh


def terrain_skirt(part, base_z, sampler):
    mesh = r3d.Mesh()
    rings = [part["points"]] + list(part.get("holes", []))
    for ring in rings:
        for index in range(len(ring) - 1):
            x0, y0, _ = ring[index]
            x1, y1, _ = ring[index + 1]
            if math.hypot(x1 - x0, y1 - y0) < 1e-8:
                continue
            ground_0 = sampler.z(x0, y0)
            ground_1 = sampler.z(x1, y1)
            at_base_0 = abs(base_z - ground_0) < 1e-8
            at_base_1 = abs(base_z - ground_1) < 1e-8
            if at_base_0 and at_base_1:
                continue
            start = len(mesh.Vertices)
            if at_base_0:
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Vertices.Add(x1, y1, ground_1)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2)
            elif at_base_1:
                mesh.Vertices.Add(x0, y0, ground_0)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2)
            else:
                mesh.Vertices.Add(x0, y0, ground_0)
                mesh.Vertices.Add(x1, y1, ground_1)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2, start + 3)
    mesh.Compact()
    return mesh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", help="Optional JSON build summary")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    run = data["run"]
    sampler = TerrainSampler(data.get("terrain"))
    model = r3d.File3dm()
    model.ApplicationName = "rhino-site-data-model"
    model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
    model.Settings.ModelAbsoluteTolerance = 0.001
    model.Settings.ModelAngleToleranceDegrees = 1.0
    document_values = {
        "site.name": run["site_name"],
        "site.generated_utc": run["generated_utc"],
        "site.semantic_source": run["semantic_source"],
        "site.source_release": run["source_release"],
        "site.projected_crs": run["projected_crs"],
        "site.origin_wgs84": json.dumps(run["origin_wgs84"]),
        "site.origin_projected": json.dumps(run["origin_projected"]),
        "site.vertical_datum": run.get("vertical_datum") or "not set",
        "site.source_manifest": run["source_manifest_path"],
        "site.report": run["report_path"],
        "site.height_rules": "3.5 m floor; 3-floor occupied fallback; 1-floor small-building and building-part fallback",
    }
    for key, value in document_values.items():
        model.Strings[key] = str(value)

    earth = model.Settings.EarthAnchorPoint
    earth.Name = run["site_name"] + " local origin"
    earth.EarthBasepointLongitude = float(run["origin_wgs84"][0])
    earth.EarthBasepointLatitude = float(run["origin_wgs84"][1])
    earth.ModelBasePoint = r3d.Point3d(0, 0, 0)
    earth.ModelNorth = r3d.Vector3d(0, 1, 0)

    cache = {}

    def layer(path, visible=True, color=(120, 120, 120, 255)):
        if path in cache:
            return cache[path]
        parent_id = uuid.UUID(int=0)
        partial = []
        for part in path.split("::"):
            partial.append(part)
            full = "::".join(partial)
            if full in cache:
                parent_id = model.Layers.FindIndex(cache[full]).Id
                continue
            item = r3d.Layer()
            item.Name = safe_name(part)
            item.ParentLayerId = parent_id
            item.Visible = visible if full == path else True
            item.Color = color
            index = model.Layers.Add(item)
            cache[full] = index
            parent_id = model.Layers.FindIndex(index).Id
        return cache[path]

    def attributes(layer_index, name, record=None, role=None, part_index=None):
        item = r3d.ObjectAttributes()
        item.LayerIndex = layer_index
        item.Name = name
        item.ColorSource = r3d.ObjectColorSource.ColorFromLayer
        if role:
            item.SetUserString("geometry_role", role)
        if part_index is not None:
            item.SetUserString("clipped_part_index", str(part_index))
        if record:
            item.SetUserString("source_feature_id", str(record.get("id")))
            item.SetUserString("source_feature_type", str(record.get("feature_type")))
            item.SetUserString("source_feature_version", str(record.get("version")))
            item.SetUserString("generic_category", "::".join(record.get("category_path") or []))
            item.SetUserString("source_properties_json", json.dumps(record.get("properties") or {}, ensure_ascii=False, sort_keys=True))
            item.SetUserString("source_records_json", json.dumps(record.get("sources") or (record.get("properties") or {}).get("sources") or [], ensure_ascii=False, sort_keys=True))
        return item

    colors = {
        "Buildings": (196, 126, 70, 255),
        "Transport": (80, 80, 80, 255),
        "Water": (30, 125, 215, 255),
        "Land Use": (55, 150, 75, 255),
        "Places": (220, 80, 140, 255),
        "Terrain": (170, 185, 140, 255),
        "Boundary": (230, 45, 45, 255),
    }
    layer(ROOT, True)
    layer(ROOT + "::2D", False)
    layer(ROOT + "::3D", True)
    counts = Counter()
    warnings = []

    terrain = sampler.mesh()
    if terrain:
        index = layer(ROOT + "::3D::Terrain", True, colors["Terrain"])
        model.Objects.AddMesh(terrain, attributes(index, "Terrain", role="terrain_mesh"))
        counts["terrain_mesh"] += 1

    for boundary_name in ("site", "context"):
        boundary = data.get(boundary_name) or {}
        for part_index, part in enumerate(boundary.get("parts") or []):
            index_2d = layer(ROOT + "::2D::Boundary::" + boundary_name.title(), True, colors["Boundary"])
            model.Objects.AddCurve(polyline_curve(part["points"], z_override=0.0), attributes(index_2d, boundary_name.title(), role="source_plan_boundary", part_index=part_index))
            index_3d = layer(ROOT + "::3D::Boundary::" + boundary_name.title(), True, colors["Boundary"])
            model.Objects.AddCurve(polyline_curve(part["points"], z_function=sampler.z), attributes(index_3d, boundary_name.title(), role="terrain_draped_boundary", part_index=part_index))
            counts["boundaries"] += 2

    for record in data.get("features") or []:
        category = [safe_name(value) for value in record.get("category_path") or ["Other"]]
        category_text = "::".join(category)
        theme = category[0]
        color = colors.get(theme, (120, 120, 120, 255))
        name = record.get("name") or "{} {}".format(record.get("feature_type"), record.get("id"))
        for part_index, part in enumerate(record.get("parts") or []):
            index_2d = layer(ROOT + "::2D::" + category_text, True, color)
            attrs_2d = attributes(index_2d, name, record, "source_plan_" + part["kind"].lower(), part_index)
            attrs_2d.SetUserString("source_z", "0")
            if part["kind"] == "Point":
                x, y, _ = part["points"][0]
                model.Objects.AddPoint(r3d.Point3d(x, y, 0), attrs_2d)
            else:
                model.Objects.AddCurve(polyline_curve(part["points"], z_override=0.0), attrs_2d)
                for hole_index, hole in enumerate(part.get("holes") or []):
                    hole_attrs = attributes(index_2d, name + " hole", record, "source_plan_hole", part_index)
                    hole_attrs.SetUserString("hole_index", str(hole_index))
                    model.Objects.AddCurve(polyline_curve(hole, z_override=0.0), hole_attrs)
            counts["source_2d"] += 1

            unresolved_part = record.get("feature_type") == "building_part" and (record.get("properties") or {}).get("is_underground")
            path_3d = category_text
            if unresolved_part:
                path_3d = "Buildings::Underground::Vertical Position Unresolved"
            index_3d = layer(ROOT + "::3D::" + path_3d, not unresolved_part, color)
            attrs_3d = attributes(index_3d, name + " on terrain", record, "terrain_draped_" + part["kind"].lower(), part_index)
            if part["kind"] == "Point":
                x, y, _ = part["points"][0]
                model.Objects.AddPoint(r3d.Point3d(x, y, sampler.z(x, y)), attrs_3d)
            else:
                model.Objects.AddCurve(polyline_curve(part["points"], z_function=sampler.z), attrs_3d)
                for hole_index, hole in enumerate(part.get("holes") or []):
                    hole_attrs = attributes(index_3d, name + " hole on terrain", record, "terrain_draped_hole", part_index)
                    hole_attrs.SetUserString("hole_index", str(hole_index))
                    model.Objects.AddCurve(polyline_curve(hole, z_function=sampler.z), hole_attrs)
            counts["terrain_draped"] += 1

            is_building = record.get("feature_type") in {"building", "building_part"}
            if not is_building or part["kind"] != "Polygon":
                continue
            height, height_method, estimated = height_rule(record)
            if height is None:
                continue
            reference_z, sample_count = reference_ground(part, sampler)
            offset, offset_method, conflict = part_bottom_rule(record)
            if conflict:
                warnings.append({"id": record.get("id"), "warning": "min_height and min_floor conflict; min_height used"})
            bottom_z = reference_z + offset
            top_z = bottom_z + height
            if top_z <= bottom_z:
                warnings.append({"id": record.get("id"), "warning": "non-positive building height"})
                continue
            properties = record.get("properties") or {}
            if record.get("feature_type") == "building_part":
                volume_branch = "Buildings::Part Volumes"
                volume_visible = True
            elif properties.get("has_parts"):
                volume_branch = "Buildings::Parent Envelope"
                volume_visible = False
            else:
                volume_branch = "Buildings::Volumes"
                volume_visible = True
            volume_layer = layer(ROOT + "::3D::" + volume_branch + "::" + category[-1], volume_visible, color)
            volume_attrs = attributes(volume_layer, name + " volume", record, "building_volume", part_index)
            volume_attrs.SetUserString("reference_ground_z", str(reference_z))
            volume_attrs.SetUserString("reference_ground_sample_count", str(sample_count))
            volume_attrs.SetUserString("bottom_offset_m", str(offset))
            volume_attrs.SetUserString("bottom_offset_method", offset_method)
            volume_attrs.SetUserString("building_height_m", str(height))
            volume_attrs.SetUserString("height_method", height_method)
            volume_attrs.SetUserString("height_is_estimated", str(estimated).lower())
            volume_attrs.SetUserString("volume_direction", "+Z")
            mass = flat_mass(part, bottom_z, top_z)
            model.Objects.AddMesh(mass, volume_attrs)
            counts["building_volumes"] += 1

            if record.get("feature_type") == "building" and sampler.available:
                skirt = terrain_skirt(part, reference_z, sampler)
                if len(skirt.Faces) > 0:
                    skirt_layer = layer(ROOT + "::3D::Buildings::Terrain Skirts::" + category[-1], True, color)
                    skirt_attrs = attributes(skirt_layer, name + " terrain skirt", record, "building_terrain_skirt", part_index)
                    skirt_attrs.SetUserString("reference_ground_z", str(reference_z))
                    model.Objects.AddMesh(skirt, skirt_attrs)
                    counts["terrain_skirts"] += 1

    annotation_layer = layer(ROOT + "::QA::Annotations::Run Info", True, (30, 30, 30, 255))
    bounds = (data.get("context") or {}).get("bounds_local") or [-150, -150, 150, 150]
    x, y = bounds[0], bounds[3]
    lines = [
        run["site_name"],
        "Generated: " + run["generated_utc"],
        "Source: {} {}".format(run["semantic_source"], run["source_release"]),
        "Context: {} {}".format((data.get("context") or {}).get("selection_method") or "not set", json.dumps(bounds)),
        "CRS: " + run["projected_crs"],
        "Terrain: {}".format((data.get("terrain") or {}).get("dataset") or "flat or not set"),
        "Vertical datum: " + str(run.get("vertical_datum") or "not set"),
        "Height rule: 3.5 m per floor",
        "Manifest: " + run["source_manifest_path"],
        "Report: " + run["report_path"],
    ]
    for index, text in enumerate(lines):
        model.Objects.AddTextDot(text, r3d.Point3d(x, y - index * 5.0, 0), attributes(annotation_layer, "Run Info", role="run_annotation"))
        counts["run_annotations"] += 1

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if not model.Write(str(output), 8):
        raise RuntimeError("Could not write " + str(output))
    summary = {"output": str(output), "counts": dict(sorted(counts.items())), "warnings": warnings}
    if args.summary:
        Path(args.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
