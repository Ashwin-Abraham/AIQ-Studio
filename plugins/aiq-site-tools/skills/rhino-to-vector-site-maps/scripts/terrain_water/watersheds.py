"""Partition each triangle into three vertex catchment cells."""

from collections import defaultdict
import math

from shapely.geometry import Polygon, mapping
from shapely import union_all


PALETTE = ["#DCEEF8", "#B5D9EA", "#CFD5EF", "#BDE4DE",
           "#A8C6DC", "#DCD6EC", "#CDE9ED", "#B7D3C9"]


def midpoint(a, b):
    return tuple((a[k] + b[k]) / 2 for k in range(3))


def choose_colour(used):
    for colour in PALETTE:
        if colour not in used:
            return colour
    # Extend the pale blue palette if a high-degree basin uses every default.
    for red in range(170, 221, 5):
        for green in range(190, 236, 5):
            colour = f"#{red:02X}{green:02X}F0"
            if colour not in used:
                return colour
    raise ValueError("Too many adjacent basins for this palette; use a project palette.")


def delineate(terrain, drainage):
    """Return XYZ cells for Rhino and dissolved XY polygons for SVG.

    Each vertex owns one third of each incident triangle's plan area. A cell
    follows that vertex's terminal. This is a mesh-resolution approximation.
    """
    cells, polygons, adjacency = [], defaultdict(list), defaultdict(set)
    for index, triangle in enumerate(terrain.triangles):
        points = [terrain.vertices[v] for v in triangle]
        centre = tuple(sum(p[k] for p in points) / 3 for k in range(3))
        roots = [drainage.terminal[v] for v in triangle]
        for root in roots:
            adjacency[root].update(other for other in roots if other != root)
        for i, vertex in enumerate(triangle):
            a, b, c = points[i], points[(i + 1) % 3], points[(i + 2) % 3]
            ring = [a, midpoint(a, b), centre, midpoint(c, a)]
            root = drainage.terminal[vertex]
            cells.append({"id": f"cell-{index}-{i}", "source_face": terrain.source_faces[index],
                          "vertex_id": vertex, "terminal_id": f"basin-{root}", "points": ring})
            polygons[root].append(Polygon([p[:2] for p in ring]))

    # Colour adjacent basins differently; IDs and outlines also distinguish them.
    colours = {}
    for root in sorted(polygons, key=lambda r: (-len(adjacency[r]), r)):
        used = {colours[n] for n in adjacency[root] if n in colours}
        colours[root] = choose_colour(used)
    basins = []
    for root in sorted(polygons):
        # A sub-micrometre overlay grid avoids cracks from midpoint round-off.
        shape = union_all(polygons[root], grid_size=1e-8)
        terminal = drainage.terminals[root]
        if not math.isclose(shape.area, terminal["area_m2"], rel_tol=1e-7, abs_tol=1e-6):
            raise ValueError("Watershed area does not match its drainage terminal.")
        basins.append({"id": f"basin-{root}", **terminal, "colour": colours[root],
                       "geometry": mapping(shape)})
    return {"basins": basins, "cells": cells}
