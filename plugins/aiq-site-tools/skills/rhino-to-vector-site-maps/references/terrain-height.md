# Terrain Height

First complete the terrain check in the [terrain workflow](terrain-analysis.md). Show ground elevation, not building height.

## Rhino specification

1. Use terrain vertex Z values in metres. Apply a documented vertical origin offset when the model uses local Z. State the vertical datum. If the datum is unknown, label values **Local model elevation (m); datum unknown** and record the limitation.
2. Find the minimum and maximum within the map extent. Select up to ten rounded equal-interval bands that include both extremes. Use fewer bands for a small range and one band for constant elevation. Record the breaks; retain negative elevations.
3. Split each analysis triangle at the band elevation planes. Interpolate linearly along its edges. Retain the resulting polygons in Rhino at their terrain elevations. Use lower-inclusive, upper-exclusive bands, with the maximum in the final band.
4. Check that band polygons cover the valid terrain plan area without gaps or overlaps. Check their vertex elevations against the assigned band. Record minimum and maximum elevation, relief (`maximum - minimum`), and plan area per band within the site boundary.

## SVG specification

Export the checked band polygons through the shared terrain workflow. Use this sequence from low to high: `#F7FCFD`, `#E5F5F9`, `#CCECE6`, `#A8DDB5`, `#7BCCC4`, `#4EB3D3`, `#2B8CBE`, `#0868AC`, `#084081`, `#041F4A`. For fewer bands, sample the sequence in order; for one band, use `#7BCCC4`.

Use solid fills with no internal strokes. Label the legend **Terrain elevation (m)** and state the datum, or use the local elevation label above. Show all band limits and a No data key where needed. Include the source resolution and site elevation range. Use the same breaks for comparison maps.
