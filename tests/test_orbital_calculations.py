#====== Playtow/PeriodicTable2/tests/test_orbital_calculations.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

"""
Unit tests for orbital calculations and electron configuration
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unified_table import UnifiedTable


class TestOrbitalCalculations(unittest.TestCase):
    """Test orbital calculation functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.table = UnifiedTable()

    def test_hydrogen_orbitals(self):
        """Test orbital calculation for Hydrogen (Z=1)"""
        orbitals = self.table.get_available_orbitals(1)

        # Hydrogen has 1 electron in 1s
        self.assertEqual(len(orbitals), 1)
        self.assertEqual(orbitals[0], (1, 0, 0, '1s'))

    def test_helium_orbitals(self):
        """Test orbital calculation for Helium (Z=2)"""
        orbitals = self.table.get_available_orbitals(2)

        # Helium has 2 electrons in 1s
        self.assertEqual(len(orbitals), 1)
        self.assertEqual(orbitals[0], (1, 0, 0, '1s'))

    def test_carbon_orbitals(self):
        """Test orbital calculation for Carbon (Z=6)"""
        orbitals = self.table.get_available_orbitals(6)

        # Carbon: 1s² 2s² 2p²
        # Should have 1s, 2s, 2px, 2py, 2pz
        self.assertEqual(len(orbitals), 5)

        # Check first three orbitals
        self.assertEqual(orbitals[0][:3], (1, 0, 0))  # 1s
        self.assertEqual(orbitals[1][:3], (2, 0, 0))  # 2s
        self.assertEqual(orbitals[2][:3], (2, 1, -1))  # 2p

    def test_neon_orbitals(self):
        """Test orbital calculation for Neon (Z=10)"""
        orbitals = self.table.get_available_orbitals(10)

        # Neon: 1s² 2s² 2p⁶
        # Should have 1s, 2s, 2px, 2py, 2pz (5 total)
        self.assertEqual(len(orbitals), 5)

    def test_scandium_orbitals(self):
        """Test orbital calculation for Scandium (Z=21) - first 3d element"""
        orbitals = self.table.get_available_orbitals(21)

        # Should include 3d orbitals
        has_3d = any(n == 3 and l == 2 for n, l, m, label in orbitals)
        self.assertTrue(has_3d, "Scandium should have 3d orbitals")

    def test_orbital_filling_order(self):
        """Test that orbitals follow Aufbau principle"""
        # Potassium (Z=19) should fill 4s before 3d
        orbitals = self.table.get_available_orbitals(19)

        # Should have 4s orbital
        has_4s = any(n == 4 and l == 0 for n, l, m, label in orbitals)
        self.assertTrue(has_4s, "Potassium should have 4s orbital")

        # Should NOT have 3d orbital (not filled yet)
        has_3d = any(n == 3 and l == 2 for n, l, m, label in orbitals)
        self.assertFalse(has_3d, "Potassium should not have 3d orbitals")

    def test_orbital_label_format(self):
        """Test orbital label formatting"""
        orbitals = self.table.get_available_orbitals(6)  # Carbon

        # Check that labels are properly formatted
        labels = [label for n, l, m, label in orbitals]
        self.assertIn('1s', labels)
        self.assertIn('2s', labels)
        # Should have p orbital labels with x, y, z notation
        p_orbitals = [label for label in labels if '2p' in label]
        self.assertEqual(len(p_orbitals), 3)

    def test_maximum_element(self):
        """Test orbital calculation for heaviest natural element"""
        orbitals = self.table.get_available_orbitals(118)  # Oganesson

        # Should have many orbitals
        self.assertGreater(len(orbitals), 30)

        # Should have 7s orbital
        has_7s = any(n == 7 and l == 0 for n, l, m, label in orbitals)
        self.assertTrue(has_7s, "Element 118 should have 7s orbital")


if __name__ == '__main__':
    unittest.main()
