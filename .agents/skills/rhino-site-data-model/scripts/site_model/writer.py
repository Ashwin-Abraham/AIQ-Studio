"""Single-owner document edits. Geometry preparation never uses this module."""

import json
import os
from pathlib import Path
import tempfile
import uuid

import rhino3dm as r3d

from .contract import file_sha256

OWNER = "rhino-site-data-model"


class Cancelled(RuntimeError):
    pass


def owned(attrs):
    return attrs.GetUserString("site_owner") == OWNER


def active_objects(doc, Rhino):
    """Return live normal, locked, hidden, and reference objects."""
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.IncludeLights = True
    settings.IncludeGrips = False
    settings.NormalObjects = True
    settings.LockedObjects = True
    settings.HiddenObjects = True
    settings.ReferenceObjects = True
    return list(doc.Objects.GetObjectList(settings))


def check_frame(model_units, strings, data, has_objects):
    if not has_objects:
        return
    if str(model_units) not in ("UnitSystem.Meters", "Meters"):
        raise ValueError("Existing model must use metres; convert inputs before this workflow")
    for key in ("projected_crs", "origin_projected", "origin_wgs84"):
        current = strings("site." + key)
        expected = data["run"][key]
        if not current:
            raise ValueError("Existing model has no site." + key + "; establish its coordinate frame first")
        actual = json.loads(current) if key.startswith("origin_") else current
        if actual != expected:
            raise ValueError("Existing model coordinate frame does not match sources: " + key)


