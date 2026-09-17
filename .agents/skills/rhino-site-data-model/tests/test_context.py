import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from shapely.geometry import box


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "derive_context.py"
SPEC = importlib.util.spec_from_file_location("derive_context", SCRIPT)
derive_context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(derive_context)


class EstimatedContextTests(unittest.TestCase):
    def test_default_margin_expands_each_side_of_site_envelope(self):
        site = box(10.0, 20.0, 210.0, 120.0)

        context = derive_context.estimated_context(site)

        self.assertEqual(context.bounds, (-90.0, -80.0, 310.0, 220.0))

    def test_custom_margin_is_supported(self):
        site = box(-25.0, -10.0, 25.0, 10.0)

        context = derive_context.estimated_context(site, 40.0)

        self.assertEqual(context.bounds, (-65.0, -50.0, 65.0, 50.0))

    def test_margin_must_be_positive_and_finite(self):
        site = box(0.0, 0.0, 10.0, 10.0)

        for invalid in (0, -1, math.inf, math.nan, "100"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    derive_context.estimated_context(site, invalid)

    def test_cli_records_default_margin_instead_of_legacy_multiplier(self):
        site = {
            "type": "Polygon",
            "coordinates": [[
                [-0.1600, 51.4780],
                [-0.1580, 51.4780],
                [-0.1580, 51.4790],
                [-0.1600, 51.4790],
                [-0.1600, 51.4780],
            ]],
        }
        with tempfile.TemporaryDirectory() as temporary_dir:
            site_path = Path(temporary_dir) / "site.geojson"
            output_path = Path(temporary_dir) / "context.json"
            site_path.write_text(json.dumps(site), encoding="utf-8")
            arguments = [
                str(SCRIPT),
                "--site",
                str(site_path),
                "--output",
                str(output_path),
            ]

            with mock.patch.object(sys, "argv", arguments), mock.patch(
                "sys.stdout", new_callable=io.StringIO
            ):
                derive_context.main()

            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(result["context_margin_metres"], 100.0)
            self.assertEqual(
                result["context_selection_method"],
                "site envelope plus 100 m safety margin",
            )
            site_bounds = result["site_bounds_local"]
            context_bounds = result["context_bounds_local"]
            for site_value, context_value in zip(site_bounds[:2], context_bounds[:2]):
                self.assertAlmostEqual(site_value - context_value, 100.0, places=6)
            for site_value, context_value in zip(site_bounds[2:], context_bounds[2:]):
                self.assertAlmostEqual(context_value - site_value, 100.0, places=6)


if __name__ == "__main__":
    unittest.main()
