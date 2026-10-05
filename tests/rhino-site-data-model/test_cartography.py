import sys
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH

sys.path.insert(0, str(SCRIPTS_PATH))
from site_model.cartography import LayerStyle, style_for, transport_style, TRANSPORT_STANDARD


def record(kind, **properties):
    return {'feature_type': kind, 'properties': properties}


class CartographyTests(unittest.TestCase):
    def test_transport_mapping_and_unknown_subtypes(self):
        cases = [
            ('road', 'PRIMARY', 'primary'),
            ('road', 'footway', 'path'),
            ('road', 'cycleway', 'cycleway'),
            ('rail', 'standard_gauge', 'rail'),
            ('rail', 'tram', 'other_rail'),
            ('water', '', 'water_route'),
            ('rail', 'future_class', 'unknown'),
            ('future_subtype', 'primary', 'unknown'),
            ('', '', 'unknown'),
        ]
        for subtype, class_name, expected in cases:
            with self.subTest(subtype=subtype, class_name=class_name):
                self.assertEqual(transport_style({'subtype': subtype, 'class': class_name})['id'], expected)

    def test_transport_styles_have_unique_mappings_and_supported_patterns(self):
        styles = json.loads(TRANSPORT_STANDARD.read_text(encoding='utf-8'))['styles']
        self.assertEqual(len({s['id'] for s in styles}), len(styles))
        mappings = []
        for style in styles:
            self.assertEqual(style['line_pattern'], 'solid')
            self.assertGreater(style['width_mm'], 0)
            self.assertRegex(style['color'], r'^#[0-9A-F]{6}$')
            mappings.extend((style['subtype'], c) for c in (style['classes'] or [None]))
        self.assertEqual(len(set(mappings)), len(mappings))

    def test_rhino_reads_shared_tokens_without_a_second_palette(self):
        # A style edit must reach both consumers without another code change.
        tokens = {'id': 'primary', 'subtype': 'road', 'classes': ['primary'],
                  'color': '#123456', 'width_mm': .42, 'draw_order': 81234,
                  'line_pattern': 'solid'}
        with patch('site_model.cartography._transport_styles', return_value=[tokens]):
            properties = {'subtype': 'road', 'class': 'primary'}
            svg = transport_style(properties)
            rhino = style_for(record('segment', **properties))
        self.assertEqual(svg['color'], '#123456')
        self.assertEqual(rhino.color, (18, 52, 86, 255))
        self.assertEqual(rhino.plot_weight_mm, svg['width_mm'])
        self.assertEqual(rhino.display_order, svg['draw_order'])

    def test_reference_styles_and_fallback(self):
        self.assertEqual(style_for(record('land_cover', subtype='forest')).color[:3], (117,169,116))
        self.assertEqual(style_for(record('land_use', subtype='residential')).plot_weight_mm, .13)
        self.assertEqual(style_for(record('building', **{'class':'residential'})).color[:3], (201,188,111))
        self.assertEqual(style_for(record('unknown')).color[:3], (135,135,132))
        with self.assertRaises(Exception):
            style_for(record('land')).color = (0,0,0,255)

    def test_semantic_draw_order(self):
        kinds = [
            record('bathymetry', depth=10), record('land'), record('land_cover', subtype='grass'),
            record('land_use', subtype='residential'), record('water'), record('building'),
            record('segment', subtype='road', **{'class':'service'}), record('infrastructure'),
        ]
        orders = [style_for(item).display_order for item in kinds]
        self.assertEqual(orders, sorted(orders))
        self.assertGreater(style_for(record('segment', subtype='road', **{'class':'primary'})).display_order,
                           style_for(record('segment', subtype='road', **{'class':'secondary'})).display_order)
        self.assertGreater(style_for(record('bathymetry', depth=100)).display_order,
                           style_for(record('bathymetry', depth=10)).display_order)
        self.assertGreater(style_for(boundary='site').display_order, style_for(record('infrastructure')).display_order)
        self.assertGreater(style_for(role='run_annotation').display_order, style_for(boundary='site').display_order)


if __name__ == '__main__':
    unittest.main()
