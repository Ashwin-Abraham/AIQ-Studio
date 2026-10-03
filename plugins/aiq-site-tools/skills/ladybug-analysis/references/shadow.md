# Seasonal shadows

Use the March equinox, June solstice, September equinox, and December solstice dates for the supplied year. Resolve the event dates from a reliable astronomical source and record that source. Convert each event to the site's local standard date. Do not assume that fixed calendar dates are exact each year. Name events by month so that hemisphere does not change their meaning.

For each date, calculate shadows at **08:00, 12:00, and 16:00 local standard time**, unless the caller supplies other times. Record the UTC offset. Apply daylight saving only when the caller requests civil clock times and supplies or resolves the applicable timezone rules.

Use `ladybug.sunpath.Sunpath` to calculate solar altitude, azimuth, and direction. Convert the caller's north direction to Ladybug's counterclockwise angle from model +Y. Cast rays from the target samples towards the sun, using the reverse of Ladybug's incoming sun vector. Use Rhino mesh intersections through `ladybug_rhino` for blockage.

Classify samples as sunlit or shaded. A surface facing away from the sun is shaded even if its ray reaches the sky. Include obstruction by other target faces; use a small recorded surface offset to avoid immediate intersection with the originating face. Calculate shaded-area percentage with target face areas, not sample counts.

When the sun is at or below the horizon, label the case `sun below horizon`. Do not report it as obstruction-caused shade. Keep that case in the 12-case output.

Deliver one labelled view and result layer for each case, plus a CSV with date, time basis, sun position, sample classifications, and area summaries. Use the same camera, extent, and colours across the 12 views. These are snapshots; do not convert them into daily sunlight hours.

API references: [Sunpath](https://www.ladybug.tools/ladybug/docs/ladybug.sunpath.html), [Rhino intersections](https://www.ladybug.tools/ladybug-rhino/docs/ladybug_rhino.intersect.html).
