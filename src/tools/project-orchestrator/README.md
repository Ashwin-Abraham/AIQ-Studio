# Project Orchestrator

Project Orchestrator displays the site planning stages, project records, decisions, and file links.

Use Vue 3 with the Options API. Follow [the Vue coding standards](VUE_CODING_STANDARDS.md) for implementation.

The standards were copied from `AIQ-Resi-UI/AIQ-Resi-UI/VUE_CODING_STANDARDS.md` in the nearby local repository.

Run `npm install`, then `npm run dev`. Open `http://127.0.0.1:5174/` in Edge or Chrome.

To open the same URL in SketchUp, open the Ruby Console and run
`load 'ABSOLUTE_PATH_TO_TOOL/hosts/sketchup/project_orchestrator.rb'`.
Use forward slashes in the path. Keep the local server running while the dialog is open.

Select a stage to see its record below the graph. The local UI shows the example project's immediate subfolders on load. Select another local project folder to replace that list. The graph uses the example project record in the local UI, or the embedded record in an export. Folder selection only sets the folder shown in the files panel. The chat panel shows an empty state.

Run `npm run lint`, `npm run type-check`, and `npm test` before completing a code change.

Run `npm run build` to build the application and update the generated workflow template in the plugin assets. Then run `python plugins/aiq-site-tools/skills/project-setup/scripts/render_project_workflow.py <project-folder>` from the repository root to export a standalone `workflow.html`. The export contains the Vue build and project record. Keep it beside `project.json` so relative file links work.

## Code structure

- `ProjectOrchestrator.vue` holds the selected stage and connects the page components.
- `components/` contains the header, diagram, stage node, legend, controls, and detail panel. Each component owns its styles.
- `WorkflowService.ts` defines the stages, loads the project record, and builds file links.
- `ViewportService.ts` calculates zoom bounds and the diagram view.
- `ProjectFolderService.ts` selects a folder through the browser or the SketchUp dialog and returns the immediate subfolder names.
- `models/` contains one exported type per file.
- `styles.css` contains shared colours and page defaults.

Edit the Vue source. The plugin template and example workflow HTML are generated outputs.
