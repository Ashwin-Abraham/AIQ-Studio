"""Regression checks for source and stage boundaries; no geospatial imports."""

import copy
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH
import sys
import tempfile
import unittest

sys.path.insert(0, str(SCRIPTS_PATH))
from site_model.contract import (CONTRACT_VERSION, atomic_json, check_checkpoint, confined_path,
                                 file_sha256, load_json, source_digest,
                                 validate_sources, validate_terrain)


def sources():
    ring = {"kind": "Polygon", "points": [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 0, 0]], "holes": []}
    return {"run": {"site_name": "Test", "generated_utc": "2026-09-16T12:00:00Z",
                    "semantic_source": "Overture Maps", "source_release": "2026-08-19.0",
                    "projected_crs": "EPSG:27700", "origin_wgs84": [0, 51.5],
                    "origin_projected": [500000, 180000], "vertical_datum": "not set",
                    "source_manifest_path": "manifest.json", "report_path": "report.md"},
            "site": {"parts": [copy.deepcopy(ring)]}, "context": {"parts": [copy.deepcopy(ring)]},
            "features": [{"id": "one", "feature_type": "building", "version": 1,
                          "category_path": ["Buildings", "Footprints"], "properties": {"height": 10},
                          "sources": [], "parts": [ring]}]}


def terrain():
    return {"projected_crs": "EPSG:27700", "origin_projected": [500000, 180000],
            "vertical_datum": "ODN", "rows": [[[0, 0, 2], [2, 1, 3]], [[-1, 2, 4], [1, 3, 5]]]}


class ContractTests(unittest.TestCase):
    def test_sources_need_no_terrain_and_allow_no_features(self):
        data = sources()
        self.assertIs(validate_sources(data), data)
        data["features"] = []
        validate_sources(data)
        data["terrain"] = terrain()
        with self.assertRaisesRegex(ValueError, "separate terrain"):
            validate_sources(data)

    def test_rejects_nonfinite_and_nonplanar_coordinates(self):
        for value in (float("nan"), float("inf"), True, "3"):
            data = sources()
            data["features"][0]["parts"][0]["points"][1][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_sources(data)
        data = sources()
        data["site"]["parts"][0]["points"][1][2] = 1
        with self.assertRaisesRegex(ValueError, "Z=0"):
            validate_sources(data)

    def test_rejects_open_shell_and_open_hole(self):
        for hole in (False, True):
            data = sources()
            part = data["features"][0]["parts"][0]
            if hole:
                part["holes"] = [[[1, 1, 0], [2, 1, 0], [2, 2, 0], [1, 2, 0]]]
            else:
                part["points"][-1] = [0, 10, 0]
            with self.subTest(hole=hole), self.assertRaisesRegex(ValueError, "closed"):
                validate_sources(data)

    def test_rejects_duplicate_identity_but_allows_same_id_in_other_type(self):
        data = sources()
        data["features"].append(copy.deepcopy(data["features"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_sources(data)
        data["features"][1]["feature_type"] = "building_part"
        validate_sources(data)

    def test_rejects_transport_connector_features(self):
        data = sources()
        data["features"][0]["feature_type"] = "connector"
        with self.assertRaisesRegex(ValueError, "Unsupported source feature type: connector"):
            validate_sources(data)

    def test_rejects_missing_metadata_and_empty_category(self):
        data = sources()
        del data["run"]["projected_crs"]
        with self.assertRaises(ValueError):
            validate_sources(data)
        data = sources()
        data["features"][0]["category_path"] = []
        with self.assertRaises(ValueError):
            validate_sources(data)

    def test_digest_ignores_output_metadata_but_detects_geometry_and_frame(self):
        data = sources()
        expected = source_digest(data)
        for name in ("generated_utc", "report_path", "source_manifest_path", "vertical_datum"):
            data["run"][name] = "changed"
        data["terrain"] = {}
        self.assertEqual(expected, source_digest(data))
        data["features"][0]["properties"]["height"] = 20
        self.assertNotEqual(expected, source_digest(data))
        data = sources()
        data["run"]["origin_projected"][0] += 1
        self.assertNotEqual(expected, source_digest(data))

    def test_terrain_checks_affine_grid_and_frame(self):
        validate_terrain(terrain(), sources())
        for key, value in (("origin_projected", [0, 0]), ("projected_crs", "EPSG:4326"), ("vertical_datum", "")):
            data = terrain()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_terrain(data, sources())
        data = terrain()
        data["rows"][1][1][0] += 0.01
        with self.assertRaisesRegex(ValueError, "affine"):
            validate_terrain(data, sources())

    def test_terrain_rejects_short_ragged_degenerate_and_nonfinite_grids(self):
        grids = [[], [[[0, 0, 0], [1, 0, 0]]],
                 [[[0, 0, 0], [1, 0, 0]], [[0, 1, 0]]],
                 [[[0, 0, 0], [1, 0, 0]], [[2, 0, 0], [3, 0, 0]]],
                 [[[0, 0, 0], [1, 0, 0]], [[0, 1, 0], [1, 1, float("nan")]]]]
        for grid in grids:
            data = terrain()
            data["rows"] = grid
            with self.subTest(grid=grid), self.assertRaises(ValueError):
                validate_terrain(data, sources())

    def test_strict_json_and_atomic_write_preserve_previous_file_on_bad_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for bad in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}', '[]'):
                path.write_text(bad, encoding="utf-8")
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    load_json(path)
            atomic_json(path, {"good": 1})
            with self.assertRaises(ValueError):
                atomic_json(path, {"bad": float("nan")})
            self.assertEqual({"good": 1}, load_json(path))
            self.assertEqual([path], list(Path(directory).iterdir()))

    def test_confined_paths_reject_parent_and_absolute_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            self.assertEqual((root / "sources.json").resolve(), confined_path(root, "sources.json"))
            for path in ("../outside.json", Path(directory) / "outside.json"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    confined_path(root, path)
            link = root / "outside-link"
            try:
                link.symlink_to(Path(directory), target_is_directory=True)
            except OSError:
                return  # Windows accounts can lack permission to create symlinks.
            with self.assertRaises(ValueError):
                confined_path(root, "outside-link/outside.json")

    def test_checkpoint_detects_changes_in_saved_model_sources_and_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "model.3dm"
            model.write_bytes(b"saved model")
            audit = Path(directory) / "audit.json"
            atomic_json(audit, {"checked": True})
            data = sources()
            checkpoint = {"schema": "rhino-site-model-checkpoint", "version": CONTRACT_VERSION,
                          "source_digest": source_digest(data), "model_sha256": file_sha256(model),
                          "checked_and_saved": True, "audit_path": "audit.json", "audit_sha256": file_sha256(audit)}
            self.assertIs(checkpoint, check_checkpoint(checkpoint, data, model))
            for key, value in (("version", CONTRACT_VERSION + 1), ("checked_and_saved", False), ("source_digest", "stale"), ("model_sha256", "stale")):
                changed = dict(checkpoint, **{key: value})
                with self.subTest(key=key), self.assertRaises(ValueError):
                    check_checkpoint(changed, data, model)
            atomic_json(audit, {"checked": False})
            with self.assertRaisesRegex(ValueError, "audit"):
                check_checkpoint(checkpoint, data, model)
            del checkpoint["audit_path"]
            with self.assertRaises(ValueError):
                check_checkpoint(checkpoint, data, model)


if __name__ == "__main__":
    unittest.main()
