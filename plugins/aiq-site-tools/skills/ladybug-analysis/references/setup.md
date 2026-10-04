# Ladybug setup

Use this workflow for setup checks and before analysis; reuse a successful check while the host and runtime are unchanged. A check-only request reports missing components without installing them. Setup does not run an analysis or change model geometry.

1. Resolve the analysis type and execution host. Read the [runtime record](runtime-record.md) for saved paths and versions. Prefer the caller's environment key, otherwise a compatible entry; ask only if equally suitable entries remain. A missing record starts discovery, not a failed installation.
2. Check Python in the selected host. Reuse a compatible runtime; if external Python needs installation or an environment, follow the shared [Python guidance](../../rhino-site-data-model/references/PYTHON-SCRIPTING-GUIDANCE.md) and the selected Python version's official installation instructions. Keep managed runtimes outside projects.
3. Check the required imports and versions using [Ladybug packages](ladybug-packages.md). Install or repair only missing or incompatible dependencies. Confirm host compatibility rather than treating the Rhino installation check as proof that packages can run.
4. For radiation, follow [Radiance setup](radiance-installation.md) to check the engine and configure the worker; install or repair it only when needed. Other analysis types skip this step.
5. Update the runtime record with the checks and any failures. Return the environment key, versions, usable analysis types, resolved runtime paths, and launch configuration to the caller. Return unresolved components with a repair action. Portable project records retain only keys and versions.

Checks use imports and executable version/help calls, not sample calculations. If an in-Rhino check must be run manually, provide a script that saves its results and leave that host unchecked until the results are available.
