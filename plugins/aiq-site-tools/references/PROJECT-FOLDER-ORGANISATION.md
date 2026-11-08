# AIQ Studio Project Folder Organisation

Use this reference when you create a project folder or place AIQ Studio files in an existing one. The project root is the folder the user chooses. Keep paths in `project.json` relative to that root so the project can move as one folder.

## Default layout

For a new project, use this layout as a starting point. Create a folder when work first needs it.

```text
<project>/
├── project.json                    Paths and current project status
├── workflow.html                   Read-only view of the project record
├── project-log.md                  Dated changes and decisions
├── .agents/                        Project-local agent instructions and helpers, if needed
├── 01_Admin/
│   ├── brief/
│   ├── programme/
│   └── schedule/
├── 02_Correspondence/
│   ├── client/
│   └── transmittals/
├── 03_Site_Research/
│   ├── source/
│   │   ├── surveys/
│   │   └── reference/
│   ├── models/
│   ├── artifacts/
│   ├── reports/
│   └── published/
├── 04_Design/
│   ├── 01_Feasibility/
│   │   ├── artifacts/
│   │   └── published/
│   ├── 02_Concept/
│   │   └── <option>/
│   │       ├── overview.md         Vision, stages and current status
│   │       ├── 01_Parti/artifacts/
│   │       ├── 02_Zoning/artifacts/
│   │       ├── 03_Massing/artifacts/
│   │       ├── models/
│   │       └── published/
│   ├── 03_Design_Development/
│   │   ├── models/
│   │   ├── artifacts/
│   │   └── published/
│   └── 04_Construction_Documents/
│       ├── models/
│       ├── artifacts/
│       └── published/
├── 05_Consultants/
│   ├── civil/
│   ├── landscape/
│   └── structure/
├── 06_Approvals/
├── 07_Construction/
└── Z_Archive/
```

Keep each design option together. Add its stage folders as work progresses; use the project's actual stage names. Record a short vision and stage summary in the option's `overview.md`. Record dated changes in `project-log.md` and point to the active option and stage from `project.json`.

Keep the stage record in `project.json` and generate `workflow.html` beside it with the [project workflow renderer](PROJECT-WORKFLOW.md). Use `.agents/` only for project-local agent material that has no place in a work area. A project can start without this folder.

## Where files go

- `source/` holds unchanged supplied or downloaded files. Record their origin and relevant source details.
- `models/` holds working design models. Put deliberate snapshots in a nearby `backups/` folder.
- `artifacts/` holds generated files beside the work that produced them, such as processed data, SVGs, image variants, analysis runs and review captures. Add a workflow subfolder when runs would otherwise mix.
- `reports/` holds audits and validation reports. Add one near another work area when needed.
- `published/` holds issued files. Record each issue or revision in the project log.
- `Z_Archive/` holds superseded files retained for reference.

Working, shared and published describe a file's review state. The numbered folders describe the design phase. Use the project's existing review process and record the issued location in `project.json`.

## Adapt an existing project

Inspect the existing folders, then map each needed **role** to its current path in `project.json`. Keep the user's folder names and files in place. For example, an existing project might contain:

```text
<project>/
├── Survey/Received/boundary.dwg
├── Survey/Analysis/
├── Design/Rhino/
└── Issue/Client/
```

Its path map could be:

```json
{
  "folders": {
    "siteSources": "Survey/Received",
    "siteArtifacts": "Survey/Analysis",
    "workingModels": "Design/Rhino",
    "publishedOutputs": "Issue/Client"
  }
}
```

The site skill reads `siteSources` before using `boundary.dwg` and writes derived site data to `siteArtifacts`. When an option begins, add its own paths and short status to the manifest. Each skill reads the mapped paths before saving files and updates the manifest when it creates a work area. Keep reusable scripts in the installed skill and project-specific scripts with their related artifacts. Store relative paths and omit credentials and machine-specific temporary paths.

The folder mapping is complete when every active work area has a recorded destination, the paths resolve from the project root, and the original source files remain unchanged.

For runtime and temporary files, follow [Python scripting guidance](../skills/rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md).
