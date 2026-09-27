# Rhino Image Capture

Use [../scripts/image_capture.py](../scripts/image_capture.py) for general PNG capture.
Read [usage and input options](image-capture-usage.md) before calling it.

- Follow [Rhino document editing guidance](RHINO-DOCUMENT-EDITING-GUIDANCE.md), including its computer-use restriction.
- Run inside Rhino 8 Python 3 on the main UI thread through an existing programmatic runner. An external Python process cannot capture the open document with this script.
- Supply the captured document's path and runtime serial number, an absolute output directory, and image requests. Keep project values in caller configuration.
- The script prepares the camera in a separate viewport, applies it briefly for API capture, and restores the source camera in `finally`. It does not activate or redraw the view, change selection or layers, or save the model.
- Do not replace a failed API capture with desktop automation without explicit user approval.
- Inspect captured images when the task needs visual review. Capture success alone is not a validation result.
