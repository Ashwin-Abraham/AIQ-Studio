# Building placement

Use Overture `Building` and `BuildingPart` fields before fallback rules. Keep the property-level source for each height value.

## Reference ground elevation

Sample the terrain inside and along the building footprint. Use the highest valid sample as the flat reference ground elevation. Record the sample method, terrain source, and sample count.

If terrain data is absent, use Z = 0 and state that the building has no terrain placement.

## Main building height

Use this priority:

1. Explicit `height`.
2. `num_floors × 3.5 m`.
3. Three floors, or 10.5 m, for a normal occupied building.
4. One floor, or 3.5 m, for a garage, shed, service building, or small outbuilding.
5. No default volume for a roof, carport, or shelter.

If an explicit `roof_height` accompanies a floor-derived height, add it. Do not add it to an explicit total `height`.

Store `height_method`, `height_is_estimated`, floor-to-floor value, and the input fields on the volume.

## Main mass and terrain skirt

- Create the building mass from one flat reference ground elevation.
- Keep its roof horizontal.
- Generate its volume in world `+Z`.
- Do not use polygon winding to select the extrusion direction.
- Create a separate skirt from the flat mass base down to the sampled terrain along each footprint ring.
- Put skirts on `AIQ Site::3D::Buildings::Terrain Skirts`.

The skirt is terrain-adjustment geometry. It is not part of the source building height.

## Building parts

Every part references its parent with `building_id`. Use this placement order:

### Bottom offset

1. Explicit `min_height`.
2. `min_floor × 3.5 m`.
3. Zero.

### Part height

1. Explicit `height`.
2. `num_floors × 3.5 m`.
3. One floor, or 3.5 m.

Calculate:

```text
part_bottom_z = reference_ground_z + bottom_offset
part_top_z = part_bottom_z + part_height
```

An explicit metric value takes priority over a floor-derived value. If both exist and differ beyond the model tolerance, use the metric value and record the conflict.

If `is_underground` is true and there is no reliable depth or bottom elevation, keep the footprint on `Underground::Vertical Position Unresolved`. Do not create a volume.

When valid part volumes exist, show them by default. Keep the complete parent volume as a hidden parent envelope. This prevents two visible masses from occupying the same space while retaining both representations.
