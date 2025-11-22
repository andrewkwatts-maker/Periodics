"""
Molecule Info Panel
Displays detailed information about selected molecules.
Supports inline editing mode for Add/Edit operations.
"""

import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QFrame,
                                QStackedWidget)
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QRadialGradient, QPainterPath

from core.molecule_enums import (MolecularGeometry, BondType, MoleculePolarity,
                                  MoleculeCategory, MoleculeState, get_element_color)
from data.data_manager import DataCategory


class MoleculeStructureWidget(QFrame):
    """Widget to display molecular structure diagram"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.molecule = None
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            QFrame {
                background: rgba(25, 25, 45, 200);
                border: 2px solid #4fc3f7;
                border-radius: 12px;
            }
        """)

    def set_molecule(self, mol):
        """Set molecule to display"""
        self.molecule = mol
        self.update()

    def paintEvent(self, event):
        """Paint the molecular structure"""
        super().paintEvent(event)

        if not self.molecule:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(self.width(), self.height()) * 0.35

        composition = self.molecule.get('Composition', [])
        bonds = self.molecule.get('Bonds', [])
        geometry = self.molecule.get('geometry', 'Linear')

        if not composition:
            painter.setPen(QPen(QColor(150, 150, 150)))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No structure data")
            painter.end()
            return

        # Calculate atom positions
        atom_positions = self._calculate_atom_positions(composition, geometry, cx, cy, radius)

        # Draw bonds
        self._draw_bonds(painter, atom_positions, bonds, cx, cy)

        # Draw atoms
        for atom in atom_positions:
            self._draw_atom(painter, atom)

        # Draw geometry label
        painter.setPen(QPen(QColor(100, 150, 200)))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(10, self.height() - 10, f"Geometry: {geometry}")

        painter.end()

    def _calculate_atom_positions(self, composition, geometry, cx, cy, radius):
        """Calculate atom positions based on geometry"""
        positions = []
        total_atoms = sum(c.get('Count', 1) for c in composition)

        if total_atoms == 0:
            return positions

        # Different arrangements based on geometry
        if geometry == 'Linear':
            # Horizontal line
            step = radius * 1.5 / max(total_atoms - 1, 1) if total_atoms > 1 else 0
            start_x = cx - (total_atoms - 1) * step / 2
            atom_idx = 0
            for comp in composition:
                element = comp.get('Element', '?')
                count = comp.get('Count', 1)
                for i in range(count):
                    positions.append({
                        'element': element,
                        'x': start_x + atom_idx * step,
                        'y': cy,
                        'radius': self._get_atom_radius(element)
                    })
                    atom_idx += 1

        elif geometry == 'Bent':
            # V-shape
            angle = math.radians(104.5)  # Typical bent angle
            central_atom = composition[0] if composition else {'Element': '?'}
            positions.append({
                'element': central_atom.get('Element', '?'),
                'x': cx,
                'y': cy,
                'radius': self._get_atom_radius(central_atom.get('Element', '?'))
            })
            # Add peripheral atoms
            if len(composition) > 1:
                peripheral = composition[1]
                count = peripheral.get('Count', 1)
                for i in range(count):
                    a = -math.pi/2 + (i - (count-1)/2) * angle / max(count-1, 1)
                    positions.append({
                        'element': peripheral.get('Element', '?'),
                        'x': cx + radius * 0.7 * math.cos(a),
                        'y': cy + radius * 0.7 * math.sin(a),
                        'radius': self._get_atom_radius(peripheral.get('Element', '?'))
                    })

        elif geometry in ['Tetrahedral', 'Trigonal Pyramidal']:
            # 3D projection
            central = composition[0] if composition else {'Element': '?'}
            positions.append({
                'element': central.get('Element', '?'),
                'x': cx,
                'y': cy,
                'radius': self._get_atom_radius(central.get('Element', '?'))
            })
            # Peripheral atoms in a circle
            atom_idx = 0
            for comp in composition[1:] if len(composition) > 1 else []:
                element = comp.get('Element', '?')
                count = comp.get('Count', 1)
                base_angle = 2 * math.pi / max(sum(c.get('Count', 1) for c in composition[1:]), 1)
                for i in range(count):
                    a = atom_idx * base_angle - math.pi/2
                    positions.append({
                        'element': element,
                        'x': cx + radius * 0.65 * math.cos(a),
                        'y': cy + radius * 0.65 * math.sin(a),
                        'radius': self._get_atom_radius(element)
                    })
                    atom_idx += 1

        elif geometry == 'Trigonal Planar':
            # Triangle arrangement
            central = composition[0] if composition else {'Element': '?'}
            positions.append({
                'element': central.get('Element', '?'),
                'x': cx,
                'y': cy,
                'radius': self._get_atom_radius(central.get('Element', '?'))
            })
            for i, comp in enumerate(composition[1:] if len(composition) > 1 else []):
                count = comp.get('Count', 1)
                for j in range(count):
                    a = (i * count + j) * 2 * math.pi / 3 - math.pi/2
                    positions.append({
                        'element': comp.get('Element', '?'),
                        'x': cx + radius * 0.6 * math.cos(a),
                        'y': cy + radius * 0.6 * math.sin(a),
                        'radius': self._get_atom_radius(comp.get('Element', '?'))
                    })

        elif geometry == 'Planar Hexagonal':
            # Hexagon (like benzene)
            atom_idx = 0
            for comp in composition:
                element = comp.get('Element', '?')
                count = comp.get('Count', 1)
                for i in range(count):
                    a = atom_idx * math.pi / 3 - math.pi/2
                    r = radius * 0.6 if element == 'C' else radius * 0.85
                    positions.append({
                        'element': element,
                        'x': cx + r * math.cos(a),
                        'y': cy + r * math.sin(a),
                        'radius': self._get_atom_radius(element)
                    })
                    atom_idx += 1

        else:
            # Default circular arrangement
            atom_idx = 0
            for comp in composition:
                element = comp.get('Element', '?')
                count = comp.get('Count', 1)
                for i in range(count):
                    if total_atoms == 1:
                        positions.append({
                            'element': element,
                            'x': cx,
                            'y': cy,
                            'radius': self._get_atom_radius(element)
                        })
                    else:
                        a = atom_idx * 2 * math.pi / total_atoms - math.pi/2
                        positions.append({
                            'element': element,
                            'x': cx + radius * 0.6 * math.cos(a),
                            'y': cy + radius * 0.6 * math.sin(a),
                            'radius': self._get_atom_radius(element)
                        })
                    atom_idx += 1

        return positions

    def _get_atom_radius(self, element):
        """Get display radius for an element"""
        radii = {
            'H': 15, 'C': 22, 'N': 20, 'O': 18, 'S': 24, 'P': 23,
            'Cl': 22, 'Br': 25, 'F': 16, 'I': 28, 'Na': 26, 'K': 28
        }
        return radii.get(element, 20)

    def _draw_bonds(self, painter, positions, bonds, cx, cy):
        """Draw bonds between atoms"""
        if len(positions) < 2:
            return

        # Draw lines from center to all peripheral atoms (simplified)
        if len(positions) > 1:
            center = positions[0]
            for atom in positions[1:]:
                # Determine bond type (simplified)
                painter.setPen(QPen(QColor(180, 180, 180), 3))
                painter.drawLine(
                    QPointF(center['x'], center['y']),
                    QPointF(atom['x'], atom['y'])
                )

    def _draw_atom(self, painter, atom):
        """Draw a single atom"""
        x, y = atom['x'], atom['y']
        r = atom['radius']
        element = atom['element']

        color = QColor(get_element_color(element))

        # Glow effect
        glow = QRadialGradient(x, y, r * 1.8)
        glow_color = QColor(color)
        glow_color.setAlpha(60)
        glow.setColorAt(0, glow_color)
        glow_color.setAlpha(0)
        glow.setColorAt(1, glow_color)
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(x, y), r * 1.8, r * 1.8)

        # Atom sphere
        gradient = QRadialGradient(x - r * 0.3, y - r * 0.3, r * 1.5)
        gradient.setColorAt(0, color.lighter(140))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(130))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawEllipse(QPointF(x, y), r, r)

        # Element symbol
        text_color = QColor(0, 0, 0) if color.lightness() > 128 else QColor(255, 255, 255)
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Arial", int(r * 0.7), QFont.Weight.Bold))
        painter.drawText(QPointF(x - r * 0.4, y + r * 0.3), element)


