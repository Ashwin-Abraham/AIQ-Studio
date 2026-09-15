# AIQ Studio Project Folder Organisation

## Purpose

This document defines the expected folder structure for an installed AIQ Studio workspace.

## Workspace root

The installation process creates an `AIQ Studio` folder. Use this folder as the workspace root.

The user can specify an existing file to edit. In this case, use the folder that contains the specified file as the project root.

```text
AIQ Studio/
|-- .agents/
|   |-- PROJECT-FOLDER-ORGANISATION.md
|   `-- skills/
`-- Projects/
```

- `.agents/` contains installed agent resources.
- `.agents/skills/` contains reusable workflows that are available to all projects.
- `Projects/` contains all user project data.

Do not put user project data directly in the workspace root or in `.agents/`.

## Project structure

Create one self-contained folder for each project.

```text
AIQ Studio/
`-- Projects/
    `-- <project-name>/
        |-- Models/
        |   |-- <project-name>.3dm
        |   `-- backups/
        |-- artifacts/
        |   `-- <workflow-or-dataset-name>/
        |       |-- source/
        |       |   |-- raw/
        |       |   `-- source-manifest.json
        |       |-- processed/
        |       |-- reports/
        |       `-- scripts/
        |-- documents/
        |-- exports/
        `-- project.json
```

Use a clear project name that is safe for a Windows folder. Do not use a location name alone when two projects can use the same location.

## Folder responsibilities

### `Models/`

Store the project's working and final Rhino models here.

- Use the project name for the main model.
- Put deliberate model snapshots in `Models/backups/`.
- Do not treat Rhino `.3dmbak` or `.rhl` files as project deliverables.

### `artifacts/`

Store reproducible workflow data under a named workflow or dataset folder.

- `source/raw/` contains unchanged downloaded or supplied source files.
- `source/source-manifest.json` records source URLs, releases, licences, bounds, coordinate systems, and download dates.
- `processed/` contains normalized inputs used to build the model.
- `reports/` contains validation audits, model reports, logs, and preview images.
- `scripts/` contains scripts adapted for this project or workflow run.

Reusable scripts must stay in `.agents/skills/<skill-name>/scripts/`. Copy or create a script under a project only when it contains project-specific inputs or behavior.

### `documents/`

Store project briefs, notes, decisions, and other project records here.

### `exports/`

Store files prepared for delivery or use in other applications. Examples include PDF, Illustrator, SVG, PNG, and ZIP files.

### `project.json`

Use this file for stable project metadata. Start with this structure:

```json
{
  "schemaVersion": 1,
  "id": "<project-id>",
  "name": "<project-name>",
  "createdAt": "<ISO-8601-date-time>",
  "updatedAt": "<ISO-8601-date-time>",
  "coordinateReferenceSystem": null,
  "mainModel": "Models/<project-name>.3dm",
  "folders": {
    "models": "Models",
    "artifacts": "artifacts",
    "documents": "documents",
    "exports": "exports"
  },
  "workflows": []
}
```

A project can add fields when necessary. Preserve the names and meanings of the common fields.

Do not store credentials, access tokens, or machine-specific temporary paths in this file.

## Workflow rules

- Keep each project self-contained so that a user can move, copy, archive, or delete it as one folder.
- Keep raw source files unchanged. Write transformations to `processed/`.
- Record enough source and processing metadata to reproduce the model.
- Put final deliverables in `Models/` or `exports/`, not in temporary directories.
- Do not write data into another project unless the user explicitly selects that project.

## Runtime and temporary files

Follow [Python scripting guidance](PYTHON-SCRIPTING-GUIDANCE.md) for environment creation, dependency management, temporary files, project-specific scripts, and reusable modules.
