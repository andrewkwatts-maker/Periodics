#====== Playtow/PeriodicTable2/tests/test_property_encoding.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

"""
Unit tests for property encoding system (colors, sizes, visual mappings)
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unified_table import UnifiedTable
from PySide6.QtGui import QColor


class TestPropertyEncoding(unittest.TestCase):
    """Test property encoding and visual mapping"""

    def setUp(self):
        """Set up test fixtures"""
        self.table = UnifiedTable()
        # Create a sample element for testing
        self.sample_element = {
            'symbol': 'C',
            'z': 6,
            'ie': 11.26,
            'electronegativity': 2.55,
            'atomic_radius': 70,
            'melting_point': 3823,
            'boiling_point': 4098,
            'density': 2.267,
            'electron_affinity': 1.262,
            'valence_electrons': 4,
            'block': 'p',
            'block_color': QColor(100, 150, 200),
            'wavelength_nm': 247.9
        }

    def test_fill_property_independence(self):
        """Test that fill property doesn't affect other properties"""
        self.table.fill_property = "wavelength"
        self.table.border_color_property = "ionization"

        fill_color = self.table.get_property_color(self.sample_element, self.table.fill_property, "fill")
        border_color = self.table.get_property_color(self.sample_element, self.table.border_color_property, "border")

        # Colors should be different
        self.assertNotEqual(fill_color.rgba(), border_color.rgba())

    def test_border_color_property(self):
        """Test that border color property works independently"""
        # Set different properties
        self.table.fill_property = "block"
        self.table.border_color_property = "electron_affinity"

        border_color = self.table.get_property_color(
            self.sample_element,
            self.table.border_color_property,
            "border"
        )

        # Should return a valid color
        self.assertIsInstance(border_color, QColor)
        self.assertTrue(border_color.isValid())

    def test_fade_system_per_property(self):
        """Test that fade values are independent per property"""
        self.table.fill_fade = 0.5
        self.table.border_color_fade = 0.0
        self.table.ring_color_fade = 1.0

        # Get colors with different fade values
        fill_color = self.table.get_property_color(self.sample_element, "wavelength", "fill")
        border_color = self.table.get_property_color(self.sample_element, "wavelength", "border")
        ring_color = self.table.get_property_color(self.sample_element, "wavelength", "ring")

        # Faded color should have lower alpha
        self.assertLess(fill_color.alpha(), 255)
        # No fade should have higher alpha
        self.assertEqual(border_color.alpha(), 255)
        # Full fade should have lowest alpha
        self.assertEqual(ring_color.alpha(), 0)

    def test_property_color_none(self):
        """Test that 'none' property returns default color"""
        color = self.table.get_property_color(self.sample_element, "none", "fill")

        self.assertEqual(color, QColor(100, 100, 150, 255))

    def test_atomic_number_color(self):
        """Test atomic number color mapping"""
        color = self.table.get_property_color(self.sample_element, "atomic_number", "fill")

        # Should return HSV-based color
        self.assertIsInstance(color, QColor)
        self.assertTrue(color.isValid())

    def test_border_size_property(self):
        """Test border size calculation"""
        self.table.border_size_property = "valence"

        size = self.table.get_border_width(self.sample_element)

        # Should return a valid size
        self.assertGreater(size, 0)
        self.assertIsInstance(size, (int, float))

    def test_ring_size_property(self):
        """Test inner ring size calculation"""
        self.table.ring_size_property = "atomic_number"

        size = self.table.get_inner_ring_size(self.sample_element)

        # Should return fraction between 0 and 1
        self.assertGreaterEqual(size, 0.0)
        self.assertLessEqual(size, 1.0)

    def test_glow_properties(self):
        """Test glow radius and intensity calculations"""
        self.table.glow_radius_property = "radius"
        self.table.glow_intensity_property = "density"

        radius = self.table.get_glow_radius_percent(self.sample_element)
        intensity = self.table.get_glow_intensity(self.sample_element)

        # Should return valid percentages
        self.assertGreaterEqual(radius, 0.0)
        self.assertLessEqual(radius, 1.0)
        self.assertGreaterEqual(intensity, 0.0)
        self.assertLessEqual(intensity, 1.0)

    def test_property_color_consistency(self):
        """Test that same property returns same color"""
        color1 = self.table.get_property_color(self.sample_element, "block", "fill")
        color2 = self.table.get_property_color(self.sample_element, "block", "fill")

        self.assertEqual(color1.rgba(), color2.rgba())


if __name__ == '__main__':
    unittest.main()