class MoleculeInfoPanel(QWidget):
    """Panel displaying detailed molecule information with inline editing support"""

    # Signals for data management
    data_saved = Signal(dict)
    edit_cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.molecule = None
        self._editor = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget for switching between display and edit modes
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Display mode widget
        self.display_widget = QWidget()
        display_layout = QVBoxLayout(self.display_widget)
        display_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Molecule Analysis")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #4fc3f7;")
        display_layout.addWidget(title)

        # Structure widget
        self.structure_widget = MoleculeStructureWidget()
        display_layout.addWidget(self.structure_widget)

        # Info text
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background: rgba(25, 25, 45, 200);
                color: white;
                border: 2px solid #4fc3f7;
                border-radius: 12px;
                padding: 15px;
                font-size: 13px;
            }
        """)
        display_layout.addWidget(self.info_text)

        self.stack.addWidget(self.display_widget)
        self.show_default()

    def start_add(self, template_data=None):
        """Start add mode with inline editor"""
        from ui.inline_editor import InlineDataEditor

        if self._editor is None:
            self._editor = InlineDataEditor()
            self._editor.data_saved.connect(self._on_editor_saved)
            self._editor.edit_cancelled.connect(self._on_editor_cancelled)
            self.stack.addWidget(self._editor)

        self._editor.start_add(DataCategory.MOLECULES, template_data)
        self.stack.setCurrentWidget(self._editor)

    def start_edit(self, data):
        """Start edit mode with inline editor"""
        from ui.inline_editor import InlineDataEditor

        if self._editor is None:
            self._editor = InlineDataEditor()
            self._editor.data_saved.connect(self._on_editor_saved)
            self._editor.edit_cancelled.connect(self._on_editor_cancelled)
            self.stack.addWidget(self._editor)

        self._editor.start_edit(DataCategory.MOLECULES, data)
        self.stack.setCurrentWidget(self._editor)

    def _on_editor_saved(self, data):
        """Handle save from editor"""
        self.stack.setCurrentWidget(self.display_widget)
        self.data_saved.emit(data)

    def _on_editor_cancelled(self):
        """Handle cancel from editor"""
        self.stack.setCurrentWidget(self.display_widget)
        self.edit_cancelled.emit()

    def show_default(self):
        """Show default message"""
        self.structure_widget.set_molecule(None)
        self.info_text.setHtml("""
            <h3 style='color: #4fc3f7;'>Click any molecule to view:</h3>
            <ul>
                <li><b>Molecular Structure</b></li>
                <li><b>Bond Information</b></li>
                <li><b>Physical Properties</b></li>
                <li><b>Chemical Properties</b></li>
                <li><b>Applications</b></li>
            </ul>
            <p style='background: rgba(100,200,255,0.15); padding: 10px; border-radius: 5px;'>
            <b>Tip:</b> Use the control panel to filter molecules by category,
            polarity, or physical state.
            </p>
        """)

    def update_molecule(self, mol):
        """Update panel with molecule data"""
        if not mol:
            self.show_default()
            return

        self.molecule = mol
        self.structure_widget.set_molecule(mol)

        # Build HTML content
        name = mol.get('Name', 'Unknown')
        formula = mol.get('Formula', '')
        mass = mol.get('mass', 0)
        geometry = mol.get('geometry', 'Unknown')
        bond_type = mol.get('bond_type', 'Unknown')
        polarity = mol.get('polarity', 'Unknown')
        state = mol.get('state', 'Unknown')
        melting = mol.get('melting_point', 0)
        boiling = mol.get('boiling_point', 0)
        density = mol.get('density', 0)
        dipole = mol.get('dipole_moment', 0)
        bond_angle = mol.get('bond_angle', 0)
        applications = mol.get('Applications', [])
        iupac = mol.get('IUPAC_Name', '')
        category = mol.get('category', 'Unknown')

        # Get colors
        geometry_color = MolecularGeometry.get_color(geometry)
        polarity_color = MoleculePolarity.get_color(polarity)
        category_color = MoleculeCategory.get_color(category)
        state_color = MoleculeState.get_color(state)

        # Build composition text
        composition = mol.get('Composition', [])
        comp_text = ", ".join([f"{c['Element']}: {c['Count']}" for c in composition])

        # Build bonds text
        bonds = mol.get('Bonds', [])
        unique_bonds = set()
        for b in bonds:
            unique_bonds.add(f"{b['From']}-{b['To']} ({b['Type']})")
        bonds_text = ", ".join(list(unique_bonds)[:3])
        if len(unique_bonds) > 3:
            bonds_text += f" +{len(unique_bonds)-3} more"

        apps_html = ""
        if applications:
            apps_html = "<h3 style='color: #4fc3f7; margin-top: 15px;'>Applications:</h3><ul>"
            for app in applications[:5]:
                apps_html += f"<li>{app}</li>"
            apps_html += "</ul>"

        html = f"""
            <h2 style='color: #4fc3f7;'>{name}</h2>
            <div style='font-size: 18px; font-weight: bold; color: white;'>{formula}</div>
            <div style='color: #aaa; font-size: 10px;'>IUPAC: {iupac}</div>
            <hr style='border-color: #4fc3f7;'>

            <h3 style='color: #4fc3f7;'>Molecular Properties:</h3>
            <table style='width: 100%; color: white; line-height: 1.8;'>
                <tr>
                    <td><b>Molecular Mass:</b></td>
                    <td><b style='color: #00ff88;'>{mass:.2f}</b> g/mol</td>
                </tr>
                <tr>
                    <td><b>Geometry:</b></td>
                    <td><span style='background: {geometry_color}; padding: 2px 8px;
                        border-radius: 4px; color: black;'>{geometry}</span></td>
                </tr>
                <tr>
                    <td><b>Bond Type:</b></td>
                    <td><b style='color: #ff8800;'>{bond_type}</b></td>
                </tr>
                <tr>
                    <td><b>Bond Angle:</b></td>
                    <td>{bond_angle:.1f}°</td>
                </tr>
                <tr>
                    <td><b>Polarity:</b></td>
                    <td><span style='background: {polarity_color}; padding: 2px 8px;
                        border-radius: 4px;'>{polarity}</span></td>
                </tr>
                <tr>
                    <td><b>Dipole Moment:</b></td>
                    <td>{dipole:.2f} D</td>
                </tr>
            </table>

            <h3 style='color: #4fc3f7; margin-top: 15px;'>Physical Properties:</h3>
            <table style='width: 100%; color: white; line-height: 1.8;'>
                <tr>
                    <td><b>State at STP:</b></td>
                    <td><span style='background: {state_color}; padding: 2px 8px;
                        border-radius: 4px;'>{state}</span></td>
                </tr>
                <tr>
                    <td><b>Melting Point:</b></td>
                    <td><b style='color: #00ff88;'>{melting:.1f} K</b> ({melting - 273.15:.1f}°C)</td>
                </tr>
                <tr>
                    <td><b>Boiling Point:</b></td>
                    <td><b style='color: #00ff88;'>{boiling:.1f} K</b> ({boiling - 273.15:.1f}°C)</td>
                </tr>
                <tr>
                    <td><b>Density:</b></td>
                    <td>{density:.4f} g/cm³</td>
                </tr>
            </table>

            <h3 style='color: #4fc3f7; margin-top: 15px;'>Composition:</h3>
            <div style='color: white;'>{comp_text}</div>

            <h3 style='color: #4fc3f7; margin-top: 10px;'>Bonds:</h3>
            <div style='color: white; font-size: 11px;'>{bonds_text}</div>

            {apps_html}

            <div style='background: rgba(100,200,255,0.15); padding: 12px; border-radius: 8px;
                border-left: 4px solid {category_color}; margin-top: 15px;'>
                <p style='margin: 0;'><b>Category:</b> {category}</p>
            </div>
        """
        self.info_text.setHtml(html)
