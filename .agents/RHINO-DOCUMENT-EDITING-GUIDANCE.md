# Rhino Document Editing Guidance

## Purpose

This document defines the base rules for workflows that edit a Rhino document.

Prefer to open the target Rhino document before an editing workflow starts. If the document does not exist, create it and then open it in Rhino before editing.

Workflow-specific skills can add stricter geometry, layer, metadata, and validation rules.

## Visible progress

The user must see visible progress in stages to help them understand what is being created and edited progressively. They should see the model develop in Rhino.

Edit the open target document in stages, redraw after each batch, and show progress. Keep Rhino responsive.

Offline preparation is allowed. Do not substitute a completed file for progressive edits without user approval.

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

## Computer use

Use APIs and scripts for Rhino operations. Computer-use tools, desktop screen capture, and mouse or keyboard automation are forbidden unless no suitable programmatic method is available and the user explicitly approves the specific action.

Explain the need and scope before requesting approval. An API failure does not grant approval. This restriction also applies to starting scripts through the Rhino interface. Image capture through the Rhino API does not require computer-use approval.

## Progressive editing

Apply changes to the open Rhino document in logical stages:

1. Validate the prepared input.
2. Create or update layers, materials, and other required definitions.
3. Add or update reference geometry.
4. Add or update primary geometry.
5. Validate the complete document.
6. Save according to the agreed save policy.

Within each stage, process objects in bounded batches. Apply attributes and metadata with each object.

For each batch:

- Set the batch size to give about 5–6 batches per stage. Use more batches only when needed to keep Rhino responsive.
- Confirm that the captured document is still the target.
- Check for user cancellation.
- Add or update the objects.
- Record created, updated, skipped, and failed object counts.
- Update the Rhino status bar and redraw the views.

Adjust batch size to keep Rhino responsive. Periodically zoom to the recently added geometry.

Validate each completed stage before you continue. Keep redraw available throughout the operation.

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

For image capture, use the [rhino-image-capture skill](skills/rhino-image-capture/SKILL.md) and its reusable script. It captures images through the Rhino API for review, progress records, or other uses and restores temporary camera settings. It does not perform validation or connect an external process to Rhino.

## Validation

Use lightweight checks during batches. Run full validation only at each required saved-stage boundary, including the final save. Do not repeat a successful save-and-reopen audit unless the document, source inputs, or review requirements changed.

Validate through RhinoCommon and saved-file checks. Capture review images through the Rhino API. Preserve the user's view and selection. Report unavailable checks as incomplete. A captured image is not a completed visual check; inspect it and record the result.

When the workflow saves the document, confirm that the saved `.3dm` can be read again. Inspect useful views and report all failed checks. Do not describe a failed check as successful.

## Workflow-specific guidance

Keep domain rules in the applicable workflow skill. Examples include site boundaries, Overture taxonomy, terrain placement, building-height rules, manufacturing tolerances, fabrication layers, and drawing standards.

This document supplies the common live-editing behavior.
