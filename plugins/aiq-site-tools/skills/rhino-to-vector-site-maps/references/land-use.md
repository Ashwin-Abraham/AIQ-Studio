# Land Use

Show the predominant recorded human use of areas from `land_use`. Keep physical land cover and building use as separate meanings. Draw specific contained uses above broad enclosing uses, such as pitches and gardens above a park. For conflicting overlaps, select a source explicitly and record the decision. Keep unresolved conflicts as separate layers with a report entry.

| Legend group | RGB hex or style | Source examples or rule |
| --- | --- | --- |
| Residential | `#D8BE66` | Residential |
| Commercial and retail | `#E78A52` | Commercial, retail |
| Industrial and utilities | `#8C78A8` | Industrial, works |
| Education and institutions | `#527CB8` | School, university, hospital, institutional, religious |
| Parks and recreation | `#D3E6AF` | Park, pitch, playground, recreation ground, zoo |
| Gardens and productive land | `#A5B85B` | Garden, allotments, farmland, orchard, managed forest |
| Transport | `#7D8993` | Railway, highway, pedestrian, plaza |
| Development land | `#C49A78` | Construction; brownfield without confirmed unused status |
| Unused land | No fill; `#8C8C8C` diagonal hatch | Recorded unused or disused status |
| Other recorded use | `#B6ADA0` | A valid use that does not fit the groups above |

Use the table order in the legend, and semantic containment for paint order. Keep detailed source classes as sublayers. Preserve protected designations as outlines or hatches over the selected use.

For **Unused land**, use a single 45-degree hatch, 0.15 mm stroke, and 1.5 mm spacing at print size. The area and the pattern background must have no fill, so the base map remains visible. Clip the hatch to polygon holes. Record the evidence for unused status: an explicit source property or a documented project correction. Brownfield, greenfield, and missing data alone do not establish current unused status. Keep construction distinct from unused land.

Leave areas without mapped use without thematic fill or hatch. Explain them as **No mapped land-use data** in a coverage note. Map source lines and points as their native marks; they do not establish an area. Preserve source names and add selected area labels. Draw light building outlines above land-use fills so the urban form remains readable.

Check that unused land has evidence and a transparent hatch, data gaps remain distinct, and nested uses remain visible. Compute coverage from polygon unions inside the stated extent so overlaps do not inflate the area. The result describes mapped use, not ownership, public access, or planning status.
