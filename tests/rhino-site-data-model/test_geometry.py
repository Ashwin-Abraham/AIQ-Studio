import copy
import json
import sys
import unittest
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH
from unittest.mock import patch
sys.path.insert(0,str(SCRIPTS_PATH))
from site_model.geometry import (prepare_stage, TerrainSampler, polygon_from_part,
                                 flat_mass, planar_fill, reference_ground)

def fixture():
    part={'kind':'Polygon','points':[[0,0,9],[10,0,9],[10,10,9],[0,10,9],[0,0,9]],'holes':[[[3,3,9],[3,7,9],[7,7,9],[7,3,9],[3,3,9]]]}
    return {'run':{'site_name':'Test','generated_utc':'2026-01-01','semantic_source':'Overture','source_release':'test','projected_crs':'EPSG:27700','origin_wgs84':[0,51],'origin_projected':[0,0],'vertical_datum':'test','source_manifest_path':'manifest','report_path':'report'},'site':{'parts':[part]},'context':{'parts':[part]},'features':[{'id':'building1','feature_type':'building','category_path':['Buildings','Residential'],'properties':{'height':12},'parts':[part]}]}

class GeometryTests(unittest.TestCase):
    def test_partition_skips_context_and_preserves_part_identity(self):
        data=fixture();data['_include_context']=False;data['site']['parts']=[];data['context']['parts']=[]
        data['features'][0]['parts'][0].update(source_part_index=7,clipped_part_index=12)
        terrain={'rows':[[[0,0,1],[10,0,2]],[[0,10,3],[10,10,4]]]}
        model=prepare_stage(data,'3d',terrain=terrain)
        for obj in model.Objects:
            self.assertNotIn(obj.Attributes.GetUserString('geometry_role'),{'terrain_mesh','run_annotation'})
            self.assertEqual(obj.Attributes.GetUserString('source_part_index'),'7')
            self.assertEqual(obj.Attributes.GetUserString('clipped_part_index'),'12')

    def test_road_flags_and_elevation_rules_keep_z_unresolved(self):
        for props in ({'road_flags':[{'between':[0,1],'values':['is_bridge']}]},{'elevation':[{'between':[0,1],'value':1}]},{'elevation':[{'unknown':'rule'}]}):
            data=fixture();record=data['features'][0];record.update(feature_type='segment',category_path=['Transport','Roads'],properties=props)
            record['parts']=[{'kind':'LineString','points':[[0,0,0],[10,10,0]]}]
            model=prepare_stage(data,'3d',flat_elevation=15)
            obj=next(o for o in model.Objects if o.Attributes.GetUserString('source_feature_id'))
            self.assertEqual(obj.Attributes.GetUserString('geometry_role'),'vertical_position_unresolved')
            self.assertEqual(obj.Geometry.GetBoundingBox().Max.Z,0)
            self.assertFalse(model.Layers.FindIndex(obj.Attributes.LayerIndex).Visible)

    def test_parent_without_valid_parts_remains_visible(self):
        data=fixture();data['features'][0]['properties']['has_parts']=True
        model=prepare_stage(data,'3d',flat_elevation=0)
        volume=next(obj for obj in model.Objects if obj.Attributes.GetUserString('geometry_role')=='building_volume')
        self.assertTrue(model.Layers.FindIndex(volume.Attributes.LayerIndex).Visible)

    def test_concave_mass_with_reversed_winding(self):
        part={'kind':'Polygon','points':[[0,0,0],[0,8,0],[2,8,0],[2,2,0],[8,2,0],[8,0,0],[0,0,0]],'holes':[]}
        mesh=flat_mass(part,3,8)
        self.assertTrue(mesh.IsClosed)
        self.assertEqual(len(mesh.Normals),len(mesh.Vertices))
        area=0
        for a,b,c,d in mesh.Faces:
            p,q,r=[mesh.Vertices[i] for i in (a,b,c)]
            if p.Z==q.Z==r.Z==8:
                signed=(q.X-p.X)*(r.Y-p.Y)-(q.Y-p.Y)*(r.X-p.X)
                self.assertGreater(signed,0)
                area+=signed/2
        self.assertAlmostEqual(area,polygon_from_part(part).area)

    def test_reference_ground_includes_interior_peak(self):
        part={'kind':'Polygon','points':[[0,0,0],[10,0,0],[10,10,0],[0,10,0],[0,0,0]]}
        rows=[[[x,y,30 if x==5 and y==5 else 0] for x in (0,5,10)] for y in (0,5,10)]
        self.assertEqual(reference_ground(part,TerrainSampler({'rows':rows}))[0],30)

    def test_file_can_cross_worker_boundary(self):
        import rhino3dm
        model=prepare_stage(fixture(),'2d')
        copy=rhino3dm.File3dm.Decode(model.Encode())
        self.assertEqual(len(copy.Objects),len(model.Objects))
    def test_full_source_metadata_is_only_on_2d_objects(self):
        data=fixture();data['features'][0]['sources']=[{'dataset':'test'}]
        plan=prepare_stage(data,'2d')
        source=next(o for o in plan.Objects if o.Attributes.GetUserString('source_feature_id'))
        self.assertEqual(json.loads(source.Attributes.GetUserString('source_properties_json')),{'height':12})
        self.assertEqual(json.loads(source.Attributes.GetUserString('source_records_json')),[{'dataset':'test'}])
        self.assertEqual(source.Attributes.GetUserString('generic_category'),'Buildings::Residential')
        derived=prepare_stage(data,'3d',flat_elevation=0)
        for obj in (o for o in derived.Objects if o.Attributes.GetUserString('source_feature_id')):
            self.assertEqual(obj.Attributes.GetUserString('source_feature_type'),'building')
            self.assertFalse(obj.Attributes.GetUserString('source_properties_json'))
            self.assertFalse(obj.Attributes.GetUserString('source_records_json'))
            self.assertFalse(obj.Attributes.GetUserString('generic_category'))
        volume=next(o for o in derived.Objects if o.Attributes.GetUserString('geometry_role')=='building_volume')
        self.assertEqual(volume.Attributes.GetUserString('height_method'),'explicit height')

    def test_2d_never_constructs_sampler(self):
        with patch('site_model.geometry.TerrainSampler',side_effect=AssertionError('terrain touched')), patch('site_model.geometry.height_rule',side_effect=AssertionError('3D heights touched')):
            model=prepare_stage(fixture(),'2d',terrain={'invalid':True})
        self.assertFalse(any(layer.Name=='3D' for layer in model.Layers))
        self.assertTrue(next(layer for layer in model.Layers if layer.Name=='2D').Visible)
        for obj in model.Objects:
            box=obj.Geometry.GetBoundingBox();self.assertAlmostEqual(box.Min.Z,0);self.assertAlmostEqual(box.Max.Z,0)
        self.assertEqual(sum(o.Attributes.GetUserString('hole_index')=='0' for o in model.Objects),3)
    def test_3d_requires_explicit_placement(self):
        with self.assertRaises(ValueError):prepare_stage(fixture(),'3d')
    def test_closed_mass_holes_and_positive_z(self):
        model=prepare_stage(fixture(),'3d',flat_elevation=5)
        mass=next(o.Geometry for o in model.Objects if o.Attributes.GetUserString('geometry_role')=='building_volume')
        self.assertTrue(mass.IsClosed)
        self.assertAlmostEqual(mass.GetBoundingBox().Min.Z,5);self.assertAlmostEqual(mass.GetBoundingBox().Max.Z,17)
        from shapely.geometry import Polygon
        polygon=polygon_from_part(fixture()['features'][0]['parts'][0]);area=0
        for a,b,c,d in mass.Faces:
            pts=[mass.Vertices[i] for i in (a,b,c)]
            if all(p.Z==17 for p in pts):
                tri=Polygon([(p.X,p.Y) for p in pts]);self.assertTrue(polygon.covers(tri));area+=tri.area
        self.assertAlmostEqual(area,polygon.area)
    def test_hashes_stable_and_geometry_sensitive(self):
        def hashes(m):return {o.Attributes.GetUserString('site_key'):o.Attributes.GetUserString('site_content_hash') for o in m.Objects}
        first=hashes(prepare_stage(fixture(),'2d'));second=hashes(prepare_stage(fixture(),'2d'));self.assertEqual(first,second)
        data=fixture();data['features'][0]['parts'][0]['points'][1][0]=11
        third=hashes(prepare_stage(data,'2d'));self.assertEqual(set(first),set(third));self.assertNotEqual(first,third)
        from site_model.cartography import LayerStyle, style_for as real_style
        def changed_style(record=None, **options):
            style=real_style(record, **options)
            return LayerStyle(style.color,style.plot_weight_mm,style.display_order+(7 if record else 0))
        with patch('site_model.geometry.style_for',side_effect=changed_style):
            fourth=hashes(prepare_stage(fixture(),'2d'))
        self.assertEqual(set(first),set(fourth));self.assertNotEqual(first,fourth)
    def test_terrain_rejects_missing_and_outside(self):
        terrain={'rows':[[[0,0,1],[10,0,2]],[[0,10,3],[10,10,4]]]};sampler=TerrainSampler(terrain)
        self.assertAlmostEqual(sampler.z(5,5),2.5)
        with self.assertRaises(ValueError):sampler.z(11,5)
        terrain['rows'][0][0][2]=None
        with self.assertRaises(ValueError):TerrainSampler(terrain)
    def test_parent_hidden_and_part_offset(self):
        data=fixture();data['features'][0]['properties']['has_parts']=True
        part=copy.deepcopy(data['features'][0]);part.update(id='part1',feature_type='building_part');part['properties']={'min_height':4,'height':3,'building_id':'building1'};data['features'].append(part)
        model=prepare_stage(data,'3d',flat_elevation=2)
        for obj in model.Objects:
            if obj.Attributes.GetUserString('geometry_role')!='building_volume':continue
            if obj.Attributes.GetUserString('source_feature_id')=='building1':self.assertFalse(model.Layers.FindIndex(obj.Attributes.LayerIndex).Visible)
            else:self.assertAlmostEqual(obj.Geometry.GetBoundingBox().Min.Z,6)

    def test_planar_fill_preserves_hole_and_is_flat(self):
        from shapely.geometry import Polygon
        part=fixture()['features'][0]['parts'][0]
        mesh=planar_fill(part)
        area=0
        polygon=polygon_from_part(part)
        for a,b,c,d in mesh.Faces:
            points=[mesh.Vertices[i] for i in (a,b,c)]
            triangle=Polygon([(point.X,point.Y) for point in points])
            self.assertTrue(polygon.covers(triangle))
            self.assertTrue(all(point.Z == 0 for point in points))
            area+=triangle.area
        self.assertAlmostEqual(area,polygon.area)
        self.assertEqual(len(mesh.Normals),len(mesh.Vertices))

    def test_new_themes_have_safe_2d_and_3d_representations(self):
        data=fixture();part=data['features'][0]['parts'][0]
        data['features']=[
            {'id':'bathy','feature_type':'bathymetry','version':1,'category_path':['Bathymetry','Depth 20 m'],'properties':{'depth':20},'sources':[],'parts':[part]},
            {'id':'cover','feature_type':'land_cover','version':1,'category_path':['Land Cover','Forest'],'properties':{'subtype':'forest'},'sources':[],'parts':[part]},
            {'id':'infra','feature_type':'infrastructure','version':1,'category_path':['Infrastructure','Power','Substation'],'properties':{'subtype':'power','class':'substation','height':12},'sources':[],'parts':[{'kind':'Point','points':[[5,5,0]],'source_part_index':0,'clipped_part_index':0}]},
        ]
        plan=prepare_stage(data,'2d')
        fills=[obj for obj in plan.Objects if obj.Attributes.GetUserString('geometry_role')=='source_plan_fill']
        self.assertEqual({obj.Attributes.GetUserString('source_feature_type') for obj in fills},{'bathymetry','land_cover'})
        for obj in fills:
            self.assertEqual(obj.Geometry.GetBoundingBox().Min.Z,0)
            self.assertEqual(obj.Attributes.PlotWeightSource.name,'PlotWeightFromLayer')
        model=prepare_stage(data,'3d',flat_elevation=7)
        derived=[obj for obj in model.Objects if obj.Attributes.GetUserString('source_feature_type')]
        self.assertEqual({obj.Attributes.GetUserString('source_feature_type') for obj in derived},{'infrastructure'})
        item=derived[0];self.assertEqual(item.Attributes.GetUserString('geometry_role'),'vertical_position_unresolved')
        self.assertEqual(item.Geometry.GetBoundingBox().Max.Z,0)
        self.assertFalse(model.Layers.FindIndex(item.Attributes.LayerIndex).Visible)
if __name__=='__main__':unittest.main()
