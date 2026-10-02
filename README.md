# AIQ Studio

AIQ Studio provides AI workflows for architecture, engineering, and construction. **AIQ Site Tools** has two skills: one builds a Rhino site model, and one makes vector site analysis maps from its checked 2D data.

## Installation

[![Codex](assets/installation/codex.png)](docs/distribution.md#install-in-codex) [![Claude Code](assets/installation/claude-code.png)](docs/distribution.md#install-in-claude-code) [![OpenCode](assets/installation/opencode.png)](docs/distribution.md#install-in-opencode)

## Workflows

These examples use the Thames Wharf site in Poplar, London.

<details>
<summary><strong>Site model creation</strong></summary>

Give the agent a site boundary or an existing Rhino model, and a project folder. For example:

> Use Rhino Site Data Model to build a 2D site model for this boundary. Add terrain and 3D buildings.

The site model joins mapped buildings, streets, land, water, and terrain in one `.3dm` file. It keeps the checked 2D source layers, adds 3D building volumes, and records source data and validation results.

### Sample outputs

The `.3dm` model has 344 layers of site data. The wide view shows the model and its main layer groups. The close views show the terrain mesh in section and building detail.

![Rhino view of the Thames Wharf model with its main layer groups](docs/images/poplar/model-context.png)

| Terrain mesh in section | Building detail |
| :---: | :---: |
| [![Rhino view of a cutaway from the terrain mesh](docs/images/poplar/model-terrain-section.png)](docs/images/poplar/model-terrain-section.png) | [![Close Rhino view of building volumes by the river](docs/images/poplar/model-building-detail.png)](docs/images/poplar/model-building-detail.png) |

</details>

<details>
<summary><strong>Site Analysis creation</strong></summary>

Use the checked site model for the map workflow:

> Use Vector Site Maps to make site analysis boards from this model.

### Sample outputs

The editable SVG maps share one frame. Each map contains its base map and one theme: figure ground, green structure, or blue structure.

| Figure ground | Green structure | Blue structure |
| :---: | :---: | :---: |
| [![Figure ground map of Thames Wharf](docs/images/poplar/Figure_ground.svg)](docs/images/poplar/Figure_ground.svg) | [![Green structure map of Thames Wharf](docs/images/poplar/Green_structure.svg)](docs/images/poplar/Green_structure.svg) | [![Blue structure map of Thames Wharf](docs/images/poplar/Blue_structure.svg)](docs/images/poplar/Blue_structure.svg) |

The export also includes the [three-board site analysis SVG](docs/images/poplar/Site_Analysis.svg). The workflow can save a review PDF. Native Illustrator files need an application that can save and check `.ai` files.

</details>

For release work, see the [package guide](docs/packaging.md).
