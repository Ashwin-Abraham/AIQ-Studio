---
name: rhino-image-capture
description: Capture PNG images of an open Rhino document through RhinoCommon for progress records, review, presentation, or other image uses. Does not control the desktop, create a Rhino connection, or validate model geometry.
---

# Rhino Image Capture

Use [scripts/image_capture.py](scripts/image_capture.py) for general PNG capture.
Read [usage and input options](references/usage.md) before calling it.

- Follow [Rhino document editing guidance](../../RHINO-DOCUMENT-EDITING-GUIDANCE.md), including its computer-use restriction.
- Run inside Rhino 8 Python 3 on the main UI thread through an existing programmatic runner. An external Python process cannot capture the open document with this script.
- Supply the captured document's path and runtime serial number, an absolute output directory, and image requests. Keep project values in caller configuration.
- The script prepares the camera in a separate viewport, applies it briefly for API capture, and restores the source camera in `finally`. It does not activate or redraw the view, change selection or layers, or save the model.
- Do not replace a failed API capture with desktop automation without explicit user approval.
- Inspect captured images when the task needs visual review. Capture success alone is not a validation result.

## Dependencies and tests

Requires Rhino 8 on Windows, Python 3.9 or later, RhinoCommon, and System.Drawing
provided by Rhino. No pip packages are required.

Run the public-interface tests with an existing managed Python environment:

```text
python -B -m unittest discover -s .agents/skills/rhino-image-capture/tests -v
```

The tests use a fake capture backend. They check capture orchestration and file
handling, not native rendering. See the usage reference for the live-test checks.
