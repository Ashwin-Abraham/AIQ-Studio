# Rhino Document Editing Guidance

## Purpose

This document defines the base rules for workflows that edit a Rhino document.

Prefer to open the target Rhino document before an editing workflow starts. If the document does not exist, create it and then open it in Rhino before editing.

Workflow-specific skills can add stricter geometry, layer, metadata, and validation rules.

## Confirm the target document

Before an edit:

- Confirm that Rhino has an active document.
- Capture the `RhinoDoc` reference once and continue to use that reference.
- Record its file path and `RuntimeSerialNumber`.
- Check whether the document has unsaved changes.
- Check the document units, absolute tolerance, angle tolerance, axes, and georeferencing.

Do not repeatedly resolve `RhinoDoc.ActiveDoc` during one operation. The active document can change while a command runs. Use the captured document reference and confirm its runtime serial number before each mutation stage.

Ask the user before editing when the active document has unsaved changes that the workflow would need to save, discard, or replace.

Do not close or save an unrelated document.

## Choose the editing method

Use RhinoCommon inside Rhino for live document changes. Offline libraries can prepare geometry or create a separate `.3dm`, but they do not provide progressive edits to the open Rhino document.

Use this separation:

1. Prepare and validate input data without changing the document.
2. Pass the prepared data to one maintained Rhino editing entry point.
3. Apply document changes through the captured `RhinoDoc`.
4. Report progress, allow cancellation, and redraw during the edit.

Do not create a new project-specific bridge script only to connect an external process to Rhino. Prefer a maintained runner that accepts the target document identity, operation name, input path, and settings.

Avoid hard-coded model paths in reusable Rhino editing code.

## Progressive editing

Divide a large edit into logical stages and object batches. A typical sequence is:

1. Validate the prepared input.
2. Create or update required document definitions, such as layers, materials, blocks, and annotation styles.
3. Add or update simple reference geometry.
4. Add or update primary geometry in batches.
5. Apply object attributes and metadata.
6. Run document-level validation.
7. Save only when the agreed save policy requires it.

For each visible stage or batch:

- Add or update a bounded set of objects.
- Update the Rhino status-bar progress meter.
- Redraw the document views.
- Check for user cancellation.
- Confirm that the captured document is still the target.
- Record created, updated, skipped, and failed object counts.

Select batch size from elapsed time and Rhino responsiveness. Do not require one fixed object count for all geometry types. Expensive meshes can need smaller batches than points or curves.

Do not disable redraw for the complete operation when progressive display is required. Redraw at useful intervals instead of after every object.

Do not use one large `RhinoDoc.Import` operation when the user must see geometry appear progressively. Read or prepare the source content first, map its document definitions, and add its objects to the active document in batches. Use `Import` only when an atomic, all-at-once result is acceptable.

## Rhino interface responsiveness

Run document mutations on Rhino's main interface thread. Keep expensive data parsing and geometry preparation outside the mutation loop when RhinoCommon permits it.

For long operations:

- Show the current stage and percentage in Rhino.
- Keep the status text short.
- Check for Escape between batches.
- Stop at a safe batch boundary when the user cancels.
- Always hide or release the progress meter when the operation finishes or fails.

Use Rhino's documented interfaces for view redraw, progress display, cancellation, and main-thread invocation:

- [ViewTable.Redraw](https://developer.rhino3d.com/api/rhinocommon/rhino.docobjects.tables.viewtable/redraw)
- [StatusBar.ShowProgressMeter](https://developer.rhino3d.com/api/rhinocommon/rhino.ui.statusbar/showprogressmeter)
- [RhinoApp.EscapeKeyPressed](https://developer.rhino3d.com/api/rhinocommon/rhino.rhinoapp/escapekeypressed)
- [RhinoApp.InvokeOnUiThread](https://developer.rhino3d.com/api/RhinoCommon/html/M_Rhino_RhinoApp_InvokeOnUiThread.htm)

## Undo, cancellation, and rollback

Set the undo policy before document mutation.

Use one undo record per logical stage by default. If a stage fails or the user cancels it, undo the incomplete stage and keep only completed, validated stages.

Use one undo record for the complete operation when the request must be atomic. In that case, roll back all changes if any required stage fails.

Follow these rules:

- Give each undo record a clear description.
- Check that `BeginUndoRecord` returned a valid record number.
- End only a record that this workflow started.
- Close an open record in `finally` logic.
- Do not leave partial objects from an incomplete batch.
- State whether cancellation kept completed stages or rolled back the complete operation.

When Rhino already records undo for the running command, use that command record instead of starting a conflicting record.

See [RhinoDoc.BeginUndoRecord](https://developer.rhino3d.com/api/rhinocommon/rhino.rhinodoc/beginundorecord).

## Ownership and repeatable edits

Generated geometry must have a clear owner. Use a dedicated root layer or another explicit ownership scheme for each workflow.

Make the replacement scope clear before deleting existing generated objects.

## Units, tolerances, and coordinates

Use the open document's valid units, tolerances, axes, and georeferencing. Transform incoming geometry into that coordinate and unit system before insertion.

## View and selection state

Restore the active view, projection, selection, layer states, and display settings after a temporary visual check. Do not save temporary review settings unless they are part of the requested result.

## Validation

Validate each completed stage enough to prevent invalid state from accumulating. Run full validation after the final mutation.

When the workflow saves the document, confirm that the saved `.3dm` can be read again. Inspect useful views and report all failed checks. Do not describe a failed check as successful.

## Workflow-specific guidance

Keep domain rules in the applicable workflow skill. Examples include site boundaries, Overture taxonomy, terrain placement, building-height rules, manufacturing tolerances, fabrication layers, and drawing standards.

This document supplies the common live-editing behavior.
