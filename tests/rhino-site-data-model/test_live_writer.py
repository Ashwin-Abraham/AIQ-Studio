#! python 3
"""Run in Rhino 8 Python 3. Uses only an isolated headless scratch document.

Set SITE_MODEL_RHINO_TEST_DEPS to a Python 3.9 rhino3dm package directory when
it is not installed in Rhino's Python environment. Results are written to
TEMP/site-model-live-writer-results.json. Normal CPython test discovery skips.
The workflow test uses the managed Python 3.12 runtime when available. Its
fallback uses the existing Python312 installation with rhino3dm and Shapely
2.1+ in TEMP/site-model-worker-test-deps; it does not install packages itself.
"""
import io
import json
import os
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH
import sys
sys.dont_write_bytecode = True
import tempfile
import traceback
import unittest

sys.path.insert(0, str(SCRIPTS_PATH))
deps = os.environ.get("SITE_MODEL_RHINO_TEST_DEPS", str(Path(tempfile.gettempdir()) / "site-model-rhino-test-deps"))
if Path(deps).exists() and sys.version_info[:2] == (3, 9):
    sys.path.insert(0, deps)
try:
    import Rhino
except ImportError:
    Rhino = None


@unittest.skipIf(Rhino is None, "Requires Rhino 8 Python 3")
class LiveWriterTests(unittest.TestCase):
    def setUp(self):
        import rhino3dm as r3d
        self.r3d = r3d
        self.active_serial = Rhino.RhinoDoc.ActiveDoc.RuntimeSerialNumber
        self.folder = tempfile.TemporaryDirectory(prefix="site-live-test-")
        self.path = Path(self.folder.name) / "scratch.3dm"
        self.sources = {"run": {"projected_crs": "EPSG:27700", "origin_projected": [0, 0], "origin_wgs84": [0, 51]}}
        model = r3d.File3dm()
        model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
        for key, value in self.sources["run"].items():
            model.Strings["site." + key] = json.dumps(value) if isinstance(value, list) else value
        self.user_id = str(model.Objects.AddPoint(r3d.Point3d(99, 99, 99)))
        self.assertTrue(model.Write(str(self.path), 8))
        self.doc = Rhino.RhinoDoc.OpenHeadless(str(self.path))
        self.assertIsNotNone(self.doc)
        self.writer = None

    def tearDown(self):
        if self.writer:
            self.writer.close()
        self.doc.Dispose()
        self.folder.cleanup()
        self.assertEqual(Rhino.RhinoDoc.ActiveDoc.RuntimeSerialNumber, self.active_serial)

    def prepared(self, x=1):
        r3d = self.r3d
        model = r3d.File3dm()
        root = r3d.Layer(); root.Name = "AIQ Site"
        root_index = model.Layers.Add(root)
        branch = r3d.Layer(); branch.Name = "2D"; branch.ParentLayerId = model.Layers.FindIndex(root_index).Id
        layer_index = model.Layers.Add(branch)
        attrs = r3d.ObjectAttributes(); attrs.LayerIndex = layer_index
        for key, value in {"site_owner": "rhino-site-data-model", "site_stage": "2d", "site_key": "point",
                           "site_content_hash": str(x), "geometry_role": "source_plan_point"}.items():
            attrs.SetUserString(key, value)
        model.Objects.AddPoint(r3d.Point3d(x, 2, 0), attrs)
        return model

    def new_writer(self, **kwargs):
        from site_model.writer import RhinoWriter
        self.writer = RhinoWriter(self.path, self.sources, document=self.doc, **kwargs)
        return self.writer

    def test_save_reopen_and_update_preserve_user_object(self):
        writer = self.new_writer()
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects))
        writer.finish(); writer.save()
        self.assertEqual(Path(self.doc.Path).resolve(), self.path.resolve())
        saved = self.r3d.File3dm.Read(str(self.path))
        self.assertEqual(len(saved.Objects), 2)
        self.assertIn(self.user_id, [str(obj.Attributes.Id) for obj in saved.Objects])
        original_id = str(next(obj.Id for obj in self.doc.Objects if obj.Attributes.GetUserString("site_key") == "point"))
        writer.begin("2d")
        changed = self.prepared(3)
        writer.apply(changed, list(changed.Objects)); writer.finish(); writer.save()
        self.assertEqual(writer.counts["updated"], 1)
        saved = self.r3d.File3dm.Read(str(self.path))
        point = next(obj for obj in saved.Objects if obj.Attributes.GetUserString("site_key") == "point")
        self.assertEqual(point.Geometry.Location.X, 3)
        self.assertEqual(str(point.Attributes.Id), original_id)

    def test_cancel_rolls_back_objects_layers_strings_and_disk(self):
        from site_model.writer import Cancelled
        cancelled = [False]
        writer = self.new_writer(cancel=lambda: cancelled[0])
        before_bytes = self.path.read_bytes()
        before_layers = [(layer.FullPath, layer.IsVisible) for layer in self.doc.Layers]
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects))
        self.doc.Strings.SetString("site.test", "temporary")
        cancelled[0] = True
        with self.assertRaises(Cancelled): writer.finish()
        writer.rollback()
        self.assertEqual([str(obj.Id) for obj in self.doc.Objects], [self.user_id])
        self.assertEqual([(layer.FullPath, layer.IsVisible) for layer in self.doc.Layers if not layer.IsDeleted], before_layers)
        self.assertFalse(self.doc.Strings.GetValue("site.test"))
        self.assertEqual(self.path.read_bytes(), before_bytes)

    def test_identity_change_is_rejected(self):
        writer = self.new_writer()
        writer.serial += 1
        with self.assertRaisesRegex(ValueError, "identity"):
            writer.pump()

    def test_deleted_object_history_does_not_make_document_nonempty(self):
        from System import Guid
        self.assertTrue(self.doc.Objects.Delete(Guid(self.user_id), True))
        self.doc.Modified = False
        writer = self.new_writer()
        self.assertTrue(writer.initialize_anchor)

    def test_hidden_live_object_keeps_document_nonempty(self):
        from System import Guid
        self.assertTrue(self.doc.Objects.Hide(Guid(self.user_id), True))
        self.doc.Modified = False
        writer = self.new_writer()
        self.assertFalse(writer.initialize_anchor)

    def test_rollback_ignores_deleted_layer_history(self):
        layer = Rhino.DocObjects.Layer()
        layer.Name = "Deleted before workflow"
        index = self.doc.Layers.Add(layer)
        self.assertGreaterEqual(index, 0)
        self.assertTrue(self.doc.Layers.Delete(index, True))
        self.doc.Modified = False
        writer = self.new_writer()
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects))
        writer.rollback()
        self.assertEqual([str(obj.Id) for obj in self.doc.Objects], [self.user_id])

    def test_manual_geometry_edit_is_replaced_even_with_old_content_hash(self):
        writer = self.new_writer()
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects)); writer.finish(); writer.save()
        point = next(obj for obj in self.doc.Objects if obj.Attributes.GetUserString("site_key") == "point")
        self.doc.Objects.Replace(point.Id, Rhino.Geometry.Point(Rhino.Geometry.Point3d(50, 50, 0)))
        writer.begin("2d")
        writer.apply(prepared, list(prepared.Objects)); writer.finish(); writer.save()
        point = next(obj for obj in self.doc.Objects if obj.Attributes.GetUserString("site_key") == "point")
        self.assertEqual(point.Geometry.Location.X, 1)
        self.assertEqual(writer.counts["updated"], 1)

    def test_cancel_before_begin_does_not_rollback_saved_stage(self):
        from site_model.writer import Cancelled
        cancelled = [False]
        writer = self.new_writer(cancel=lambda: cancelled[0])
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects)); writer.finish(); writer.save()
        before = {str(obj.Id) for obj in self.doc.Objects}
        cancelled[0] = True
        with self.assertRaises(Cancelled): writer.begin("3d")
        self.assertFalse(writer.transaction_open)
        writer.rollback()
        self.assertEqual({str(obj.Id) for obj in self.doc.Objects}, before)

    def test_cancel_replacement_restores_original_geometry_and_id(self):
        writer = self.new_writer()
        writer.begin("2d")
        prepared = self.prepared()
        writer.apply(prepared, list(prepared.Objects)); writer.finish(); writer.save()
        before = [(str(obj.Id), obj.Geometry.GetBoundingBox(True).Min.X) for obj in self.doc.Objects]
        before_bytes = self.path.read_bytes()
        writer.begin("2d")
        prepared = self.prepared(20)
        writer.apply(prepared, list(prepared.Objects))
        writer.rollback()
        self.assertEqual(sorted((str(obj.Id), obj.Geometry.GetBoundingBox(True).Min.X) for obj in self.doc.Objects), sorted(before))
        self.assertEqual(self.path.read_bytes(), before_bytes)

    def test_full_workflow_2d_then_3d_with_external_preparation(self):
        from site_model.workflow import run
        from site_model.writer import RhinoWriter
        from site_model.contract import atomic_json
        polygon = {"kind": "Polygon", "points": [[0,0,0],[10,0,0],[10,10,0],[0,10,0],[0,0,0]], "holes": []}
        data = {"run": {**self.sources["run"], "site_name": "Live test", "generated_utc": "2026-09-16",
                        "semantic_source": "test", "source_release": "test", "vertical_datum": "not set",
                        "source_manifest_path": "manifest.json", "report_path": "report.md"},
                "site": {"parts": [polygon]}, "context": {"parts": [polygon], "bounds_local": [0,0,10,10]},
                "features": [{"id": "building", "feature_type": "building", "version": 1,
                              "category_path": ["Buildings", "Residential"], "properties": {"height": 12},
                              "sources": [], "parts": [polygon]}]}
        source = Path(self.folder.name) / "sources.json"
        atomic_json(source, data)
        configured = os.environ.get("SITE_MODEL_WORKER_PYTHON")
        python = (Path(configured) if configured else
                  Path(os.environ["LOCALAPPDATA"]) / "AIQ Studio/runtimes/python/py312-geospatial-system-v1/Scripts/python.exe")
        if not python.exists():
            # Use an existing interpreter with isolated test dependencies.
            python = Path.home() / "AppData/Local/Programs/Python/Python312/python.exe"
            from unittest.mock import patch
            env = patch.dict(os.environ, {"PYTHONPATH": str(Path(tempfile.gettempdir()) / "site-model-worker-test-deps")})
            env.start()
            self.addCleanup(env.stop)
        def writer_factory(*args, **kwargs):
            return RhinoWriter(*args, document=self.doc, **kwargs)
        result = run(Path(self.folder.name), source, self.path, stage="2d", backend="live",
                     workers=2, worker_python=python, writer_factory=writer_factory, batch_size=3)
        self.assertTrue(result["stages"][0]["passed"], result)
        saved = self.r3d.File3dm.Read(str(self.path))
        plan_ids = {str(obj.Attributes.Id) for obj in saved.Objects}
        result = run(Path(self.folder.name), source, self.path, stage="3d", backend="live",
                     workers=2, worker_python=python, writer_factory=writer_factory, flat_elevation=0, batch_size=3)
        self.assertTrue(result["stages"][0]["passed"], result)
        saved = self.r3d.File3dm.Read(str(self.path))
        self.assertTrue(plan_ids <= {str(obj.Attributes.Id) for obj in saved.Objects})
        self.assertEqual(sum(obj.Attributes.GetUserString("geometry_role") == "building_volume" for obj in saved.Objects), 1)
        result = run(Path(self.folder.name), source, self.path, stage="2d", backend="live",
                     workers=2, worker_python=python, writer_factory=writer_factory, batch_size=3)
        self.assertTrue(result["stages"][0]["passed"], result)
        saved = self.r3d.File3dm.Read(str(self.path))
        self.assertTrue(plan_ids <= {str(obj.Attributes.Id) for obj in saved.Objects})
        self.assertEqual(sum(obj.Attributes.GetUserString("geometry_role") == "building_volume" for obj in saved.Objects), 0)


if __name__ == "__main__":
    # Rhino retains imported modules across script runs; test current files.
    for name in list(sys.modules):
        if name == "site_model" or name.startswith("site_model."):
            del sys.modules[name]
    output = io.StringIO()
    try:
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LiveWriterTests))
        report = {"passed": result.wasSuccessful(), "tests": result.testsRun, "skipped": len(result.skipped), "output": output.getvalue()}
    except Exception:
        report = {"passed": False, "error": traceback.format_exc()}
    Path(tempfile.gettempdir(), "site-model-live-writer-results.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
