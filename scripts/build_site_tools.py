"""Build the two distributable skills from the maintained .agents sources."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"
TARGET = ROOT / "plugins" / "aiq-site-tools" / "skills"
SKILLS = ("rhino-site-data-model", "rhino-to-vector-site-maps")
GUIDES = (
    "SUBAGENT-DELEGATION-GUIDANCE.md",
    "RHINO-DOCUMENT-EDITING-GUIDANCE.md",
    "PYTHON-SCRIPTING-GUIDANCE.md",
    "PROJECT-FOLDER-ORGANISATION.md",
)


def included(path: Path) -> bool:
    return not any(part in {"tests", "__pycache__", "options"} for part in path.parts) and path.suffix not in {".pyc", ".pyo"}


def decoded(data: bytes) -> str:
    return data.decode("utf-8").replace("\r\n", "\n")


def package_bytes(source: Path, destination: Path) -> bytes:
    data = content(source, destination)
    if destination.suffix == ".md":
        return data.replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n"
    return data


def content(source: Path, destination: Path) -> bytes:
    data = source.read_bytes()
    if source.name == "PROJECT-FOLDER-ORGANISATION.md":
        value = decoded(data)
        start = value.index("## Workspace root")
        end = value.index("## Project structure", start)
        value = value[:start] + (
            "## Workspace root\n\nChoose a workspace folder with the user. Put each project in its `Projects/` folder. "
            "If the user supplies an existing model, use its project folder. The installed skills stay in the plugin or global skills location.\n\n"
        ) + value[end:]
        value = value.replace("AIQ Studio/", "<workspace>/")
        value = value.replace("Reusable scripts must stay in `.agents/skills/<skill-name>/scripts/`.",
                              "Reusable scripts stay in the installed skill's `scripts/` folder.")
        return value.encode("utf-8")
    if source.name == "PYTHON-SCRIPTING-GUIDANCE.md":
        value = decoded(data)
        start = value.index("## Standard locations")
        end = value.index("## Python runtime environments", start)
        value = value[:start] + (
            "## Standard locations\n\nKeep reusable scripts in the installed skill's `scripts/` folder. "
            "Put project scripts in `<project>/artifacts/<workflow>/scripts/`. "
            "Keep project data out of the installed skill.\n\n"
        ) + value[end:]
        value = value.replace("Never create `.venv`, `venv`, or `site-packages` inside `AIQ Studio/Projects/`.",
                              "Keep `.venv`, `venv`, and `site-packages` outside every project folder.")
        value = value.replace("Create the reusable implementation in the applicable skill.",
                              "Create the reusable implementation in the maintained source skill, then rebuild the package.")
        return value.encode("utf-8")
    if source.name == "SUBAGENT-DELEGATION-GUIDANCE.md":
        value = decoded(data)
        value = value.replace('Use `fork_turns: "none"` with a self-contained task when possible. Give recent turns only when the task needs them. Do not copy the full conversation by default.', "Give each worker only the context it needs.")
        return value.encode("utf-8")
    if source.name == "usage.md" and source.parent.name == "references" and source.parent.parent.name == "rhino-image-capture":
        value = decoded(data)
        return value.split("## Status and tests", 1)[0].encode("utf-8")
    if source.name == "RHINO-DOCUMENT-EDITING-GUIDANCE.md":
        value = decoded(data)
        value = value.replace("skills/rhino-image-capture/SKILL.md", "image-capture.md")
        return value.encode("utf-8")
    if source.name == "SKILL.md" and source.parent.name == "rhino-image-capture":
        value = decoded(data)
        value = value.split("---\n", 2)[-1].lstrip()
        value = value.split("## Dependencies and tests", 1)[0]
        value = value.replace("scripts/image_capture.py", "../scripts/image_capture.py")
        value = value.replace("references/usage.md", "image-capture-usage.md")
        value = value.replace("../../RHINO-DOCUMENT-EDITING-GUIDANCE.md", "RHINO-DOCUMENT-EDITING-GUIDANCE.md")
        return value.encode("utf-8")
    if source.name == "SKILL.md" and source.parent.name == "rhino-site-data-model":
        value = decoded(data)
        for guide in GUIDES:
            value = value.replace(f"../../{guide}", f"references/{guide}")
        return value.encode("utf-8")
    if source.name == "staged-workflow.md" and source.parent.name == "references":
        value = decoded(data)
        for guide in GUIDES:
            value = value.replace(f"../../../{guide}", guide)
        value = value.replace("Codex sub-agents", "agent sub-agents")
        return value.encode("utf-8")
    return data


def expected_files() -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    for skill in SKILLS:
        folder = SOURCE / skill
        for source in folder.rglob("*"):
            if source.is_file() and included(source.relative_to(folder)):
                destination = TARGET / skill / source.relative_to(folder)
                result[destination] = package_bytes(source, destination)
    for guide in GUIDES:
        destination = TARGET / SKILLS[0] / "references" / guide
        result[destination] = package_bytes(ROOT / ".agents" / guide, destination)
    capture = SOURCE / "rhino-image-capture"
    capture_files = {
        capture / "SKILL.md": TARGET / SKILLS[0] / "references" / "image-capture.md",
        capture / "references" / "usage.md": TARGET / SKILLS[0] / "references" / "image-capture-usage.md",
        capture / "scripts" / "image_capture.py": TARGET / SKILLS[0] / "scripts" / "image_capture.py",
    }
    for source, destination in capture_files.items():
        result[destination] = package_bytes(source, destination)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check that the packaged skills match the sources")
    args = parser.parse_args()
    if not TARGET.resolve().is_relative_to(ROOT.resolve()):
        parser.error("Package target is outside the repository")
    expected = expected_files()
    stale = []
    for destination, data in expected.items():
        actual = destination.read_bytes() if destination.exists() else None
        if actual is not None and destination.suffix == ".md":
            actual = actual.replace(b"\r\n", b"\n")
        if actual != data:
            stale.append(destination.relative_to(ROOT))
            if not args.check:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
    if args.check:
        for skill in SKILLS:
            folder = TARGET / skill
            if folder.exists():
                stale.extend(path.relative_to(ROOT) for path in folder.rglob("*") if path.is_file() and path not in expected)
        if stale:
            print("Package is out of date:")
            for path in stale:
                print(path)
            return 1
        broken = []
        for document in TARGET.rglob("*.md"):
            for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if link.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                if not (document.parent / link.split("#", 1)[0]).resolve().exists():
                    broken.append((document.relative_to(ROOT), link))
        if broken:
            for document, link in broken:
                print(f"Broken link: {document} -> {link}")
            return 1
        print("Package matches the maintained skills.")
    else:
        print(f"Wrote {len(expected)} skill files to {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
