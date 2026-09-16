# Rhino image capture

Reusable script for general image capture, not model validation. It requires
Rhino 8 on Windows with Python 3 and the bundled RhinoCommon/System.Drawing APIs.
No extra package installation is required.

Call [scripts/image_capture.py](../scripts/image_capture.py) from an existing programmatic Rhino runner on
Rhino's main UI thread. It is not a connection or desktop automation script.
Do not start it through mouse or keyboard automation without explicit approval.

The script prepares camera settings in an independent viewport, then captures through
`RhinoView.CaptureToBitmap` with explicit display attributes. It applies the camera
temporarily without activating or redrawing the view and restores it in `finally`.
Selection, layers, geometry, the document's modified flag, and the saved model are preserved.
Images show the document's current object/layer visibility and selection display.
Supported views are open viewports; named-view records and layout details are not
separate selectors in this script. Omit `view` to use the document's active view.

## Usage inside Rhino Python 3

```python
import importlib.util
import sys
sys.dont_write_bytecode = True

spec = importlib.util.spec_from_file_location("image_capture", script_path)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)

# doc is the document already captured and checked by the editing runner.
result = capture.capture_images({
    "document_serial": int(doc.RuntimeSerialNumber),
    "document_path": doc.Path,
    "output_root": output_directory,
    "images": [
        {"file": "current.png", "width": 1600, "height": 1200},
        {"file": "plan.png", "projection": "Top", "display_mode": "Shaded",
         "bounds": [-100, -100, 0, 100, 100, 50]}
    ]
}, cancelled=cancellation_requested)
```

Supply absolute paths for the script, output directory, and saved document.
Bounds use model coordinates and model units: min X/Y/Z, then max X/Y/Z.
Optional `grid` and `axes` values default to false. PNG paths must stay inside
the output directory. Existing files and duplicate names are rejected before capture.
Use a new output folder or new names for another run.

Results describe capture success only. Inspect the images separately for review,
presentation, progress records, or validation. A failed capture leaves no output
file; earlier completed images remain. Cancellation is checked between images.

`main(["--config", config_path])` accepts the same configuration as JSON and returns
0 for completion, 1 for partial capture, or 2 for input/runtime errors. Run it inside
Rhino; a normal external Python process cannot capture the open Rhino document.

## Status and tests

Live capture passed on Rhino 8.32.26160.13001 on Windows on 2026-09-16.
The test used RhinoCode and a separate three-box fixture document. Wireframe
perspective, plan, and shaded PNGs were captured at 1200 x 900 and visually inspected.
Camera/frustum, active view, non-empty selection, layers, object count, geometry CRCs,
and the modified flag were unchanged. Invalid display-mode capture produced no file.

Run `python -B -m unittest discover -s '.agents/skills/rhino-image-capture/tests'`
from the workspace root. These tests use a fake capture backend to check the public
interface, path restrictions, identity failures, partial failure, and cancellation.
They do not prove native rendering. The separate live test covers the modes and
environment listed above; it does not cover every display mode or graphics driver.

API references:

- https://developer.rhino3d.com/api/rhinocommon/rhino.display.rhinoview/capturetobitmap
