# Overlay contract

Use a self-contained SVG with `xmlns="http://www.w3.org/2000/svg"` and `viewBox="0 0 1000 600"`. The canvas uses the same 1000 by 600 diagram frame. Draw shapes at their intended position in that frame.

Use plain paths, lines, polygons, rectangles, circles, ellipses and text. Groups, definitions and markers are supported. Use presentation attributes for colour and stroke. Keep the background transparent so the shared base stays visible. The importer rejects scripts, event handlers, linked resources, images and unsupported elements.

Each option holds one SVG per stage in its `overlays` map, keyed by zero-based stage index. Import replaces only the current stage's overlay. Earlier overlays remain visible; later overlays are hidden. The import belongs to the stage selected when the file was chosen. The overlay is rendered as an image; individual AI shapes cannot yet be edited in the canvas.

An exported session uses version 2 and contains its version, canvas frame, base source, active option ID and all options. Each option contains its stable ID, name, stage index, drawing objects with creation stages, SVG sources by stage and notes. Use the option ID when preparing a response. A future live adapter must also check the option revision before applying a delayed response.
