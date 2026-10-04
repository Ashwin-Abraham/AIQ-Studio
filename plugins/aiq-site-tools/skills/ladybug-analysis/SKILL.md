---
name: ladybug-analysis
description: Run Ladybug radiation, seasonal shadow, or isovist analysis from caller-supplied Rhino geometry, layers, or observation points and heights. Also check, install, or repair the required Python, Ladybug, and Radiance setup.
---

# Ladybug analysis

Run only the selected analysis types. For setup-only requests, go directly to [Ladybug setup](references/setup.md) with the analysis type and host.

## Check Rhino availability

Confirm that Rhino 7 or later is installed.

## Ask for inputs

The caller can be a user or another agent. Use inputs already supplied. Ask for missing required inputs in one grouped request, then wait for the answers before the affected analysis. Do not infer target layers, obstruction layers, or the analysis type.

Ask for:

- Analysis type: `radiation`, `shadow`, or `isovist`. Accept `view` as isovist. Run multiple types only when the caller selects them.
- Rhino document and project folder.
- Target objects or full layer paths for radiation and shadow; observation points or a point layer for isovist.
- Obstruction objects or full layer paths. The caller must explicitly state if there are no obstructions.
- The required inputs for the selected type below.

| Type | Required inputs | Defaults to state to the caller |
| --- | --- | --- |
| Radiation | EPW weather file, analysis period, model north direction, target grid size | Use the EPW location and local standard time; report cumulative radiation in kWh/m². |
| Shadow | Latitude, longitude, UTC offset for local standard time, year, model north direction, target grid size | Use the two equinox and two solstice dates for that year, at 08:00, 12:00, and 16:00 local standard time. |
| Isovist | Observation points, height or height per point, height reference, maximum view distance, angular step | Use a horizontal 360-degree isovist at each observation height. A restricted field of view requires direction and angle. |

For isovists, ask whether heights are offsets above supplied point Z values, offsets above a named ground surface, or absolute model Z values. Ground-relative heights require the ground geometry. Keep each point paired with its height; one height can apply to all points. Weather and solar location are not required for isovists.

At script execution, confirm that Rhino has the caller's selected document open before reading geometry. If the document is missing or does not match, ask the caller to open or identify it and wait. Read model units from that document and record them with the inputs. Resolve empty or ambiguous selections with the caller. Preserve object IDs and full layer paths in the run record.

## Prepare the runtime

Follow [Ladybug setup](references/setup.md) and use its returned runtime and launch configuration. Continue with each analysis only when its required hosts and dependencies are available.

## Execute the selected analysis

1. Before creating project scripts, read [Python scripting guidance](../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). Before placing project outputs, read [project folder organisation](../rhino-site-data-model/references/PROJECT-FOLDER-ORGANISATION.md). Before editing Rhino, read [Rhino document editing guidance](../rhino-site-data-model/references/RHINO-DOCUMENT-EDITING-GUIDANCE.md).
2. Prepare only the supplied geometry. Preserve source objects. Mesh targets and obstructions at the recorded resolution. Keep target sample positions, face areas, outward normals, and source IDs together. Record the sample offset used to avoid a ray hitting its own source face. Include target geometry where it can obstruct other target samples. Report geometry that cannot be used; do not silently omit it.
3. Read only the selected method: [radiation](references/radiation.md), [shadow](references/shadow.md), or [isovist](references/isovist.md). Execute that method with the resolved inputs.
4. Write generated objects under `AIQ Climate::<analysis-type>::<run-id>`. Tag objects with the workflow and run IDs. Preserve source geometry and earlier runs. Save project scripts and run records under `artifacts/ladybug-analysis/`; put delivery files in `exports/`.
5. Deliver the result geometry, labelled images, CSV values, and run record. Record input selections, units, settings, sources, runtime versions, and failures. Report actual result counts and incomplete cases. Do not describe a failed or unexecuted analysis as complete.
