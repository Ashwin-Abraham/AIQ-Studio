"""Capture PNG images inside Rhino 8 Python 3, without desktop automation.

Call capture_images from an existing Rhino runner on its UI thread. This module
does not connect to Rhino, open/save models, edit layers, or inspect image quality.
Imports have no Rhino dependency or file-system side effects. Run Python with -B
or set sys.dont_write_bytecode before importing this module.
"""
import argparse
import json
import math
from pathlib import Path


def _requests(config):
    root = Path(config['output_root']).expanduser()
    if not root.is_absolute():
        raise ValueError('output_root must be absolute')
    root = root.resolve()
    if type(config['document_serial']) is not int or config['document_serial'] <= 0:
        raise ValueError('document_serial must be a positive integer')
    path = Path(config['document_path'])
    if not path.is_absolute():
        raise ValueError('document_path must be absolute')
    items = config['images']
    if not isinstance(items, list) or not items:
        raise ValueError('images must be a non-empty list')
    requests, used = [], set()
    for item in items:
        request = dict(item)
        relative = Path(request['file'])
        target = (root / relative).resolve()
        if relative.is_absolute() or not target.is_relative_to(root) or target.suffix.lower() != '.png':
            raise ValueError('Each image must be a PNG inside output_root')
        if target in used or target.exists():
            raise ValueError('Duplicate or existing image: ' + str(target))
        used.add(target)
        for key, default in [('width', 1600), ('height', 1200)]:
            value = request.setdefault(key, default)
            if type(value) is not int or not 1 <= value <= 8192:
                raise ValueError(key + ' must be between 1 and 8192 pixels')
        if request['width'] * request['height'] > 32000000:
            raise ValueError('Image exceeds 32 million pixels')
        if request.get('projection', 'current') not in ('current', 'Top', 'Bottom', 'Front', 'Back', 'Left', 'Right', 'Perspective'):
            raise ValueError('Unknown projection')
        if 'bounds' in request:
            bounds = request['bounds']
            if not isinstance(bounds, list) or len(bounds) != 6 or any(type(v) not in (int, float) or not math.isfinite(v) for v in bounds):
                raise ValueError('bounds must contain six finite numbers')
            if any(bounds[i] > bounds[i+3] for i in range(3)) or bounds[:3] == bounds[3:]:
                raise ValueError('bounds must define a non-zero box')
        for key in ('grid', 'axes'):
            if key in request and type(request[key]) is not bool:
                raise ValueError(key + ' must be boolean')
        for key in ('view', 'display_mode'):
            if key in request and (not isinstance(request[key], str) or not request[key]):
                raise ValueError(key + ' must be a non-empty name')
        requests.append((request, target))
    return root, requests


