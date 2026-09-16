#!/usr/bin/env python3
"""Prepare, apply, resume, migrate, or audit separate site-model stages."""

import argparse
import json
from pathlib import Path
import sys

# Also prevent local bytecode when this entry point runs inside Rhino Python.
sys.dont_write_bytecode = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root")
    parser.add_argument("--input", help="Terrain-free processed source JSON")
    parser.add_argument("--output", help="Target 3DM; open it first for a live run")
    parser.add_argument("--stage", choices=("2d", "3d", "all"), default="all")
    parser.add_argument("--backend", choices=("live", "file"), default="live")
    parser.add_argument("--terrain")
    parser.add_argument("--flat-elevation", type=float)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--worker-python", help="Managed external Python for parallel jobs inside Rhino")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--partition-size", type=int, default=1000)
    parser.add_argument("--checkpoint")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--visual-inspection", choices=("passed", "failed", "not-possible"), default="not-possible")
    parser.add_argument("--visual-notes", default="")
    parser.add_argument("--migrate-input", help="Split legacy combined JSON; --input is the new source output")
    parser.add_argument("--terrain-output", help="Separate terrain output for migration")
    parser.add_argument("--worker-job", help=argparse.SUPPRESS)
    parser.add_argument("--worker-result", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        from site_model import workflow
        from site_model.contract import atomic_json, confined_path
        if args.worker_job:
            if not args.worker_result:
                parser.error("--worker-result is required")
            workflow.prepare_worker(args.worker_job, args.worker_result)
            return 0
        if not args.project_root:
            parser.error("--project-root is required")
        if args.migrate_input:
            if not args.input:
                parser.error("--input is required as the new source output")
            old = confined_path(args.project_root, args.migrate_input)
            new = confined_path(args.project_root, args.input)
            terrain = confined_path(args.project_root, args.terrain_output) if args.terrain_output else None
            if old == new or terrain in (old, new):
                parser.error("Migration output paths must be separate from the input and each other")
            result = workflow.migrate(old, new, terrain)
        elif args.audit_only:
            from site_model.audit import audit_file
            if not args.output or args.stage == "all":
                parser.error("Audit requires --output and --stage 2d or 3d")
            target = confined_path(args.project_root, args.output)
            result = audit_file(target, args.stage, args.visual_inspection, args.visual_notes)
            atomic_json(str(target) + "." + args.stage + ".review.audit.json", result)
        else:
            if not args.input or not args.output:
                parser.error("--input and --output are required")
            result = workflow.run(args.project_root, args.input, args.output, args.stage, args.backend,
                                  args.terrain, args.flat_elevation, args.workers, args.batch_size,
                                  args.partition_size, args.checkpoint, args.worker_python,
                                  progress=lambda event: print(json.dumps(event), flush=True))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print("Site model: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
