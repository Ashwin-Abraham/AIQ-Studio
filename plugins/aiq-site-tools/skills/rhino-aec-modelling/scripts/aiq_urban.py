"""Call AIQ Urban messages from Python running on Rhino's UI thread."""

import json
from uuid import UUID


_GEOMETRY_ACTIONS = frozenset({"transit", "building", "zone", "divider", "landuse"})
_OTHER_ACTIONS = frozenset({"landuselistedit", "exportexcel"})


def send(message_type, *, object_ids=None, **fields):
    """Apply one AIQ Urban action to the active Rhino document."""
    import clr
    import Rhino
    from System import AppDomain

    document = Rhino.RhinoDoc.ActiveDoc
    if document is None:
        raise RuntimeError("Open the target Rhino document first.")

    action = message_type.lower()
    if action not in _GEOMETRY_ACTIONS | _OTHER_ACTIONS:
        raise ValueError(f"Unsupported AIQ Urban action: {message_type}")
    if "messageType" in fields or "objectIds" in fields:
        raise ValueError("Pass message_type and object_ids as separate arguments.")

    message = {"messageType": action, **fields}
    if action in _GEOMETRY_ACTIONS:
        if object_ids is None or isinstance(object_ids, (str, bytes)):
            raise ValueError(f"{action} needs a list of Rhino object IDs.")
        ids = list(dict.fromkeys(str(UUID(str(value))) for value in object_ids))
        if not ids:
            raise ValueError(f"{action} needs at least one Rhino object ID.")
        message["objectIds"] = ids
    elif object_ids is not None:
        raise ValueError(f"{action} does not take Rhino object IDs.")

    if action == "exportexcel" and not str(fields.get("filePath", "")).strip():
        raise ValueError("exportexcel needs a filePath.")

    assembly = next(
        (
            item
            for item in AppDomain.CurrentDomain.GetAssemblies()
            if item.GetName().Name == "AIQ.Urban.RhinoPlugin"
        ),
        None,
    )
    if assembly is None:
        raise RuntimeError("Load the AIQ Urban plug-in in Rhino first.")

    clr.AddReference(assembly.FullName)
    from AIQ.Urban.RhinoPlugin.HTML_UI import MessageConverter

    active_document = Rhino.RhinoDoc.ActiveDoc
    if active_document is None or active_document.RuntimeSerialNumber != document.RuntimeSerialNumber:
        raise RuntimeError("The active Rhino document changed before the AIQ Urban call.")

    response = MessageConverter.Convert(json.dumps(message)).HandleMessage()
    if action == "exportexcel" and response.Status != "Succeeded":
        raise RuntimeError(response.ErrorMessage or f"Excel export: {response.Status}")
    return response
