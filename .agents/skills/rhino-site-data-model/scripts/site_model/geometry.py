#!/usr/bin/env python3
"""Prepare independent Rhino stages in memory from checked source features."""

import hashlib
import json
import math
import uuid

import rhino3dm as r3d
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles

from .contract import METADATA_CONTRACT

def triangulate(polygon):
    return list(constrained_delaunay_triangles(polygon).geoms)

FLOOR_HEIGHT = 3.5
ROOT = "AIQ Site"
COLORS = {
    "Buildings": (196, 126, 70, 255), "Transport": (80, 80, 80, 255),
    "Water": (30, 125, 215, 255), "Land Use": (55, 150, 75, 255),
    "Places": (220, 80, 140, 255), "Terrain": (170, 185, 140, 255),
    "Boundary": (230, 45, 45, 255), "QA": (30, 30, 30, 255),
}


def finalize_mesh(mesh):
    mesh.Compact()
    mesh.Normals.ComputeNormals()
    mesh.Normals.UnitizeNormals()
    return mesh


def safe_name(value):
    return str(value or "Other Unclassified").replace("::", "-")


def polyline_curve(points, z_function=None, z_override=None):
    polyline = r3d.Polyline()
    for x, y, z in points:
        value = z_override if z_override is not None else z_function(x, y) if z_function else z
        polyline.Add(x, y, value)
    return polyline.ToPolylineCurve()


class TerrainSampler:
    def __init__(self, terrain, flat_elevation=None):
        self.flat_elevation = flat_elevation
        self.rows = (terrain or {}).get("rows") or []
        self.row_count = len(self.rows)
        self.column_count = len(self.rows[0]) if self.rows else 0
        self.available = self.row_count >= 2 and self.column_count >= 2
        if not self.available:
            if self.rows or flat_elevation is None or not math.isfinite(flat_elevation):
                raise ValueError("Provide a valid terrain grid or an explicit finite flat elevation")
        if self.available:
            if any(len(row) != self.column_count for row in self.rows):
                raise ValueError("Terrain grid rows have different lengths")
            if any(len(p) != 3 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in p) for row in self.rows for p in row):
                raise ValueError("Terrain grid contains missing or non-finite values")
            p00, p01, p10 = self.rows[0][0], self.rows[0][1], self.rows[1][0]
            self.p00 = p00
            self.ax, self.ay = p01[0] - p00[0], p01[1] - p00[1]
            self.bx, self.by = p10[0] - p00[0], p10[1] - p00[1]
            self.determinant = self.ax * self.by - self.ay * self.bx
            if abs(self.determinant) < 1e-12:
                raise ValueError("Terrain grid axes are degenerate")
            for r, row in enumerate(self.rows):
                for c, point in enumerate(row):
                    if abs(point[0] - (p00[0] + c*self.ax + r*self.bx)) > 1e-6 or abs(point[1] - (p00[1] + c*self.ay + r*self.by)) > 1e-6:
                        raise ValueError("Terrain grid must use regular coordinates")

    def z(self, x, y):
        if not self.available:
            return self.flat_elevation
        dx, dy = x - self.p00[0], y - self.p00[1]
        column_value = (dx * self.by - dy * self.bx) / self.determinant
        row_value = (self.ax * dy - self.ay * dx) / self.determinant
        if column_value < -1e-8 or row_value < -1e-8 or column_value > self.column_count - 1 + 1e-8 or row_value > self.row_count - 1 + 1e-8:
            raise ValueError("Geometry is outside terrain coverage")
        c0 = max(0, min(self.column_count - 2, math.floor(column_value)))
        r0 = max(0, min(self.row_count - 2, math.floor(row_value)))
        u = max(0.0, min(1.0, column_value - c0))
        v = max(0.0, min(1.0, row_value - r0))
        z00, z01 = self.rows[r0][c0][2], self.rows[r0][c0 + 1][2]
        z10, z11 = self.rows[r0 + 1][c0][2], self.rows[r0 + 1][c0 + 1][2]
        return (1 - u) * (1 - v) * z00 + u * (1 - v) * z01 + (1 - u) * v * z10 + u * v * z11

    def mesh(self):
        if not self.available:
            return None
        mesh = r3d.Mesh()
        for row in self.rows:
            for x, y, z in row:
                mesh.Vertices.Add(x, y, z)
        for row_index in range(self.row_count - 1):
            for column_index in range(self.column_count - 1):
                a = row_index * self.column_count + column_index
                mesh.Faces.AddFace(a, a + 1, a + 1 + self.column_count, a + self.column_count)
        return finalize_mesh(mesh)


