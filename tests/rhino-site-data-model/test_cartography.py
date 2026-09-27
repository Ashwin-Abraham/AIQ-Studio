import sys
import unittest
from pathlib import Path
from _site_model_paths import SCRIPTS_PATH

sys.path.insert(0, str(SCRIPTS_PATH))
from site_model.cartography import LayerStyle, style_for


def record(kind, **properties):
    return {'feature_type': kind, 'properties': properties}


class CartographyTests(unittest.TestCase):
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
