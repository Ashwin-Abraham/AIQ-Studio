---
name: ladybug-analysis
description: Run Ladybug radiation, seasonal shadow, or isovist analysis from caller-supplied Rhino geometry, layers, or observation points and heights. Also check whether the required Ladybug setup is available.
---

# Ladybug analysis

Run only the analysis type selected by the caller. Keep installation details in the separate installation skill.

## Check Rhino availability

Rhino 8 is required for radiation, shadow, and isovist analysis, including setup-only checks through this skill. Before collecting analysis inputs or checking Ladybug dependencies, use the existing Rhino connection to make a read-only call inside Rhino. Confirm that the session responds and can execute Python 3 with RhinoCommon. An installed application or a visible window alone is not sufficient.

If Rhino is absent, closed, unsupported, unreachable, or unable to execute the required Python call, reply `Rhino unavailable` and stop. Do not install dependencies, start an analysis, or use an offline geometry fallback. If the connection is lost during a run, stop further work and report `Rhino unavailable`; identify any partial outputs already created.

Continue only after the live session check succeeds. This check does not run a sample analysis or change the document.

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

Confirm that the connected session has the caller's selected document open before reading geometry. If the document is missing or does not match, ask the caller to open or identify it and wait. Read model units from that document and record them with the inputs. Resolve empty or ambiguous selections with the caller. Preserve object IDs and full layer paths in the run record.

## Check Ladybug availability

After the Rhino check succeeds, check the dependencies. This is not an analysis pre-check. When the caller asks to check setup only, ask only for the intended analysis type and host; skip analysis inputs and execution.

Read the [runtime record contract](../ladybug-install/references/runtime-record.md) to locate the managed runtime. Use its recorded paths and check imports for the selected type in the actual host: `ladybug` and `ladybug_geometry`; `ladybug_radiance` and its configured Radiance executables for radiation; `ladybug_rhino` and RhinoCommon inside Rhino for geometry operations. For radiation, apply the recorded Radiance root through `ladybug_radiance.config.folders.radiance_path` in a fresh worker before importing analysis modules, and apply the recorded process environment. Reuse a successful check from the current session if the host and runtime have not changed.

Read and follow [Ladybug installation](../ladybug-install/SKILL.md) only if the required runtime, package, or executable is missing or incompatible. If the caller requested a check only, report missing setup without installing it. Keep the installation skill unloaded when setup is available. Do not run fixture calculations, sample analyses, or test scenes before the requested analysis.

## Execute the selected analysis

1. Before creating project scripts or choosing a runtime, read [Python scripting guidance](../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). Before placing project outputs, read [project folder organisation](../rhino-site-data-model/references/PROJECT-FOLDER-ORGANISATION.md). Before editing Rhino, read [Rhino document editing guidance](../rhino-site-data-model/references/RHINO-DOCUMENT-EDITING-GUIDANCE.md).
2. Prepare only the supplied geometry. Preserve source objects. Mesh targets and obstructions at the recorded resolution. Keep target sample positions, face areas, outward normals, and source IDs together. Record the sample offset used to avoid a ray hitting its own source face. Include target geometry where it can obstruct other target samples. Report geometry that cannot be used; do not silently omit it.
3. Read only the selected method: [radiation](references/radiation.md), [shadow](references/shadow.md), or [isovist](references/isovist.md). Execute that method with the resolved inputs.
4. Write generated objects under `AIQ Climate::<analysis-type>::<run-id>`. Tag objects with the workflow and run IDs. Preserve source geometry and earlier runs. Save project scripts and run records under `artifacts/ladybug-analysis/`; put delivery files in `exports/`.
5. Deliver the result geometry, labelled images, CSV values, and run record. Record input selections, units, settings, sources, runtime versions, and failures. Report actual result counts and incomplete cases. Do not describe a failed or unexecuted analysis as complete.
