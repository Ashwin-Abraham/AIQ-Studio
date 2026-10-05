"""Trace the shared graph into non-duplicated lines between junctions."""

import math


def trace_paths(terrain, drainage, min_area_m2=0.0, min_length_m=0.0):
    """Return connected XYZ paths, directed downstream, on terrain edges.

    Threshold only the display network, not watershed calculation. Each selected
    edge occurs once; split lines at confluences so common tails are not copied.
    """
    if not math.isfinite(min_area_m2) or min_area_m2 < 0:
        raise ValueError("Minimum contributing area must be finite and nonnegative.")
    if not math.isfinite(min_length_m) or min_length_m < 0:
        raise ValueError("Minimum branch length must be finite and nonnegative.")
    selected = {a for a, b in enumerate(drainage.receiver)
                if b is not None and drainage.accumulation[a] >= min_area_m2}
    incoming = [0] * len(terrain.vertices)
    for a in selected:
        incoming[drainage.receiver[a]] += 1
    paths = []
    for start in sorted(selected):
        if incoming[start] == 1:
            continue
        vertices, a = [start], start
        while a in selected:
            b = drainage.receiver[a]
            vertices.append(b)
            if incoming[b] != 1:
                break
            a = b
        paths.append({"id": f"flow-{start}", "vertex_ids": vertices,
                      "points": [terrain.vertices[v] for v in vertices],
                      "terminal_id": f"basin-{drainage.terminal[start]}",
                      "area_m2": [drainage.accumulation[v] for v in vertices],
                      "flat_steps": [i for i, v in enumerate(vertices[:-1])
                                     if v in drainage.flat_links]})
    for path in paths:
        path["length_m"] = math.fsum(math.dist(a[:2], b[:2])
                                    for a, b in zip(path["points"], path["points"][1:]))
    # Keep the downstream tails of retained branches, even when those tails are
    # short. Removing them would leave a visible line ending before its outlet.
    by_start = {path["vertex_ids"][0]: path for path in paths}
    keep = {path["id"] for path in paths if path["length_m"] >= min_length_m}
    for path in paths:
        if path["id"] not in keep:
            continue
        following = by_start.get(path["vertex_ids"][-1])
        while following and following["id"] not in keep:
            keep.add(following["id"])
            following = by_start.get(following["vertex_ids"][-1])
    return [path for path in paths if path["id"] in keep]
