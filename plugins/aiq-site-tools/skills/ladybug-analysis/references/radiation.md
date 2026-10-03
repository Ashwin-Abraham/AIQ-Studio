# Radiation

Use `ladybug.epw.EPW`, a Ladybug `Wea`, and `ladybug_radiance.skymatrix.SkyMatrix` for the supplied weather file and period. Use `ladybug_radiance.study.radiation.RadiationStudy` with the target mesh and obstruction geometry. Convert Rhino geometry through `ladybug_rhino` inside Rhino; pass serialised Ladybug geometry to the external radiation runtime.

Record the weather source, station, location, selected hours, north convention, sky density, ground reflectance, mesh resolution, and sample offset. Check missing weather values while loading the selected period and report them instead of replacing them with zero. Use the documented north convention: counterclockwise from model +Y. Convert the caller's north convention explicitly.

Calculate cumulative incident radiation in kWh/m². Keep total, direct, and diffuse values separate where available. Report the area-weighted mean and range. Use face areas in m² when calculating total incident energy in kWh. Label the period and units on the coloured target mesh and legend.

This method excludes reflected solar energy from surrounding geometry. Record that limit in the result. Incident solar energy is not electrical yield or building energy use.

Deliver sample values with positions and source IDs, the coloured mesh, a legend, images, and the calculation settings. Store Radiance intermediate files in the operating-system temporary directory and remove them after the run.

API references: [SkyMatrix](https://www.ladybug.tools/ladybug-radiance/docs/ladybug_radiance.skymatrix.html), [RadiationStudy](https://www.ladybug.tools/ladybug-radiance/docs/ladybug_radiance.study.radiation.html).
