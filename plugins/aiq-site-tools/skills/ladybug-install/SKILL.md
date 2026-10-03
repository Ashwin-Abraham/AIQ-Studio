---
name: ladybug-install
description: Install or repair Ladybug Python dependencies for AIQ Studio when setup is requested or the Ladybug analysis skill reports missing or incompatible dependencies.
---

# Ladybug installation

Prepare the runtime for the requested analysis: radiation, shadow, or isovist. Installation does not start an analysis or change model geometry.

## Runtime setup

1. Read the shared [Python scripting guidance](../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md). Use its managed environment method and locations. Keep runtime files outside all project folders.
2. Resolve the requested analysis and execution host. Radiation uses external CPython. Shadow and isovist calculations use Ladybug geometry and Rhino mesh intersections inside Rhino 8 Python 3. The external Python environment does not supply RhinoCommon.
3. Select compatible versions from the official package metadata. Use `ladybug-core` (import `ladybug`) and `ladybug-geometry` (import `ladybug_geometry`). Add `ladybug-radiance` for radiation. Add `ladybug-rhino` for Rhino geometry conversion and intersections. Do not substitute the unrelated package named `ladybug`.
4. Resolve and save exact direct and transitive dependency versions in a lock under the AIQ Studio runtime store. Include the Python version, platform, and dependency lock hash in the environment key. Reuse a matching environment. Otherwise create a new managed environment with the selected Python executable and install the locked dependencies through that environment's `python -m pip`. Keep installation separate from analysis scripts.
5. For Rhino operations, make the compatible pure Python Ladybug packages available to Rhino's Python 3 runtime through its supported package mechanism or a managed dependency directory for that host. Keep this directory outside projects. Do not add an external environment's complete `site-packages` to Rhino's search path: its Python version and native dependencies can differ. Record the Rhino Python version and its dependency lock separately.
6. For radiation only, read [Radiance installation](references/radiance-installation.md) when the engine is missing, incompatible, or needs configuration repair. Reuse an available compatible engine. Skip this reference for shadow and isovist setup.
7. Check dependency consistency and import the required modules in each actual execution host. Check the required Radiance executable availability for radiation. Do not run a sample analysis or a test scene. Mark an incomplete environment unusable and report the failed package or executable and its repair action.

## Completion

Write the [runtime record](references/runtime-record.md) when setup succeeds or fails. Return the environment key, Python version, dependency lock hash, package versions, supported analysis types, and any unresolved setup failure. Keep executable paths in the local record; portable project files store only the environment key and versions. Resume the caller only when the requested dependencies are available. Do not start an analysis when the request is installation only.

## Sources

Read the relevant source when selecting package versions or configuring a host:

- [Ladybug core](https://github.com/ladybug-tools/ladybug): weather and sun position library.
- [Ladybug geometry](https://github.com/ladybug-tools/ladybug-geometry): geometry library.
- [Ladybug Rhino](https://github.com/ladybug-tools/ladybug-rhino): Rhino host integration and dependencies.
- [Ladybug Radiance](https://github.com/ladybug-tools/ladybug-radiance): radiation dependencies.
