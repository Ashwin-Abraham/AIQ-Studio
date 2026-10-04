# Ladybug runtime record

Ladybug setup owns this record of runtime paths, versions, and check results; it is not proof of analysis accuracy.

## Location and selection

On Windows, store the local registry at `%LOCALAPPDATA%/AIQ Studio/runtimes/ladybug/runtime-registry.json`. Keep runtime locks and installation data outside project folders. For another supported operating system, use its per-user application data directory with the same `AIQ Studio/runtimes/ladybug/` suffix and record the resolved location in the setup response.

The JSON root has `schemaVersion: 1` and `environments`, an object keyed by the managed environment key. Each entry describes one selected external Python environment and its associated Rhino package setup. Keep entries for other environments when updating the registry. Write through a temporary sibling file, then replace the registry after the complete JSON has been written.

## Entry fields

| Field | Value |
| --- | --- |
| `platform`, `architecture` | Operating system and processor architecture. |
| `python` | Object with `version`, absolute `executable`, `lockPath`, `lockSha256`, and `packages` mapping package names to exact versions. |
| `rhino` | Object with `version`, `pythonVersion`, `packageLocation`, `lockPath`, `lockSha256`, `packages`, and `status`. This records package setup, not proof of a live connection. |
| `radiance` | `null` when not configured; otherwise the object defined below. |
| `analysisStatus` | Object with `radiation`, `shadow`, and `isovist`, each set to `available`, `unavailable`, or `unchecked`. |
| `checkedAt` | UTC timestamp in ISO 8601 format. |
| `failures` | Array of objects with `component`, `message`, and `repairAction`; empty if none. |

The `radiance` object contains `version`, absolute `root`, `binPath`, `libPath`, `sourceUrl`, `releaseTag`, `assetSha256`, `requiredExecutables`, `processEnvironment`, `status`, and `checkedAt`. `requiredExecutables` is an array of names for the selected calculation mode. `processEnvironment` maps variable names to ordered path entries to prepend in the worker. Preserve the worker's existing entries. Status is `available`, `unavailable`, or `unchecked`.

For a reused engine of unknown origin, set unavailable source metadata to `null` and record that its origin was not verified. Do not invent a release URL or checksum. Record failed installation attempts in `failures`; do not replace a working engine entry with a partial installation.

## Status and configuration

Stored status is the last check result. Setup verifies paths, versions, and required imports in the selected host before reuse. Record untested hosts as `unchecked`; a missing Radiance entry affects only radiation. This record does not require a live control connection to Rhino.

Setup returns the selected paths and launch configuration to analysis. Each fresh radiation worker applies the Radiance root and process environment before importing analysis modules. Keep absolute paths in this local record; portable project files store environment keys and versions.
