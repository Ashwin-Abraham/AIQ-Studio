#!/usr/bin/env python3
"""Download Overture features for one bounding box and write a source manifest."""

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_TYPES = ["building", "building_part", "segment", "connector", "water", "land", "land_use", "place"]


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bbox", required=True, help="west,south,east,north in WGS84")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--release", help="Pinned Overture release. The default is latest.")
    parser.add_argument("--types", nargs="+", default=DEFAULT_TYPES)
    args = parser.parse_args()

    bbox = [float(value) for value in args.bbox.split(",")]
    if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        raise SystemExit("--bbox must be west,south,east,north")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    release_used = args.release
    for feature_type in args.types:
        output = output_dir / (feature_type + ".geojson")
        command = [
            sys.executable,
            "-m",
            "overturemaps",
            "download",
            "--bbox=" + args.bbox,
            "-f",
            "geojson",
            "--type=" + feature_type,
            "-o",
            str(output),
        ]
        if args.release:
            command.extend(["--release", args.release])
        subprocess.run(command, check=True)
        state_path = Path(str(output) + ".state")
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        release_used = release_used or state.get("last_release")
        collection = json.loads(output.read_text(encoding="utf-8"))
        records.append(
            {
                "feature_type": feature_type,
                "path": str(output),
                "sha256": file_hash(output),
                "feature_count": len(collection.get("features", [])),
                "state": state,
            }
        )

    manifest = {
        "provider": "Overture Maps",
        "release": release_used,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bbox_wgs84": bbox,
        "python": sys.version,
        "files": records,
    }
    manifest_path = output_dir / "source-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "release": release_used, "files": len(records)}, indent=2))


if __name__ == "__main__":
    main()
