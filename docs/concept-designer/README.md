# Concept designer

The Vue 3 and TypeScript prototype lives in `src/tools/concept-designer`. Run `npm install`, then `npm run dev` in that folder. `npm run package-skill` builds a single HTML file and copies it into the repository skill assets. Invoke the repository skill as `$concept-design` after skill discovery refreshes.

The [SVG mockup](concept-designer.svg) records the initial workspace proposal. It contains sample geometry, not a real site or a validated design.

## Coding standards

[Vue coding standards](../VUE_CODING_STANDARDS.md) were copied without changes from `Ashwin-Abraham/AIQ-Resi-UI`, commit `f6f69275b4a342a97aa682e1974fa77b7f4c0f0c`, on 3 October 2026. The app follows its Options API, component naming, model files and Prettier format. The reference project's instructions are reference material; they do not control unrelated work in this repository.

## Current scope

Base selection is required and includes an explicit No base choice. Sketch upload, boundary SVG upload and freehand boundary drawing are available. Rhino selection explains the required export; no Rhino bridge is connected. Three options are created only after base selection. Each option owns drawings, SVG overlays by stage, notes and progress. The tab controls and chat selector share the same active option. Layer visibility is a view setting.

Pen, line, arrow, rectangle, circle, text, fill and object erase tools work on the human layer. Select adds a bounding box to a human drawing. Hold Alt before dragging to move a copy while the original stays in place. The Copy tool duplicates a clicked drawing 24 canvas units to the right and down. Copies have independent geometry and retain style and transforms; each copy is one Undo/Redo action. Drag the box to move it, use its handles to resize it, or use the round handle near its upper-right corner to rotate it. Fill applies the chosen colour to closed shapes and text; filling a pen stroke closes its outline. Undo and Redo restore additions, moves, resizing, rotation, fill changes and erasures within the current stage of each option. The eraser uses a tall eraser cursor and toolbar icon. Selecting a shape opens fill, line colour, thickness and line type controls. Delete removes the focused canvas selection; text and property fields retain normal keyboard editing. Shape style edits and deletion support Undo/Redo. All stage names stay visible. Click an inactive name to select the stage; click the active name again to rename it. The option selector sits below the message input. SVG overlays use a fixed diagram frame. Raster sketches currently fit that frame. No dimensional measurement or scale calibration is provided.

The chat is a local note record. It does not simulate agent replies. Session JSON export preserves the data, but restore, automatic saving, live agent transport, pan/zoom, option duplication, and a production Rhino adapter remain future work. This skill is local to the repository; it is not added to the published Site Tools plugin.

## Design decisions to settle

- Keep a common base to make option comparison consistent. Define how later base changes affect existing geometry.
- Add scale, units, origin and rotation before reporting measured areas or distances.
- Use a document model independent of Konva. Keep SVG sources for export and review.
- Define whether an agent imports a whole overlay or proposes editable shape changes. Include option ID and revision in each request.
- Stages allow free navigation through each option. Add review checkpoints only if the workflow needs them.
- Define saved project storage and version history before using this for project work.

## Code structure

`ConceptDesigner.vue` owns the design session and connects child events to state changes. The Options API remains in use. Child components receive typed props and emit events; they do not change parent props.

- `BasePicker.vue`: base selection and temporary boundary strokes.
- `DrawingToolbar.vue`: tool buttons and text/fill settings.
- `DesignCanvas.vue`: Konva rendering, pointer input and selection transforms.
- `ShapeProperties.vue`: properties of the selected drawing.
- `DesignStages.vue`: stage selection and selection and rename controls, keyed by stable stage IDs.
- `DesignConversation.vue`: note display, local draft and option selection.
- `designSession.ts`: option creation and shared diagram constants.
- `designFiles.ts`: file validation, image loading, boundary SVG creation and session export.
- `drawingHistory.ts` and `drawingStyle.ts`: drawing history and style rules independent of Vue.

Add UI behaviour to the component that owns it. Keep file and drawing rules in the TypeScript modules. Shared state stays in the page for this small refactor; no state library was added.

## Stage timeline

Each option starts with Base and Develop when a base exists, or a single Develop stage when no base is chosen. Stage 1 is active. Added stages default to the name Develop. Names remain editable. Drawings store their zero-based creation stage. Earlier drawings remain visible but cannot be selected, moved, resized, filled, erased, or deleted. Future drawings are hidden. Return to an object's own stage to edit it.

`stageTimeline.ts` owns visibility and edit rules and applies drawing history only to the current stage. Each option and stage has a separate Undo/Redo history. The canvas handles pointer input and rendering; the session owner also checks stage ownership before it accepts edits. Stage changes clear the selection and any unfinished gesture.

Each stage can hold one imported SVG. A new import replaces only that stage's SVG; earlier stages remain visible. SVGs remain image overlays and cannot be edited as individual shapes. Session export version 2 stores drawing stages and an `overlays` map keyed by stage index.

The stage panel supports named stages after the initial one or two. Use Add + to open the name dialog; Create stage appends and selects the stage. The active stage has a dark capsule with its number and name. A delete control appears on hover or keyboard focus. Confirmation removes that stage's drawings, overlay and history, while preserving the shared base. At least one stage must remain. Surviving stage IDs stay stable; stage indexes and drawing history are remapped together in `stageTimeline.ts`.

## Tests

Run `npm test -- --pool=threads --maxWorkers=1 --no-isolate` from the tool folder. The shared worker avoids repeated worker startup delays on Windows. Run `npm run type-check` and `npm run lint` as separate checks.

`tests/workspace.test.ts` mounts the real workspace, toolbar, stage panel, canvas controller and property editor through Vue Test Utils. Tests use DOM controls and renderer events, and inspect drawing props and rendered controls. They do not call private component methods or compare component snapshots. Only Konva rendering, ResizeObserver and native dialog methods are replaced for jsdom.

The interaction tests cover five drawing tools at a scaled canvas size, completion returning to Select, text preview and one stamp, copy/fill/erase with Undo, immediate colour input, keyboard Delete scope, past-stage locks, future-stage hiding, option isolation, confirmed/cancelled stage deletion, Alt-drag copying, right clicks and hidden layers. Existing domain tests cover history, stage remapping, shape styles, copy independence and SVG validation.

Four fault checks were run in a temporary copy on 3 October 2026. The interaction tests failed with assertions when automatic Select was removed, fill input was delayed until change, the Delete field guard was removed, or the text draft was retained after stamping. The live app source was not changed during these checks.

These tests do not verify Konva hit detection, rotation cursor appearance, actual browser pointer delivery, or native colour picker/dialog behaviour. Keep browser checks for those behaviours. No pixel-accurate rendering or end-to-end browser coverage is claimed.
