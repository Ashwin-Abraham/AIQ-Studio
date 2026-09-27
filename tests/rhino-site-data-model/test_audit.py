"""Audit failures must identify damaged generated geometry, not user objects."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH

sys.path.insert(0, str(SCRIPTS_PATH))
import rhino3dm as r3d
from site_model.audit import DOCUMENT_KEYS, OWNER, audit_file, audit_model
from site_model.contract import METADATA_CONTRACT


def attributes(key, role, stage="2d", source=False, full_source=None, source_id="a"):
    attrs = r3d.ObjectAttributes()
    for name, value in {"site_owner": OWNER, "site_key": key, "site_stage": stage, "geometry_role": role}.items():
        attrs.SetUserString(name, value)
    if source:
        values = {"source_feature_id": source_id, "source_feature_type": "building",
                  "source_feature_version": "1"}
        include_details = full_source if full_source is not None else stage == "2d"
        if include_details:
            values.update(generic_category="Buildings", source_properties_json="{}",
                          source_records_json="[]")
        for name, value in values.items():
            attrs.SetUserString(name, value)
    return attrs


def model_2d():
    model = r3d.File3dm()
    model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
    for name in DOCUMENT_KEYS:
        model.Strings[name] = METADATA_CONTRACT if name == "site.metadata_contract" else "test"
    for name in ("site", "context"):
        curve = r3d.PolylineCurve([r3d.Point3d(0, 0, 0), r3d.Point3d(2, 0, 0),
                                   r3d.Point3d(2, 2, 0), r3d.Point3d(0, 0, 0)])
        model.Objects.AddCurve(curve, attributes(name, "source_plan_boundary"))
    model.Objects.AddTextDot("test", r3d.Point3d(0, 0, 0), attributes("annotation", "run_annotation"))
    model.Objects.AddPoint(r3d.Point3d(0, 0, 0), attributes("source-metadata", "source_plan_point", source=True))
    return model


def add_3d(model):
    for name in ("site", "context"):
        model.Objects.AddPoint(r3d.Point3d(0, 0, 0), attributes(name + "-3d", "terrain_draped_boundary", "3d"))


class AuditTests(unittest.TestCase):
    def checks(self, result):
        return {failure["check"] for failure in result["failures"]}

    def test_2d_needs_no_terrain_or_masses(self):
        result = audit_model(model_2d(), "2d")
        self.assertTrue(result["passed"], result)
        self.assertIn("building_placement", result["checks_not_applicable"])
        self.assertEqual(result["visual_inspection"], "not-possible")
        self.assertTrue(result["warnings"])

    def test_user_geometry_is_not_a_site_source(self):
        model = model_2d()
        attrs = r3d.ObjectAttributes()
        attrs.SetUserString("geometry_role", "source_plan_point")
        model.Objects.AddPoint(r3d.Point3d(0, 0, 50), attrs)
        self.assertTrue(audit_model(model, "2d")["passed"])

    def test_owned_source_z_and_metadata_failures(self):
        model = model_2d()
        model.Objects.AddPoint(r3d.Point3d(0, 0, 5), attributes("source", "source_plan_point"))
        checks = self.checks(audit_model(model, "2d"))
        self.assertTrue({"source_plan_z", "source_metadata"} <= checks)

    def test_duplicate_keys_and_missing_owner(self):
        model = model_2d()
        model.Objects.AddPoint(r3d.Point3d(0, 0, 0), attributes("site", "source_plan_boundary"))
        attrs = r3d.ObjectAttributes()
        attrs.SetUserString("site_key", "unowned")
        model.Objects.AddPoint(r3d.Point3d(0, 0, 0), attrs)
        self.assertTrue({"duplicate_keys", "ownership_metadata"} <= self.checks(audit_model(model, "2d")))

    def test_stage_scope(self):
        model = model_2d()
        add_3d(model)
        self.assertIn("stage_scope", self.checks(audit_model(model, "2d")))
        self.assertTrue(audit_model(model, "3d")["passed"])

    def test_open_mass_is_rejected_even_with_valid_placement(self):
        model = model_2d()
        add_3d(model)
        mesh = r3d.Mesh()
        for xyz in ((0, 0, 0), (1, 0, 0), (0, 0, 10)):
            mesh.Vertices.Add(*xyz)
        mesh.Faces.AddFace(0, 1, 2)
        attrs = attributes("mass", "building_volume", "3d", source=True)
        for key, value in {"reference_ground_z": "0", "bottom_offset_m": "0", "building_height_m": "10", "volume_direction": "+Z"}.items():
            attrs.SetUserString(key, value)
        model.Objects.AddMesh(mesh, attrs)
        self.assertIn("closed_building_volume", self.checks(audit_model(model, "3d")))

    def test_3d_checks_retained_2d_and_json(self):
        model = model_2d()
        add_3d(model)
        attrs = attributes("source", "source_plan_point", source=True)
        attrs.SetUserString("source_properties_json", "[]")
        model.Objects.AddPoint(r3d.Point3d(0, 0, 3), attrs)
        self.assertTrue({"source_plan_z", "source_metadata_json"} <= self.checks(audit_model(model, "3d")))

    def test_3d_rejects_duplicated_details_and_unresolved_reference(self):
        model = model_2d()
        add_3d(model)
        duplicated = attributes("derived-details", "terrain_draped_point", "3d", source=True, full_source=True)
        model.Objects.AddPoint(r3d.Point3d(0, 0, 0), duplicated)
        missing = attributes("derived-missing", "terrain_draped_point", "3d", source=True, source_id="missing")
        model.Objects.AddPoint(r3d.Point3d(0, 0, 0), missing)
        checks = self.checks(audit_model(model, "3d"))
        self.assertTrue({"derived_metadata_duplication", "source_metadata_reference"} <= checks)

    def test_closed_mass_and_bad_top_elevation(self):
        for height, expected in ((10, True), (12, False)):
            model = model_2d()
            add_3d(model)
            mesh = r3d.Mesh()
            for xyz in ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                        (0, 0, 10), (1, 0, 10), (1, 1, 10), (0, 1, 10)):
                mesh.Vertices.Add(*xyz)
            for face in ((3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                mesh.Faces.AddFace(*face)
            attrs = attributes("mass", "building_volume", "3d", source=True)
            for key, value in {"reference_ground_z": "0", "bottom_offset_m": "0",
                               "building_height_m": str(height), "volume_direction": "+Z"}.items():
                attrs.SetUserString(key, value)
            model.Objects.AddMesh(mesh, attrs)
            result = audit_model(model, "3d")
            self.assertEqual(result["passed"], expected, result)
            if not expected:
                self.assertIn("building_placement", self.checks(result))

    def test_saved_model_is_reopened_and_hashed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.3dm"
            self.assertTrue(model_2d().Write(str(path), 8))
            result = audit_file(path, "2d")
            self.assertTrue(result["passed"], result)
            self.assertTrue(result["reopened"])
            self.assertEqual(result["model_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            path.write_text("not a model")
            self.assertFalse(audit_file(path, "2d")["reopened"])

    def test_visual_failure_and_invalid_stage(self):
        self.assertIn("visual_inspection", self.checks(audit_model(model_2d(), "2d", "failed", "Missing edge")))
        with self.assertRaises(ValueError):
            audit_model(model_2d(), "all")


if __name__ == "__main__":
    unittest.main()
