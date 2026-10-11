# AIQ Urban concepts and classes

AIQ Urban supports master plans and conceptual building massing.

- A `Transit` has a centreline, type, and width. AIQ Urban offsets the centreline to form a corridor.
- Enclosed spaces in transit corridors form `Parcel` objects. `ParcelBoundary` objects can split or enclose them. Each `Parcel` has one `Use`. Parcels are regenerated when transit corridors or parcel boundaries change, so a `Parcel.Id` can change.
- A `Building` has a mass and `FloorPlate` objects. Each `FloorPlate` can have a different `Use`.
- `UrbanModel.Instance.Uses` is the shared use list. Each `Use` has an `Id`, `Name`, and `Color`. Assign uses from this list.
- A `Zone` is a named study boundary. It reports metrics for elements whose representative points fall inside it.