class FileWriter:
    """Explicit offline adapter. A failed stage does not change the saved file."""

    def __init__(self, path, sources, cancel=None, progress=None):
        self.path = Path(path)
        self.cancel = cancel or (lambda: False)
        self.progress = progress or (lambda event: None)
        self.initial_hash = file_sha256(self.path) if self.path.exists() else None
        self.model = r3d.File3dm.Read(str(self.path)) if self.path.exists() else r3d.File3dm()
        if self.model is None:
            raise ValueError("Cannot read target model")
        check_frame(self.model.Settings.ModelUnitSystem, lambda k: self.model.Strings[k], sources, len(self.model.Objects) > 0)
        self.model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
        self.stage = None
        self.transaction_open = False
        self.initialize_anchor = len(self.model.Objects) == 0

    def pump(self):
        if self.cancel():
            raise Cancelled("Cancelled; the incomplete stage was rolled back")

    def begin(self, stage):
        self.pump()
        self.before = self.model.Encode()
        self.stage, self.seen = stage, set()
        self.existing = {o.Attributes.GetUserString("site_key"): o for o in self.model.Objects if owned(o.Attributes)}
        if len(self.existing) != sum(owned(o.Attributes) for o in self.model.Objects):
            raise ValueError("Target has duplicate generated keys; repair ownership before update")
        self.layer_map = {l.FullPath: l.Index for l in self.model.Layers}
        self.counts = dict(created=0, updated=0, skipped=0, deleted=0)
        self.transaction_open = True

    def apply(self, prepared, objects):
        self.pump()
        for layer in prepared.Layers:
            if layer.FullPath in self.layer_map:
                item = self.model.Layers.FindIndex(self.layer_map[layer.FullPath])
                item.Color, item.PlotColor = layer.Color, layer.PlotColor
                item.PlotWeight, item.Visible = layer.PlotWeight, layer.Visible
            else:
                item = r3d.Layer()
                item.Name, item.Color, item.Visible = layer.Name, layer.Color, layer.Visible
                item.PlotColor, item.PlotWeight = layer.PlotColor, layer.PlotWeight
                parent = layer.FullPath.rpartition("::")[0]
                if parent:
                    item.ParentLayerId = self.model.Layers.FindIndex(self.layer_map[parent]).Id
                self.layer_map[layer.FullPath] = self.model.Layers.Add(item)
        for obj in objects:
            attrs = r3d.ObjectAttributes()
            attrs.LayerIndex = obj.Attributes.LayerIndex
            attrs.Name = obj.Attributes.Name
            attrs.ColorSource = obj.Attributes.ColorSource
            attrs.PlotColorSource = obj.Attributes.PlotColorSource
            attrs.PlotWeightSource = obj.Attributes.PlotWeightSource
            attrs.LinetypeSource = obj.Attributes.LinetypeSource
            attrs.DisplayOrder = obj.Attributes.DisplayOrder
            for name, value in obj.Attributes.GetUserStrings():
                attrs.SetUserString(name, value)
            key = attrs.GetUserString("site_key")
            if not owned(attrs) or attrs.GetUserString("site_stage") != self.stage or not key:
                raise ValueError("Batch contains invalid ownership or stage metadata")
            if key in self.seen:
                # Common boundary and annotation objects are identical across partitions.
                previous = self.existing.get(key)
                if previous and previous.Attributes.GetUserString("site_content_hash") != attrs.GetUserString("site_content_hash"):
                    raise ValueError("Conflicting generated key across partitions: " + key)
                continue
            self.seen.add(key)
            previous = self.existing.get(key)
            if (previous and previous.Attributes.GetUserString("site_content_hash") == attrs.GetUserString("site_content_hash")
                    and previous.Geometry.Encode() == obj.Geometry.Encode()):
                self.counts["skipped"] += 1
                continue
            attrs.LayerIndex = self.layer_map[prepared.Layers.FindIndex(attrs.LayerIndex).FullPath]
            if previous:
                attrs.Id = previous.Attributes.Id
                self.model.Objects.Delete(previous.Attributes.Id)
                self.counts["updated"] += 1
            else:
                self.counts["created"] += 1
            identifier = self.model.Objects.Add(obj.Geometry, attrs)
            if identifier == uuid.UUID(int=0):
                raise RuntimeError("Could not add prepared object")
            self.existing[key] = self.model.Objects.FindId(identifier)
        for key, value in prepared.Strings:
            self.model.Strings[key] = value
        if self.initialize_anchor:
            self.model.Settings.EarthAnchorPoint = prepared.Settings.EarthAnchorPoint
        self.model.Settings.RenderSettings.RenderBackFaces = True
        self.progress(dict(stage=self.stage, **self.counts))

    def finish(self):
        self.pump()
        for obj in list(self.model.Objects):
            attrs = obj.Attributes
            if owned(attrs) and ((attrs.GetUserString("site_stage") == self.stage and attrs.GetUserString("site_key") not in self.seen) or
                                 (self.stage == "2d" and attrs.GetUserString("site_stage") == "3d")):
                self.model.Objects.Delete(attrs.Id)
                self.counts["deleted"] += 1
        for layer in self.model.Layers:
            if layer.FullPath == "AIQ Site::2D":
                layer.Visible = self.stage == "2d"
            elif layer.FullPath == "AIQ Site::3D":
                layer.Visible = self.stage == "3d"
        self.model.Strings["site.completed_stage"] = self.stage

    def save(self):
        self.pump()
        current = file_sha256(self.path) if self.path.exists() else None
        if current != self.initial_hash:
            raise ValueError("Target file changed during preparation")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(dir=self.path.parent, suffix=".3dm")
        os.close(fd)
        try:
            if not self.model.Write(name, 8) or r3d.File3dm.Read(name) is None:
                raise RuntimeError("Saved stage cannot be read")
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        self.initial_hash = file_sha256(self.path)
        self.transaction_open = False

    def rollback(self):
        self.model = r3d.File3dm.Decode(self.before)
        self.transaction_open = False

    def close(self):
        pass