def polygon_from_part(part):
    outer = [(point[0], point[1]) for point in part["points"]]
    holes = [[(point[0], point[1]) for point in ring] for ring in part.get("holes", [])]
    polygon = Polygon(outer, holes)
    if not polygon.is_valid or polygon.is_empty or polygon.area <= 0:
        raise ValueError("Polygon must be valid and have positive area")
    return orient(polygon, sign=1.0)


def polygon_rings(polygon):
    return [list(polygon.exterior.coords)] + [list(ring.coords) for ring in polygon.interiors]


def reference_ground(part, sampler):
    polygon = polygon_from_part(part)
    samples = [(point[0], point[1]) for point in part["points"]]
    samples.extend((point[0], point[1]) for ring in part.get("holes", []) for point in ring)
    for triangle in triangulate(polygon):
        if polygon.covers(triangle.representative_point()):
            point = triangle.representative_point()
            samples.append((point.x, point.y))
    if sampler.available:
        # Bound the grid search to this footprint; never scan a full site per building.
        xmin, ymin, xmax, ymax = polygon.bounds
        grid = []
        for x, y in ((xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)):
            dx, dy = x - sampler.p00[0], y - sampler.p00[1]
            grid.append(((dx * sampler.by - dy * sampler.bx) / sampler.determinant,
                         (sampler.ax * dy - sampler.ay * dx) / sampler.determinant))
        cmin = max(0, math.floor(min(p[0] for p in grid)))
        cmax = min(sampler.column_count - 1, math.ceil(max(p[0] for p in grid)))
        rmin = max(0, math.floor(min(p[1] for p in grid)))
        rmax = min(sampler.row_count - 1, math.ceil(max(p[1] for p in grid)))
        for row in sampler.rows[rmin:rmax + 1]:
            for x, y, _ in row[cmin:cmax + 1]:
                if polygon.covers(Point(x, y)):
                    samples.append((x, y))
    values = [sampler.z(x, y) for x, y in samples]
    return max(values) if values else 0.0, len(values)


def height_rule(record):
    properties = record.get("properties") or {}
    feature_type = record.get("feature_type")
    if feature_type == "building_part":
        if properties.get("is_underground"):
            return None, "underground vertical position unresolved", False
        if properties.get("height") is not None:
            return float(properties["height"]), "explicit height", False
        if properties.get("num_floors") is not None:
            return float(properties["num_floors"]) * FLOOR_HEIGHT, "num_floors x 3.5 m", True
        return FLOOR_HEIGHT, "one-floor building-part fallback", True

    if properties.get("height") is not None:
        return float(properties["height"]), "explicit height", False
    if properties.get("num_floors") is not None:
        value = float(properties["num_floors"]) * FLOOR_HEIGHT
        if properties.get("roof_height") is not None:
            value += float(properties["roof_height"])
            return value, "num_floors x 3.5 m plus explicit roof_height", True
        return value, "num_floors x 3.5 m", True
    class_name = str(properties.get("class") or "").lower()
    subtype = str(properties.get("subtype") or "").lower()
    if class_name in {"roof", "carport", "shelter"}:
        return None, "default volume excluded for class", False
    if class_name in {"garage", "garages", "shed", "service", "outbuilding"} or subtype in {"service", "outbuilding"}:
        return FLOOR_HEIGHT, "one-floor small-building fallback", True
    return 3.0 * FLOOR_HEIGHT, "three-floor occupied-building fallback", True


