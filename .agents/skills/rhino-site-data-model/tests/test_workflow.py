import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rhino3dm as r3d
from site_model.contract import atomic_json, file_sha256, load_json
from site_model.workflow import run, migrate
from site_model.writer import Cancelled, FileWriter


def fixture():
    polygon = dict(kind="Polygon", points=[[0,0,0],[10,0,0],[10,10,0],[0,10,0],[0,0,0]], holes=[])
    return dict(run=dict(site_name="Fixture", generated_utc="2026-09-16", semantic_source="test",
                         source_release="test", projected_crs="EPSG:27700", origin_projected=[0,0],
                         origin_wgs84=[0,51], vertical_datum="not set", source_manifest_path="manifest.json", report_path="report.md"),
                site=dict(parts=[polygon]), context=dict(parts=[polygon], bounds_local=[0,0,10,10]),
                features=[dict(id="b1", feature_type="building", version=1, category_path=["Buildings","Residential"],
                               properties=dict(height=12), sources=[], parts=[polygon])])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "sources.json", self.root / "model.3dm"
        atomic_json(self.source, fixture())

    def run_stage(self, stage, **kwargs):
        return run(self.root, self.source, self.output, stage=stage, backend="file", **kwargs)

    def test_2d_then_3d_preserves_plan_and_rerun_ids(self):
        with patch("site_model.geometry.TerrainSampler", side_effect=AssertionError("terrain used")):
            result = self.run_stage("2d")
        self.assertTrue(result["stages"][0]["passed"], result)
        plan = r3d.File3dm.Read(str(self.output))
        identities = {str(o.Attributes.Id) for o in plan.Objects}
        result = self.run_stage("3d", flat_elevation=0)
        self.assertTrue(result["stages"][0]["passed"], result)
        model = r3d.File3dm.Read(str(self.output))
        self.assertTrue(identities <= {str(o.Attributes.Id) for o in model.Objects})
        before = {str(o.Attributes.Id) for o in model.Objects}
        self.run_stage("3d", flat_elevation=0)
        self.assertEqual(before, {str(o.Attributes.Id) for o in r3d.File3dm.Read(str(self.output)).Objects})

    def test_3d_cannot_start_without_checkpoint(self):
        with self.assertRaises(ValueError):
            self.run_stage("3d", flat_elevation=0)
        self.assertFalse(self.output.exists())

    def test_unknown_heights_do_not_block_2d(self):
        source = fixture()
        source["features"][0]["properties"] = {"height": "unresolved", "num_floors": "unknown"}
        atomic_json(self.source, source)
        self.assertTrue(self.run_stage("2d")["stages"][0]["passed"])

    def test_external_worker_failure_rolls_back(self):
        self.run_stage("2d")
        before = file_sha256(self.output)
        with self.assertRaisesRegex(ValueError, "not visible"):
            self.run_stage("2d", workers=2, worker_python=str(self.root / "missing-python.exe"))
        self.assertEqual(before, file_sha256(self.output))

    def test_worker_preflight_happens_before_writer_construction(self):
        calls = []
        def writer_factory(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("writer must not be constructed")
        with self.assertRaisesRegex(ValueError, "not visible"):
            run(self.root, self.source, self.output, stage="2d", backend="live", workers=2,
                worker_python=str(self.root / "missing-python.exe"), writer_factory=writer_factory)
        self.assertEqual(calls, [])

    def test_terrain_run_uses_the_checked_frame(self):
        terrain = self.root / "terrain.json"
        atomic_json(terrain, dict(projected_crs="EPSG:27700", origin_projected=[0,0], vertical_datum="ODN",
                                  rows=[[[0,0,2],[10,0,2]],[[0,10,2],[10,10,2]]]))
        result = self.run_stage("all", terrain_path=terrain)
        self.assertTrue(all(a["passed"] for a in result["stages"]), result)
        model = r3d.File3dm.Read(str(self.output))
        mass = next(o for o in model.Objects if o.Attributes.GetUserString("geometry_role") == "building_volume")
        self.assertEqual(mass.Geometry.GetBoundingBox().Min.Z, 2)
        self.assertEqual(model.Strings["site.vertical_datum"], "ODN")

    def test_source_change_rejects_3d(self):
        self.run_stage("2d")
        source = fixture()
        source["features"][0]["properties"]["height"] = 15
        atomic_json(self.source, source)
        original = file_sha256(self.output)
        with self.assertRaisesRegex(ValueError, "different source"):
            self.run_stage("3d", flat_elevation=0)
        self.assertEqual(original, file_sha256(self.output))

    def test_user_geometry_survives_2d_updates(self):
        self.run_stage("2d")
        model = r3d.File3dm.Read(str(self.output))
        user_id = model.Objects.AddPoint(r3d.Point3d(20,20,20))
        model.Write(str(self.output), 8)
        self.run_stage("2d")
        self.assertIsNotNone(r3d.File3dm.Read(str(self.output)).Objects.FindId(user_id))

    def test_cancel_and_failed_save_keep_previous_file(self):
        self.run_stage("2d")
        original = file_sha256(self.output)
        events = []
        with self.assertRaises(Cancelled):
            self.run_stage("2d", batch_size=1, progress=events.append, cancel=lambda: bool(events))
        self.assertEqual(original, file_sha256(self.output))
        with patch.object(FileWriter, "save", side_effect=RuntimeError("disk full")):
            with self.assertRaisesRegex(RuntimeError, "disk full"):
                self.run_stage("2d")
        self.assertEqual(original, file_sha256(self.output))

    def test_failed_terrain_retains_completed_2d(self):
        terrain = self.root / "terrain.json"
        atomic_json(terrain, {"rows": []})
        with self.assertRaises(ValueError):
            self.run_stage("all", terrain_path=terrain)
        self.assertTrue(self.output.exists())
        self.assertEqual(load_json(str(self.output) + ".checkpoint.json")["completed_stage"], "2d")

    def test_parallel_matches_serial_and_cleans_temporaries(self):
        source = fixture()
        extra = copy.deepcopy(source["features"][0])
        extra["id"] = "b2"
        source["features"].append(extra)
        atomic_json(self.source, source)
        self.run_stage("all", flat_elevation=0, partition_size=1)
        def hashes():
            return {o.Attributes.GetUserString("site_key"): o.Attributes.GetUserString("site_content_hash")
                    for o in r3d.File3dm.Read(str(self.output)).Objects}
        serial = hashes()
        self.run_stage("all", flat_elevation=0, workers=2, partition_size=1)
        self.assertEqual(serial, hashes())
        self.assertFalse(list(self.root.rglob("__pycache__")))

    def test_outside_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "inside the project"):
            run(self.root, self.source, self.root.parent / "bad.3dm", stage="2d", backend="file")

    def test_migration_preserves_source_geometry(self):
        legacy = fixture()
        legacy["terrain"] = dict(provider="test", dataset="test", vertical_datum="ODN",
                                 rows=[[[0,0,1],[10,0,1]],[[0,10,1],[10,10,1]]])
        old = self.root / "old.json"
        atomic_json(old, legacy)
        migrate(old, self.source, self.root / "terrain.json")
        self.assertEqual(fixture(), load_json(self.source))
        self.assertIn("terrain", load_json(old))

    def test_cli_build_and_audit(self):
        entry = Path(__file__).resolve().parents[1] / "scripts/run_site_model.py"
        base = [sys.executable, "-B", str(entry), "--project-root", str(self.root), "--output", str(self.output), "--stage", "2d"]
        result = subprocess.run(base + ["--input", str(self.source), "--backend", "file"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(base + ["--audit-only"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
