"""Export a paper-space scene through Rhino 8's native Illustrator writer."""
import argparse
import json
import os
from pathlib import Path
import sys


def export(scene_path, rhino_system):
    import rhinoinside
    rhinoinside.load(rhino_system)
    import Rhino
    import System
    from System.Drawing import Color

    loaded, plugin_id = Rhino.PlugIns.PlugIn.LoadPlugIn(str(Path(rhino_system).parent / "Plug-ins" / "export_AI.rhp"))
    print("AI export plug-in:", loaded, flush=True)

    scene_path = Path(scene_path).resolve()
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    stem = scene_path.name.removesuffix(".scene.json")
    target = scene_path.with_name(stem + ".ai")
    drawing = scene_path.with_name(stem + ".paper.3dm")
    if target.exists() or drawing.exists():
        raise FileExistsError("Use a new output folder; existing exports are kept")
    doc = Rhino.RhinoDoc.Create(None)
    try:
        doc.ModelUnitSystem = Rhino.UnitSystem.Millimeters
        doc.ModelAbsoluteTolerance = 0.0001
        def color(value):
            return Color.FromArgb(int(value[1:3],16), int(value[3:5],16), int(value[5:7],16))
        def point(xy):
            return Rhino.Geometry.Point3d(xy[0], scene["height_mm"]-xy[1], 0)
        layers = {}
        # Separate fill and stroke layers keep both editable and in draw order.
        def attrs(name, rgb, width, order):
            if name not in layers:
                layer = Rhino.DocObjects.Layer()
                layer.Name = name.replace("::", " / ")
                layer.Color = color(rgb)
                layer.PlotColor = color(rgb)
                layer.PlotWeight = width
                layers[name] = doc.Layers.Add(layer)
            a = Rhino.DocObjects.ObjectAttributes()
            a.LayerIndex = layers[name]
            a.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
            a.ObjectColor = color(rgb)
            a.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
            a.PlotColor = color(rgb)
            a.PlotWeightSource = Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
            a.PlotWeight = width
            a.DisplayOrder = order
            return a
        def added(result):
            if result == System.Guid.Empty:
                raise RuntimeError("Rhino could not add a drawing object")
        layer_specs = {}
        for item in scene["items"]:
            if item["kind"] == "text":
                layer_specs[item["layer"]] = (item["color"], .1)
            else:
                if item["fill"]:
                    layer_specs[item["layer"] + " / Fill"] = (item["fill"], 0)
                if item["stroke"]:
                    layer_specs[item["layer"] + " / Line"] = (item["stroke"], item["width"])
        # Rhino's AI writer emits layers in reverse table order.
        for name in reversed(layer_specs):
            rgb, width = layer_specs[name]
            attrs(name, rgb, width, 0)
        for index, item in enumerate(scene["items"]):
            if item["kind"] == "text":
                text = Rhino.Geometry.TextEntity()
                text.Plane = Rhino.Geometry.Plane.WorldXY
                text.PlainText = item["text"]
                text.TextHeight = 1.0
                outlines = text.Explode()
                bounds = Rhino.Geometry.BoundingBox.Empty
                for curve in outlines:
                    bounds.Union(curve.GetBoundingBox(True))
                if not outlines or bounds.Max.Y <= bounds.Min.Y:
                    raise RuntimeError("Could not create text outlines")
                factor = item["size"] * .72 / (bounds.Max.Y-bounds.Min.Y)
                shift = point([item["x"], item["y"]]) - Rhino.Geometry.Point3d(bounds.Min.X*factor, bounds.Min.Y*factor, 0)
                for curve in outlines:
                    curve.Transform(Rhino.Geometry.Transform.Scale(Rhino.Geometry.Point3d.Origin, factor))
                    curve.Transform(Rhino.Geometry.Transform.Translation(shift))
                fills = Rhino.Geometry.Hatch.Create(outlines, 0, 0, 1, doc.ModelAbsoluteTolerance)
                if not fills:
                    raise RuntimeError("Could not fill text outlines")
                for fill in fills:
                    added(doc.Objects.AddHatch(fill, attrs(item["layer"], item["color"], 0, index)))
                continue
            curves = System.Array[Rhino.Geometry.Curve]([
                Rhino.Geometry.PolylineCurve(System.Array[Rhino.Geometry.Point3d]([point(xy) for xy in ring]))
                for ring in item["rings"]])
            if item["fill"]:
                hatches = Rhino.Geometry.Hatch.Create(curves, 0, 0, 1, doc.ModelAbsoluteTolerance)
                if not hatches:
                    raise RuntimeError(f"Could not create a fill on {item['layer']}")
                for hatch in hatches:
                    added(doc.Objects.AddHatch(hatch, attrs(item["layer"] + " / Fill", item["fill"], 0, index)))
            if item["stroke"]:
                for curve in curves:
                    added(doc.Objects.AddCurve(curve, attrs(item["layer"] + " / Line", item["stroke"], item["width"], index)))
        options = Rhino.FileIO.FileAiWriteOptions()
        options.PreserveModelScale = True
        options.RhinoScale = 1.0
        options.AIScale = 1.0
        options.AiUnits = Rhino.FileIO.FileAiWriteOptions.Units.Millimeters
        options.ExportHatchesAsSolidFills = True
        options.ExportViewBoundary = False
        options.OrderLayers = True
        options.UseCMYK = False
        # A top parallel viewport fixes the projection independently of user view state.
        view = doc.Views.Add("Plan", Rhino.Display.DefinedViewportProjection.Top,
                             System.Drawing.Rectangle(0, 0, 1200, 850), False)
        doc.Views.ActiveView = view
        view.ActiveViewport.SetProjection(Rhino.Display.DefinedViewportProjection.Top, "Plan", True)
        if not doc.Write3dmFile(str(drawing), Rhino.FileIO.FileWriteOptions()):
            raise RuntimeError("Could not save the paper-space audit model")
        # Rhino 8.32 writes XY coordinates as PostScript points. Convert the
        # temporary document explicitly; this also keeps text at physical size.
        doc.AdjustModelUnitSystem(Rhino.UnitSystem.PrinterPoints, True)
        if not Rhino.FileIO.FileAi.Write(str(target), doc, options):
            raise RuntimeError("Rhino AI export failed: " + Rhino.RhinoApp.CommandHistoryWindowText)
        from render_ai import validate_ai
        validation = validate_ai(target)
        report = {"ai_file": str(target), "bytes": target.stat().st_size,
                  "writer": "Rhino native AI export", "rhino_version": str(Rhino.RhinoApp.Version),
                  "paper_units": "mm", "export_scale": "1:1", "drawing_scale": scene["scale"],
                  "rhino_objects": doc.Objects.Count, "rhino_layers": doc.Layers.Count,
                  "text": "Outlined vector lettering; source wording remains in scene JSON and SVG",
                  "bounding_box_points": validation["bounding_box_points"],
                  "illustrator_open_check": "Not run: Adobe Illustrator is not installed"}
        target.with_suffix(".export.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2), flush=True)
    finally:
        doc.Dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene")
    parser.add_argument("--rhino-system", default=r"C:\Program Files\Rhino 8\System")
    args = parser.parse_args()
    export(args.scene, args.rhino_system)
    # The standalone worker has saved and validated all files and disposed its
    # document. End here to avoid Rhino/pythonnet GIL finalizers during CPython
    # shutdown. This affects only this worker, not a user's desktop Rhino.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
