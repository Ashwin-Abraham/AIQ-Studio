# Radiance installation and repair

Use this reference for radiation setup checks and repairs. Radiance is a separate native engine; installing `ladybug-radiance` does not install it. For check-only requests, report missing components without installing them.

## Locate or install

1. Read the [runtime record](runtime-record.md). Inspect the recorded Radiance location first, then any caller-supplied location and the locations found by Ladybug's configuration API. Inspect existing installations without changing them. A directory alone is not proof that the engine can run.
2. Identify the operating system, architecture, engine version, and selected Ladybug package version. Reuse an engine that meets the selected package's documented requirements and the availability checks below. If version compatibility is not established, report it as unresolved instead of calling the pair tested.
3. If installation is needed, select a specific stable release from the [official Radiance installers](https://www.radiance-online.org/download-install/installation-information), which link to [LBNL release assets](https://github.com/LBNL-ETA/Radiance/releases). Record the exact release tag and asset URL. Match the operating system and architecture. Do not use a moving pre-release as the default.
4. Use the release's documented installation or archive method. On Windows, prefer `%LOCALAPPDATA%/AIQ Studio/runtimes/radiance/<release>-<architecture>/` when that method supports a custom destination. Preserve the release's `bin` and `lib` layout and licence files. If its installer cannot use this location, report the installation requirement; do not invent extraction commands or silently replace another installation.
5. Record the downloaded asset's SHA-256. Compare it with a publisher checksum when supplied; label a locally calculated hash as a record of the download, not publisher verification. Preserve working installations while preparing a new one. Mark a partial installation unusable.

## Configure the selected Python runtime

Use the selected engine root, with its `bin` and `lib` directories, in Ladybug's `folders.radiance_path`. Configure a fresh worker before importing `skymatrix`, `intersection`, or `study.radiation`: these modules can retain executable paths at import time. Restart the worker after a path change.

Keep the setup local to the worker. Supply required executable and library search paths through its process environment. Preserve inherited environment entries when adding paths. Do not edit the machine-wide environment or installed package source to configure this workflow. Record the selected paths under [the runtime record contract](runtime-record.md) so each worker can apply the same configuration.

Consult the selected version's [configuration API](https://www.ladybug.tools/ladybug-radiance/docs/ladybug_radiance.config.html) and [implementation](https://www.ladybug.tools/ladybug-radiance/docs/_modules/ladybug_radiance/config.html) if path handling differs. The configured root must resolve to the intended executable and library directories.

## Check availability

Check in the actual external Python worker. Do not create a sky matrix, test scene, or sample analysis.

- Confirm that Ladybug resolves the recorded engine and reads its version.
- Check `gendaymtx`, `oconv`, and `rcontrib` for the sky and intersection calculations. Check `obj2mesh` when Radiance mesh conversion is selected. Include executables used by the selected Ladybug version for discovery and version detection; these can include `rad`, `mkpmap`, or `rtrace`.
- Confirm that the required executables start using their documented version or help options, with a short timeout and closed standard input. Interpret help exit codes according to the tool; a nonzero help exit alone does not prove installation failure. Report loader errors, missing libraries, or timeouts by executable name.
- Confirm that required Radiance library resources are present for the selected calculation path.

The executable list comes from the [sky matrix implementation](https://www.ladybug.tools/ladybug-radiance/docs/_modules/ladybug_radiance/skymatrix.html) and [intersection implementation](https://www.ladybug.tools/ladybug-radiance/docs/_modules/ladybug_radiance/intersection.html). Check the installed version when its requirements differ.

## Complete or stop

Write the engine version, source, installation paths, required executables, check results, and time to the runtime record. Set Radiance status to `available` only when its availability checks pass. This status confirms dependency availability, not numerical accuracy or a tested simulation.

Return unresolved components and repair actions to Ladybug setup. Preserve working engine records when a replacement fails.
