import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import rhino3dm as r3d


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PATH = (
    REPO_ROOT
    / "plugins"
    / "aiq-site-tools"
    / "skills"
    / "rhino-site-data-model"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS_PATH))
from site_model import geometry as BUILDER

RUNNER_PATH = SCRIPTS_PATH / "run_site_model.py"


def face_normal(mesh, face_index):
    face = mesh.Faces[face_index]
    a = mesh.Vertices[face[0]]
    b = mesh.Vertices[face[1]]
    c = mesh.Vertices[face[2]]
    ab = (b.X - a.X, b.Y - a.Y, b.Z - a.Z)
    ac = (c.X - a.X, c.Y - a.Y, c.Z - a.Z)
    return (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )


def face_center(mesh, face_index):
    face = mesh.Faces[face_index]
    indices = list(face[:3]) if face[2] == face[3] else list(face)
    points = [mesh.Vertices[index] for index in indices]
    return (
        sum(point.X for point in points) / len(points),
        sum(point.Y for point in points) / len(points),
    )


class SiteMeshTests(unittest.TestCase):
    def setUp(self):
        # The source exterior is clockwise. The source hole is counter-clockwise.
        self.part = {
            "kind": "Polygon",
            "points": [[0, 0, 0], [0, 4, 0], [4, 4, 0], [4, 0, 0], [0, 0, 0]],
            "holes": [
                [[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], [1, 1, 0]]
            ],
        }

    def assert_wall_directions(self, mesh):
        outer_center = (2.0, 2.0)
        hole_center = (2.0, 2.0)
        for face_index in range(4):
            normal = face_normal(mesh, face_index)
            center = face_center(mesh, face_index)
            radial = (center[0] - outer_center[0], center[1] - outer_center[1])
            self.assertGreater(normal[0] * radial[0] + normal[1] * radial[1], 0)
        for face_index in range(4, 8):
            normal = face_normal(mesh, face_index)
            center = face_center(mesh, face_index)
            into_hole = (hole_center[0] - center[0], hole_center[1] - center[1])
            self.assertGreater(normal[0] * into_hole[0] + normal[1] * into_hole[1], 0)

    def test_building_and_skirt_use_normalized_rings_and_store_normals(self):
        mass = BUILDER.flat_mass(self.part, 0.0, 5.0)
        self.assert_wall_directions(mass)
        self.assertEqual(len(mass.Normals), len(mass.Vertices))

        sampler = BUILDER.TerrainSampler(
            {"rows": [[[0, 0, 0], [4, 0, 1]], [[0, 4, 2], [4, 4, 3]]]}
        )
        skirt = BUILDER.terrain_skirt(self.part, 3.0, sampler)
        self.assert_wall_directions(skirt)
        self.assertEqual(len(skirt.Normals), len(skirt.Vertices))

    def test_terrain_mesh_stores_normals(self):
        sampler = BUILDER.TerrainSampler(
            {"rows": [[[0, 0, 0], [1, 0, 0]], [[0, 1, 0], [1, 1, 0]]]}
        )
        mesh = sampler.mesh()
        self.assertEqual(len(mesh.Normals), len(mesh.Vertices))

    def test_written_model_renders_backfaces(self):
        data = {
            "run": {
                "site_name": "Backface test",
                "generated_utc": "2026-09-12T00:00:00Z",
                "semantic_source": "test",
                "source_release": "test",
                "projected_crs": "EPSG:32749",
                "origin_wgs84": [110.5, -6.9],
                "origin_projected": [0, 0],
                "vertical_datum": "test",
                "source_manifest_path": "test-manifest.json",
                "report_path": "test-report.md",
            },
            "site": {"parts": [self.part]},
            "context": {"parts": [self.part], "bounds_local": [0, 0, 4, 4]},
            "features": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "output.3dm"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            subprocess.run(
                [sys.executable, "-B", str(RUNNER_PATH), "--project-root", directory,
                 "--input", str(input_path), "--output", str(output_path),
                 "--backend", "file", "--stage", "all", "--flat-elevation", "0"],
                check=True,
                capture_output=True,
                text=True,
            )
            model = r3d.File3dm.Read(str(output_path))
            self.assertTrue(model.Settings.RenderSettings.RenderBackFaces)
            self.assertEqual(model.Strings["site.render_backfaces"], "true")


if __name__ == "__main__":
    unittest.main()
