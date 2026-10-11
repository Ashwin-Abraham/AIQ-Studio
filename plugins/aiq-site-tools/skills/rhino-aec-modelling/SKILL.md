---
name: rhino-aec-modelling
description: Model zones, roads, parcels, buildings, and uses in an open Rhino document through AIQ Urban and Rhino Python.
---

# Rhino AEC Modelling

## Install AIQ Urban if needed

If the `AIQUrban` command is unavailable, run Rhino's `_PackageManager`. Search the Online tab for `AIQ_Urban`, select a compatible version, and click Install. Ask the user for permission to save the current Rhino file and restart Rhino with that file to load the package.

## Using AIQ Urban

Read [AIQ Urban concepts and classes](references/aiq-urban-concepts-and-classes.md).

Start AIQ Urban in the target Rhino document. Run Python in that Rhino session.

1. Check the active document, units, and existing model. Make or find the source Rhino objects.
2. Read [AIQ Urban actions](references/aiq-urban-actions.md) for the message fields and object types you need.
3. Use [aiq_urban.py](scripts/aiq_urban.py) to pass the object IDs to AIQ Urban. Apply one clear model change at a time.
4. Check the returned model state or export status. Inspect the changed Rhino model before the next change.
