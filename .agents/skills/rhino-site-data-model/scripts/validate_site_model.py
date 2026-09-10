#!/usr/bin/env python3
"""Audit a Rhino site data model and record failures without stopping the workflow."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import rhino3dm as r3d


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--visual-inspection", choices=["passed", "failed", "not-possible"], default="not-possible")
    parser.add_argument("--visual-notes", default="")
    args = parser.parse_args()

    model_path = Path(args.model).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    warnings = []
    model = r3d.File3dm.Read(str(model_path)) if model_path.exists() else None
    if model is None:
        failures.append({"check": "reopen", "message": "The Rhino model could not be opened"})
        audit = {
            "model": str(model_path),
            "passed": False,
            "failures": failures,
            "warnings": warnings,
            "visual_inspection": args.visual_inspection,
            "visual_notes": args.visual_notes,
        }
        output_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        print(json.dumps(audit, indent=2))
        return

    objects = list(model.Objects)
    layers = list(model.Layers)
    roles = Counter(obj.Attributes.GetUserString("geometry_role") or "missing" for obj in objects)
    invalid = [str(obj.Attributes.Id) for obj in objects if not obj.Geometry.IsValid]
    if invalid:
        failures.append({"check": "valid_geometry", "object_ids": invalid})
    if str(model.Settings.ModelUnitSystem) != "UnitSystem.Meters":
        failures.append({"check": "model_units", "value": str(model.Settings.ModelUnitSystem)})

    source_objects = [obj for obj in objects if (obj.Attributes.GetUserString("geometry_role") or "").startswith("source_plan")]
    wrong_source_z = []
    missing_source_data = []
    for obj in source_objects:
        bounds = obj.Geometry.GetBoundingBox()
        if abs(bounds.Min.Z) > 1e-8 or abs(bounds.Max.Z) > 1e-8:
            wrong_source_z.append(str(obj.Attributes.Id))
        role = obj.Attributes.GetUserString("geometry_role") or ""
        if role != "source_plan_boundary":
            required = ["source_feature_id", "source_feature_type", "source_properties_json", "source_records_json"]
            missing = [key for key in required if obj.Attributes.GetUserString(key) is None]
            if missing:
                missing_source_data.append({"object_id": str(obj.Attributes.Id), "missing": missing})
    if wrong_source_z:
        failures.append({"check": "source_plan_z", "object_ids": wrong_source_z})
    if missing_source_data:
        failures.append({"check": "source_metadata", "objects": missing_source_data})

    volumes = [obj for obj in objects if obj.Attributes.GetUserString("geometry_role") == "building_volume"]
    bad_volumes = []
    for obj in volumes:
        bounds = obj.Geometry.GetBoundingBox()
        try:
            reference_z = float(obj.Attributes.GetUserString("reference_ground_z"))
            bottom_offset = float(obj.Attributes.GetUserString("bottom_offset_m"))
            expected_bottom = reference_z + bottom_offset
        except (TypeError, ValueError):
            bad_volumes.append({"object_id": str(obj.Attributes.Id), "reason": "missing placement metadata"})
            continue
        if obj.Attributes.GetUserString("volume_direction") != "+Z":
            bad_volumes.append({"object_id": str(obj.Attributes.Id), "reason": "volume direction is not +Z"})
        elif bounds.Max.Z <= bounds.Min.Z:
            bad_volumes.append({"object_id": str(obj.Attributes.Id), "reason": "non-positive vertical extent"})
        elif abs(bounds.Min.Z - expected_bottom) > 0.01:
            bad_volumes.append({"object_id": str(obj.Attributes.Id), "reason": "bottom elevation does not match placement rule"})
        elif bounds.Min.Z + 0.01 < reference_z:
            bad_volumes.append({"object_id": str(obj.Attributes.Id), "reason": "mass starts below reference ground"})
    if bad_volumes:
        failures.append({"check": "building_placement", "objects": bad_volumes})

    parent_layers = {layer.Index: layer for layer in layers if "::Buildings::Parent Envelope" in layer.FullPath}
    visible_parent_envelopes = []
    for obj in volumes:
        layer = parent_layers.get(obj.Attributes.LayerIndex)
        if layer and layer.Visible:
            visible_parent_envelopes.append(str(obj.Attributes.Id))
    if visible_parent_envelopes:
        failures.append({"check": "parent_envelope_visibility", "object_ids": visible_parent_envelopes})

    required_document_text = [
        "site.name",
        "site.source_release",
        "site.projected_crs",
        "site.origin_wgs84",
        "site.origin_projected",
        "site.vertical_datum",
    ]
    missing_document_text = [key for key in required_document_text if not model.Strings[key]]
    if missing_document_text:
        failures.append({"check": "document_metadata", "missing": missing_document_text})
    if roles["source_plan_boundary"] < 2:
        failures.append({"check": "boundaries", "message": "Site and context source boundaries are required"})
    if roles["run_annotation"] == 0:
        failures.append({"check": "run_annotation", "message": "Run information annotation is missing"})
    if args.visual_inspection == "not-possible":
        warnings.append({"check": "visual_inspection", "message": "Plan and perspective inspection was not possible"})
    elif args.visual_inspection == "failed":
        failures.append({"check": "visual_inspection", "message": args.visual_notes or "Visual inspection failed"})

    audit = {
        "model": str(model_path),
        "model_sha256": sha256(model_path),
        "passed": not failures,
        "object_count": len(objects),
        "layer_count": len(layers),
        "role_counts": dict(sorted(roles.items())),
        "invalid_geometry_count": len(invalid),
        "source_plan_object_count": len(source_objects),
        "building_volume_count": len(volumes),
        "terrain_skirt_count": roles["building_terrain_skirt"],
        "visual_inspection": args.visual_inspection,
        "visual_notes": args.visual_notes,
        "failures": failures,
        "warnings": warnings,
    }
    output_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
