# Export procedure

## Runtime and input

Use Windows, 64-bit Python, an installed and licensed Rhino 8, and Ghostscript. Install the Python packages from `scripts/requirements.txt`. The workflow was checked with Rhino 8.32 and Ghostscript 10.08.0.

The previous [pull request #13](https://github.com/Ashwin-Abraham/AIQ-Studio/pull/13) creates a hidden `AIQ Site::2D` branch. The supplied Poplar model uses `Poplar_Overture::2D`. The reader finds either root. Select `--root` if the file contains more than one source plan.

Source curves must be valid polylines at Z = 0. Points are supported. Polygon holes use `geometry_role=source_plan_hole`, the source feature ID, and the clipped part index. The reader supports the metadata names from the earlier Poplar model and the merged site model workflow. It fails if a hole has no unique parent.

## Run the Poplar example

Run these commands from the repository root. Use a new output directory for each application.

For one command that performs all three stages, use:

```powershell
python .agents/skills/rhino-plan-export/scripts/run_workflow.py `
  --model "Models/Poplar Recreation Ground - Overture.3dm" `
  --config .agents/skills/rhino-plan-export/references/poplar-sheets.json `
  --output artifacts/poplar-plans `
  --ghostscript "C:/Program Files/gs/gs10.08.0/bin/gswin64c.exe"
```

The separate stage commands are:

```powershell
python -m pip install -r .agents/skills/rhino-plan-export/scripts/requirements.txt

python .agents/skills/rhino-plan-export/scripts/export_plan.py `
  --model "Models/Poplar Recreation Ground - Overture.3dm" `
  --config .agents/skills/rhino-plan-export/references/poplar-sheets.json `
  --output artifacts/poplar-plans

python .agents/skills/rhino-plan-export/scripts/export_illustrator.py `
  artifacts/poplar-plans/poplar-context-plan.scene.json

python .agents/skills/rhino-plan-export/scripts/export_illustrator.py `
  artifacts/poplar-plans/poplar-site-plan.scene.json

python .agents/skills/rhino-plan-export/scripts/render_ai.py `
  artifacts/poplar-plans/poplar-context-plan.ai `
  --ghostscript "C:/Program Files/gs/gs10.08.0/bin/gswin64c.exe"

python .agents/skills/rhino-plan-export/scripts/render_ai.py `
  artifacts/poplar-plans/poplar-site-plan.ai `
  --ghostscript "C:/Program Files/gs/gs10.08.0/bin/gswin64c.exe"
```

Use the actual Ghostscript executable path on the host. The renderer reads the exported `.ai`, not the SVG. Rhino's legacy AI file refers to external Adobe PostScript resources. `rhino-ai-preview.ps` supplies the limited drawing operators used by this workflow. `render_ai.py` rejects other operators and incorrect page extents. This preview is a check of the exported paths; it does not replace an Illustrator open-and-edit check.

## Sheet settings

Copy `poplar-sheets.json` for another model. Change the title, source notes, date, extent, scale, and north basis. Bounds are `[xmin, ymin, xmax, ymax]` in model-local metres. The template uses A3 landscape. The map must fit a 267 by 237 mm frame. The script fails if the extent does not fit at the selected scale. It does not silently fit or rescale the drawing.

Confirm that north is model +Y. The arrow is labelled model north. Do not claim true north from a projected CRS without a meridian convergence check. Keep source notes specific to the model.

For a scale denominator `S`, one metre occupies `1000 / S` mm on paper. The context example is 1:3000. Its 200 m scale bar is 66.6667 mm long. The site example is 1:1250. Its 80 m scale bar is 64 mm long.

The AI writer uses a separate Rhino document with a Top parallel viewport. A `.paper.3dm` audit file preserves the drawing in paper millimetres. Immediately before AI export, the temporary document changes to printer points. Tests on Rhino 8.32 found that the AI writer emitted XY coordinates in points without the expected unit conversion. The renderer checks the A3 extent to detect changes in this behaviour in later Rhino versions.

Text is exported as filled vector outlines to avoid a second unit conversion in the native text exporter. The scene JSON and SVG retain the source wording. Geometry, fill and line layers remain editable in Illustrator. Font substitution is not needed for the AI outlines.

## Other Rhino models

For a model without a source `2D` branch, first create the required plan geometry in Rhino. Use a Top parallel view and `Make2D` for visible roof and model outlines. Use a defined horizontal cutting plane and section geometry for a floor plan. Save these results into a separate copy with a clear 2D root and category layers. Convert non-polyline curves at a recorded chord tolerance before this script reads them. Keep section cuts and projected lines in separate layers.

This version automates the source-footprint route. It does not calculate hidden lines, floor sections, contours, road widths, or roof details. Mesh wireframe edges are not a substitute for visible outlines. McNeel documents the [AI exporter](https://docs.mcneel.com/rhino/8/help/en-us/fileio/ai_ai_import_export.htm) and the [HiddenLineDrawing API](https://developer.rhino3d.com/api/rhinocommon/rhino.geometry.hiddenlinedrawing).

## Checks and delivery

```powershell
python -m unittest discover -s .agents/skills/rhino-plan-export/scripts -p "test_*.py"
```

Inspect each PNG at sheet size and close range. Check source geometry, courtyards, line weights, boundary position, layer order, scale bar, and text. Deliver the `.ai` and `.png` files. Keep the scene, SVG, paper model, and reports with them. Preserve the original `.3dm` file. State any unavailable Illustrator check.
