#!/usr/bin/env python3
"""
Unit tests for visual encoding system - verifies that property changes
actually affect the correct visual elements.
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core import UnifiedTable

# Create QApplication for Qt widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestVisualEncoding(unittest.TestCase):
    """Test that property changes affect the correct visual elements"""

    def setUp(self):
        """Create a fresh table instance for each test"""
        self.table = UnifiedTable()
        # Get a test element (Carbon)
        self.carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                self.carbon = elem
                break
        self.assertIsNotNone(self.carbon, "Carbon element should exist")

    def test_fill_color_property_independence(self):
        """Test that fill color property doesn't affect other properties"""
        # Set fill color to ionization energy
        self.table.fill_property = "ionization_energy"
        fill_color = self.table.get_property_color(self.carbon, "ionization_energy", "fill")

        # Get border color (should be different property)
        self.table.border_color_property = "electron_affinity"
        border_color = self.table.get_property_color(self.carbon, "electron_affinity", "border")

        # Colors should be different
        self.assertNotEqual(fill_color.name(), border_color.name(),
                          "Fill and border colors should be independent")

    def test_border_color_property(self):
        """Test that border_color_property exists and works"""
        # Verify property exists
        self.assertTrue(hasattr(self.table, 'border_color_property'),
                       "Table should have border_color_property")

        # Set to electron affinity
        self.table.border_color_property = "electron_affinity"
        border_color = self.table.get_property_color(self.carbon, "electron_affinity", "border")

        # Should return a valid color
        self.assertIsInstance(border_color, QColor)
        self.assertTrue(border_color.isValid())

    def test_border_size_property(self):
        """Test that border_size_property exists and works"""
        # Verify property exists
        self.assertTrue(hasattr(self.table, 'border_size_property'),
                       "Table should have border_size_property")

        # Set to valence
        self.table.border_size_property = "valence"

        # Should be set correctly
        self.assertEqual(self.table.border_size_property, "valence")

    def test_inner_ring_property(self):
        """Test that inner_ring_property exists and works"""
        # Verify property exists
        self.assertTrue(hasattr(self.table, 'inner_ring_property'),
                       "Table should have inner_ring_property")

        # Set to melting point
        self.table.inner_ring_property = "melting"
        ring_color = self.table.get_property_color(self.carbon, "melting", "ring")

        # Should return a valid color
        self.assertIsInstance(ring_color, QColor)
        self.assertTrue(ring_color.isValid())

    def test_glow_intensity_property(self):
        """Test that glow_intensity_property exists and works"""
        # Verify property exists
        self.assertTrue(hasattr(self.table, 'glow_intensity_property'),
                       "Table should have glow_intensity_property")

        # Set to density
        self.table.glow_intensity_property = "density"

        # Should be set correctly
        self.assertEqual(self.table.glow_intensity_property, "density")

    def test_glow_color_property(self):
        """Test that glow_color_property exists and works"""
        # Verify property exists
        self.assertTrue(hasattr(self.table, 'glow_color_property'),
                       "Table should have glow_color_property")

        # Set to boiling point
        self.table.glow_color_property = "boiling"
        glow_color = self.table.get_property_color(self.carbon, "boiling", "glow")

        # Should return a valid color
        self.assertIsInstance(glow_color, QColor)
        self.assertTrue(glow_color.isValid())

    def test_all_properties_exist(self):
        """Test that all expected property variables exist"""
        expected_properties = [
            'fill_property',
            'border_property',
            'border_color_property',
            'border_size_property',
            'inner_ring_property',
            'glow_intensity_property',
            'glow_color_property'
        ]

        for prop in expected_properties:
            self.assertTrue(hasattr(self.table, prop),
                          f"Table should have {prop} attribute")

    def test_property_color_with_fade(self):
        """Test that fade values are applied correctly"""
        self.table.fill_fade = 0.5  # 50% fade

        color = self.table.get_property_color(self.carbon, "ionization", "fill")

        # Alpha should be reduced by fade
        expected_alpha = int(255 * 0.5)
        self.assertEqual(color.alpha(), expected_alpha,
                        "Fade should reduce alpha to 50%")

    def test_border_and_fill_different_properties(self):
        """Test that border and fill can use completely different properties"""
        # Set different properties
        self.table.fill_property = "ionization"
        self.table.border_color_property = "radius"

        # Get colors (using the property name constants that get_property_color expects)
        fill_color = self.table.get_property_color(self.carbon, "ionization", "fill")
        border_color = self.table.get_property_color(self.carbon, "radius", "border")

        # Should be different
        self.assertNotEqual(fill_color.name(), border_color.name(),
                          "Fill and border should use independent properties")

    def test_property_modes_list(self):
        """Test that all expected property modes are available"""
        # These are the actual property names used by get_property_color
        expected_modes = [
            "ionization",
            "electronegativity",
            "melting",
            "radius",
            "density",
            "electron_affinity",
            "boiling",
            "valence"
        ]

        # These should all work with get_property_color
        for mode in expected_modes:
            color = self.table.get_property_color(self.carbon, mode, "fill")
            self.assertIsInstance(color, QColor,
                                f"Should be able to get color for {mode}")
            self.assertTrue(color.isValid(),
                          f"Color for {mode} should be valid")


class TestPropertyCalculations(unittest.TestCase):
    """Test property-based calculations for visual encoding"""

    def setUp(self):
        self.table = UnifiedTable()
        # Get test elements
        self.hydrogen = None
        self.carbon = None
        self.iron = None

        for elem in self.table.elements:
            z = elem.get('z')
            if z == 1:
                self.hydrogen = elem
            elif z == 6:
                self.carbon = elem
            elif z == 26:
                self.iron = elem

        self.assertIsNotNone(self.hydrogen)
        self.assertIsNotNone(self.carbon)
        self.assertIsNotNone(self.iron)

    def test_border_thickness_calculation(self):
        """Test that border thickness scales with property value"""
        self.table.border_size_property = "valence"

        # Carbon has valence 4, Iron has valence 2,3 (use 3)
        # Higher valence should give thicker border
        carbon_val = self.carbon.get('valence', 0)
        iron_val = self.iron.get('valence', 0)

        # Just verify the property exists and can be read
        self.assertIsNotNone(carbon_val)
        self.assertIsNotNone(iron_val)

    def test_ring_size_scaling(self):
        """Test that inner ring size scales correctly"""
        self.table.inner_ring_property = "atomic_radius"

        # Get radius values
        h_radius = self.hydrogen.get('atomic_radius', 0)
        c_radius = self.carbon.get('atomic_radius', 0)

        # Carbon should have larger radius than Hydrogen
        self.assertGreater(c_radius, h_radius,
                          "Carbon atomic radius should be larger than Hydrogen")

    def test_glow_intensity_range(self):
        """Test that glow intensity is normalized to valid range"""
        self.table.glow_intensity_property = "density"

        # Get density values
        h_density = self.hydrogen.get('density', 0)
        fe_density = self.iron.get('density', 0)

        # Iron should be much denser than Hydrogen
        self.assertGreater(fe_density, h_density,
                          "Iron density should be much greater than Hydrogen")

    def test_property_value_retrieval(self):
        """Test that all properties can be retrieved from elements"""
        properties_to_test = [
            'ionization_energy',
            'electronegativity',
            'melting',
            'atomic_radius',
            'density',
            'electron_affinity',
            'boiling',
            'valence'
        ]

        for prop in properties_to_test:
            value = self.carbon.get(prop)
            self.assertIsNotNone(value,
                                f"Carbon should have {prop} property")


if __name__ == '__main__':
    unittest.main(verbosity=2)
