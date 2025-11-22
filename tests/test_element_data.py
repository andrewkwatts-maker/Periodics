#!/usr/bin/env python3
"""
Unit tests for element data loading and properties
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from core import UnifiedTable

# Create QApplication for Qt widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestElementData(unittest.TestCase):
    """Test element data loading and access"""

    def setUp(self):
        self.table = UnifiedTable()

    def test_elements_loaded(self):
        """Test that elements are loaded"""
        self.assertIsNotNone(self.table.elements,
                           "Elements list should exist")
        self.assertGreater(len(self.table.elements), 0,
                          "Should have loaded elements")

    def test_element_count(self):
        """Test that we have 118 elements"""
        # Should have all elements up to Oganesson
        self.assertEqual(len(self.table.elements), 118,
                        "Should have 118 elements")

    def test_hydrogen_properties(self):
        """Test Hydrogen (Z=1) has expected properties"""
        hydrogen = None
        for elem in self.table.elements:
            if elem.get('z') == 1:
                hydrogen = elem
                break

        self.assertIsNotNone(hydrogen, "Hydrogen should exist")
        self.assertEqual(hydrogen.get('symbol'), 'H')
        self.assertEqual(hydrogen.get('name'), 'Hydrogen')
        self.assertEqual(hydrogen.get('block'), 's')
        self.assertEqual(hydrogen.get('period'), 1)
        self.assertEqual(hydrogen.get('group'), 1)

    def test_carbon_properties(self):
        """Test Carbon (Z=6) has expected properties"""
        carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                carbon = elem
                break

        self.assertIsNotNone(carbon, "Carbon should exist")
        self.assertEqual(carbon.get('symbol'), 'C')
        self.assertEqual(carbon.get('name'), 'Carbon')
        self.assertEqual(carbon.get('block'), 'p')
        self.assertEqual(carbon.get('period'), 2)
        self.assertEqual(carbon.get('group'), 14)

    def test_iron_properties(self):
        """Test Iron (Z=26) has expected properties"""
        iron = None
        for elem in self.table.elements:
            if elem.get('z') == 26:
                iron = elem
                break

        self.assertIsNotNone(iron, "Iron should exist")
        self.assertEqual(iron.get('symbol'), 'Fe')
        self.assertEqual(iron.get('name'), 'Iron')
        self.assertEqual(iron.get('block'), 'd')
        self.assertEqual(iron.get('period'), 4)
        self.assertEqual(iron.get('group'), 8)

    def test_all_elements_have_required_properties(self):
        """Test that all elements have required properties"""
        required_props = ['z', 'symbol', 'name', 'block', 'period', 'group']

        for elem in self.table.elements:
            for prop in required_props:
                self.assertIn(prop, elem,
                            f"Element {elem.get('symbol', '?')} missing {prop}")
                self.assertIsNotNone(elem.get(prop),
                                   f"Element {elem.get('symbol', '?')} has None {prop}")

    def test_all_elements_have_numeric_properties(self):
        """Test that all elements have numeric properties for visualization"""
        numeric_props = [
            'ionization_energy',
            'atomic_radius',
            'density',
            'melting',
            'boiling'
        ]

        for elem in self.table.elements:
            symbol = elem.get('symbol', '?')
            for prop in numeric_props:
                value = elem.get(prop)
                self.assertIsNotNone(value,
                                   f"{symbol} should have {prop}")
                # Should be a number
                self.assertIsInstance(value, (int, float),
                                    f"{symbol} {prop} should be numeric")

    def test_element_blocks(self):
        """Test that elements are in correct blocks"""
        # Count elements by block
        block_counts = {'s': 0, 'p': 0, 'd': 0, 'f': 0}

        for elem in self.table.elements:
            block = elem.get('block')
            self.assertIn(block, block_counts,
                         f"Element {elem.get('symbol')} has invalid block {block}")
            block_counts[block] += 1

        # Should have elements in all blocks
        self.assertGreater(block_counts['s'], 0, "Should have s-block elements")
        self.assertGreater(block_counts['p'], 0, "Should have p-block elements")
        self.assertGreater(block_counts['d'], 0, "Should have d-block elements")
        self.assertGreater(block_counts['f'], 0, "Should have f-block elements")

    def test_periods_and_groups(self):
        """Test that period and group values are reasonable"""
        for elem in self.table.elements:
            period = elem.get('period')
            group = elem.get('group')

            # Period should be 1-7
            self.assertGreaterEqual(period, 1,
                                  f"{elem.get('symbol')} period too low")
            self.assertLessEqual(period, 7,
                                f"{elem.get('symbol')} period too high")

            # Group should be 1-18 (or None for f-block)
            if group is not None:
                self.assertGreaterEqual(group, 1,
                                      f"{elem.get('symbol')} group too low")
                self.assertLessEqual(group, 18,
                                    f"{elem.get('symbol')} group too high")

    def test_ionization_energy_range(self):
        """Test that ionization energies are in expected range"""
        for elem in self.table.elements:
            ie = elem.get('ionization_energy')
            # Should be between ~3.5 eV (Cs) and ~25 eV (He)
            self.assertGreater(ie, 0,
                             f"{elem.get('symbol')} IE should be positive")
            self.assertLess(ie, 30,
                          f"{elem.get('symbol')} IE seems unreasonably high")

    def test_atomic_radius_range(self):
        """Test that atomic radii are in expected range"""
        for elem in self.table.elements:
            radius = elem.get('atomic_radius')
            # Should be between ~30 pm and ~350 pm
            self.assertGreater(radius, 0,
                             f"{elem.get('symbol')} radius should be positive")
            self.assertLess(radius, 400,
                          f"{elem.get('symbol')} radius seems unreasonably high")


class TestIsotopeData(unittest.TestCase):
    """Test isotope data for elements"""

    def setUp(self):
        self.table = UnifiedTable()

    def test_carbon_isotopes(self):
        """Test Carbon isotope data"""
        carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                carbon = elem
                break

        isotopes = carbon.get('isotopes', [])
        self.assertIsNotNone(isotopes, "Carbon should have isotopes")
        self.assertGreater(len(isotopes), 0, "Carbon should have at least one isotope")

        # Carbon-12 should be most common
        c12 = None
        for iso in isotopes:
            if iso.get('mass_number') == 12:
                c12 = iso
                break

        self.assertIsNotNone(c12, "Carbon-12 should exist")
        self.assertGreater(c12.get('abundance', 0), 90,
                          "Carbon-12 should be most abundant")

    def test_hydrogen_isotopes(self):
        """Test Hydrogen isotope data"""
        hydrogen = None
        for elem in self.table.elements:
            if elem.get('z') == 1:
                hydrogen = elem
                break

        isotopes = hydrogen.get('isotopes', [])
        self.assertGreater(len(isotopes), 0,
                          "Hydrogen should have isotopes")

        # Should have protium (H-1), deuterium (H-2), tritium (H-3)
        mass_numbers = [iso.get('mass_number') for iso in isotopes]
        self.assertIn(1, mass_numbers, "Should have H-1")

    def test_all_elements_have_isotopes(self):
        """Test that all elements have isotope data"""
        for elem in self.table.elements:
            isotopes = elem.get('isotopes', [])
            self.assertIsNotNone(isotopes,
                                f"{elem.get('symbol')} should have isotopes list")
            self.assertGreater(len(isotopes), 0,
                             f"{elem.get('symbol')} should have at least one isotope")


class TestColorCalculations(unittest.TestCase):
    """Test color calculation functions"""

    def setUp(self):
        self.table = UnifiedTable()
        self.carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                self.carbon = elem
                break

    def test_get_block_color(self):
        """Test block color calculation"""
        from utils.calculations import get_block_color
        from PySide6.QtGui import QColor

        s_color = get_block_color('s')
        p_color = get_block_color('p')
        d_color = get_block_color('d')
        f_color = get_block_color('f')

        # All should be valid colors
        self.assertIsInstance(s_color, QColor)
        self.assertIsInstance(p_color, QColor)
        self.assertIsInstance(d_color, QColor)
        self.assertIsInstance(f_color, QColor)

        # All should be different
        self.assertNotEqual(s_color.name(), p_color.name())
        self.assertNotEqual(p_color.name(), d_color.name())
        self.assertNotEqual(d_color.name(), f_color.name())

    def test_get_property_color_returns_valid_color(self):
        """Test that get_property_color returns valid QColor"""
        from PySide6.QtGui import QColor

        color = self.table.get_property_color(self.carbon, "ionization_energy", "fill")

        self.assertIsInstance(color, QColor)
        self.assertTrue(color.isValid())

    def test_different_properties_give_different_colors(self):
        """Test that different properties produce different colors"""
        ie_color = self.table.get_property_color(self.carbon, "ionization_energy", "fill")
        radius_color = self.table.get_property_color(self.carbon, "atomic_radius", "fill")

        # Should be different (Carbon's IE and radius are very different)
        self.assertNotEqual(ie_color.name(), radius_color.name())


if __name__ == '__main__':
    unittest.main(verbosity=2)
