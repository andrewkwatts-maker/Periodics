"""
Molecule Unified Table Widget
Main visualization widget for displaying molecules with various layouts.
"""

import json
import math
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QRadialGradient,
                           QLinearGradient, QPainterPath, QGuiApplication)

from data.molecule_loader import MoleculeDataLoader
from core.molecule_enums import (MoleculeLayoutMode, MolecularGeometry, BondType,
                                  MoleculePolarity, MoleculeCategory, MoleculeState,
                                  get_element_color)
from layouts.molecule_grid_layout import MoleculeGridLayout
from layouts.molecule_mass_layout import MoleculeMassLayout
from layouts.molecule_polarity_layout import MoleculePolarityLayout
from layouts.molecule_bond_layout import MoleculeBondLayout
from layouts.molecule_geometry_layout import MoleculeGeometryLayout
from layouts.molecule_phase_diagram_layout import MoleculePhaseDiagramLayout
from layouts.molecule_dipole_layout import MoleculeDipoleLayout
from layouts.molecule_density_layout import MoleculeDensityLayout
from layouts.molecule_bond_complexity_layout import MoleculeBondComplexityLayout


class MoleculeUnifiedTable(QWidget):
    """Main widget for visualizing molecules"""

    # Signals
    molecule_selected = Signal(dict)
    molecule_hovered = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        # Data
        self.loader = MoleculeDataLoader()
        self.base_molecules = self.loader.load_all_molecules()
        self.positioned_molecules = []

        # State
        self.layout_mode = MoleculeLayoutMode.GRID
        self.hovered_molecule = None
        self.selected_molecule = None

        # Filters
        self.category_filter = None  # None means show all
        self.polarity_filter = None
        self.state_filter = None

        # Visual settings
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.scroll_offset_y = 0

        # Layout renderers
        self.layouts = {
            MoleculeLayoutMode.GRID: MoleculeGridLayout(self.width(), self.height()),
            MoleculeLayoutMode.MASS_ORDER: MoleculeMassLayout(self.width(), self.height()),
            MoleculeLayoutMode.POLARITY: MoleculePolarityLayout(self.width(), self.height()),
            MoleculeLayoutMode.BOND_TYPE: MoleculeBondLayout(self.width(), self.height()),
            MoleculeLayoutMode.GEOMETRY: MoleculeGeometryLayout(self.width(), self.height()),
            MoleculeLayoutMode.PHASE_DIAGRAM: MoleculePhaseDiagramLayout(self.width(), self.height()),
            MoleculeLayoutMode.DIPOLE: MoleculeDipoleLayout(self.width(), self.height()),
            MoleculeLayoutMode.DENSITY: MoleculeDensityLayout(self.width(), self.height()),
            MoleculeLayoutMode.BOND_COMPLEXITY: MoleculeBondComplexityLayout(self.width(), self.height()),
        }

        # Initialize layout
        self._update_layout()

    def set_layout_mode(self, mode):
        """Set the layout mode"""
        if isinstance(mode, str):
            mode = MoleculeLayoutMode.from_string(mode)
        self.layout_mode = mode
        self._update_layout()
        self.update()

    def set_category_filter(self, category):
        """Set category filter (Organic, Inorganic, Ionic, or None for all)"""
        self.category_filter = category
        self._update_layout()
        self.update()

    def set_polarity_filter(self, polarity):
        """Set polarity filter"""
        self.polarity_filter = polarity
        self._update_layout()
        self.update()

    def set_state_filter(self, state):
        """Set state filter"""
        self.state_filter = state
        self._update_layout()
        self.update()

    def _get_filtered_molecules(self):
        """Get molecules after applying filters"""
        molecules = self.base_molecules.copy()

        if self.category_filter:
            molecules = [m for m in molecules if m.get('category') == self.category_filter]

        if self.polarity_filter:
            molecules = [m for m in molecules if m.get('polarity') == self.polarity_filter]

        if self.state_filter:
            molecules = [m for m in molecules if m.get('state') == self.state_filter]

        return molecules

    def _update_layout(self):
        """Recalculate positions for all molecules"""
        molecules = self._get_filtered_molecules()
        layout = self.layouts.get(self.layout_mode)

        if layout:
            layout.update_dimensions(self.width(), self.height())
            self.positioned_molecules = layout.calculate_layout(molecules)

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        for layout in self.layouts.values():
            layout.update_dimensions(self.width(), self.height())
        self._update_layout()

    def paintEvent(self, event):
        """Paint the molecule visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        self._draw_background(painter)

        # Apply transformations
        painter.translate(self.pan_x, self.pan_y - self.scroll_offset_y)
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw group headers if applicable
        if self.layout_mode in [MoleculeLayoutMode.POLARITY, MoleculeLayoutMode.BOND_TYPE,
                                MoleculeLayoutMode.GEOMETRY, MoleculeLayoutMode.PHASE_DIAGRAM,
                                MoleculeLayoutMode.DIPOLE, MoleculeLayoutMode.DENSITY,
                                MoleculeLayoutMode.BOND_COMPLEXITY]:
            self._draw_group_headers(painter)

        # Draw molecules
        for mol in self.positioned_molecules:
            self._draw_molecule_card(painter, mol)

        painter.end()

    def _draw_background(self, painter):
        """Draw the dark gradient background"""
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 10, 26))
        gradient.setColorAt(1, QColor(26, 26, 46))
        painter.fillRect(self.rect(), QBrush(gradient))

    def _draw_group_headers(self, painter):
        """Draw group section headers"""
        layout = self.layouts.get(self.layout_mode)
        if not hasattr(layout, 'get_group_headers'):
            return

        headers = layout.get_group_headers(self.positioned_molecules)

        for header in headers:
            y = header.get('y', 0)
            name = header.get('name', '')
            color = header.get('color', '#FFFFFF')

            # Draw header background
            header_rect = QRectF(20, y, self.width() - 40, 35)
            painter.setPen(Qt.PenStyle.NoPen)

            header_color = QColor(color)
            header_color.setAlpha(40)
            painter.setBrush(QBrush(header_color))
            painter.drawRoundedRect(header_rect, 5, 5)

            # Draw header text
            painter.setPen(QPen(QColor(color)))
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.drawText(header_rect.adjusted(15, 0, 0, 0),
                           Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                           name)

            # Draw underline
            painter.setPen(QPen(QColor(color), 2))
            painter.drawLine(int(header_rect.left() + 10), int(header_rect.bottom()),
                           int(header_rect.right() - 10), int(header_rect.bottom()))

    def _draw_molecule_card(self, painter, mol):
        """Draw a single molecule card"""
        x = mol.get('x', 0)
        y = mol.get('y', 0)
        width = mol.get('width', 150)
        height = mol.get('height', 170)

        is_hovered = mol == self.hovered_molecule
        is_selected = mol == self.selected_molecule

        # Card background
        card_rect = QRectF(x, y, width, height)

        # Gradient background
        gradient = QLinearGradient(x, y, x, y + height)
        if is_selected:
            gradient.setColorAt(0, QColor(80, 80, 120, 220))
            gradient.setColorAt(1, QColor(60, 60, 100, 220))
        elif is_hovered:
            gradient.setColorAt(0, QColor(70, 70, 100, 200))
            gradient.setColorAt(1, QColor(50, 50, 80, 200))
        else:
            gradient.setColorAt(0, QColor(60, 60, 80, 180))
            gradient.setColorAt(1, QColor(40, 40, 60, 180))

        painter.setBrush(QBrush(gradient))

        # Border
        border_color = QColor(mol.get('color', '#4FC3F7'))
        if is_selected:
            border_color.setAlpha(255)
            painter.setPen(QPen(border_color, 3))
        elif is_hovered:
            border_color.setAlpha(200)
            painter.setPen(QPen(border_color, 2))
        else:
            border_color.setAlpha(150)
            painter.setPen(QPen(border_color, 1))

        painter.drawRoundedRect(card_rect, 10, 10)

        # Draw molecule structure visualization
        self._draw_molecule_structure(painter, mol, x + width/2, y + 50, min(width, height) * 0.25)

        # Draw text info
        self._draw_molecule_info(painter, mol, x, y, width, height)

    def _draw_molecule_structure(self, painter, mol, cx, cy, radius):
        """Draw a simplified molecular structure visualization"""
        composition = mol.get('Composition', [])
        bonds = mol.get('Bonds', [])

        if not composition:
            return

        # Calculate atom positions based on geometry
        geometry = mol.get('geometry', 'Linear')
        atom_positions = self._calculate_atom_positions(composition, geometry, cx, cy, radius)

        # Draw bonds first
        painter.setPen(QPen(QColor(200, 200, 200, 150), 2))
        for bond in bonds:
            bond_type = bond.get('Type', 'Single')
            # For simplicity, draw lines between center and atoms
            if bond_type == 'Double':
                painter.setPen(QPen(QColor(100, 150, 255, 180), 3))
            elif bond_type == 'Triple':
                painter.setPen(QPen(QColor(150, 100, 255, 180), 4))
            else:
                painter.setPen(QPen(QColor(200, 200, 200, 150), 2))

        # Draw atoms
        for atom_info in atom_positions:
            ax, ay = atom_info['x'], atom_info['y']
            element = atom_info['element']
            atom_radius = atom_info['radius']

            # Get element color
            color = QColor(get_element_color(element))

            # Draw atom glow
            glow_gradient = QRadialGradient(ax, ay, atom_radius * 1.5)
            glow_color = QColor(color)
            glow_color.setAlpha(80)
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(ax, ay), atom_radius * 1.5, atom_radius * 1.5)

            # Draw atom
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))
            painter.drawEllipse(QPointF(ax, ay), atom_radius, atom_radius)

            # Draw element symbol
            painter.setPen(QPen(QColor(0, 0, 0) if color.lightness() > 128 else QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", int(atom_radius * 0.8), QFont.Weight.Bold))
            text_rect = QRectF(ax - atom_radius, ay - atom_radius, atom_radius * 2, atom_radius * 2)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, element)

    def _calculate_atom_positions(self, composition, geometry, cx, cy, radius):
        """Calculate positions for atoms based on molecular geometry"""
        positions = []
        total_atoms = sum(c.get('Count', 1) for c in composition)

        if total_atoms == 0:
            return positions

        # Calculate position for each atom type
        angle_step = 2 * math.pi / max(total_atoms, 1)
        current_angle = -math.pi / 2  # Start from top

        atom_index = 0
        for comp in composition:
            element = comp.get('Element', '?')
            count = comp.get('Count', 1)

            # Size based on element (rough approximation)
            base_radius = 12
            if element in ['C', 'N', 'O', 'S']:
                base_radius = 14
            elif element in ['H']:
                base_radius = 8
            elif element in ['Cl', 'Br', 'I']:
                base_radius = 16

            for i in range(count):
                if total_atoms == 1:
                    # Single atom at center
                    ax, ay = cx, cy
                elif total_atoms == 2:
                    # Linear arrangement
                    offset = radius * 0.6 * (1 if atom_index == 0 else -1)
                    ax, ay = cx + offset, cy
                else:
                    # Circular arrangement
                    ax = cx + radius * 0.8 * math.cos(current_angle)
                    ay = cy + radius * 0.8 * math.sin(current_angle)
                    current_angle += angle_step

                positions.append({
                    'element': element,
                    'x': ax,
                    'y': ay,
                    'radius': base_radius
                })
                atom_index += 1

        return positions

    def _draw_molecule_info(self, painter, mol, x, y, width, height):
        """Draw molecule text information"""
        # Formula
        formula = mol.get('formula', '')
        painter.setPen(QPen(QColor(79, 195, 247)))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        formula_rect = QRectF(x, y + 90, width, 20)
        painter.drawText(formula_rect, Qt.AlignmentFlag.AlignCenter, formula)

        # Name
        name = mol.get('name', '')
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 9))
        name_rect = QRectF(x, y + 110, width, 18)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, name)

        # Properties
        painter.setPen(QPen(QColor(200, 200, 200, 180)))
        painter.setFont(QFont("Arial", 8))

        # Mass
        mass = mol.get('mass', 0)
        mass_rect = QRectF(x + 5, y + 130, width - 10, 15)
        painter.drawText(mass_rect, Qt.AlignmentFlag.AlignCenter, f"{mass:.1f} amu")

        # State indicator
        state = mol.get('state', 'Unknown')
        state_color = MoleculeState.get_color(state)
        painter.setPen(QPen(QColor(state_color), 2))
        painter.setBrush(QBrush(QColor(state_color)))
        state_x = x + width - 15
        state_y = y + 150
        painter.drawEllipse(QPointF(state_x, state_y), 5, 5)

        # Polarity indicator
        polarity = mol.get('polarity', 'Unknown')
        polarity_color = MoleculePolarity.get_color(polarity)
        painter.setPen(QPen(QColor(polarity_color), 2))
        painter.setBrush(QBrush(QColor(polarity_color)))
        polarity_x = x + 15
        painter.drawEllipse(QPointF(polarity_x, state_y), 5, 5)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        # Transform mouse position
        x = (event.position().x() - self.pan_x) / self.zoom_level
        y = (event.position().y() - self.pan_y + self.scroll_offset_y) / self.zoom_level

        layout = self.layouts.get(self.layout_mode)
        if layout:
            mol = layout.get_molecule_at_position(x, y, self.positioned_molecules)

            if mol != self.hovered_molecule:
                self.hovered_molecule = mol
                if mol:
                    self.molecule_hovered.emit(mol)
                self.update()

    def mousePressEvent(self, event):
        """Handle mouse click for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.hovered_molecule:
                self.selected_molecule = self.hovered_molecule
                self.molecule_selected.emit(self.selected_molecule)
                # Copy molecule data to clipboard
                clipboard_text = json.dumps(self.selected_molecule, indent=2, default=str)
                QGuiApplication.clipboard().setText(clipboard_text)
                self.update()

    def wheelEvent(self, event):
        """Handle scroll wheel for zooming/scrolling"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            factor = 1.1 if delta > 0 else 0.9
            self.zoom_level = max(0.5, min(2.0, self.zoom_level * factor))
        else:
            # Scroll
            delta = event.angleDelta().y()
            self.scroll_offset_y = max(0, self.scroll_offset_y - delta / 2)

        self.update()

    def reset_view(self):
        """Reset zoom and scroll to default"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.scroll_offset_y = 0
        self.update()

    def get_content_height(self):
        """Get the total content height for scrolling"""
        layout = self.layouts.get(self.layout_mode)
        if layout and hasattr(layout, 'get_content_height'):
            return layout.get_content_height(self.positioned_molecules)
        return self.height()
