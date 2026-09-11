"""Tests of geometry and scale invariants; no licensed Rhino runtime required."""
import json
from pathlib import Path
import tempfile
import unittest

import rhino3dm as r3d
from shapely.geometry import Polygon

from export_plan import read_features, build_scene
from render_ai import validate_ai


class PlanExportTests(unittest.TestCase):
    def model(self, folder, z=0, hole=True, orphan=False, units=r3d.UnitSystem.Meters):
        model = r3d.File3dm()
        model.Settings.ModelUnitSystem = units
        root = r3d.Layer()
        root.Name = "Test"
        root_id = model.Layers.Add(root)
        parent = r3d.Layer()
        parent.Name = "2D"
        parent.ParentLayerId = model.Layers.FindIndex(root_id).Id
        parent.Visible = False
        parent_id = model.Layers.Add(parent)
        layer = r3d.Layer()
        layer.Name = "Buildings"
        layer.ParentLayerId = model.Layers.FindIndex(parent_id).Id
        layer_id = model.Layers.Add(layer)
        for size, role in [(10, "source_plan_polygon")] + ([(4, "source_plan_hole")] if hole else []):
            attr = r3d.ObjectAttributes()
            attr.LayerIndex = layer_id
            attr.SetUserString("source_feature_id", "orphan" if orphan and size == 4 else "building")
            attr.SetUserString("geometry_role", role)
            attr.SetUserString("clipped_part_index", "0")
            ring = [r3d.Point3d(x,y,z) for x,y in [(-size,-size),(size,-size),(size,size),(-size,size),(-size,-size)]]
            model.Objects.AddCurve(r3d.PolylineCurve(ring), attr)
        path = Path(folder) / "input.3dm"
        self.assertTrue(model.Write(str(path), 8))
        return path

    def config(self):
        path = Path(__file__).parent.parent / "references" / "poplar-sheets.json"
        return json.loads(path.read_text())["sheets"][0]

    def test_hidden_source_branch_and_courtyard(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.model(folder)
            before = path.read_bytes()
            features, report = read_features(path)
            self.assertEqual(len(features), 1)
            self.assertEqual(features[0]["geometry"].area, 400-64)
            self.assertEqual(report["polygon_holes"], 1)
            self.assertEqual(path.read_bytes(), before)

    def test_millimetres_are_converted_to_metres(self):
        with tempfile.TemporaryDirectory() as folder:
            features, _ = read_features(self.model(folder, hole=False, units=r3d.UnitSystem.Millimeters))
            self.assertAlmostEqual(features[0]["geometry"].area, .0004)

    def test_nonplanar_input_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "Z = 0"):
                read_features(self.model(folder, z=1))

    def test_orphan_hole_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "parent"):
                read_features(self.model(folder, orphan=True))

    def test_clipping_and_paper_scale(self):
        config = self.config()
        config.update(bounds_m=[-5,-5,5,5], scale=100, scale_bar_m=5)
        feature = {"geometry": Polygon([(-10,-10),(10,-10),(10,10),(-10,10)]),
                   "layer": "Buildings", "id": "1", "name": "Building", "metadata": {}}
        scene = build_scene([feature], {}, config)
        drawing = next(i for i in scene["items"] if i["layer"] == "60 Buildings")
        xs = [p[0] for p in drawing["rings"][0]]
        self.assertAlmostEqual(max(xs)-min(xs), 100)
        self.assertAlmostEqual(scene["report"]["scale_bar_paper_mm"], 50)

    def test_extent_that_does_not_fit_fails(self):
        config = self.config()
        config["scale"] = 100
        with self.assertRaisesRegex(ValueError, "does not fit"):
            build_scene([], {}, config)

    def test_ai_wrong_units_and_unknown_operator_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"plan.ai"
            content = "%!PS-Adobe-3.0\n%%Creator: Rhinoceros\n%%BoundingBox: -1 -1 421 298\n%%EndSetup\n0 0 m\n%%PageTrailer\n"
            path.write_text(content)
            with self.assertRaisesRegex(ValueError, "scale or extent"):
                validate_ai(path)
            path.write_text(content.replace("421 298", "1191 842").replace("0 0 m", "unknown_operator"))
            with self.assertRaisesRegex(ValueError, "operators"):
                validate_ai(path)


if __name__ == "__main__":
    unittest.main()
