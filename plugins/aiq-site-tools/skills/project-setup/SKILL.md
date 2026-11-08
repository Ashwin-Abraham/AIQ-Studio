---
name: project-setup
description: Start or adapt an AIQ Studio project folder with a project manifest and a local workflow view.
---

# Project setup

1. Confirm the project root. Inspect existing files before creating folders. Use [project folder organisation](../../references/PROJECT-FOLDER-ORGANISATION.md) to choose a layout that fits the project. Create only folders needed for current work.
2. Create or update `project.json`. Record the project name and relative folder roles. Preserve existing manifest data. Use [the workflow record](../../references/PROJECT-WORKFLOW.md) for stage status and file links. Set only known facts; leave unstarted nodes out.
3. Keep a `project-log.md` for dated decisions. Run the installed plugin's `scripts/render_project_workflow.py` with the project root as its argument. The script writes `workflow.html` beside `project.json`.
4. Open the HTML and check that the project name, stage status, decisions and links match the manifest. Setup is complete when active work areas resolve from the root and the view reflects the record.
