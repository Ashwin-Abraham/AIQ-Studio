# AIQ Studio workflows

An AEC workflow takes a project from stated needs and site evidence through design, analysis and issued work. Each step leaves files and decisions that a later step can check or revise. AIQ Site Tools provides the workflows below; a project can start at the step its existing information supports.

## Skills

| Skill | What it produces | How it fits |
| --- | --- | --- |
| [Programme Brief](skills/programme-brief/SKILL.md) | A spreadsheet of uses, areas and capacities, with assumptions and sources. | Gives site and design work a measurable demand. |
| [Rhino Site Data Model](skills/rhino-site-data-model/SKILL.md) | A checked Rhino site model, source data and validation report. | Gives design and analysis a shared site base. |
| [Vector Site Maps](skills/rhino-to-vector-site-maps/SKILL.md) | Editable site analysis maps and a review PDF. | Makes site conditions visible for design decisions. |
| [Ladybug Analysis](skills/ladybug-analysis/SKILL.md) | Radiation, shadow or isovist results from selected Rhino geometry. | Tests site or design options and can inform later map or model revisions. |
| [Rhino AEC Modelling](skills/rhino-aec-modelling/SKILL.md) | Zones, roads, parcels and building massing in Rhino through AIQ Urban. | Turns a design option into a model that can be inspected and revised. |

The Programme Brief and site model can develop in parallel. Site maps and analysis inform concept decisions; AIQ Urban models a selected option. Analysis can then send the team back to the brief, maps or model. Concept reasoning and option selection remain design decisions made with the project team.

## Start or resume a project

Choose a project folder and read [project folder organisation](references/PROJECT-FOLDER-ORGANISATION.md). For a new project, create only the folders needed for the current work. For an existing project, record its folder paths in `project.json` and use those paths when a skill saves files. Keep the current option and stage in the manifest, a short account of each option in its `overview.md`, and dated decisions in `project-log.md`.
