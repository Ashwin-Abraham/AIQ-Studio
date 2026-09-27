"""Disable backface culling in Rhino display modes.

Run this script inside Rhino after the site model opens. The 3DM render setting and
the Rhino viewport display-mode setting are separate settings.
"""

import Rhino


def main():
    changed = []
    for mode in Rhino.Display.DisplayModeDescription.GetDisplayModes():
        attributes = mode.DisplayAttributes
        if not attributes.CullBackfaces:
            continue
        attributes.CullBackfaces = False
        if Rhino.Display.DisplayModeDescription.UpdateDisplayMode(mode):
            changed.append(mode.EnglishName)

    document = Rhino.RhinoDoc.ActiveDoc
    if document:
        document.Views.Redraw()
    print("Backface culling disabled in {} display mode(s).".format(len(changed)))


if __name__ == "__main__":
    main()
