"""
Alloy Info Panel
Displays detailed information about selected alloys including:
- Microstructure visualization
- Properties bar chart
- Component pie chart
- Phase diagram view
"""

import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame, QTabWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QRadialGradient, QPainterPath, QLinearGradient

from core.alloy_enums import (AlloyCategory, CrystalStructure, ComponentRole, get_element_color)

# Import crystalline math for microstructure visualization
try:
    from utils.crystalline_math import VoronoiTessellation, SimplexNoise, MicrostructureRenderer
    HAS_CRYSTALLINE_MATH = True
except ImportError:
    HAS_CRYSTALLINE_MATH = False


class MicrostructureWidget(QFrame):
    """Widget to display alloy microstructure"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.alloy = None
        self.setMinimumHeight(180)
        self.setStyleSheet("""
            QFrame {
                background: rgba(25, 25, 45, 200);
                border: 2px solid #B08264;
                border-radius: 12px;
            }
        """)

    def set_alloy(self, alloy):
        """Set alloy to display"""
        self.alloy = alloy
        self.update()

    def paintEvent(self, event):
        """Paint the microstructure visualization"""
        super().paintEvent(event)

        if not self.alloy:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Voronoi grain structure
        self._draw_grain_structure(painter)

        # Draw structure legend
        self._draw_legend(painter)

        painter.end()

    def _draw_grain_structure(self, painter):
        """Draw Voronoi-like grain structure with IPF coloring"""
        margin = 15
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin - 25  # Leave space for legend

        # Get microstructure parameters
        grain_seed_density = self.alloy.get('grain_seed_density', 400)
        grain_size = self.alloy.get('grain_size', 50)

        # Calculate number of grains based on area
        area_mm2 = (width * height) / 10000  # Convert to mm^2 approx
        num_grains = max(10, min(50, int(area_mm2 * grain_seed_density / 10000)))

        # Generate deterministic grain centers based on alloy name
        seed = sum(ord(c) for c in self.alloy.get('name', 'alloy'))

        grain_centers = []
        for i in range(num_grains):
            # Pseudo-random positions
            gx = margin + ((seed * (i + 1) * 17 + i * 31) % int(width))
            gy = margin + ((seed * (i + 1) * 23 + i * 43) % int(height))

            # Random-ish orientation for IPF coloring
            phi1 = (seed * (i + 3) * 7) % 360
            phi = (seed * (i + 5) * 11) % 90
            phi2 = (seed * (i + 7) * 13) % 90

            grain_centers.append({
                'x': gx, 'y': gy,
                'orientation': (phi1, phi, phi2),
                'size': grain_size * (0.8 + 0.4 * ((seed + i) % 10) / 10)
            })

        # Draw grain regions
        for i, grain in enumerate(grain_centers):
            # IPF-like coloring based on orientation
            phi1, phi, phi2 = grain['orientation']
            r = int((phi1 / 360) * 200 + 55)
            g = int((phi / 90) * 200 + 55)
            b = int((phi2 / 90) * 200 + 55)
            grain_color = QColor(r, g, b, 180)

            # Draw grain as polygon-like region
            size = grain['size'] * 0.3

            gradient = QRadialGradient(grain['x'], grain['y'], size)
            gradient.setColorAt(0, grain_color.lighter(115))
            gradient.setColorAt(0.7, grain_color)
            gradient.setColorAt(1, grain_color.darker(110))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw as slightly irregular polygon
            path = QPainterPath()
            for j in range(6):
                angle = j * math.pi / 3 + (seed + i * j) % 10 * 0.1
                r_var = size * (0.9 + 0.2 * ((seed + i + j) % 10) / 10)
                px = grain['x'] + r_var * math.cos(angle)
                py = grain['y'] + r_var * math.sin(angle)
                if j == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            painter.drawPath(path)

        # Draw grain boundaries
        painter.setPen(QPen(QColor(30, 30, 40, 200), 1))
        for grain in grain_centers:
            size = grain['size'] * 0.3
            path = QPainterPath()
            for j in range(6):
                angle = j * math.pi / 3 + (seed + grain_centers.index(grain) * j) % 10 * 0.1
                r_var = size * (0.9 + 0.2 * ((seed + grain_centers.index(grain) + j) % 10) / 10)
                px = grain['x'] + r_var * math.cos(angle)
                py = grain['y'] + r_var * math.sin(angle)
                if j == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            painter.drawPath(path)

    def _draw_legend(self, painter):
        """Draw structure legend at bottom"""
        structure = self.alloy.get('crystal_structure', 'Unknown')
        structure_color = QColor(CrystalStructure.get_color(structure))

        # Background
        legend_rect = QRectF(10, self.height() - 30, self.width() - 20, 22)
        painter.setBrush(QBrush(QColor(30, 30, 50, 200)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(legend_rect, 5, 5)

        # Structure indicator
        painter.setBrush(QBrush(structure_color))
        painter.drawEllipse(QPointF(25, self.height() - 19), 6, 6)

        # Text
        painter.setPen(QPen(QColor(200, 200, 220)))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(int(legend_rect.left() + 25), int(self.height() - 14),
                        f"{structure} - IPF Colored Grains")


class PropertiesBarWidget(QFrame):
    """Widget to display properties as bar chart"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.alloy = None
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame {
                background: rgba(25, 25, 45, 200);
                border: 2px solid #B08264;
                border-radius: 12px;
            }
        """)

    def set_alloy(self, alloy):
        """Set alloy to display"""
        self.alloy = alloy
        self.update()

    def paintEvent(self, event):
        """Paint the properties bar chart"""
        super().paintEvent(event)

        if not self.alloy:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Properties to display with their ranges for normalization
        properties = [
            ('Tensile Strength', self.alloy.get('tensile_strength', 0), 2000, '#4CAF50'),
            ('Yield Strength', self.alloy.get('yield_strength', 0), 1500, '#2196F3'),
            ('Hardness (HB)', self.alloy.get('hardness', 0), 600, '#FF9800'),
            ('Elongation (%)', self.alloy.get('elongation', 0), 60, '#9C27B0'),
        ]

        margin = 15
        bar_height = 18
        spacing = 8
        label_width = 110
        bar_start = margin + label_width
        bar_width = self.width() - bar_start - margin - 50

        y = margin

        # Title
        painter.setPen(QPen(QColor(200, 200, 220)))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(margin, y + 12, "Mechanical Properties")
        y += 25

        painter.setFont(QFont("Arial", 9))

        for name, value, max_val, color in properties:
            # Label
            painter.setPen(QPen(QColor(180, 180, 200)))
            painter.drawText(margin, int(y + bar_height - 4), name)

            # Bar background
            bar_rect = QRectF(bar_start, y, bar_width, bar_height)
            painter.setBrush(QBrush(QColor(50, 50, 70)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(bar_rect, 3, 3)

            # Value bar
            fill_width = min(bar_width, (value / max_val) * bar_width) if max_val > 0 else 0
            fill_rect = QRectF(bar_start, y, fill_width, bar_height)

            gradient = QLinearGradient(bar_start, y, bar_start + fill_width, y)
            bar_color = QColor(color)
            gradient.setColorAt(0, bar_color.darker(120))
            gradient.setColorAt(1, bar_color)

            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(fill_rect, 3, 3)

            # Value text
            painter.setPen(QPen(QColor(255, 255, 255)))
            unit = 'MPa' if 'Strength' in name else '%' if 'Elongation' in name else ''
            painter.drawText(int(bar_start + bar_width + 5), int(y + bar_height - 4),
                           f"{value:.0f}{unit}")

            y += bar_height + spacing

        painter.end()


class CompositionPieWidget(QFrame):
    """Widget to display composition as pie chart"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.alloy = None
        self.setMinimumHeight(180)
        self.setStyleSheet("""
            QFrame {
                background: rgba(25, 25, 45, 200);
                border: 2px solid #B08264;
                border-radius: 12px;
            }
        """)

    def set_alloy(self, alloy):
        """Set alloy to display"""
        self.alloy = alloy
        self.update()

    def paintEvent(self, event):
        """Paint the composition pie chart"""
        super().paintEvent(event)

        if not self.alloy:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Title
        painter.setPen(QPen(QColor(200, 200, 220)))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(15, 22, "Composition")

        components = self.alloy.get('Components', [])
        if not components:
            painter.setFont(QFont("Arial", 9))
            painter.drawText(15, 60, "No composition data")
            painter.end()
            return

        # Calculate average percentages and sort by amount
        comp_data = []
        for comp in components:
            elem = comp.get('Element', '?')
            min_pct = comp.get('MinPercent', 0)
            max_pct = comp.get('MaxPercent', 0)
            avg_pct = (min_pct + max_pct) / 2
            if avg_pct > 0.5:  # Only show significant components
                comp_data.append((elem, avg_pct))

        comp_data.sort(key=lambda x: -x[1])
        total = sum(pct for _, pct in comp_data)

        # Draw pie chart
        cx = 90
        cy = 105
        radius = 55

        start_angle = 90 * 16  # Start from top

        for elem, pct in comp_data:
            span_angle = int((pct / total) * 360 * 16) if total > 0 else 0

            color = QColor(get_element_color(elem))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))

            pie_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            painter.drawPie(pie_rect, start_angle, span_angle)

            start_angle += span_angle

        # Draw center circle
        painter.setBrush(QBrush(QColor(30, 30, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius * 0.4, radius * 0.4)

        # Draw legend
        legend_x = 160
        legend_y = 40
        painter.setFont(QFont("Arial", 8))

        for i, (elem, pct) in enumerate(comp_data[:6]):  # Max 6 items in legend
            color = QColor(get_element_color(elem))

            # Color box
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x, legend_y + i * 18, 12, 12)

            # Text
            painter.setPen(QPen(QColor(200, 200, 220)))
            painter.drawText(legend_x + 18, legend_y + i * 18 + 10, f"{elem}: {pct:.1f}%")

        painter.end()


class AlloyInfoPanel(QWidget):
    """Panel displaying detailed alloy information"""

    def __init__(self):
        super().__init__()
        self.alloy = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Alloy Analysis")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #B08264;")
        layout.addWidget(title)

        # Create tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #B08264;
                border-radius: 8px;
                background: rgba(25, 25, 45, 150);
            }
            QTabBar::tab {
                background: rgba(40, 40, 60, 200);
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #B08264;
            }
            QTabBar::tab:hover {
                background: rgba(176, 130, 100, 150);
            }
        """)

        # Overview tab
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        overview_layout.setSpacing(10)

        self.microstructure_widget = MicrostructureWidget()
        overview_layout.addWidget(self.microstructure_widget)

        self.properties_widget = PropertiesBarWidget()
        overview_layout.addWidget(self.properties_widget)

        self.tabs.addTab(overview_widget, "Overview")

        # Composition tab
        comp_widget = QWidget()
        comp_layout = QVBoxLayout(comp_widget)

        self.composition_widget = CompositionPieWidget()
        comp_layout.addWidget(self.composition_widget)

        self.tabs.addTab(comp_widget, "Composition")

        # Details tab
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background: rgba(25, 25, 45, 200);
                color: white;
                border: 2px solid #B08264;
                border-radius: 12px;
                padding: 15px;
                font-size: 12px;
            }
        """)
        self.tabs.addTab(self.info_text, "Details")

        layout.addWidget(self.tabs)

        self.show_default()

    def show_default(self):
        """Show default message"""
        self.microstructure_widget.set_alloy(None)
        self.properties_widget.set_alloy(None)
        self.composition_widget.set_alloy(None)

        self.info_text.setHtml("""
            <h3 style='color: #B08264;'>Click any alloy to view:</h3>
            <ul>
                <li><b>Microstructure Visualization</b></li>
                <li><b>Mechanical Properties</b></li>
                <li><b>Elemental Composition</b></li>
                <li><b>Lattice Properties</b></li>
                <li><b>Applications</b></li>
            </ul>
            <p style='background: rgba(176,130,100,0.15); padding: 10px; border-radius: 5px;'>
            <b>Tip:</b> Use the control panel to filter alloys by category,
            crystal structure, or primary element.
            </p>
        """)

    def update_alloy(self, alloy):
        """Update panel with alloy data"""
        if not alloy:
            self.show_default()
            return

        self.alloy = alloy
        self.microstructure_widget.set_alloy(alloy)
        self.properties_widget.set_alloy(alloy)
        self.composition_widget.set_alloy(alloy)

        # Build HTML content
        name = alloy.get('Name', 'Unknown')
        formula = alloy.get('formula', '')
        category = alloy.get('category', 'Unknown')
        subcategory = alloy.get('subcategory', '')
        description = alloy.get('description', '')

        # Physical properties
        density = alloy.get('density', 0)
        melting_point = alloy.get('melting_point', 0)
        thermal_cond = alloy.get('thermal_conductivity', 0)
        youngs_mod = alloy.get('youngs_modulus', 0)

        # Mechanical properties
        tensile = alloy.get('tensile_strength', 0)
        yield_str = alloy.get('yield_strength', 0)
        hardness = alloy.get('hardness', 0)
        elongation = alloy.get('elongation', 0)

        # Lattice properties
        structure = alloy.get('crystal_structure', 'Unknown')
        lattice_a = alloy.get('lattice_parameter_a', 0)
        packing = alloy.get('packing_factor', 0)

        # Colors
        category_color = AlloyCategory.get_color(category)
        structure_color = CrystalStructure.get_color(structure)

        # Applications
        applications = alloy.get('Applications', [])
        apps_html = ""
        if applications:
            apps_html = "<h3 style='color: #B08264; margin-top: 15px;'>Applications:</h3><ul>"
            for app in applications[:5]:
                apps_html += f"<li>{app}</li>"
            apps_html += "</ul>"

        # Components
        components = alloy.get('Components', [])
        comp_html = ""
        if components:
            comp_html = "<h3 style='color: #B08264; margin-top: 15px;'>Components:</h3>"
            comp_html += "<table style='width: 100%; color: white;'>"
            for comp in components[:8]:
                elem = comp.get('Element', '?')
                min_pct = comp.get('MinPercent', 0)
                max_pct = comp.get('MaxPercent', 0)
                role = comp.get('Role', '')
                role_color = ComponentRole.get_color(role)
                comp_html += f"""
                    <tr>
                        <td><b>{elem}</b></td>
                        <td>{min_pct:.1f} - {max_pct:.1f}%</td>
                        <td><span style='color: {role_color};'>{role}</span></td>
                    </tr>
                """
            comp_html += "</table>"

        html = f"""
            <h2 style='color: #B08264;'>{name}</h2>
            <div style='font-size: 16px; font-weight: bold; color: white;'>{formula}</div>
            <div style='color: #aaa; font-size: 11px;'>{description[:100]}{'...' if len(description) > 100 else ''}</div>
            <hr style='border-color: #B08264;'>

            <h3 style='color: #B08264;'>Physical Properties:</h3>
            <table style='width: 100%; color: white; line-height: 1.8;'>
                <tr>
                    <td><b>Density:</b></td>
                    <td><b style='color: #00ff88;'>{density:.2f}</b> g/cm³</td>
                </tr>
                <tr>
                    <td><b>Melting Point:</b></td>
                    <td><b style='color: #00ff88;'>{melting_point:.0f} K</b> ({melting_point - 273.15:.0f}°C)</td>
                </tr>
                <tr>
                    <td><b>Thermal Conductivity:</b></td>
                    <td>{thermal_cond:.1f} W/m·K</td>
                </tr>
                <tr>
                    <td><b>Young's Modulus:</b></td>
                    <td>{youngs_mod:.0f} GPa</td>
                </tr>
            </table>

            <h3 style='color: #B08264; margin-top: 15px;'>Mechanical Properties:</h3>
            <table style='width: 100%; color: white; line-height: 1.8;'>
                <tr>
                    <td><b>Tensile Strength:</b></td>
                    <td><b style='color: #4CAF50;'>{tensile:.0f}</b> MPa</td>
                </tr>
                <tr>
                    <td><b>Yield Strength:</b></td>
                    <td><b style='color: #2196F3;'>{yield_str:.0f}</b> MPa</td>
                </tr>
                <tr>
                    <td><b>Hardness:</b></td>
                    <td>{hardness:.0f} HB</td>
                </tr>
                <tr>
                    <td><b>Elongation:</b></td>
                    <td>{elongation:.0f}%</td>
                </tr>
            </table>

            <h3 style='color: #B08264; margin-top: 15px;'>Lattice Properties:</h3>
            <table style='width: 100%; color: white; line-height: 1.8;'>
                <tr>
                    <td><b>Crystal Structure:</b></td>
                    <td><span style='background: {structure_color}; padding: 2px 8px;
                        border-radius: 4px; color: black;'>{structure}</span></td>
                </tr>
                <tr>
                    <td><b>Lattice Parameter:</b></td>
                    <td>{lattice_a:.2f} pm</td>
                </tr>
                <tr>
                    <td><b>Packing Factor:</b></td>
                    <td>{packing:.2f}</td>
                </tr>
            </table>

            {comp_html}

            {apps_html}

            <div style='background: rgba(176,130,100,0.15); padding: 12px; border-radius: 8px;
                border-left: 4px solid {category_color}; margin-top: 15px;'>
                <p style='margin: 0;'><b>Category:</b> {category}</p>
                <p style='margin: 0;'><b>Sub-category:</b> {subcategory}</p>
            </div>
        """
        self.info_text.setHtml(html)
