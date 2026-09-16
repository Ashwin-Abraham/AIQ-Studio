"""Stage-aware checks for saved site models. User objects are not site outputs."""

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import rhino3dm as r3d

OWNER = "rhino-site-data-model"
DOCUMENT_KEYS = ("site.name", "site.source_release", "site.projected_crs",
                 "site.origin_wgs84", "site.origin_projected", "site.vertical_datum")
SOURCE_KEYS = ("source_feature_id", "source_feature_type", "source_feature_version",
               "source_properties_json", "source_records_json")


def audit_model(model, stage, visual_inspection="not-possible", visual_notes=""):
    """Check generated geometry. A 3D audit also checks retained 2D geometry.

    ``passed`` describes these programmatic checks only. Visual inspection has
    a separate status. Source count reconciliation belongs to the stage writer,
    which has the input manifest; it cannot be inferred from a model alone.
    """
    if stage not in {"2d", "3d"}:
        raise ValueError("stage must be 2d or 3d")
    if visual_inspection not in {"passed", "failed", "not-possible"}:
        raise ValueError("Invalid visual inspection status")
    failures, warnings = [], []

    def fail(check, **details):
        failures.append({"check": check, **details})

    objects, layers = list(model.Objects), list(model.Layers)
    layers_by_index = {layer.Index: layer for layer in layers}
    owned = []
    for obj in objects:
        attrs = obj.Attributes
        owner = attrs.GetUserString("site_owner")
        if owner == OWNER:
            owned.append(obj)
        elif not owner and (attrs.GetUserString("site_key") or attrs.GetUserString("site_stage")):
            fail("ownership_metadata", object_id=str(attrs.Id), message="Site output has no owner")
    roles = Counter(obj.Attributes.GetUserString("geometry_role") or "missing" for obj in owned)
    keys = Counter()
    invalid_count = 0
    volumes = []
    sources = []
    for obj in owned:
        attrs, geometry = obj.Attributes, obj.Geometry
        object_id = str(attrs.Id)
        role = attrs.GetUserString("geometry_role")
        obj_stage = attrs.GetUserString("site_stage")
        key = attrs.GetUserString("site_key")
        if not key or not role or obj_stage not in {"2d", "3d"}:
            fail("ownership_metadata", object_id=object_id,
                 message="Owned output needs site_key, site_stage, and geometry_role")
        if key:
            keys[key] += 1
        if obj_stage == "3d" and stage == "2d":
            fail("stage_scope", object_id=object_id, message="2D checkpoint contains owned 3D geometry")
        if role and role.startswith("source_plan") and obj_stage != "2d":
            fail("stage_metadata", object_id=object_id, message="Source plan must belong to 2D")
        if role and (role.startswith("terrain_") or role.startswith("building_")) and obj_stage != "3d":
            fail("stage_metadata", object_id=object_id, message="3D geometry must belong to 3D")
        if not geometry.IsValid:
            invalid_count += 1
            fail("valid_geometry", object_id=object_id)
        if role and role.startswith("source_plan"):
            sources.append(obj)
            bounds = geometry.GetBoundingBox()
            if not all(math.isfinite(z) and abs(z) <= 1e-8 for z in (bounds.Min.Z, bounds.Max.Z)):
                fail("source_plan_z", object_id=object_id)
        if role not in {"source_plan_boundary", "terrain_draped_boundary", "terrain_mesh", "run_annotation"}:
            missing = [name for name in SOURCE_KEYS if not attrs.GetUserString(name)]
            if missing:
                fail("source_metadata", object_id=object_id, missing=missing)
            for name, expected in (("source_properties_json", dict), ("source_records_json", list)):
                value = attrs.GetUserString(name)
                if value:
                    try:
                        if not isinstance(json.loads(value), expected):
                            raise ValueError("Wrong JSON type")
                    except (ValueError, TypeError):
                        fail("source_metadata_json", object_id=object_id, field=name)
        if stage == "3d" and role == "building_volume":
            volumes.append(obj)
            closed = geometry.IsClosed if isinstance(geometry, r3d.Mesh) else getattr(geometry, "IsSolid", False)
            if not closed:
                fail("closed_building_volume", object_id=object_id)
            bounds = geometry.GetBoundingBox()
            try:
                reference = float(attrs.GetUserString("reference_ground_z"))
                offset = float(attrs.GetUserString("bottom_offset_m"))
                height = float(attrs.GetUserString("building_height_m"))
                if not all(math.isfinite(v) for v in (reference, offset, height)):
                    raise ValueError("Non-finite placement")
                if (attrs.GetUserString("volume_direction") != "+Z" or height <= 0
                        or bounds.Max.Z <= bounds.Min.Z or bounds.Min.Z < reference - .01
                        or abs(bounds.Min.Z - reference - offset) > .01
                        or abs(bounds.Max.Z - reference - offset - height) > .01):
                    fail("building_placement", object_id=object_id, message="Mass does not match its placement metadata")
            except (TypeError, ValueError):
                fail("building_placement", object_id=object_id, message="Missing or invalid placement metadata")
            layer = layers_by_index.get(attrs.LayerIndex)
            if layer and "::Buildings::Parent Envelope" in layer.FullPath and layer.Visible:
                fail("parent_envelope_visibility", object_id=object_id)
    duplicate_keys = sorted(key for key, count in keys.items() if count > 1)
    if duplicate_keys:
        fail("duplicate_keys", keys=duplicate_keys)
    if model.Settings.ModelUnitSystem != r3d.UnitSystem.Meters:
        fail("model_units", value=str(model.Settings.ModelUnitSystem))
    missing_document = [key for key in DOCUMENT_KEYS if not model.Strings[key]]
    if missing_document:
        fail("document_metadata", missing=missing_document)
    if roles["source_plan_boundary"] < 2:
        fail("boundaries", message="Site and context source boundaries are required")
    if roles["run_annotation"] == 0:
        fail("run_annotation", message="Run annotation is missing")
    if stage == "3d" and roles["terrain_draped_boundary"] < 2:
        fail("draped_boundaries", message="Site and context 3D boundaries are required")
    if visual_inspection == "not-possible":
        warnings.append({"check": "visual_inspection", "message": "Visual inspection was not performed"})
    elif visual_inspection == "failed":
        fail("visual_inspection", message=visual_notes or "Visual inspection failed")
    counts = {"objects": len(objects), "owned_objects": len(owned), "layers": len(layers),
              "invalid_geometry": invalid_count, "source_plan_objects": len(sources),
              "building_volumes": len(volumes), "terrain_skirts": roles["building_terrain_skirt"]}
    return {"stage": stage, "passed": not failures, "failures": failures, "warnings": warnings,
            "counts": counts, "role_counts": dict(sorted(roles.items())),
            "object_count": len(objects), "layer_count": len(layers),
            "invalid_geometry_count": invalid_count, "source_plan_object_count": len(sources),
            "building_volume_count": len(volumes), "terrain_skirt_count": roles["building_terrain_skirt"],
            "checks_not_applicable": ["building_placement", "closed_building_volume", "draped_boundaries"] if stage == "2d" else [],
            "visual_inspection": visual_inspection, "visual_notes": visual_notes}


def audit_file(path, stage, visual_inspection="not-possible", visual_notes=""):
    """Reopen and hash a saved checkpoint before auditing it."""
    if stage not in {"2d", "3d"}:
        raise ValueError("stage must be 2d or 3d")
    path = Path(path).resolve()
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        model = r3d.File3dm.Read(str(path))
        if model is None:
            raise ValueError("The Rhino model could not be opened")
    except (OSError, ValueError, RuntimeError) as error:
        return {"model": str(path), "stage": stage, "passed": False, "reopened": False,
                "failures": [{"check": "reopen", "message": str(error)}], "warnings": [], "counts": {},
                "visual_inspection": visual_inspection, "visual_notes": visual_notes}
    result = audit_model(model, stage, visual_inspection, visual_notes)
    return {**result, "model": str(path), "model_sha256": digest.hexdigest(), "reopened": True}
