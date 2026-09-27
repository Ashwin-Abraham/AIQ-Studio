"""Central Overture type policy for acquisition, normalization, and Rhino output.

This module uses only the Python standard library so every pipeline stage can
use the same type rules without loading geometry or Rhino libraries.
"""

from dataclasses import dataclass


def clean(value):
    value = str(value or "Other Unclassified").replace("-", " ").replace("_", " ").replace("::", " ")
    return " ".join(part.capitalize() for part in value.split())


@dataclass(frozen=True)
class FeatureProfile:
    source_geometry: frozenset
    normalized_geometry: frozenset
    polygon_plan: str = "outline"
    three_d: str = "drape"


_POLYGON = frozenset(("Polygon", "MultiPolygon"))
_LINE = frozenset(("LineString", "MultiLineString"))
_POINT = frozenset(("Point", "MultiPoint"))
PROFILES = {
    "building": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "building"),
    "building_part": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "building"),
    "segment": FeatureProfile(_LINE, frozenset(("LineString",)), "outline", "drape"),
    "water": FeatureProfile(_POLYGON | _LINE, frozenset(("Polygon", "LineString")), "fill", "drape"),
    "land": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "drape"),
    "land_use": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "drape"),
    "place": FeatureProfile(_POINT, frozenset(("Point",)), "outline", "drape"),
    "bathymetry": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "omit"),
    "infrastructure": FeatureProfile(frozenset(("Point", "LineString", "Polygon", "MultiPolygon")), frozenset(("Point", "LineString", "Polygon")), "fill", "unresolved"),
    "land_cover": FeatureProfile(_POLYGON, frozenset(("Polygon",)), "fill", "omit"),
}

SUPPORTED_FEATURE_TYPES = tuple(PROFILES)
LAND_COVER_SUBTYPES = frozenset((
    "barren", "crop", "forest", "grass", "mangrove", "moss", "shrub", "snow", "urban", "wetland",
))


def profile(feature_type):
    try:
        return PROFILES[feature_type]
    except KeyError as error:
        raise ValueError("Unsupported feature type; use: " + ", ".join(SUPPORTED_FEATURE_TYPES)) from error


def validate_types(feature_types):
    if not feature_types or len(set(feature_types)) != len(feature_types):
        raise ValueError("Choose one or more distinct feature types")
    for feature_type in feature_types:
        profile(feature_type)
    return list(feature_types)


def validate_source_geometry(feature_type, geometry_type):
    if geometry_type not in profile(feature_type).source_geometry:
        raise ValueError("{} does not accept {} geometry".format(feature_type, geometry_type))


def validate_normalized_geometry(feature_type, geometry_kind):
    if geometry_kind not in profile(feature_type).normalized_geometry:
        raise ValueError("{} does not accept normalized {} geometry".format(feature_type, geometry_kind))


def validate_properties(feature_type, properties):
    if not isinstance(properties, dict):
        raise ValueError(feature_type + " properties must be an object")
    if feature_type == "bathymetry":
        depth = properties.get("depth")
        if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
            raise ValueError("bathymetry.depth must be a non-negative integer")
    elif feature_type == "land_cover":
        subtype = properties.get("subtype")
        if subtype not in LAND_COVER_SUBTYPES:
            raise ValueError("land_cover.subtype must be one of: " + ", ".join(sorted(LAND_COVER_SUBTYPES)))
    elif feature_type == "infrastructure":
        for name in ("subtype", "class"):
            value = properties.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("infrastructure.{} must be a nonempty string".format(name))
    return properties


def category_path(feature_type, properties):
    validate_properties(feature_type, properties)
    subtype = properties.get("subtype")
    class_name = properties.get("class")
    if feature_type == "building":
        return ["Buildings", "Footprints", clean(class_name or subtype)]
    if feature_type == "building_part":
        return ["Buildings", "Parts", clean(class_name or subtype)]
    if feature_type == "segment":
        if subtype == "road":
            return ["Transport", "Roads", clean(class_name)]
        if subtype == "rail":
            return ["Transport", "Railway", clean(class_name)]
        return ["Transport", "Water Routes", clean(class_name or subtype)]
    if feature_type == "water":
        return ["Water", clean(subtype), clean(class_name)]
    if feature_type == "land_use":
        return ["Land Use", clean(subtype), clean(class_name)]
    if feature_type == "land":
        return ["Base", "Land", clean(class_name or subtype)]
    if feature_type == "place":
        hierarchy = ((properties.get("taxonomy") or {}).get("hierarchy") or [])
        return ["Places", clean(hierarchy[0] if hierarchy else "Other")]
    if feature_type == "bathymetry":
        return ["Bathymetry", "Depth {} m".format(properties["depth"])]
    if feature_type == "infrastructure":
        return ["Infrastructure", clean(subtype), clean(class_name)]
    if feature_type == "land_cover":
        return ["Land Cover", clean(subtype)]
    raise ValueError("Unsupported feature type: " + feature_type)


def plan_representation(feature_type, geometry_kind):
    item = profile(feature_type)
    validate_normalized_geometry(feature_type, geometry_kind)
    return "fill" if geometry_kind == "Polygon" and item.polygon_plan == "fill" else geometry_kind.lower()


def three_d_policy(feature_type):
    return profile(feature_type).three_d
