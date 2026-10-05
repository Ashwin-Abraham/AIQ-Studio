"""One acyclic receiver graph for both drainage products."""

from collections import deque
from dataclasses import dataclass
import heapq
import math


@dataclass
class Drainage:
    receiver: list
    terminal: list
    terminals: dict
    accumulation: list
    flat_links: set


def route(terrain):
    """Choose steepest descending edges, then route exact flats to lower exits.

    Flat paths use shortest horizontal edge distance, with vertex-ID ties.
    Closed flats remain unresolved. No depression filling or Z changes occur.
    """
    points = terrain.vertices
    receiver = [None] * len(points)
    for a, adjacent in enumerate(terrain.neighbours):
        x, y, z = points[a]
        candidates = []
        for b in adjacent:
            bx, by, bz = points[b]
            if bz < z:
                gradient = (z - bz) / math.hypot(x - bx, y - by)
                candidates.append((-gradient, b))
        if candidates:
            receiver[a] = min(candidates)[1]

    flat_links, visited, terminal_roots, terminals = set(), set(), {}, {}
    for seed in range(len(points)):
        if seed in visited:
            continue
        plateau, queue = [], [seed]
        visited.add(seed)
        while queue:
            a = queue.pop()
            plateau.append(a)
            for b in terrain.neighbours[a]:
                if b not in visited and points[b][2] == points[a][2]:
                    visited.add(b)
                    queue.append(b)
        exits = sorted(a for a in plateau if receiver[a] is not None)
        if len(plateau) == 1 and exits:
            continue
        if not exits:
            root = min(plateau)
            kind = "unresolved_flat" if len(plateau) > 1 else (
                "boundary_exit" if root in terrain.boundary else "sink")
            terminals[root] = {"kind": kind, "vertices": sorted(plateau),
                               "point": points[root], "touches_boundary":
                               any(v in terrain.boundary for v in plateau)}
            terminal_roots.update((a, root) for a in plateau)
            continue
        # Multi-source Dijkstra stays on this level and never changes a lower exit.
        best = {a: (0.0, a) for a in exits}
        heap = [(0.0, a, a) for a in exits]
        heapq.heapify(heap)
        while heap:
            distance, exit_id, a = heapq.heappop(heap)
            if best.get(a) != (distance, exit_id):
                continue
            for b in terrain.neighbours[a]:
                if points[b][2] != points[a][2]:
                    continue
                step = math.hypot(points[b][0] - points[a][0],
                                  points[b][1] - points[a][1])
                candidate = (distance + step, exit_id)
                if candidate < best.get(b, (math.inf, math.inf)):
                    best[b] = candidate
                    receiver[b] = a
                    flat_links.add(b)
                    heapq.heappush(heap, (*candidate, b))

    # Topological order detects cycles and accumulates plan area in linear time.
    incoming = [0] * len(points)
    for b in receiver:
        if b is not None:
            incoming[b] += 1
    queue = deque(a for a, degree in enumerate(incoming) if degree == 0)
    order, accumulation = [], terrain.local_area.copy()
    while queue:
        a = queue.popleft()
        order.append(a)
        b = receiver[a]
        if b is not None:
            if points[b][2] > points[a][2]:
                raise ValueError("Drainage contains an uphill link.")
            accumulation[b] += accumulation[a]
            incoming[b] -= 1
            if incoming[b] == 0:
                queue.append(b)
    if len(order) != len(points):
        raise ValueError("Drainage contains a cycle.")
    terminal = [None] * len(points)
    for a in reversed(order):
        b = receiver[a]
        terminal[a] = terminal_roots[a] if b is None else terminal[b]
    for root, item in terminals.items():
        item["area_m2"] = math.fsum(accumulation[v] for v in item["vertices"])
    total = math.fsum(item["area_m2"] for item in terminals.values())
    if not math.isclose(total, math.fsum(terrain.local_area), rel_tol=1e-10, abs_tol=1e-8):
        raise ValueError("Drainage area balance failed.")
    return Drainage(receiver, terminal, terminals, accumulation, flat_links)
