# Rhino structure

## Coordinate system

- Use metres.
- Select a suitable projected CRS for the site.
- Put the site centroid near the Rhino origin.
- Set north to world `+Y`.
- Set a WGS84 Earth Anchor when the file format and runtime support it.
- Store the projected CRS, WGS84 origin, projected origin, transformation, and vertical datum as document user text.

For an existing model, use its valid units and georeferencing. Transform the site data into that system. Do not change existing units or the Earth Anchor without explicit approval. If georeferencing is incomplete or contradictory, stop and ask before geometry creation.

The current writer accepts metre-based documents with matching `site.projected_crs`, `site.origin_projected`, and `site.origin_wgs84` user text. It rejects other existing frames; it does not convert their units or coordinates automatically.

## Root and branches

Use this base structure. Add only category layers that contain objects.

```text
AIQ Site::
  2D::
    Boundary::
    Buildings::
    Transport::
      Roads::
      Railway::
      Water Routes::
      Connectors::
    Water::
    Land Use::
    Places::
    QA::Annotations::Run Info::
  3D::
    Boundary::
    Terrain::
    Buildings::
      Footprints::
      Volumes::
      Parts::
      Part Volumes::
      Parent Envelope::
      Terrain Skirts::
      Underground::Vertical Position Unresolved::
    Transport::
      Roads::
      Railway::
      Water Routes::
      Vertical Position Unresolved::
    Water::
    Land Use::
    Places::
    QA::Annotations::Run Info::
```

The `2D` parent is visible during a 2D run. Hide it when the 3D stage is complete, and show the `3D` parent. Source geometry stays at Z = 0. Both branches use the same XY position so the user can compare them.

Generated objects use `site_owner = rhino-site-data-model`, `site_stage`, and a stable `site_key`. Use these fields to replace stage outputs. Preserve user objects, including objects on generated layers. Do not infer ownership from a layer name. The [staged workflow](staged-workflow.md) defines replacement and checkpoint rules.

Use generic classes for layer names. Keep the exact source class, subtype, taxonomy, and other fields as metadata.

## Geometry rules

- Preserve polygon holes and multipolygon parts.
- Normalize polygon rings before mesh creation. Use counter-clockwise exterior rings and clockwise hole rings for building walls and terrain skirts.
- Compute and store normals on each generated mesh.
- Set the document to render backfaces so open mesh faces are visible from both sides. When Rhino is available, run `scripts/disable_backface_culling.py` inside Rhino to turn off the separate application-level viewport setting.
- Clip working geometry to the context before conversion to Rhino geometry.
- Put clipped-part indices on derived objects.
- Keep points as points and linear networks as curves unless the user asks for widths or surfaces.
- Drape ordinary surface roads and railways onto terrain for the 3D comparison branch.
- Put unresolved bridges, tunnels, underground segments, and conflicting level rules in a separate unresolved layer. Do not infer their Z position.
- Do not infer water elevation. A terrain-draped water curve is only a comparison geometry and must say so in metadata.