def part_bottom_rule(record):
    properties = record.get("properties") or {}
    if record.get("feature_type") != "building_part":
        return 0.0, "ground", False
    if properties.get("min_height") is not None:
        conflict = False
        if properties.get("min_floor") is not None:
            conflict = abs(float(properties["min_height"]) - float(properties["min_floor"]) * FLOOR_HEIGHT) > 0.001
        return float(properties["min_height"]), "explicit min_height", conflict
    if properties.get("min_floor") is not None:
        return float(properties["min_floor"]) * FLOOR_HEIGHT, "min_floor x 3.5 m", False
    return 0.0, "zero bottom offset", False


def flat_mass(part, bottom_z, top_z):
    polygon = polygon_from_part(part)
    rings = polygon_rings(polygon)
    mesh = r3d.Mesh()
    for ring in rings:
        for index in range(len(ring) - 1):
            x0, y0 = ring[index]
            x1, y1 = ring[index + 1]
            start = len(mesh.Vertices)
            mesh.Vertices.Add(x0, y0, bottom_z)
            mesh.Vertices.Add(x1, y1, bottom_z)
            mesh.Vertices.Add(x1, y1, top_z)
            mesh.Vertices.Add(x0, y0, top_z)
            mesh.Faces.AddFace(start, start + 1, start + 2, start + 3)
    for triangle in triangulate(polygon):
        if not polygon.covers(triangle.representative_point()):
            continue
        points = list(orient(triangle, sign=1.0).exterior.coords)[:3]
        top = len(mesh.Vertices)
        for x, y in points:
            mesh.Vertices.Add(x, y, top_z)
        mesh.Faces.AddFace(top, top + 1, top + 2)
        bottom = len(mesh.Vertices)
        for x, y in points:
            mesh.Vertices.Add(x, y, bottom_z)
        mesh.Faces.AddFace(bottom + 2, bottom + 1, bottom)
    return finalize_mesh(mesh)


def terrain_skirt(part, base_z, sampler):
    mesh = r3d.Mesh()
    rings = polygon_rings(polygon_from_part(part))
    for ring in rings:
        for index in range(len(ring) - 1):
            x0, y0 = ring[index]
            x1, y1 = ring[index + 1]
            if math.hypot(x1 - x0, y1 - y0) < 1e-8:
                continue
            ground_0 = sampler.z(x0, y0)
            ground_1 = sampler.z(x1, y1)
            at_base_0 = abs(base_z - ground_0) < 1e-8
            at_base_1 = abs(base_z - ground_1) < 1e-8
            if at_base_0 and at_base_1:
                continue
            start = len(mesh.Vertices)
            if at_base_0:
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Vertices.Add(x1, y1, ground_1)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2)
            elif at_base_1:
                mesh.Vertices.Add(x0, y0, ground_0)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2)
            else:
                mesh.Vertices.Add(x0, y0, ground_0)
                mesh.Vertices.Add(x1, y1, ground_1)
                mesh.Vertices.Add(x1, y1, base_z)
                mesh.Vertices.Add(x0, y0, base_z)
                mesh.Faces.AddFace(start, start + 1, start + 2, start + 3)
    return finalize_mesh(mesh)


def unresolved_transport_placement(properties):
    """Identify non-surface or uncertain source transport placement rules."""
    if any(properties.get(name) for name in ('is_bridge', 'is_tunnel', 'is_underground', 'is_elevated')):
        return True

    def flagged(value):
        if isinstance(value, str):
            return value in {'is_bridge', 'is_tunnel', 'is_underground', 'is_elevated', 'bridge', 'tunnel', 'underground', 'elevated'}
        if isinstance(value, list):
            return any(flagged(item) for item in value)
        if isinstance(value, dict):
            return any((flagged(key) and bool(item)) or flagged(item) for key, item in value.items())
        return False

    def non_surface(value):
        if value is None or value == 0 or value == '0':
            return False
        if isinstance(value, list):
            return any(non_surface(item) for item in value)
        if isinstance(value, dict):
            if 'value' in value:
                return non_surface(value['value'])
            if 'values' in value:
                return non_surface(value['values'])
        # Do not infer placement from an unrecognized elevation rule.
        return True

    return (flagged(properties.get('road_flags')) or flagged(properties.get('rail_flags'))
            or any(non_surface(properties.get(name)) for name in ('level', 'levels', 'layer', 'elevation')))


