---
name: project-orchestrator
description: Review and update an AIQ Studio project's stage status, decisions and file links in its manifest and workflow HTML.
---

# Project orchestrator

1. Read `project.json`, `project-log.md`, and the active work files. Use [the workflow record](../../references/PROJECT-WORKFLOW.md) for stage IDs and fields. Check evidence before changing a stage status.
2. Update the relevant `workflow.nodes` records. Give each active stage a short current summary, its recorded decisions, and links to files that exist. Keep the manifest's folder roles and active option consistent with the work. Add dated major decisions to `project-log.md`.
3. Render `workflow.html` with the installed plugin's `scripts/render_project_workflow.py` and open it. Check each changed node and linked file. Finish when the view matches the project files and the manifest.

The HTML is a read-only project view in this version. Its boxes open stage records; they do not run skills. People can revise an earlier stage after later work changes an assumption.
