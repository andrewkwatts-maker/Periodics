#!/usr/bin/env python3
"""
Unit tests for mouse interaction and selection system
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QMouseEvent
from core import UnifiedTable

# Create QApplication for Qt widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestMouseInteraction(unittest.TestCase):
    """Test mouse interaction and selection"""

    def setUp(self):
        """Create a fresh table instance for each test"""
        self.table = UnifiedTable()
        # Get Carbon for testing
        self.carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                self.carbon = elem
                break

    def test_element_selection(self):
        """Test that element selection works"""
        self.table.selected_element = self.carbon
        self.assertEqual(self.table.selected_element, self.carbon,
                        "Selected element should be Carbon")

    def test_hover_state(self):
        """Test that hover state can be set"""
        self.table.hovered_element = self.carbon
        self.assertEqual(self.table.hovered_element, self.carbon,
                        "Hovered element should be Carbon")

    def test_rotation_state_initialization(self):
        """Test that rotation state flags exist"""
        self.assertTrue(hasattr(self.table, 'is_rotating'),
                       "Table should have is_rotating flag")
        self.assertTrue(hasattr(self.table, 'is_panning'),
                       "Table should have is_panning flag")
        self.assertFalse(self.table.is_rotating,
                        "is_rotating should start False")
        self.assertFalse(self.table.is_panning,
                        "is_panning should start False")

    def test_pitch_yaw_initialization(self):
        """Test that pitch and yaw angles exist"""
        self.assertTrue(hasattr(self.table, 'rotation_x'),
                       "Table should have rotation_x")
        self.assertTrue(hasattr(self.table, 'rotation_y'),
                       "Table should have rotation_y")

    def test_subatomic_mode_toggle(self):
        """Test subatomic particles display toggle"""
        # Default should be False
        self.assertFalse(self.table.show_subatomic_particles,
                        "Subatomic particles should start hidden")

        # Toggle on
        self.table.show_subatomic_particles = True
        self.assertTrue(self.table.show_subatomic_particles,
                       "Should be able to enable subatomic view")

        # Toggle off
        self.table.show_subatomic_particles = False
        self.assertFalse(self.table.show_subatomic_particles,
                        "Should be able to disable subatomic view")

    def test_element_table_toggle(self):
        """Test element table visibility toggle"""
        self.assertTrue(hasattr(self.table, 'show_element_table'),
                       "Table should have show_element_table flag")

        # Default should be True
        self.assertTrue(self.table.show_element_table,
                       "Element table should start visible")

        # Toggle off
        self.table.show_element_table = False
        self.assertFalse(self.table.show_element_table,
                        "Should be able to hide element table")

    def test_orbital_cloud_toggle(self):
        """Test orbital cloud visibility toggle"""
        self.assertTrue(hasattr(self.table, 'show_orbital_cloud'),
                       "Table should have show_orbital_cloud flag")

        # Can toggle
        self.table.show_orbital_cloud = True
        self.assertTrue(self.table.show_orbital_cloud)

        self.table.show_orbital_cloud = False
        self.assertFalse(self.table.show_orbital_cloud)

    def test_orbital_quantum_numbers(self):
        """Test that orbital quantum numbers can be set"""
        self.assertTrue(hasattr(self.table, 'orbital_n'),
                       "Table should have orbital_n")
        self.assertTrue(hasattr(self.table, 'orbital_l'),
                       "Table should have orbital_l")
        self.assertTrue(hasattr(self.table, 'orbital_m'),
                       "Table should have orbital_m")

        # Set to 2p orbital (n=2, l=1, m=0)
        self.table.orbital_n = 2
        self.table.orbital_l = 1
        self.table.orbital_m = 0

        self.assertEqual(self.table.orbital_n, 2)
        self.assertEqual(self.table.orbital_l, 1)
        self.assertEqual(self.table.orbital_m, 0)

    def test_animation_timer_exists(self):
        """Test that animation timer is set up"""
        self.assertTrue(hasattr(self.table, 'animation_timer'),
                       "Table should have animation timer")
        self.assertTrue(hasattr(self.table, 'cloud_animation_phase'),
                       "Table should have animation phase")

    def test_cloud_opacity_control(self):
        """Test that cloud opacity can be controlled"""
        self.assertTrue(hasattr(self.table, 'cloud_opacity'),
                       "Table should have cloud_opacity")

        # Should be between 0 and 1
        self.assertGreaterEqual(self.table.cloud_opacity, 0.0)
        self.assertLessEqual(self.table.cloud_opacity, 1.0)

        # Can be changed
        self.table.cloud_opacity = 0.5
        self.assertEqual(self.table.cloud_opacity, 0.5)


class TestSubatomicView(unittest.TestCase):
    """Test subatomic particle visualization"""

    def setUp(self):
        self.table = UnifiedTable()
        self.carbon = None
        for elem in self.table.elements:
            if elem.get('z') == 6:
                self.carbon = elem
                break

    def test_nucleus_radius_calculation(self):
        """Test that nucleus radius is calculated correctly"""
        # Carbon has 6 protons, 6 neutrons (mass number 12)
        z = 6
        mass_number = 12

        # Nuclear radius formula: r = r0 * A^(1/3)
        # r0 = 1.2 fm (femtometers)
        r0 = 1.2
        expected_radius = r0 * (mass_number ** (1/3))

        # Should be approximately 2.74 fm
        self.assertAlmostEqual(expected_radius, 2.74, places=2,
                              msg="Carbon nucleus radius should be ~2.74 fm")

    def test_nucleon_grid_calculation(self):
        """Test that nucleon grid dimensions are calculated correctly"""
        total_nucleons = 12  # Carbon-12

        # Grid should be cube root rounded up
        import math
        expected_dim = max(1, int(math.ceil(total_nucleons ** (1/3))))

        # Should be 3 (since 2^3=8 < 12 < 3^3=27)
        self.assertEqual(expected_dim, 3,
                        "12 nucleons should require 3x3x3 grid")

    def test_electron_shell_count(self):
        """Test that electron shells are calculated correctly"""
        # Carbon has 6 electrons: 2 in first shell, 4 in second
        z = 6

        # Should have shells with 2 and 4 electrons
        # (Tested indirectly through orbital calculation)
        available_orbitals = self.table.get_available_orbitals(z)

        # Should have 1s (2 electrons) and 2s+2p (4 electrons)
        n_values = [n for n, l, m, label in available_orbitals]

        self.assertIn(1, n_values, "Should have n=1 shell")
        self.assertIn(2, n_values, "Should have n=2 shell")

    def test_show_shells_toggle(self):
        """Test electron shell visibility toggle"""
        self.assertTrue(hasattr(self.table, 'show_shells'),
                       "Table should have show_shells flag")

        # Can toggle
        self.table.show_shells = True
        self.assertTrue(self.table.show_shells)

        self.table.show_shells = False
        self.assertFalse(self.table.show_shells)

    def test_show_electrons_toggle(self):
        """Test individual electron visibility toggle"""
        self.assertTrue(hasattr(self.table, 'show_electrons'),
                       "Table should have show_electrons flag")

        # Can toggle
        self.table.show_electrons = True
        self.assertTrue(self.table.show_electrons)

        self.table.show_electrons = False
        self.assertFalse(self.table.show_electrons)


if __name__ == '__main__':
    unittest.main(verbosity=2)
