# AIQ Urban actions

Run `scripts/aiq_urban.py` in Rhino Python after you start AIQ Urban in the target document. Keep that document active. Pass object IDs from it. The helper requires a non-empty ID list for each geometry action.

| `message_type` | Required fields | Object IDs |
| --- | --- | --- |
| `transit` | `roadWidth` | One or more centreline curves. This action makes roads. |
| `building` | `floorCount`, `floorHeight`, `manual_generationType` (`Footprint` or `Mass`) | Footprint curves, or mass Breps and Extrusions. |
| `zone` | `name` | Exactly one boundary curve. |
| `divider` | None | One or more parcel boundary curves. |
| `landuse` | `use` | One or more parcel, building, or floor plate objects. The handler accepts curves and Breps. |
| `landuselistedit` | `useEditType` (`add`, `edit`, or `remove`), `name`, `color`, `id` when editing or removing | None. |
| `exportexcel` | `filePath` | None. Pass a full path to avoid a save dialog. |

Use the property names shown in the table. Create a use before you assign it. The `color` field accepts `#RRGGBB` or `R,G,B`.

```python
from aiq_urban import send

state = send(
    "building",
    object_ids=[footprint_id],
    floorCount=4,
    floorHeight=3.0,
    manual_generationType="Footprint",
)
print(state.Type, state.StudyAreaDataForUI)
```

`send` returns the .NET message from AIQ Urban. Geometry actions return `ModelStateMessage`, which has uses and study metrics. It does not list the IDs of each new urban object. `exportexcel` returns a status and file path. Handler errors raise an exception in Python.
