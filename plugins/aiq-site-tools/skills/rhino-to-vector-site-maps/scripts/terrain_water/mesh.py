"""Validate a single-valued terrain and build its edge graph."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import math

from shapely.geometry import Polygon
from shapely.ops import unary_union


@dataclass
class Terrain:
    vertices: list
    triangles: list
    source_faces: list
    neighbours: list
    boundary: set
    local_area: list
    footprint: object


def prepare_mesh(vertices, faces):
    """Accept indexed XYZ metres. Preserve holes; split quads along A-C.

    Reject duplicate XY vertices, unused vertices, overlaps, vertical faces,
    and non-manifold edges or vertex fans. Callers must weld seams first.
    """
    if not vertices or not faces:
        raise ValueError("Terrain needs vertices and faces.")
    points = []
    for point in vertices:
        if len(point) != 3 or any(isinstance(v, bool) for v in point):
            raise ValueError("Each vertex needs three finite coordinates.")
        xyz = tuple(float(v) for v in point)
        if not all(math.isfinite(v) for v in xyz):
            raise ValueError("Terrain coordinates must be finite.")
        points.append(xyz)
    if len({p[:2] for p in points}) != len(points):
        raise ValueError("Duplicate XY vertices: weld seams or resolve stacked surfaces.")

    triangles, source_faces, polygons = [], [], []
    edges = Counter()
    fans = defaultdict(list)
    neighbours = [set() for _ in points]
    local_area = [0.0] * len(points)
    for source, face in enumerate(faces):
        if len(face) not in (3, 4) or len(set(face)) != len(face):
            raise ValueError("Faces must contain three or four distinct vertex indices.")
        if any(type(i) is not int or not 0 <= i < len(points) for i in face):
            raise ValueError("Face vertex index is invalid.")
        parts = [tuple(face[:3])]
        if len(face) == 4:
            parts.append((face[0], face[2], face[3]))
        for triangle in parts:
            polygon = Polygon([points[i][:2] for i in triangle])
            if not polygon.is_valid or not math.isfinite(polygon.area) or polygon.area <= 0:
                raise ValueError("Terrain contains a face with zero or invalid plan area.")
            polygons.append(polygon)
            triangles.append(triangle)
            source_faces.append(source)
            for i, a in enumerate(triangle):
                b, c = triangle[(i + 1) % 3], triangle[(i + 2) % 3]
                edges[tuple(sorted((a, b)))] += 1
                neighbours[a].update((b, c))
                fans[a].append((b, c))
                local_area[a] += polygon.area / 3
    if any(count > 2 for count in edges.values()):
        raise ValueError("Terrain has a non-manifold edge.")
    if any(not links for links in neighbours):
        raise ValueError("Terrain contains unused vertices.")
    for pairs in fans.values():
        links = defaultdict(set)
        for a, b in pairs:
            links[a].add(b)
            links[b].add(a)
        seen, queue = set(), [next(iter(links))]
        while queue:
            vertex = queue.pop()
            if vertex not in seen:
                seen.add(vertex)
                queue.extend(links[vertex] - seen)
        if len(seen) != len(links) or any(len(v) > 2 for v in links.values()):
            raise ValueError("Terrain has a disconnected or non-manifold vertex fan.")
    footprint = unary_union(polygons)
    area = math.fsum(p.area for p in polygons)
    if area - footprint.area > max(1e-8, area * 1e-10):
        raise ValueError("Terrain faces overlap in plan. Select one ground surface.")
    boundary = {v for edge, count in edges.items() if count == 1 for v in edge}
    return Terrain(points, triangles, source_faces,
                   [sorted(v) for v in neighbours], boundary, local_area, footprint)
