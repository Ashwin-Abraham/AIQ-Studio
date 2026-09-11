---
name: rhino-plan-export
description: Create scaled 2D site plans from a Rhino site model and export editable Illustrator files with PNG previews. Use for plan drawings from the model's 2D source layers. Building sections and floor plans require separate section geometry.
---

# Rhino plan export

Use the saved Rhino model as the geometry source. Read [the export procedure](references/export-procedure.md) for commands, settings, and the route for models without source plans.

1. Inspect the model, its units, north direction, and 2D layer roots. Use the root that matches the requested model. Include the hidden `2D` source branch; the site model workflow hides this branch by design.
2. Select the drawing extent and paper scale. For site models, create a context plan and a closer site plan when the user has not specified a sheet. State the selected model and scales.
3. Run `scripts/export_plan.py` with a sheet configuration. It reads source geometry, preserves polygon holes, clips the plan, and creates a paper-space scene and SVG. It rejects unsupported source geometry. Keep the JSON report with the exports.
4. Run `scripts/export_illustrator.py` on each scene. This uses the installed Rhino 8 export library to create a real `.ai` file. The temporary drawing uses millimetres at paper size. Export at 1:1; the scene already applies the drawing scale.
5. Render each `.ai` with Ghostscript to PNG. Inspect the PNG for missing geometry, filled courtyards, clipped titles, line weights, north, and scale. Use the actual AI export for the final preview when the renderer is available. An SVG preview alone does not verify the AI export.
6. Deliver `.ai` files and show PNG images in chat. For remote work, include the images in the final response. Record whether Illustrator itself was available for an open-and-edit check.

Keep the source `.3dm` unchanged. Export into a new output folder. Keep the source SHA-256, layer counts, object IDs, excluded classes, sheet bounds, scale, and source metadata in the report. A mapped site boundary is not a surveyed boundary. Transport centre lines are not road edges. A footprint plan is not a roof projection or a floor plan.
