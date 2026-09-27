# AIQ Studio

AIQ Studio provides AI workflows for architecture, engineering, and construction. **AIQ Site Tools** has two skills: one builds a Rhino site model, and one makes vector site analysis maps from its checked 2D data.

**Installation:** See the [AIQ Site Tools installation guide](docs/distribution.md).

## Start a site project

Give the agent a site boundary or an existing Rhino model, and a project folder. For example:

> Use Rhino Site Data Model to build a 2D site model for this boundary. Add terrain and 3D buildings.

Then use the checked model for the map workflow:

> Use Vector Site Maps to make site analysis boards from this model.

## Workflow and example outputs

This example uses the Thames Wharf site in Poplar, London. The site model joins mapped buildings, streets, land, water, and terrain in one `.3dm` file. It keeps the checked 2D source layers, adds 3D building volumes, and records source data and validation results.

### 1. Review the Rhino site model

These close views use the same elevated Rhino camera. Layer visibility and display mode change to show each part of the model.

![Close Rhino view of the Thames Wharf site model, with building volumes beside the river](docs/images/poplar/model-context.png)

| Building volumes and terrain | Streets, land and water with buildings hidden |
| :---: | :---: |
| [![Rhino view of building volumes and terrain](docs/images/poplar/model-buildings.png)](docs/images/poplar/model-buildings.png) | [![Rhino view of streets, land and water](docs/images/poplar/model-landscape.png)](docs/images/poplar/model-landscape.png) |

### 2. Make vector site maps

The map workflow uses one checked 2D source and one shared map frame. Each SVG contains its base map and theme artwork. The boards show figure ground, green structure, and blue structure. Select a map to open the full SVG.

| Figure ground | Green structure | Blue structure |
| :---: | :---: | :---: |
| [![Figure ground map of Thames Wharf](docs/images/poplar/Figure_ground.svg)](docs/images/poplar/Figure_ground.svg) | [![Green structure map of Thames Wharf](docs/images/poplar/Green_structure.svg)](docs/images/poplar/Green_structure.svg) | [![Blue structure map of Thames Wharf](docs/images/poplar/Blue_structure.svg)](docs/images/poplar/Blue_structure.svg) |

The export also includes the [three-board site analysis SVG](docs/images/poplar/Site_Analysis.svg). The workflow can save a review PDF. Native Illustrator files need an application that can save and check `.ai` files.

For release work, see the [package guide](docs/packaging.md).
