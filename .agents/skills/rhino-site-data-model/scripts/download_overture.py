#!/usr/bin/env python3
"""Acquire independent Overture themes, then publish one source manifest."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from site_model.contract import atomic_json, confined_path, file_sha256, load_json
from site_model.overture_types import SUPPORTED_FEATURE_TYPES, validate_types

DEFAULT_TYPES = list(SUPPORTED_FEATURE_TYPES)
file_hash = file_sha256


def download_sources(bbox, output_dir, release=None, feature_types=None, workers=1, runner=None):
    """Download to isolated temporary files; publish only after every job succeeds.

    Parallel acquisition requires an explicit release. Sequential acquisition can
    resolve the first release from the provider state, then pin all later jobs.
    The caller must give separate output directories to separate invocations.
    """
    feature_types = validate_types(DEFAULT_TYPES if feature_types is None else feature_types)
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('workers must be between 1 and 4')
    if len(bbox) != 4 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in bbox) or not (-180 <= bbox[0] < bbox[2] <= 180 and -90 <= bbox[1] < bbox[3] <= 90):
        raise ValueError('bbox must contain west,south,east,north within WGS84 bounds')
    if release is not None and (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', release) or release.lower() in {'latest', 'unknown'}):
        raise ValueError('Release must be one explicit Overture release identifier')
    if workers > 1 and not release:
        raise ValueError('Parallel acquisition requires --release')
    runner = runner or subprocess.run
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    bbox_text = ','.join(str(v) for v in bbox)
    for feature_type in feature_types:
        confined_path(output_dir, feature_type+'.geojson')
        confined_path(output_dir, feature_type+'.geojson.state')
    confined_path(output_dir, 'source-manifest.json')

    with tempfile.TemporaryDirectory(dir=output_dir, prefix='.acquire-') as temp:
        def acquire(feature_type, pinned_release):
            output = Path(temp)/(feature_type+'.geojson')
            command = [sys.executable, '-m', 'overturemaps', 'download', '--bbox='+bbox_text, '-f', 'geojson', '--type='+feature_type, '-o', str(output)]
            if pinned_release:
                command.extend(['--release', pinned_release])
            runner(command, check=True)
            state_path = Path(str(output)+'.state')
            state = load_json(state_path) if state_path.exists() else {}
            actual_release = state.get('last_release') or pinned_release
            if not isinstance(actual_release, str) or not actual_release.strip() or actual_release.lower() in {'latest', 'unknown'} or (pinned_release and actual_release != pinned_release):
                raise ValueError('Provider release is missing or differs from the requested release')
            collection = load_json(output)
            if collection.get('type') != 'FeatureCollection' or not isinstance(collection.get('features'), list):
                raise ValueError('Downloaded file must be a GeoJSON FeatureCollection')
            return {'feature_type':feature_type, 'path':str(output_dir/(feature_type+'.geojson')), 'sha256':file_sha256(output), 'feature_count':len(collection['features']), 'state':state, 'release':actual_release}

        if workers == 1:
            records = []
            for feature_type in feature_types:
                record = acquire(feature_type, release)
                release = release or record['release']
                records.append(record)
        else:
            with ThreadPoolExecutor(max_workers=min(workers,len(feature_types))) as pool:
                records = list(pool.map(lambda feature_type: acquire(feature_type,release), feature_types))
        for record in records:
            filename = record['feature_type']+'.geojson'
            os.replace(Path(temp)/filename, output_dir/filename)
            # Publish matching state, including an empty state when the provider omitted it.
            atomic_json(output_dir/(filename+'.state'), record['state'])
        manifest = {'provider':'Overture Maps', 'release':release, 'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'bbox_wgs84':list(bbox), 'python':sys.version, 'files':records}
        atomic_json(output_dir/'source-manifest.json',manifest)
        return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bbox',required=True,help='west,south,east,north in WGS84')
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--release',help='Pinned release; required when --workers is greater than 1')
    parser.add_argument('--types',nargs='+',default=DEFAULT_TYPES,choices=DEFAULT_TYPES)
    parser.add_argument('--workers',type=int,default=1,choices=range(1,5))
    args = parser.parse_args()
    manifest = download_sources([float(v) for v in args.bbox.split(',')],args.output_dir,args.release,args.types,args.workers)
    print(json.dumps({'manifest':str(Path(args.output_dir).resolve()/'source-manifest.json'),'release':manifest['release'],'files':len(manifest['files'])},indent=2))

if __name__ == '__main__':
    main()
