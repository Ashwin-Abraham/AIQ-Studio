"""Render the standalone workflow view from a project manifest."""

import argparse
import json
from pathlib import Path


NODE_IDS = (
    "site-data",
    "programme-brief",
    "project-goals",
    "site-analysis",
    "parti-diagramming",
    "pre-concept",
    "conceptual-programme-brief",
    "concept-design",
    "detailed-concept-design",
)
STATUSES = {"not-started", "in-progress", "review", "complete"}


def render(project_root: Path) -> Path:
    manifest_path = project_root / "project.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("project.json must contain an object")
    nodes = data.get("workflow", {}).get("nodes", {})
    if not isinstance(nodes, dict):
        raise ValueError("workflow.nodes must contain an object")
    for node_id, record in nodes.items():
        if node_id not in NODE_IDS:
            raise ValueError(f"Unknown workflow node: {node_id}")
        if not isinstance(record, dict) or record.get("status", "not-started") not in STATUSES:
            raise ValueError(f"Invalid record or status for {node_id}")
        for item in record.get("files", []):
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                raise ValueError(f"Invalid file for {node_id}")
            path = Path(item["path"])
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or "\\" in item["path"] or ":" in item["path"]):
                raise ValueError(f"File path must stay inside the project: {path}")

    source = Path(__file__).resolve().parents[3] / "assets" / "project-workflow.generated.html"
    if not source.exists():
        raise FileNotFoundError("Build src/tools/project-orchestrator with npm run build first.")
    encoded = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c")
    payload = f'<script type="application/json" id="project-data">{encoded}</script>'
    html = source.read_text(encoding="utf-8").replace("<!-- PROJECT_DATA -->", payload)
    output = project_root / "workflow.html"
    output.write_text(html, encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="Folder that contains project.json")
    print(render(parser.parse_args().project_root.resolve()))
