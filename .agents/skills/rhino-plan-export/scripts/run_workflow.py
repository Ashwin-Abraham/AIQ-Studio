"""Create source plan scenes, native Illustrator exports and PNG previews."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ghostscript", required=True)
    parser.add_argument("--root")
    parser.add_argument("--rhino-system", default=r"C:\Program Files\Rhino 8\System")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    output = Path(args.output).resolve()
    def run(script, *parameters):
        subprocess.run([sys.executable, str(here/script), *map(str, parameters)], check=True, timeout=180)
    params = ["--model", args.model, "--config", args.config, "--output", output]
    if args.root:
        params += ["--root", args.root]
    run("export_plan.py", *params)
    scenes = sorted(output.glob("*.scene.json"))
    if not scenes:
        raise RuntimeError("The configuration produced no sheets")
    for scene in scenes:
        run("export_illustrator.py", scene, "--rhino-system", args.rhino_system)
        ai = scene.with_name(scene.name.removesuffix(".scene.json") + ".ai")
        run("render_ai.py", ai, "--ghostscript", args.ghostscript)
    (output/"workflow.json").write_text(json.dumps({
        "status": "exported", "sheets": [s.name.removesuffix(".scene.json") for s in scenes],
        "visual_review": "Inspect the PNG files before delivery",
        "illustrator_check": "Open-and-edit check not performed by this command"
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
