"""Executable Rhino cartographic styles and semantic draw-order rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerStyle:
    color: tuple
    plot_weight_mm: float
    display_order: int


def _style(rgb, weight, order):
    return LayerStyle(tuple(rgb) + (255,), float(weight), int(order))


_LAND_COVER = {
    "grass": (181, 211, 170), "forest": (117, 169, 116), "mangrove": (91, 151, 121),
    "shrub": (157, 190, 143), "wetland": (161, 199, 189), "barren": (218, 204, 171),
    "crop": (224, 222, 178), "moss": (190, 205, 170), "snow": (232, 239, 242),
    "urban": (214, 214, 209),
}
_LAND_USE = {
    "residential": (238, 231, 205), "commercial": (238, 215, 187),
    "industrial": (211, 207, 197), "institutional": (222, 214, 231),
    "recreation": (207, 226, 198), "agriculture": (224, 222, 178),
    "transport": (216, 218, 218), "construction": (224, 207, 185),
}
_BUILDING = {
    "residential": ((201, 188, 111), .18), "commercial": ((227, 191, 139), .18),
    "retail": ((227, 191, 139), .18), "office": ((217, 199, 175), .18),
    "industrial": ((154, 149, 135), .20), "warehouse": ((154, 149, 135), .20),
    "education": ((177, 160, 198), .20), "healthcare": ((208, 160, 170), .20),
    "medical": ((208, 160, 170), .20), "hospital": ((208, 160, 170), .20),
    "civic": ((209, 170, 127), .20), "public": ((209, 170, 127), .20),
    "religious": ((188, 163, 198), .20), "hotel": ((200, 181, 205), .18),
    "transportation": ((134, 160, 181), .25), "service": ((185, 185, 178), .13),
    "mixed": ((181, 158, 132), .20),
}
_ROAD = {
    "motorway": ((69, 44, 32), .70, 99), "trunk": ((69, 44, 32), .70, 98),
    "primary": ((104, 69, 47), .50, 90), "secondary": ((137, 103, 60), .35, 80),
    "tertiary": ((153, 133, 76), .25, 70), "local": ((167, 155, 106), .18, 60),
    "residential": ((167, 155, 106), .18, 60), "service": ((184, 178, 151), .13, 50),
}


def style_for(record=None, role=None, boundary=None):
    """Return one style. Larger display-order values draw above smaller values."""
    if boundary == "site":
        return _style((126, 53, 45), .50, 101000)
    if boundary == "context":
        return _style((150, 150, 145), .18, 100000)
    if role == "run_annotation" or role == "vertical_position_unresolved":
        return _style((173, 43, 148), .35, 110000)
    if not record:
        return _style((120, 120, 120), .18, 0)
    kind = record.get("feature_type")
    properties = record.get("properties") or {}
    subtype = str(properties.get("subtype") or "").lower()
    class_name = str(properties.get("class") or "").lower()
    if kind == "bathymetry":
        depth = min(int(properties.get("depth", 0)), 9999)
        shade = max(65, 205 - min(depth, 140))
        return _style((95, 155, shade), .13, 10000 + depth)
    if kind == "land":
        return _style((232, 229, 218), .13, 30000)
    if kind == "land_cover":
        return _style(_LAND_COVER.get(subtype, (232, 232, 228)), .13, 40000)
    if kind == "land_use":
        key = subtype if subtype in _LAND_USE else class_name
        return _style(_LAND_USE.get(key, (232, 232, 228)), .13, 50000)
    if kind == "water":
        return _style((177, 205, 226), .18, 60000)
    if kind in ("building", "building_part"):
        key = class_name if class_name in _BUILDING else subtype
        rgb, weight = _BUILDING.get(key, ((135, 135, 132), .18))
        return _style(rgb, weight, 70000)
    if kind == "segment":
        if subtype == "rail":
            major = class_name in ("rail", "main", "high_speed")
            return _style((70, 48, 32) if major else (118, 92, 68), .50 if major else .25, 81000 if major else 80500)
        rgb, weight, rank = _ROAD.get(class_name, ((111, 128, 105), .13, 10))
        return _style(rgb, weight, 80000 + rank)
    if kind == "infrastructure":
        return _style((96, 105, 112), .25, 90000)
    if kind == "place":
        return _style((220, 80, 140), .18, 95000)
    return _style((135, 135, 132), .18, 0)
