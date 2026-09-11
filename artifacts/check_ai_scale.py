import rhinoinside
rhinoinside.load(r'C:\Program Files\Rhino 8\System')
import Rhino, System
from pathlib import Path
doc=Rhino.RhinoDoc.Create(None)
doc.ModelUnitSystem=Rhino.UnitSystem.Millimeters
v=doc.Views.Add('Plan',Rhino.Display.DefinedViewportProjection.Top,System.Drawing.Rectangle(0,0,1000,700),False)
doc.Views.ActiveView=v
v.ActiveViewport.SetProjection(Rhino.Display.DefinedViewportProjection.Top,'Plan',True)
doc.Objects.AddLine(Rhino.Geometry.Point3d(0,0,0),Rhino.Geometry.Point3d(100,100,0))
for units in (Rhino.FileIO.FileAiWriteOptions.Units.Millimeters,Rhino.FileIO.FileAiWriteOptions.Units.Inches):
    for scale in (1.0,72/25.4):
        opts=Rhino.FileIO.FileAiWriteOptions()
        opts.PreserveModelScale=True
        opts.RhinoScale=1.0
        opts.AIScale=scale
        opts.AiUnits=units
        p=Path('artifacts')/f'check-{units}-{scale}.ai'
        ok=Rhino.FileIO.FileAi.Write(str(p.resolve()),doc,opts)
        print(units,scale,ok, next((x for x in p.read_text().splitlines() if 'BoundingBox' in x),''),flush=True)
doc.Dispose()
