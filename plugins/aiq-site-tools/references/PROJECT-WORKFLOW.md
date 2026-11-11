# Project workflow record

Keep `project.json` and the generated `workflow.html` together at the project root. The JSON is the editable record. The HTML is a read-only view. Run `python <plugin>/skills/project-setup/scripts/render_project_workflow.py <project-root>` after each manifest update. The page embeds the current record so it works when opened as a local file.

## Manifest fields

Keep existing `project.json` fields. Add `name` and `workflow.nodes` as needed. Each node can have:

- `status`: `not-started`, `in-progress`, `review`, or `complete`.
- `summary`: one or two sentences about the current state.
- `decisions`: an array of short, approved or recorded decisions. State assumptions as assumptions.
- `files`: an array of `{ "label": "Human name", "path": "relative/path.ext" }` objects. Paths start at the project root.

The node IDs are `site-data`, `programme-brief`, `project-goals`, `site-analysis`, `parti-diagramming`, `pre-concept`, `conceptual-programme-brief`, `concept-design`, and `detailed-concept-design`. Omit a node record until work starts. The view shows it as **Not started**. Use a file link only after the file exists. Record each major decision in `project-log.md` as well; the manifest holds its short current form.

```json
{
  "name": "Example project",
  "folders": {"siteSources": "Survey/Received"},
  "workflow": {
    "nodes": {
      "site-data": {
        "status": "in-progress",
        "summary": "The boundary survey is available. Levels remain to be checked.",
        "decisions": ["Use the received boundary survey as the site base."],
        "files": [{"label": "Boundary survey", "path": "Survey/Received/boundary.dwg"}]
      }
    }
  }
}
```

The diagram records information flow, not a fixed approval sequence. Later work can send a design decision back to an earlier node. Keep project goals and planning rules separate from the area and capacity data in the Programme Brief.