def valid_part_parents(data):
    """Return parent IDs that have at least one candidate visible part volume."""
    parents = set()
    for record in data.get('features') or []:
        properties = record.get('properties') or {}
        if record.get('feature_type') != 'building_part' or properties.get('is_underground'):
            continue
        parent_id = properties.get('building_id')
        height, _, _ = height_rule(record)
        if parent_id and height is not None and math.isfinite(height) and height > 0 and any(part.get('kind') == 'Polygon' for part in record.get('parts') or []):
            parents.add(str(parent_id))
    return parents


def prepare_stage(data, stage, terrain=None, flat_elevation=None):
    """Prepare one stage in memory. The caller owns validation, files, and writes."""
    if stage not in {'2d', '3d'}:
        raise ValueError('Stage must be 2d or 3d')
    if stage == '3d' and terrain and flat_elevation is not None:
        raise ValueError('Choose terrain or flat elevation, not both')
    sampler = TerrainSampler(terrain, flat_elevation) if stage == '3d' else None
    part_parents = (set(data['_valid_part_parents']) if '_valid_part_parents' in data else valid_part_parents(data)) if stage == '3d' else set()
    run = data['run']
    model = r3d.File3dm()
    model.ApplicationName = 'rhino-site-data-model'
    model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
    model.Settings.ModelAbsoluteTolerance = 0.001
    model.Settings.ModelAngleToleranceDegrees = 1.0
    model.Settings.RenderSettings.RenderBackFaces = True
    mapping = {'site_name':'name', 'generated_utc':'generated_utc', 'semantic_source':'semantic_source', 'source_release':'source_release', 'projected_crs':'projected_crs', 'origin_wgs84':'origin_wgs84', 'origin_projected':'origin_projected', 'vertical_datum':'vertical_datum', 'source_manifest_path':'source_manifest', 'report_path':'report'}
    for key, target in mapping.items():
        value = run.get(key, 'not set')
        model.Strings['site.' + target] = json.dumps(value) if isinstance(value, (list, dict)) else str(value)
    model.Strings['site.stage'] = stage
    model.Strings['site.metadata_contract'] = METADATA_CONTRACT
    model.Strings['site.height_rules'] = '3.5 m floor; 3-floor occupied fallback; 1-floor small-building and building-part fallback'
    model.Strings['site.render_backfaces'] = 'true'
    earth = model.Settings.EarthAnchorPoint
    earth.Name = run['site_name'] + ' local origin'
    earth.EarthBasepointLongitude, earth.EarthBasepointLatitude = run['origin_wgs84'][:2]
    earth.ModelBasePoint = r3d.Point3d(0, 0, 0)
    earth.ModelNorth = r3d.Vector3d(0, 1, 0)
    cache, keys, warnings = {}, set(), []

    def layer(path, visible=True):
        parent = uuid.UUID(int=0)
        for depth in range(1, len(path.split('::')) + 1):
            full = '::'.join(path.split('::')[:depth])
            if full not in cache:
                item = r3d.Layer()
                item.Name = full.split('::')[-1]
                item.ParentLayerId = parent
                item.Visible = visible if full == path else True
                theme = next((part for part in full.split('::') if part in COLORS), None)
                item.Color = COLORS.get(theme, (120, 120, 120, 255))
                cache[full] = model.Layers.Add(item)
            parent = model.Layers.FindIndex(cache[full]).Id
        return cache[path]

    def add(geometry, path, name, role, record=None, part=0, hole=None, extra=None, visible=True, identity=None):
        attrs = r3d.ObjectAttributes()
        attrs.LayerIndex = layer(path, visible)
        attrs.Name = str(name)
        attrs.ColorSource = r3d.ObjectColorSource.ColorFromLayer
        values = {'site_owner':'rhino-site-data-model', 'site_stage':stage, 'geometry_role':role, 'clipped_part_index':str(part)}
        if record:
            values.update(source_feature_id=str(record.get('id')), source_feature_type=str(record.get('feature_type')), source_feature_version=str(record.get('version')))
            if stage == '2d':
                values.update(generic_category='::'.join(record.get('category_path') or []), source_properties_json=json.dumps(record.get('properties') or {}, sort_keys=True, ensure_ascii=False), source_records_json=json.dumps(record.get('sources') or (record.get('properties') or {}).get('sources') or [], sort_keys=True, ensure_ascii=False))
        if hole is not None:
            values['hole_index'] = str(hole)
        values.update(extra or {})
        key_data = [run['source_release'], stage, record.get('feature_type') if record else identity, record.get('id') if record else identity, values.get('source_part_index'), part, role, hole]
        key = hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        if key in keys:
            raise ValueError('Duplicate geometry identity: ' + str(key_data))
        keys.add(key)
        values['site_key'] = key
        fingerprint = {'geometry':geometry.Encode(), 'layer':path, 'name':attrs.Name, 'visible':visible, 'metadata':values}
        values['site_content_hash'] = hashlib.sha256(json.dumps(fingerprint, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        for key, value in values.items():
            attrs.SetUserString(key, str(value))
        if not geometry.IsValid:
            raise ValueError('Invalid geometry: ' + name)
        model.Objects.Add(geometry, attrs)

    branch = ROOT + '::' + stage.upper()
    layer(branch)
    z = sampler.z if sampler else lambda x,y: 0.0
    include_context = data.get('_include_context', True)
    if include_context and sampler and sampler.available:
        add(sampler.mesh(), branch+'::Terrain', 'Terrain', 'terrain_mesh', identity='terrain')
    for boundary_name in ('site', 'context'):
        for part_index, part in enumerate((data.get(boundary_name) or {}).get('parts') or []):
            part_index = part.get('clipped_part_index', part_index)
            for hole_index, ring in enumerate([part['points']] + (part.get('holes') or [])):
                add(polyline_curve(ring, z_function=z), branch+'::Boundary::'+boundary_name.title(), boundary_name.title(), 'source_plan_boundary' if stage == '2d' else 'terrain_draped_boundary', part=part_index, hole=hole_index-1 if hole_index else None, identity=boundary_name, extra={'source_part_index':part.get('source_part_index',part_index)})
    for record in data.get('features') or []:
        category = [safe_name(v) for v in record.get('category_path') or ['Other']]
        path = branch+'::'+'::'.join(category)
        name = record.get('name') or '{} {}'.format(record.get('feature_type'),record.get('id'))
        props = record.get('properties') or {}
        underground = record.get('feature_type') == 'building_part' and props.get('is_underground')
        unresolved_transport = category[0] == 'Transport' and unresolved_transport_placement(props)
        unresolved = stage == '3d' and (underground or unresolved_transport)
        if unresolved:
            path = branch + ('::Buildings::Underground::Vertical Position Unresolved' if underground else '::Transport::Vertical Position Unresolved')
        for part_index, part in enumerate(record.get('parts') or []):
            part_index = part.get('clipped_part_index', part_index)
            part_metadata = {'source_part_index':part.get('source_part_index',part_index)}
            role = ('source_plan_' if stage == '2d' else 'terrain_draped_') + part['kind'].lower()
            extra = {'source_z':'0'} if stage == '2d' else {'placement_method':'terrain comparison only' if sampler.available else 'explicit flat elevation; no terrain placement'}
            extra.update(part_metadata)
            if stage == '3d' and category[0] == 'Water':
                extra['water_elevation_status'] = 'comparison geometry; water elevation unresolved'
            local_z = (lambda x,y: 0.0) if unresolved else z
            if unresolved:
                role = 'vertical_position_unresolved'
                extra['placement_method'] = 'unresolved; source plan at Z=0'
            if part['kind'] == 'Point':
                x,y,_ = part['points'][0]
                add(r3d.Point(r3d.Point3d(x,y,local_z(x,y))), path, name, role, record, part_index, extra=extra, visible=not unresolved)
            else:
                add(polyline_curve(part['points'], z_function=local_z), path, name, role, record, part_index, extra=extra, visible=not unresolved)
                for hole_index,hole in enumerate(part.get('holes') or []):
                    add(polyline_curve(hole,z_function=local_z),path,name+' hole', 'source_plan_hole' if stage == '2d' else 'terrain_draped_hole',record,part_index,hole_index,extra,not unresolved)
            if stage == '2d' or record.get('feature_type') not in {'building','building_part'} or part['kind'] != 'Polygon':
                continue
            height, method, estimated = height_rule(record)
            if height is None:
                continue
            if not math.isfinite(height) or height <= 0:
                raise ValueError('Building height must be finite and positive: '+str(record.get('id')))
            base,count = reference_ground(part,sampler)
            offset, offset_method,conflict = part_bottom_rule(record)
            if not math.isfinite(offset):
                raise ValueError('Building offset must be finite')
            if conflict:
                warnings.append({'id':record.get('id'),'warning':'min_height and min_floor conflict; min_height used'})
            if record['feature_type'] == 'building_part':
                volume_branch,visible = 'Part Volumes',True
            elif str(record.get('id')) in part_parents:
                volume_branch,visible = 'Parent Envelope',False
            else:
                volume_branch,visible = 'Volumes',True
            meta = {'reference_ground_z':base,'reference_ground_sample_count':count,'reference_ground_method':'maximum ring, interior triangle, and covered terrain grid samples','terrain_source':(terrain or {}).get('dataset','explicit flat elevation'),'bottom_offset_m':offset,'bottom_offset_method':offset_method,'building_height_m':height,'height_method':method,'height_is_estimated':str(estimated).lower(),'floor_to_floor_m':FLOOR_HEIGHT,'volume_direction':'+Z'}
            meta.update(part_metadata)
            mass = flat_mass(part,base+offset,base+offset+height)
            if not mass.IsClosed:
                raise ValueError('Building mass is not closed: '+str(record.get('id')))
            add(mass,branch+'::Buildings::'+volume_branch+'::'+category[-1],name+' volume','building_volume',record,part_index,extra=meta,visible=visible)
            if record['feature_type'] == 'building' and sampler.available:
                skirt = terrain_skirt(part,base,sampler)
                if len(skirt.Faces):
                    add(skirt,branch+'::Buildings::Terrain Skirts::'+category[-1],name+' terrain skirt','building_terrain_skirt',record,part_index,extra=dict(part_metadata,reference_ground_z=base))
    bounds = (data.get('context') or {}).get('bounds_local') or [-150,-150,150,150]
    lines = [run['site_name'], 'Stage: '+stage, 'Generated: '+run['generated_utc'], 'Source: '+run['semantic_source']+' '+run['source_release'], 'CRS: '+run['projected_crs'], 'Vertical datum: '+str(run.get('vertical_datum') or 'not set'), 'Manifest: '+run.get('source_manifest_path',''), 'Report: '+run.get('report_path','')]
    for index,text in enumerate(lines if include_context else []):
        dot = r3d.TextDot(text,r3d.Point3d(bounds[0],bounds[3]-index*5,0))
        add(dot,ROOT+'::QA::Annotations::Run Info::'+stage.upper(),'Run Info','run_annotation',part=index,identity='run')
    model.Strings['site.warnings'] = json.dumps(warnings)
    return model
