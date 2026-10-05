# Terrain Slope

First complete the terrain check in the [terrain workflow](terrain-analysis.md). Show the angle of the ground surface from horizontal in degrees.

## Rhino specification

1. Use the analysis triangles with XY and Z in the same unit. For each triangle, calculate the face normal `(nx, ny, nz)` from its edges. Calculate `slope_deg = atan2(sqrt(nx*nx + ny*ny), abs(nz)) * 180 / pi`. A horizontal face is 0 degrees. Use face normals, not smoothed vertex normals.
2. Assign each valid face to a band below. Keep the original triangle as the Rhino result geometry. Missing and rejected faces have no slope value; they are not flat ground.
3. Check all values are finite and between 0 and 90 degrees. Check the calculation with a horizontal test triangle (0 degrees) and a test triangle with equal rise and horizontal run (45 degrees). Keep test geometry out of the results.
4. Check that result faces cover the valid terrain plan area once. Record plan area per band and the plan-area-weighted mean slope within the site boundary. State that values depend on terrain resolution and triangulation.

## SVG specification

Export the checked face polygons through the shared terrain workflow. Adjacent polygons in the same band may be joined if their source IDs remain in the result record. Use solid fills with no internal strokes.

| Slope angle | Colour |
| --- | --- |
| 0 to less than 2 degrees | `#FFFFCC` |
| 2 to less than 5 degrees | `#FFEDA0` |
| 5 to less than 10 degrees | `#FED976` |
| 10 to less than 15 degrees | `#FEB24C` |
| 15 to less than 25 degrees | `#FD8D3C` |
| 25 to less than 35 degrees | `#F03B20` |
| 35 to less than 40 degrees | `#D7191C` |
| 40 to less than 45 degrees | `#BD0026` |
| 45 to 90 degrees, inclusive | `#800026` |

Label the legend **Terrain slope (degrees)**. Keep these breaks for comparison maps and show a No data key where needed. State the source resolution. These are display bands, not access or construction limits.

Include this short conversion key on every slope board. Angles are rounded.

| Angle | Slope | Height : horizontal distance |
| --- | --- | --- |
| 5.7° | 10% | 1:10 |
| 26.6° | 50% | 1:2 |
| 45° | 100% | 1:1 |

Add: **1:10 means 1 m up for every 10 m across.**