class RhinoWriter:
    """RhinoCommon adapter. Construct and call it on Rhino's main UI thread.

    A caller can supply a headless document for integration tests. Normal use
    captures the open target once. Undo records are used when no command owns
    one; a change journal also supports cancellation inside a command record.
    """

    def __init__(self, path, sources, cancel=None, progress=None, document=None):
        import Rhino
        self.Rhino = Rhino
        self.transaction_open = False
        if Rhino.RhinoApp.InvokeRequired:
            raise ValueError("Run the workflow on Rhino's main interface thread")
        self.doc = document or Rhino.RhinoDoc.ActiveDoc
        self.path = Path(path).resolve()
        if self.doc is None or Path(self.doc.Path or "").resolve() != self.path:
            raise ValueError("Open the selected target in Rhino before the live run")
        if self.doc.Modified:
            raise ValueError("Save or resolve changes in the target before the live run")
        self.serial = self.doc.RuntimeSerialNumber
        objects = active_objects(self.doc, Rhino)
        self.initialize_anchor = not objects
        check_frame(self.doc.ModelUnitSystem, lambda k: self.doc.Strings.GetValue(k), sources, bool(objects))
        self.cancel = cancel or (lambda: False)
        self.progress = progress or (lambda event: None)
        self.escaped = False
        self.initial_hash = file_sha256(self.path) if self.path.exists() else None
        self.stage = None
        self._escape = lambda sender, args: setattr(self, "escaped", True)
        Rhino.RhinoApp.EscapeKeyPressed += self._escape

    def pump(self):
        if self.doc.RuntimeSerialNumber != self.serial or Path(self.doc.Path or "").resolve() != self.path:
            raise ValueError("Target document identity changed")
        self.Rhino.RhinoApp.Wait()
        if self.doc.RuntimeSerialNumber != self.serial or Path(self.doc.Path or "").resolve() != self.path:
            raise ValueError("Target document identity changed")
        if self.escaped or self.cancel():
            raise Cancelled("Cancelled; the incomplete stage was rolled back")

    def begin(self, stage):
        self.pump()
        self.stage, self.seen, self.journal = stage, set(), []
        self.counts = dict(created=0, updated=0, skipped=0, deleted=0)
        self.new_layers = []
        self.layer_state = [(l.Id, l.IsVisible, l.ModelIsVisible, l.GetPersistentVisibility(), l.ModelPersistentVisibility,
                             l.Color, l.PlotColor, l.PlotWeight, l.LinetypeIndex)
                            for l in self.doc.Layers if l is not None and not l.IsDeleted]
        self.old_strings = [(self.doc.Strings.GetKey(i), self.doc.Strings.GetValue(i)) for i in range(self.doc.Strings.Count)]
        self.old_units = self.doc.ModelUnitSystem
        self.old_anchor = self.doc.EarthAnchorPoint
        self.old_backfaces = self.doc.RenderSettings.RenderBackfaces
        objects = active_objects(self.doc, self.Rhino)
        self.existing = {o.Attributes.GetUserString("site_key"): o for o in objects if owned(o.Attributes)}
        if len(self.existing) != sum(owned(o.Attributes) for o in objects):
            raise ValueError("Target has duplicate generated keys")
        self.undo = 0
        if not self.doc.UndoRecordingIsActive:
            self.undo = self.doc.BeginUndoRecord("Site model " + stage)
            if not self.undo:
                raise RuntimeError("Cannot start a site model undo record")
        self.transaction_open = True
        self.doc.ModelUnitSystem = self.Rhino.UnitSystem.Meters
        settings = self.doc.RenderSettings
        settings.RenderBackfaces = True
        self.doc.RenderSettings = settings
        self.Rhino.UI.StatusBar.ShowProgressMeter(self.serial, 0, 100, "Site " + stage, True, True)

    def apply(self, prepared, objects):
        self.pump()
        # Convert a bounded batch through 3DM, avoiding incompatible Python/.NET types.
        transfer = r3d.File3dm()
        for layer in prepared.Layers:
            transfer.Layers.Add(layer)
        for obj in objects:
            transfer.Objects.Add(obj.Geometry, obj.Attributes)
        import base64
        from System import Array, Byte
        native = self.Rhino.FileIO.File3dm.FromByteArray(Array[Byte](base64.b64decode(transfer.Encode())))
        if native is None:
            raise RuntimeError("Cannot read prepared Rhino batch")
        try:
            layer_map = {l.FullPath: l.Index for l in self.doc.Layers if l is not None and not l.IsDeleted}
            for layer in native.AllLayers:
                if layer.FullPath in layer_map:
                    current = self.doc.Layers[layer_map[layer.FullPath]]
                    current.Color, current.PlotColor = layer.Color, layer.PlotColor
                    current.PlotWeight, current.IsVisible = layer.PlotWeight, layer.IsVisible
                    if not current.CommitChanges():
                        raise RuntimeError("Could not update site layer style")
                else:
                    new = self.Rhino.DocObjects.Layer()
                    new.Name, new.Color, new.IsVisible = layer.Name, layer.Color, layer.IsVisible
                    new.PlotColor, new.PlotWeight = layer.PlotColor, layer.PlotWeight
                    parent = layer.FullPath.rpartition("::")[0]
                    if parent:
                        new.ParentLayerId = self.doc.Layers[layer_map[parent]].Id
                    index = self.doc.Layers.Add(new)
                    if index < 0:
                        raise RuntimeError("Could not add site layer")
                    self.new_layers.append(self.doc.Layers[index].Id)
                    layer_map[layer.FullPath] = index
            for obj in native.Objects:
                attrs = obj.Attributes.Duplicate()
                key = attrs.GetUserString("site_key")
                if not owned(attrs) or attrs.GetUserString("site_stage") != self.stage or not key:
                    raise ValueError("Batch contains invalid ownership or stage metadata")
                previous = self.existing.get(key)
                if key in self.seen:
                    if previous and previous.Attributes.GetUserString("site_content_hash") != attrs.GetUserString("site_content_hash"):
                        raise ValueError("Conflicting generated key across partitions")
                    continue
                self.seen.add(key)
                if (previous and previous.Attributes.GetUserString("site_content_hash") == attrs.GetUserString("site_content_hash")
                        and self.Rhino.Geometry.GeometryBase.GeometryEquals(previous.Geometry, obj.Geometry)):
                    self.counts["skipped"] += 1
                    continue
                attrs.LayerIndex = layer_map[native.AllLayers.FindIndex(attrs.LayerIndex).FullPath]
                if previous:
                    self._delete(previous)
                    attrs.ObjectId = previous.Id
                    self.counts["updated"] += 1
                else:
                    self.counts["created"] += 1
                identifier = self.doc.Objects.Add(obj.Geometry, attrs)
                from System import Guid
                if identifier == Guid.Empty:
                    raise RuntimeError("Could not add site object")
                self.journal.append(("add", identifier))
                self.existing[key] = self.doc.Objects.FindId(identifier)
            for key, value in prepared.Strings:
                self.doc.Strings.SetString(key, value)
            # Earth anchor is set only for an empty new model; existing frames were checked.
            if self.initialize_anchor:
                self.doc.EarthAnchorPoint = self._anchor(prepared)
        finally:
            native.Dispose()
        self.doc.Views.Redraw()
        self.Rhino.UI.StatusBar.UpdateProgressMeter(self.serial, "Site " + self.stage + ": " + str(len(self.seen)) + " objects", 0, True)
        self.progress(dict(stage=self.stage, **self.counts))

    def _anchor(self, prepared):
        anchor = self.Rhino.DocObjects.EarthAnchorPoint()
        source = prepared.Settings.EarthAnchorPoint
        anchor.Name = source.Name
        anchor.EarthBasepointLatitude = source.EarthBasepointLatitude
        anchor.EarthBasepointLongitude = source.EarthBasepointLongitude
        anchor.ModelBasePoint = self.Rhino.Geometry.Point3d.Origin
        anchor.ModelNorth = self.Rhino.Geometry.Vector3d.YAxis
        anchor.ModelEast = self.Rhino.Geometry.Vector3d.XAxis
        return anchor

    def _delete(self, obj):
        backup = (obj.Geometry.Duplicate(), obj.Attributes.Duplicate())
        if not self.doc.Objects.Delete(obj.Id, True):
            raise RuntimeError("Could not replace owned site object")
        self.journal.append(("delete", backup))

    def finish(self):
        self.pump()
        for obj in active_objects(self.doc, self.Rhino):
            attrs = obj.Attributes
            if owned(attrs) and ((attrs.GetUserString("site_stage") == self.stage and attrs.GetUserString("site_key") not in self.seen) or
                                 (self.stage == "2d" and attrs.GetUserString("site_stage") == "3d")):
                self._delete(obj)
                self.counts["deleted"] += 1
        for layer in self.doc.Layers:
            if layer.FullPath in ("AIQ Site::2D", "AIQ Site::3D"):
                visible = layer.FullPath.endswith(self.stage.upper())
                layer.IsVisible = visible
                layer.ModelIsVisible = visible
                layer.SetPersistentVisibility(visible)
                layer.ModelPersistentVisibility = visible
                layer.CommitChanges()
        self.doc.Strings.SetString("site.completed_stage", self.stage)
        self.doc.Views.Redraw()

    def save(self):
        self.pump()
        current = file_sha256(self.path) if self.path.exists() else None
        if current != self.initial_hash:
            raise ValueError("Target file changed during the live run")
        options = self.Rhino.FileIO.FileWriteOptions()
        options.SuppressDialogBoxes = True
        options.SuppressAllInput = True
        options.UpdateDocumentPath = True
        options.CreateBackupFiles = True
        if not self.doc.WriteFile(str(self.path), options):
            raise RuntimeError("Rhino could not save the active target")
        # WriteFile is the commit point. Do not roll the live document back
        # after Rhino reports a successful save, even if verification fails.
        self._end_undo()
        self.transaction_open = False
        if Path(self.doc.Path or "").resolve() != self.path:
            raise RuntimeError("Rhino changed the document path during save")
        if self.doc.Modified:
            raise RuntimeError("Rhino saved the target but left the document modified")
        if r3d.File3dm.Read(str(self.path)) is None:
            raise RuntimeError("Saved stage cannot be read")
        self.initial_hash = file_sha256(self.path)

    def _end_undo(self):
        if getattr(self, "undo", 0):
            self.doc.EndUndoRecord(self.undo)
            self.undo = 0

    def rollback(self):
        if not self.transaction_open:
            return
        try:
            for action, payload in reversed(self.journal):
                if action == "add":
                    self.doc.Objects.Delete(payload, True)
                else:
                    self.doc.Objects.Add(*payload)
            for identifier in reversed(self.new_layers):
                layer = self.doc.Layers.FindId(identifier)
                if layer is not None and not layer.IsDeleted:
                    self.doc.Layers.Delete(layer.Index, True)
            for identifier, visible, model_visible, persistent, model_persistent, color, plot_color, plot_weight, linetype_index in self.layer_state:
                layer = self.doc.Layers.FindId(identifier)
                if layer is None or layer.IsDeleted:
                    continue
                layer.IsVisible, layer.ModelIsVisible = visible, model_visible
                layer.SetPersistentVisibility(persistent)
                layer.ModelPersistentVisibility = model_persistent
                layer.Color, layer.PlotColor = color, plot_color
                layer.PlotWeight, layer.LinetypeIndex = plot_weight, linetype_index
                layer.CommitChanges()
            for i in reversed(range(self.doc.Strings.Count)):
                self.doc.Strings.Delete(self.doc.Strings.GetKey(i))
            for key, value in self.old_strings:
                self.doc.Strings.SetString(key, value)
            self.doc.ModelUnitSystem, self.doc.EarthAnchorPoint = self.old_units, self.old_anchor
            settings = self.doc.RenderSettings
            settings.RenderBackfaces = self.old_backfaces
            self.doc.RenderSettings = settings
            self.doc.Modified = False
            self.doc.Views.Redraw()
        finally:
            self._end_undo()
            self.transaction_open = False

    def close(self):
        self._end_undo()
        self.Rhino.RhinoApp.EscapeKeyPressed -= self._escape
        self.Rhino.UI.StatusBar.HideProgressMeter(self.serial)
