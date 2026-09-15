# Python Scripting Guidance

## Purpose

This document defines how AIQ Studio workflows create, locate, structure, and run Python scripts.

Use project-specific scripts by default. Create reusable scripts only after completed projects show a stable, repeated need.

## Standard locations

```text
AIQ Studio/
|-- .agents/
|   `-- skills/
|       `-- <skill-name>/
|           |-- scripts/
|           |-- tests/
|           `-- requirements.txt
`-- Projects/
    `-- <project-name>/
        `-- artifacts/
            `-- <workflow-name>/
                `-- scripts/
```

- Put reusable workflow code in `.agents/skills/<skill-name>/scripts/`.
- Put project-specific and one-time code in `Projects/<project-name>/artifacts/<workflow-name>/scripts/`.
- Do not put user project scripts in `.agents/`.
- Do not modify an installed skill to hold values for one project.

## Python runtime environments

Use an AIQ Studio managed runtime or a reusable environment outside all project folders.

On Windows, use an application data location such as:

```text
%LOCALAPPDATA%/
`-- AIQ Studio/
    `-- runtimes/
        `-- python/
            `-- <environment-key>/
```

An environment key should identify the Python version and the dependency-lock content. Projects that need the same versions must use the same environment.

Follow these rules:

- Never create `.venv`, `venv`, or `site-packages` inside `AIQ Studio/Projects/`.
- Do not create a separate environment for each project.
- Do not install packages into the user's global Python environment.
- Do not run `pip install` from a workflow script.
- Provision and verify the environment before the project workflow starts.
- Reuse an existing environment when its Python version and dependency lock match.
- Create a new environment only when no compatible managed environment exists.
- Do not store the absolute environment path in `project.json` or another portable project file.
- If environment creation fails, remove the incomplete environment or mark it as unusable.

Environment setup is application infrastructure. It is not a project artifact.

## Project-specific scripts

Keep a script project-specific when it contains or depends on:

- A project path, file name, or artifact path
- A project-specific value or local correction
- A one-time migration, recovery, or cleanup operation
- Experimental behavior that has not been used successfully on other projects
- A data transformation that is unique to the project
- Assumptions that cannot form a stable interface

Project-specific scripts can call reusable skill scripts. They must supply project values through arguments or configuration instead of changing the reusable script.

Project scripts do not need a general interface for hypothetical future uses. They must still validate inputs, keep writes inside the selected project, and report failures clearly.

## When to create a reusable script

Prefer a project-specific script until reuse is supported by evidence.

Consider promotion to a reusable skill script when:

- At least two completed projects use substantially the same operation.
- A further use is reasonably likely.
- The inputs, outputs, invariants, and failure modes can form a stable interface.
- Project differences can be supplied as arguments, configuration, or adapters.
- The common code has no embedded project values, machine paths, or project-only corrections.
- The behavior can be tested with small fixtures outside a specific project.
- One maintained implementation will give clear leverage across projects.

Do not promote a script only because it is long or might be useful one day.

When you assess earlier projects:

1. Read the earlier project scripts and reports as read-only evidence.
2. Do not edit, reorganize, or migrate an earlier project.
3. Identify the behavior that is common across the completed projects.
4. Create the reusable implementation in the applicable skill.
5. Preserve the earlier project scripts so that their results remain reproducible.
6. Use the reusable implementation for new projects and for an active project only when the user requests the change.

## Reusable module design

A reusable module must put useful behavior behind a small interface. Split code at real seams, such as configuration, core behavior, external systems, and output formatting.

Do not use a line-count limit as the main reason to split a file. Do not create shallow files that only pass arguments to another function.

Split a script when it:

- Mixes command-line handling with core processing logic
- Connects to more than one external system
- Combines input handling, transformation, external-system access, and output generation in one implementation
- Contains behavior that needs independent tests
- Has several parts that change for different reasons
- Makes callers learn implementation details that a smaller interface can hide

A typical reusable workflow can use this structure:

```text
<skill-name>/
|-- scripts/
|   |-- run_workflow.py
|   `-- <module-name>/
|       |-- __init__.py
|       |-- config.py
|       |-- core.py
|       `-- adapters.py
|-- tests/
`-- requirements.txt
```

Typical responsibilities are:

- `run_workflow.py` parses arguments and coordinates the workflow.
- `config.py` reads and validates configuration and paths.
- `core.py` contains the main reusable behavior.
- `adapters.py` connects the core behavior to external systems when an adapter is necessary.

This is a common starting point, not a required file count. Add, combine, or omit modules when the workflow has different seams.

## Script interfaces

Reusable scripts must:

- Accept project paths and settings through command-line arguments or validated configuration.
- Use `pathlib.Path` for file-system paths.
- Avoid hard-coded project values and machine-specific paths.
- State required inputs, created outputs, invariants, and failure modes.
- Validate inputs before a destructive or expensive operation.
- Return structured results from core functions where practical.
- Use clear nonzero exit codes for command-line failures.
- Put executable command-line behavior in `main()`.
- Use an `if __name__ == "__main__":` guard.
- Avoid network calls, file writes, or environment changes during module import.
- Support repeatable execution without corrupting valid existing outputs.

Accept dependencies through function or class inputs when this makes the behavior easier to test. Keep external-system details behind adapters when two or more implementations exist.

## Dependencies

- Declare reusable dependencies in the owning skill's `requirements.txt` or dependency lock.
- Keep optional dependencies separate when they support only one workflow mode.
- Do not copy installed packages into a project folder.
- Do not download dependencies during a normal workflow run.
- Report a missing dependency with the package name and required version.
- Keep environment provisioning separate from workflow execution.

## Temporary files and generated caches

Use the operating-system temporary directory for temporary downloads, conversion fragments, and task-scoped runtime files. Remove them when the workflow finishes or fails.

Do not include these items in a project:

```text
.venv/
venv/
site-packages/
__pycache__/
*.pyc
*.pyo
```

## Testing

Before a project-specific script becomes reusable, add:

- Unit tests for core processing behavior
- Small fixture data that does not depend on a live project
- An integration test for the public interface
- Tests for invalid inputs and partial failures
- A test that confirms writes stay inside the selected output root
- A test that confirms the workflow creates no environment or Python cache in the project

Test through the module interface. Do not make callers or tests depend on internal helper functions without a clear reason.
