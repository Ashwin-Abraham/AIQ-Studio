"""Small analytical terrains and CLI round trips; no live Rhino is needed."""

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from shapely.geometry import shape
from shapely.ops import unary_union

SCRIPTS = Path(__file__).resolve().parents[2] / "plugins/aiq-site-tools/skills/rhino-to-vector-site-maps/scripts"
sys.path.insert(0, str(SCRIPTS))

from analyze_water_flow import analyze
from terrain_water.files import publish, read_input
from terrain_water.flow import trace_paths
from terrain_water.mesh import prepare_mesh
from terrain_water.routing import route
from terrain_water.depressions import fill_small_depressions
from terrain_water.watersheds import delineate


def grid(size, elevation, omit=()):
    points = [(x, y, elevation(x, y)) for y in range(size) for x in range(size)]
    faces = []
    for y in range(size - 1):
        for x in range(size - 1):
            if (x, y) not in omit:
                a = y * size + x
                faces.append([a, a + 1, a + size + 1, a + size])
    used = sorted({v for face in faces for v in face})
    remap = {v: i for i, v in enumerate(used)}
    return [points[v] for v in used], [[remap[v] for v in face] for face in faces]


class DrainageTests(unittest.TestCase):
    def solve(self, elevation, size=5, omit=()):
        mesh = prepare_mesh(*grid(size, elevation, omit))
        return mesh, route(mesh)

    def test_plane_flows_downhill_and_conserves_area(self):
        mesh, drainage = self.solve(lambda x, y: -x - 0.25 * y)
        self.assertEqual(len(drainage.terminals), 1)
        self.assertAlmostEqual(next(iter(drainage.terminals.values()))["area_m2"], 16)
        for a, b in enumerate(drainage.receiver):
            if b is not None:
                self.assertIn(b, mesh.neighbours[a])
                self.assertLess(mesh.vertices[b][2], mesh.vertices[a][2])
        paths = trace_paths(mesh, drainage)
        edges = [(a, b) for p in paths for a, b in zip(p["vertex_ids"], p["vertex_ids"][1:])]
        expected = [(a, b) for a, b in enumerate(drainage.receiver) if b is not None]
        self.assertCountEqual(edges, expected)
        self.assertEqual(len(edges), len(set(edges)))

    def test_ridge_separates_two_watersheds(self):
        mesh, drainage = self.solve(lambda x, y: -abs(x - 2) - 0.1 * y)
        self.assertEqual(len(drainage.terminals), 2)
        basins = delineate(mesh, drainage)["basins"]
        self.assertEqual(len({b["colour"] for b in basins}), 2)
        polygons = [shape(b["geometry"]) for b in basins]
        self.assertAlmostEqual(sum(p.area for p in polygons), 16)
        self.assertLess(polygons[0].intersection(polygons[1]).area, 1e-8)

    def test_depression_stops_at_interior_sink(self):
        mesh, drainage = self.solve(lambda x, y: (x - 2)**2 + (y - 2)**2)
        self.assertEqual(drainage.receiver[12], None)
        self.assertEqual(drainage.terminals[12]["kind"], "sink")
        self.assertTrue(all(root == 12 for root in drainage.terminal))
        self.assertEqual(mesh.vertices[12][2], 0)

    def test_flat_without_lower_exit_is_unresolved(self):
        mesh, drainage = self.solve(lambda x, y: 0)
        self.assertTrue(all(v is None for v in drainage.receiver))
        self.assertEqual(drainage.terminals[0]["kind"], "unresolved_flat")
        self.assertEqual(trace_paths(mesh, drainage), [])
        self.assertAlmostEqual(drainage.terminals[0]["area_m2"], 16)
        self.assertEqual(len(delineate(mesh, drainage)["basins"]), 1)

    def test_flat_with_lower_exit_routes_without_cycles_or_uphill_steps(self):
        mesh, drainage = self.solve(lambda x, y: -1 if (x, y) == (4, 4) else 0)
        self.assertTrue(drainage.flat_links)
        self.assertTrue(all(root == 24 for root in drainage.terminal))
        for a, b in enumerate(drainage.receiver):
            if b is not None:
                self.assertLessEqual(mesh.vertices[b][2], mesh.vertices[a][2])

    def test_hole_remains_open_and_flow_does_not_cross_it(self):
        mesh, drainage = self.solve(lambda x, y: -x - y, omit=((1, 1),))
        basins = delineate(mesh, drainage)
        union = unary_union([shape(b["geometry"]) for b in basins["basins"]])
        self.assertAlmostEqual(union.area, 15)
        self.assertLess(union.symmetric_difference(mesh.footprint).area, 1e-6)
        for path in trace_paths(mesh, drainage):
            for a, b in zip(path["vertex_ids"], path["vertex_ids"][1:]):
                self.assertIn(b, mesh.neighbours[a])

    def test_threshold_changes_paths_not_watersheds(self):
        mesh, drainage = self.solve(lambda x, y: -x - y)
        before = delineate(mesh, drainage)
        self.assertEqual(trace_paths(mesh, drainage, 1e6), [])
        self.assertEqual(delineate(mesh, drainage), before)
        for bad in (-1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                trace_paths(mesh, drainage, bad)

    def test_shallow_depression_merges_without_changing_source(self):
        mesh, initial = self.solve(lambda x, y: -.05*x-.01*y-(.2 if (x,y)==(2,2) else 0), size=7)
        old_vertices = mesh.vertices.copy()
        filled, audit = fill_small_depressions(mesh, initial, 100, .3)
        self.assertGreater(audit['changed_vertices'], 0)
        self.assertLess(len(route(filled).terminals), len(initial.terminals))
        self.assertEqual(mesh.vertices, old_vertices)
        self.assertTrue(all(0 <= b[2]-a[2] <= .3 for a,b in zip(mesh.vertices,filled.vertices)))
        self.assertAlmostEqual(sum(t['area_m2'] for t in route(filled).terminals.values()),36)

    def test_deep_or_large_depressions_stay_unchanged(self):
        mesh, initial = self.solve(lambda x,y: -.05*x-.01*y-(2 if (x,y)==(2,2) else 0),size=7)
        for area,depth in [(100,.3),(.1,10),(0,10),(100,0)]:
            with self.subTest(area=area,depth=depth):
                filled,audit=fill_small_depressions(mesh,initial,area,depth)
                self.assertEqual(filled.vertices,mesh.vertices)
                self.assertEqual(audit['changed_vertices'],0)

    def test_length_filter_keeps_downstream_connection(self):
        from types import SimpleNamespace
        mesh=SimpleNamespace(vertices=[(0,0,2),(2,10,2),(2,0,1),(3,0,0)])
        drainage=SimpleNamespace(receiver=[2,2,3,None], accumulation=[1,1,3,4],
                                 terminal=[3,3,3,3],flat_links=set())
        paths=trace_paths(mesh,drainage,min_length_m=5)
        self.assertEqual([p['vertex_ids'] for p in paths],[[1,2],[2,3]])
        self.assertEqual(drainage.receiver,[2,2,3,None])
        self.assertEqual(trace_paths(mesh,drainage,min_length_m=50),[])

    def test_fill_and_length_limits_reject_invalid_values(self):
        mesh,drainage=self.solve(lambda x,y:-x-y)
        for value in (-1,math.inf,math.nan):
            with self.assertRaises(ValueError):fill_small_depressions(mesh,drainage,value,1)
            with self.assertRaises(ValueError):fill_small_depressions(mesh,drainage,1,value)
            with self.assertRaises(ValueError):trace_paths(mesh,drainage,min_length_m=value)

    def test_reversed_faces_give_same_routes(self):
        points, faces = grid(4, lambda x, y: -x - y)
        first = route(prepare_mesh(points, faces))
        # Preserve A-C diagonals while reversing winding.
        second = route(prepare_mesh(points, [[f[0], f[3], f[2], f[1]] for f in faces]))
        self.assertEqual(first.receiver, second.receiver)
        self.assertEqual(first.terminal, second.terminal)

    def test_steepest_edge_uses_horizontal_distance_not_only_height_drop(self):
        mesh = prepare_mesh([(0, 0, 5), (1, 0, 4), (0, 10, 0)], [[0, 1, 2]])
        self.assertEqual(route(mesh).receiver[0], 1)

    def test_equal_slopes_use_stable_vertex_id(self):
        mesh = prepare_mesh([(0, 0, 2), (1, 0, 1), (0, 1, 1)], [[0, 1, 2]])
        self.assertEqual(route(mesh).receiver[0], 1)

    def test_repeat_is_deterministic(self):
        mesh, drainage = self.solve(lambda x, y: -abs(x - 2))
        other = route(mesh)
        self.assertEqual(drainage, other)
        self.assertEqual(delineate(mesh, drainage), delineate(mesh, other))

    def test_disconnected_islands_keep_separate_outlets(self):
        points = [(0, 0, 2), (1, 0, 1), (0, 1, 0), (5, 0, 2), (6, 0, 1), (5, 1, 0)]
        mesh = prepare_mesh(points, [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(len(route(mesh).terminals), 2)

    def test_bad_meshes_are_rejected(self):
        cases = [
            ([], []),
            ([(0, 0, 0), (1, 0, 0), (0, 1, math.nan)], [[0, 1, 2]]),
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [[0, 1, 4]]),
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [[0, 1, 1]]),
            ([(0, 0, 0), (1, 0, 0), (2, 0, 0)], [[0, 1, 2]]),
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [[0, 1, 2], [0, 1, 2]]),
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 2)], [[0, 1, 2], [3, 1, 2]]),
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0), (2, 2, 0)], [[0, 1, 2]]),
            # Three faces share one edge.
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (.5, 1, 0)],
             [[0, 1, 2], [1, 0, 3], [0, 1, 4]]),
            # Disconnected triangles overlap in XY without duplicate vertices.
            ([(0, 0, 0), (2, 0, 0), (0, 2, 0), (.1, .1, 1), (1, .1, 1), (.1, 1, 1)],
             [[0, 1, 2], [3, 4, 5]]),
            # Two patches touch only at a vertex: invalid terrain connectivity.
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0)], [[0, 1, 2], [0, 3, 4]]),
        ]
        for points, faces in cases:
            with self.subTest(points=points, faces=faces), self.assertRaises(ValueError):
                prepare_mesh(points, faces)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        points, faces = grid(3, lambda x, y: -x - y)
        self.data = {"units": "metres", "metadata": {"crs": "EPSG:27700"},
                     "vertices": points, "faces": faces}
        self.input = self.root / "mesh.json"
        self.input.write_text(json.dumps(self.data))

    def test_cli_round_trip_and_no_python_cache(self):
        command = [sys.executable, "-B", str(SCRIPTS / "analyze_water_flow.py"),
                   "--input", str(self.input), "--output", str(self.root / "run"),
                   "--min-area-m2", "0"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "complete")
        self.assertGreater(report["flow_paths"], 0)
        self.assertEqual(report["watersheds"], 1)
        self.assertEqual(set(p.name for p in (self.root / "run").iterdir()), set(report["outputs"]))
        self.assertFalse(list(self.root.rglob("__pycache__")))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_products_can_run_separately(self):
        for product, wanted, absent in [("flow", "flow-paths.json", "watersheds.json"),
                                         ("watersheds", "watersheds.json", "flow-paths.json")]:
            target = self.root / product
            analyze(self.input, target, product=product, min_area_m2=0)
            self.assertTrue((target / wanted).exists())
            self.assertFalse((target / absent).exists())

    def test_no_terrain_is_an_explicit_skip(self):
        self.data.update(vertices=[], faces=[])
        self.input.write_text(json.dumps(self.data))
        report = analyze(self.input, self.root / "run")
        self.assertEqual(report["reason"], "no terrain")
        self.assertEqual([p.name for p in (self.root / "run").iterdir()], ["run.json"])

    def test_invalid_input_leaves_no_output(self):
        self.data["units"] = "feet"
        self.input.write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):
            analyze(self.input, self.root / "run")
        self.assertFalse((self.root / "run").exists())

    def test_failed_second_product_does_not_publish_first_product(self):
        with patch("analyze_water_flow.delineate", side_effect=ValueError("area check failed")):
            with self.assertRaises(ValueError):
                analyze(self.input, self.root / "run", min_area_m2=0)
        self.assertFalse((self.root / "run").exists())

    def test_bad_metadata_or_source_mapping_is_rejected(self):
        for field, value in [("metadata", {}), ("source_faces", [])]:
            with self.subTest(field=field):
                data = {**self.data, field: value}
                self.input.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    analyze(self.input, self.root / "run")

    def test_partial_write_is_removed_and_paths_cannot_escape(self):
        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                publish(self.root / "run", {"run.json": {}})
        self.assertEqual(list(self.root.iterdir()), [self.input])
        with self.assertRaises(ValueError):
            publish(self.root / "run", {"../escape.json": {}})
        self.assertFalse((self.root / "escape.json").exists())

    def test_rhino_reader_includes_hidden_mesh_and_source_ids(self):
        import rhino3dm as r
        model = r.File3dm()
        model.Settings.ModelUnitSystem = r.UnitSystem.Meters
        model.Strings["site.projected_crs"] = "EPSG:27700"
        layer = r.Layer()
        layer.Name = "Terrain"
        layer.Visible = False
        index = model.Layers.Add(layer)
        mesh = r.Mesh()
        for point in self.data["vertices"]:
            mesh.Vertices.Add(*point)
        for face in self.data["faces"]:
            mesh.Faces.AddFace(*face)
        attrs = r.ObjectAttributes()
        attrs.LayerIndex = index
        object_id = model.Objects.AddMesh(mesh, attrs)
        path = self.root / "terrain.3dm"
        self.assertTrue(model.Write(str(path), 8))
        points, faces, sources, record = read_input(path, "Terrain")
        self.assertEqual(len(points), 9)
        self.assertEqual(len(faces), 4)
        self.assertEqual(sources[0]["object_id"], str(object_id))
        self.assertEqual(record["metadata"]["crs"], "EPSG:27700")
        self.assertEqual(read_input(path, "Absent")[0], [])


if __name__ == "__main__":
    unittest.main()