class RhinoCapture:
    """Small adapter for Rhino's native image capture API."""

    def __init__(self, serial, path):
        import Rhino
        self.rhino = Rhino
        if Rhino.RhinoApp.InvokeRequired:
            raise RuntimeError('Call image capture on the Rhino UI thread')
        self.doc = Rhino.RhinoDoc.FromRuntimeSerialNumber(serial)
        self.serial = serial
        self.path = Path(path).resolve()
        self.check_identity()

    def check_identity(self):
        current = self.rhino.RhinoDoc.FromRuntimeSerialNumber(self.serial)
        if current is None or current != self.doc or int(current.RuntimeSerialNumber) != self.serial:
            raise RuntimeError('Target document is no longer open')
        if not current.Path or Path(current.Path).resolve() != self.path:
            raise RuntimeError('Target document path changed')

    def png(self, request):
        from System.Drawing import Size
        from System.Drawing.Imaging import ImageFormat
        from System.IO import MemoryStream
        rhino = self.rhino
        name = request.get('view')
        if name is None:
            view = self.doc.Views.ActiveView
        else:
            matches = [v for v in self.doc.Views if v.ActiveViewport.Name == name]
            if len(matches) != 1:
                raise ValueError('Expected one open viewport named ' + name)
            view = matches[0]
        if view is None:
            raise RuntimeError('Target document has no view')
        # Calculate the camera off-screen. Rhino requires a document view for
        # shaded capture, so apply it briefly without activation or redraw.
        viewport = rhino.Display.RhinoViewport()
        projection_info = rhino.DocObjects.ViewportInfo(view.ActiveViewport)
        original_mode = view.ActiveViewport.DisplayMode
        original_modified = self.doc.Modified
        applied = False
        bitmap = stream = render_projection = display_attributes = None
        try:
            if not viewport.SetViewProjection(projection_info, False):
                raise RuntimeError('Could not copy source camera')
            viewport.Size = Size(request['width'], request['height'])
            viewport.DisplayMode = view.ActiveViewport.DisplayMode
            projection = request.get('projection', 'current')
            if projection != 'current':
                preset = getattr(rhino.Display.DefinedViewportProjection, projection)
                if not viewport.SetProjection(preset, projection, True):
                    raise RuntimeError('Could not set capture projection')
            if 'bounds' in request:
                b = request['bounds']
                box = rhino.Geometry.BoundingBox(rhino.Geometry.Point3d(*b[:3]), rhino.Geometry.Point3d(*b[3:]))
                if not viewport.ZoomBoundingBox(box):
                    raise RuntimeError('Could not frame capture bounds')
            if 'display_mode' in request:
                mode = rhino.Display.DisplayModeDescription.FindByName(request['display_mode'])
                if mode is None:
                    raise ValueError('Unknown display mode')
                viewport.DisplayMode = mode
            viewport.ConstructionGridVisible = request.get('grid', False)
            viewport.ConstructionAxesVisible = request.get('axes', False)
            render_projection = rhino.DocObjects.ViewportInfo(viewport)
            applied = True
            if not view.ActiveViewport.SetViewProjection(render_projection, False):
                raise RuntimeError('Could not apply capture camera')
            display_attributes = viewport.DisplayMode.DisplayAttributes
            display_attributes.ViewSpecificAttributes.UseDocumentGrid = False
            display_attributes.ViewSpecificAttributes.DrawGrid = request.get('grid', False)
            display_attributes.ViewSpecificAttributes.DrawGridAxes = request.get('axes', False)
            display_attributes.ViewSpecificAttributes.DrawWorldAxes = request.get('axes', False)
            self.check_identity()
            bitmap = view.CaptureToBitmap(Size(request['width'], request['height']), display_attributes)
            if bitmap is None:
                raise RuntimeError('Rhino returned no image')
            if bitmap.Width != request['width'] or bitmap.Height != request['height']:
                raise RuntimeError('Rhino returned unexpected image dimensions')
            stream = MemoryStream()
            bitmap.Save(stream, ImageFormat.Png)
            return bytes(stream.ToArray())
        finally:
            try:
                if applied:
                    restored = view.ActiveViewport.SetViewProjection(projection_info, False)
                    view.ActiveViewport.DisplayMode = original_mode
                    if not restored:
                        raise RuntimeError('Could not restore the source camera')
                    self.doc.Modified = original_modified
            finally:
                for resource in (stream, bitmap, display_attributes, render_projection, projection_info, viewport):
                    if resource is not None:
                        resource.Dispose()


def capture_images(config, *, backend_factory=RhinoCapture, cancelled=None):
    """Return per-image results; keep completed images if later captures fail.

    Inputs: document serial/path, absolute output_root, and image requests.
    Outputs: new PNGs only; no overwrite. All paths are checked before capture.
    The caller supplies an optional cancellation callback, checked between images.
    This function reports capture completion, not visual validation.
    """
    root, requests = _requests(config)
    backend = backend_factory(config['document_serial'], config['document_path'])
    backend.check_identity()
    results = []
    for request, target in requests:
        if cancelled is not None and cancelled():
            results.append({'file': str(target), 'status': 'cancelled'})
            break
        try:
            backend.check_identity()
        except Exception as exc:
            results.append({'file': str(target), 'status': 'failed', 'error': str(exc)})
            break
        created = False
        try:
            png = backend.png(request)
            if not png.startswith(b'\x89PNG\r\n\x1a\n'):
                raise RuntimeError('Capture did not return PNG data')
            backend.check_identity()
            # Recheck after capture, before creating directories or opening files.
            if not target.resolve().is_relative_to(root):
                raise ValueError('Output path left output_root')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                created = True
                stream.write(png)
            results.append({'file': str(target), 'status': 'captured', 'width': request['width'], 'height': request['height']})
        except Exception as exc:
            if created:
                target.unlink(missing_ok=True)
            results.append({'file': str(target), 'status': 'failed', 'error': str(exc)})
    return {'completed': len(results) == len(requests) and all(r['status'] == 'captured' for r in results),
            'document_serial': config['document_serial'], 'images': results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = capture_images(json.loads(args.config.read_text(encoding='utf-8')))
    except Exception as exc:
        print(json.dumps({'completed': False, 'error': str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['completed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
