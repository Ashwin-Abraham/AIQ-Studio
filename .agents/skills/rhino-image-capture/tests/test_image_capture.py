import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/image_capture.py'
spec = importlib.util.spec_from_file_location('image_capture', SCRIPT)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)

# Small valid PNG fixture. Tests exercise orchestration, not Rhino rendering.
import base64
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aXioAAAAASUVORK5CYII=')


class Backend:
    def __init__(self, serial, path):
        self.serial, self.path = serial, path
        self.calls = 0

    def check_identity(self):
        pass

    def png(self, request):
        self.calls += 1
        return PNG


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {'document_serial': 42, 'document_path': str(self.root / 'model.3dm'),
                       'output_root': str(self.root / 'images'),
                       'images': [{'file': 'current.png', 'width': 1, 'height': 1}]}

    def test_public_interface_writes_png_without_project_caches(self):
        result = capture.capture_images(self.config, backend_factory=Backend)
        self.assertTrue(result['completed'])
        self.assertEqual((self.root / 'images/current.png').read_bytes(), PNG)
        self.assertEqual(list(self.root.rglob('*.pyc')), [])
        self.assertEqual(list(self.root.rglob('__pycache__')), [])
        self.assertFalse((self.root / '.venv').exists())

    def test_all_requests_checked_before_any_capture(self):
        self.config['images'].append({'file': '../escape.png'})
        with self.assertRaises(ValueError):
            capture.capture_images(self.config, backend_factory=Backend)
        self.assertFalse((self.root / 'images').exists())
        self.assertFalse((self.root / 'escape.png').exists())

    def test_absolute_output_name_rejected(self):
        self.config['images'][0]['file'] = str(self.root / 'outside.png')
        with self.assertRaises(ValueError):
            capture.capture_images(self.config, backend_factory=Backend)

    def test_existing_output_preserved(self):
        directory = self.root / 'images'
        directory.mkdir()
        target = directory / 'current.png'
        target.write_bytes(b'keep')
        with self.assertRaises(ValueError):
            capture.capture_images(self.config, backend_factory=Backend)
        self.assertEqual(target.read_bytes(), b'keep')

    def test_duplicate_output_rejected(self):
        self.config['images'].append(dict(self.config['images'][0]))
        with self.assertRaises(ValueError):
            capture.capture_images(self.config, backend_factory=Backend)

    def test_invalid_dimensions_bounds_projection(self):
        for change in [{'width': True}, {'width': 0}, {'width': 8192, 'height': 8192},
                       {'bounds': [0, 0, 0, -1, 1, 1]}, {'bounds': [0, 0, 0, float('nan'), 1, 1]},
                       {'projection': 'guess'}, {'axes': 'yes'}]:
            with self.subTest(change=change):
                self.config['images'] = [dict(file='current.png', **change)]
                with self.assertRaises(ValueError):
                    capture.capture_images(self.config, backend_factory=Backend)

    def test_identity_failure_prevents_output(self):
        class WrongDocument(Backend):
            def check_identity(self):
                raise RuntimeError('Wrong document')
        with self.assertRaisesRegex(RuntimeError, 'Wrong document'):
            capture.capture_images(self.config, backend_factory=WrongDocument)
        self.assertFalse((self.root / 'images').exists())

    def test_document_change_during_capture_prevents_output(self):
        class ChangedDocument(Backend):
            def check_identity(self):
                if self.calls:
                    raise RuntimeError('Document changed')
        result = capture.capture_images(self.config, backend_factory=ChangedDocument)
        self.assertFalse(result['completed'])
        self.assertFalse((self.root / 'images/current.png').exists())

    def test_partial_failure_preserves_completed_images(self):
        class Partial(Backend):
            def png(self, request):
                if request['file'] == 'bad.png':
                    raise RuntimeError('Native capture failed')
                return PNG
        self.config['images'].append({'file': 'bad.png'})
        result = capture.capture_images(self.config, backend_factory=Partial)
        self.assertFalse(result['completed'])
        self.assertEqual([x['status'] for x in result['images']], ['captured', 'failed'])
        self.assertTrue((self.root / 'images/current.png').exists())
        self.assertFalse((self.root / 'images/bad.png').exists())

    def test_bad_image_does_not_create_file(self):
        class Empty(Backend):
            def png(self, request):
                return b''
        result = capture.capture_images(self.config, backend_factory=Empty)
        self.assertFalse(result['completed'])
        self.assertFalse((self.root / 'images/current.png').exists())

    def test_cancellation_preserves_completed_images(self):
        self.config['images'].append({'file': 'second.png'})
        checks = iter([False, True])
        result = capture.capture_images(self.config, backend_factory=Backend, cancelled=lambda: next(checks))
        self.assertFalse(result['completed'])
        self.assertEqual([x['status'] for x in result['images']], ['captured', 'cancelled'])
        self.assertFalse((self.root / 'images/second.png').exists())

    def test_cli_input_failure_returns_nonzero_and_json(self):
        config = self.root / 'bad.json'
        config.write_text('{}', encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--config', str(config)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)['completed'])


if __name__ == '__main__':
    unittest.main()
