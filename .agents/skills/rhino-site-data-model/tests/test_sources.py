import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from download_overture import download_sources
from process_overture import normalize_features, process_sources
from shapely.geometry import box, mapping, Polygon, MultiPolygon


def feature(geometry,id='f1'):
    return {'type':'Feature','id':id,'geometry':mapping(geometry),'properties':{'class':'residential','sources':[]}}

def collection(*features):
    return {'type':'FeatureCollection','features':list(features)}

class AcquisitionTests(unittest.TestCase):
    def runner(self, command, check):
        output=Path(command[command.index('-o')+1])
        output.write_text(json.dumps(collection()),encoding='utf-8')
        release=command[command.index('--release')+1] if '--release' in command else '2026-08-19.0'
        Path(str(output)+'.state').write_text(json.dumps({'last_release':release}),encoding='utf-8')
    def test_parallel_workers_have_separate_files_one_manifest(self):
        barrier=threading.Barrier(2);paths=[]
        def runner(command,check):
            paths.append(command[command.index('-o')+1]);barrier.wait(timeout=5);self.runner(command,check)
        with tempfile.TemporaryDirectory() as temp:
            result=download_sources([0,0,1,1],temp,'2026-08-19.0',['building','water'],2,runner)
            self.assertEqual(len(set(paths)),2)
            self.assertEqual(len(result['files']),2)
            self.assertEqual(json.loads((Path(temp)/'source-manifest.json').read_text())['release'],'2026-08-19.0')
            self.assertFalse(list(Path(temp).glob('.acquire-*')))
    def test_sequential_resolves_release_once(self):
        commands=[]
        def runner(command,check):commands.append(command);self.runner(command,check)
        with tempfile.TemporaryDirectory() as temp:
            download_sources([0,0,1,1],temp,feature_types=['building','water'],runner=runner)
        self.assertNotIn('--release',commands[0]);self.assertEqual(commands[1][commands[1].index('--release')+1],'2026-08-19.0')
    def test_failure_preserves_existing_source_and_manifest(self):
        def runner(command,check):
            if '--type=water' in command:raise RuntimeError('download failed')
            self.runner(command,check)
        with tempfile.TemporaryDirectory() as temp:
            old=Path(temp)/'building.geojson';old.write_text('old')
            manifest=Path(temp)/'source-manifest.json';manifest.write_text('old manifest')
            with self.assertRaises(RuntimeError):download_sources([0,0,1,1],temp,'2026-08-19.0',['building','water'],runner=runner)
            self.assertEqual(old.read_text(),'old');self.assertEqual(manifest.read_text(),'old manifest')
    def test_rejects_unsafe_types_and_unpinned_parallel(self):
        with tempfile.TemporaryDirectory() as temp:
            for types,workers,release in [(['../bad'],1,None),(['water','water'],1,None),(['water'],2,None),(['water'],5,'2026-08-19.0')]:
                with self.assertRaises(ValueError):download_sources([0,0,1,1],temp,release,types,workers,self.runner)
    def test_rejects_provider_release_mismatch(self):
        def runner(command,check):
            self.runner(command,check)
            Path(command[command.index('-o')+1]+'.state').write_text(json.dumps({'last_release':'different'}))
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):download_sources([0,0,1,1],temp,'2026-08-19.0',['water'],runner=runner)
            self.assertFalse((Path(temp)/'source-manifest.json').exists())

class NormalizationTests(unittest.TestCase):
    def test_repair_retains_collapsed_line_and_polygon(self):
        polygon=Polygon([(0,0),(2,0),(2,2),(1,2),(1,3),(1,2),(0,2),(0,0)])
        records=normalize_features({'water':collection(feature(polygon))},lambda x,y,z=None:(x,y),box(-1,-1,4,4))
        self.assertEqual({part['kind'] for part in records[0]['parts']},{'Polygon','LineString'})
        self.assertTrue(records[0]['geometry_repaired'])
        self.assertEqual({part['source_part_index'] for part in records[0]['parts']},{0})
    def test_source_parts_and_clipped_parts_remain_identifiable(self):
        geometry=MultiPolygon([box(0,0,2,2),box(3,0,5,2)])
        records=normalize_features({'building':collection(feature(geometry))},lambda x,y,z=None:(x,y),box(1,-1,4,4))
        parts=records[0]['parts'];self.assertEqual([p['source_part_index'] for p in parts],[0,1]);self.assertEqual([p['clipped_part_index'] for p in parts],[0,1])
        self.assertTrue(all(p[2]==0 for part in parts for p in part['points']))
    def test_process_is_terrain_free_and_validates_contract(self):
        context={'projected_crs':'EPSG:3857','origin_projected':[0,0],'origin_wgs84':[0,0],'context_bounds_local':[-200,-200,200,200],'context_bounds_wgs84':[-.002,-.002,.002,.002],'context_selection_method':'test'}
        data=process_sources({'building':collection(feature(box(0,0,.001,.001)))},box(0,0,.001,.001),context,{'release':'2026-08-19.0'},'test','manifest','report','2026-01-01')
        self.assertNotIn('terrain',data);self.assertEqual(len(data['features']),1)
        with self.assertRaises(ValueError):process_sources({'building':collection(feature(box(0,0,.001,.001)),feature(box(0,0,.001,.001)))},box(0,0,.001,.001),context,{'release':'2026-08-19.0'},'test','manifest','report')

if __name__=='__main__':unittest.main()
