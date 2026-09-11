"""Render this workflow's native Rhino AI3 export, with strict operator checks."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def validate_ai(path):
    text = path.read_text(encoding="latin-1")
    if not text.startswith("%!PS-Adobe") or "%%Creator: Rhinoceros" not in text:
        raise ValueError("Expected a native Rhino PostScript AI export")
    content = text.split("%%EndSetup", 1)[1].split("%%PageTrailer", 1)[0]
    operators = {line.split()[-1] for line in content.splitlines()
                 if line.strip() and not line.startswith("%")}
    supported = set("XA Xa Lb Ln LB A R D i J j w M d m L l C c S s F f *u *U u U To Tp TP Tr Tf Tx TO".split())
    if operators - supported:
        raise ValueError(f"Preview does not support these AI operators: {operators - supported}")
    bbox = [float(x) for x in re.search(r"%%BoundingBox: (.*)", text)[1].split()]
    expected = [0, 0, 420*72/25.4, 297*72/25.4]
    if any(abs(x-y) > 2 for x, y in zip(bbox, expected)):
        raise ValueError(f"AI paper scale or extent is wrong: {bbox}; expected A3 in points")
    for line in content.splitlines():
        if line.endswith(" Tp"):
            values = [float(x) for x in line.split()[:-1]]
            if any(abs(x-y)>1e-5 for x,y in zip(values[:4],[1,0,0,1])):
                raise ValueError("Preview requires horizontal text")
    return {"bounding_box_points": bbox, "operators": sorted(operators),
            "ai_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ai")
    parser.add_argument("--ghostscript", required=True)
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()
    if not 72 <= args.dpi <= 600:
        raise ValueError("Use 72 to 600 DPI")
    path = Path(args.ai).resolve()
    report = validate_ai(path)
    output = path.with_suffix(".png")
    if output.exists():
        raise FileExistsError(output)
    prolog = Path(__file__).resolve().parent.parent / "references" / "rhino-ai-preview.ps"
    subprocess.run([args.ghostscript, "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dFIXEDMEDIA",
                    "-sDEVICE=png16m", f"-r{args.dpi}", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                    f"-dDEVICEWIDTHPOINTS={420*72/25.4}", f"-dDEVICEHEIGHTPOINTS={297*72/25.4}",
                    "-sFONTPATH=C:/Windows/Fonts", f"-sOutputFile={output}", str(prolog), str(path)],
                   check=True, timeout=120)
    report.update(png=str(output), dpi=args.dpi,
                  renderer="Ghostscript with the workflow's restricted Rhino AI3 preview procset",
                  note="PNG reads exported AI paths and text; Illustrator itself was not checked")
    path.with_suffix(".preview.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
