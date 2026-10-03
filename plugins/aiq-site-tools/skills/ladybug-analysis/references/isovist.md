# Isovists from points and heights

An isovist is the visible region from one observation point. Use a horizontal plane at the resolved observation height. A 3D visible volume is a separate method and needs an explicit caller request.

Resolve the eye position from each supplied point and height reference. For ground-relative heights, find the ground elevation on the named surface at the point's XY position, then add the height. Ask the caller to resolve missing or ambiguous ground intersections. Do not add a relative height to an absolute eye elevation.

Generate horizontal unit ray directions with Ladybug geometry. Use the supplied angular step across 360 degrees, or across the caller's field of view. Cast each ray against the obstruction mesh with `ladybug_rhino.intersect.intersect_mesh_rays_distance` inside Rhino. Take the nearest nonnegative hit within the maximum distance. If there is no hit, end the ray at the maximum distance and mark it as range-limited. Handle the installed API's no-hit return value explicitly.

Join endpoints in angular order to make a closed isovist polygon. For a restricted field of view, close the polygon through the observation point. Keep the polygon at eye height; a plan projection can be supplied as an additional output. Report a point inside an obstruction or on its surface as unresolved instead of inventing a visible region.

Deliver the polygon, observation marker, optional rays, and a labelled plan image for each point and height. Export visible area in m², polygon perimeter in m, minimum/mean/maximum sampled ray distance in m, and the fraction of rays limited by range. Store point IDs, eye coordinates, height reference, angular step, view range, and obstruction IDs with the values. A range-limited boundary is not a physical wall. Angular sampling gives an approximation and can miss small gaps; state the sampling step in each result.

API reference: [Rhino distance intersections](https://www.ladybug.tools/ladybug-rhino/docs/ladybug_rhino.intersect.html#ladybug_rhino.intersect.intersect_mesh_rays_distance).
