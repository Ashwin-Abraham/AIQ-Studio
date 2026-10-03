# Ladybug runtime record

This contract lets installation write setup data and analysis read it without loading installation instructions. It records availability only; it does not certify analysis results.

## Location and selection

On Windows, store the local registry at `%LOCALAPPDATA%/AIQ Studio/runtimes/ladybug/runtime-registry.json`. Keep runtime locks and installation data outside project folders. For another supported operating system, use its per-user application data directory with the same `AIQ Studio/runtimes/ladybug/` suffix and record the resolved location in the setup response.

The JSON root has `schemaVersion: 1` and `environments`, an object keyed by the managed environment key. Each entry describes one selected external Python environment and its associated Rhino package setup. Keep entries for other environments when updating the registry. Write through a temporary sibling file, then replace the registry after the complete JSON has been written.

Use the environment key from the caller or project record when supplied. Otherwise select an entry matching the current host, package requirements, and requested analysis. Ask the caller when multiple entries remain equally suitable. A missing or unreadable entry means setup is unresolved. A check-only request reports it; an analysis request follows the installation pointer in the analysis skill.

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

## Reader rules

Treat stored status as the last observed result. Confirm that the paths, versions, and required imports still apply in the current host. Reuse a current-session check only while the runtime and host are unchanged. Apply Radiance paths before importing analysis modules in a fresh external worker. A new calculation mode can require additional executables.

Read only the dependency data needed for the selected analysis. A missing Radiance entry does not affect shadow or isovist availability. Keep local absolute paths out of portable project metadata; projects store environment keys and version information only. The analysis skill's live Rhino check remains required regardless of recorded status.
