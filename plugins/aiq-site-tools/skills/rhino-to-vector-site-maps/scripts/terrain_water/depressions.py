"""Conservative, bounded filling on a separate elevation copy."""

from dataclasses import replace
import heapq
import math


def fill_small_depressions(terrain, drainage, max_area_m2=0.0, max_depth_m=0.0):
    """Priority-flood from data edges and protected large catchments.

    Accept a whole connected raised component only when both limits pass.
    Area is the sum of its original contributing catchments, not its wet area.
    A rejected component remains unchanged. This is one pass, so repeated small
    fills cannot silently exceed the depth or combined-catchment area limit.
    """
    if any(not math.isfinite(v) or v < 0 for v in (max_area_m2, max_depth_m)):
        raise ValueError("Fill limits must be finite and nonnegative.")
    original = [p[2] for p in terrain.vertices]
    audit = {"max_catchment_area_m2": max_area_m2, "max_depth_m": max_depth_m,
             "method": "one-pass priority flood; large catchments and data edges protected",
             "accepted": [], "rejected_components": 0, "changed_vertices": 0}
    if not max_area_m2 or not max_depth_m:
        return terrain, audit
    seeds = set(terrain.boundary)
    seeds.update(i for i, root in enumerate(drainage.terminal)
                 if drainage.terminals[root]["area_m2"] > max_area_m2)
    levels = [math.inf] * len(original)
    heap = []
    for i in sorted(seeds):
        levels[i] = original[i]
        heap.append((levels[i], i))
    heapq.heapify(heap)
    while heap:
        level, a = heapq.heappop(heap)
        if level != levels[a]:
            continue
        for b in terrain.neighbours[a]:
            candidate = max(level, original[b])
            if candidate < levels[b]:
                levels[b] = candidate
                heapq.heappush(heap, (candidate, b))
    if any(not math.isfinite(v) for v in levels):
        raise ValueError("A terrain component has no drainage boundary.")
    pending = {i for i in range(len(original)) if levels[i] > original[i]}
    effective = original.copy()
    while pending:
        start = min(pending)
        pending.remove(start)
        component, queue = [], [start]
        while queue:
            a = queue.pop()
            component.append(a)
            for b in terrain.neighbours[a]:
                if b in pending:
                    pending.remove(b)
                    queue.append(b)
        roots = sorted({drainage.terminal[v] for v in component})
        area = math.fsum(drainage.terminals[root]["area_m2"] for root in roots)
        depth = max(levels[v] - original[v] for v in component)
        if area > max_area_m2 or depth > max_depth_m:
            audit["rejected_components"] += 1
            continue
        for v in component:
            effective[v] = levels[v]
        audit["accepted"].append({"vertices": sorted(component), "source_terminals": roots,
                                  "catchment_area_m2": area, "max_depth_m": depth,
                                  "fill_volume_m3": math.fsum((levels[v]-original[v])*terrain.local_area[v]
                                                              for v in component)})
        audit["changed_vertices"] += len(component)
    return replace(terrain, vertices=[(p[0], p[1], effective[i])
                                      for i, p in enumerate(terrain.vertices)]), audit
