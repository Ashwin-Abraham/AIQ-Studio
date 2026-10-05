"""Read terrain inputs and publish a complete run without replacing old results."""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile


def read_input(path, layer):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if data.get("units") != "metres":
            raise ValueError("JSON terrain coordinates must use metres in XY and Z.")
        vertices, faces = data["vertices"], data["faces"]
        metadata = data.get("metadata", {})
        source_faces = data.get("source_faces", [{"face": i} for i in range(len(faces))])
    elif path.suffix.lower() == ".3dm":
        vertices, faces, source_faces, metadata = _read_rhino(path, layer)
    else:
        raise ValueError("Input must be a .json terrain or .3dm model.")
    if len(source_faces) != len(faces):
        raise ValueError("source_faces must contain one record per input face.")
    if faces and not metadata.get("crs"):
        raise ValueError("Record the projected CRS in metadata.crs or site.projected_crs.")
    return vertices, faces, source_faces, {"path": str(path.resolve()), "sha256": digest,
                                         "layer": layer, "metadata": metadata}


def _read_rhino(path, layer):
    try:
        import rhino3dm
    except ImportError as error:
        raise ValueError("Reading .3dm requires rhino3dm >=8,<9.") from error
    model = rhino3dm.File3dm.Read(str(path))
    if model is None:
        raise ValueError("Cannot read the Rhino model.")
    if model.Settings.ModelUnitSystem != rhino3dm.UnitSystem.Meters:
        raise ValueError("Export a terrain JSON in metres from the non-metre Rhino model.")
    strings = dict(model.Strings)
    metadata = {"crs": strings.get("site.projected_crs"),
                "origin_projected": strings.get("site.origin_projected"),
                "vertical_datum": strings.get("site.vertical_datum", "unknown"),
                "terrain_source": strings.get("site.terrain", "unknown"),
                "weld": "identical XYZ vertices only"}
    vertices, faces, sources, lookup = [], [], [], {}
    for obj in model.Objects:  # Saved hidden and locked objects are included.
        if model.Layers[obj.Attributes.LayerIndex].FullPath != layer:
            continue
        if not isinstance(obj.Geometry, rhino3dm.Mesh):
            raise ValueError("Terrain layer contains non-mesh geometry. Export a checked mesh.")
        indices = []
        for point in obj.Geometry.Vertices:
            xyz = (point.X, point.Y, point.Z)
            if xyz not in lookup:
                lookup[xyz] = len(vertices)
                vertices.append(xyz)
            indices.append(lookup[xyz])
        for face_id, face in enumerate(obj.Geometry.Faces):
            count = 3 if face[2] == face[3] else 4
            faces.append([indices[face[i]] for i in range(count)])
            sources.append({"object_id": str(obj.Attributes.Id), "face": face_id})
    return vertices, faces, sources, metadata


def publish(output, documents):
    """Use a new output directory. A failure cannot leave a partial final run."""
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output already exists. Select a new run directory.")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".terrain-water-", dir=output.parent)).resolve()
    try:
        for name, data in documents.items():
            if Path(name).name != name:
                raise ValueError("Output names must be file names, not paths.")
            (staging / name).write_text(json.dumps(data, allow_nan=False), encoding="utf-8")
        staging.rename(output)
    finally:
        if staging.exists() and staging.parent == output.parent:
            shutil.rmtree(staging)
