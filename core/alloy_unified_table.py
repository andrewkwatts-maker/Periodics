"""
Alloy Unified Table Widget
Main visualization widget for displaying alloys with various layouts.
Features microstructure visualization using crystalline_math module.
"""

import math
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QRadialGradient,
                           QLinearGradient, QPainterPath, QImage, QPixmap)

from data.alloy_loader import AlloyDataLoader
from core.alloy_enums import (AlloyLayoutMode, AlloyCategory, CrystalStructure,
                               AlloyProperty, get_element_color)
from layouts.alloy_category_layout import AlloyCategoryLayout
from layouts.alloy_property_layout import AlloyPropertyLayout
from layouts.alloy_composition_layout import AlloyCompositionLayout
from layouts.alloy_lattice_layout import AlloyLatticeLayout

# Import crystalline math for microstructure visualization
try:
    from utils.crystalline_math import (
        VoronoiTessellation, PerlinNoise, SimplexNoise,
        MicrostructureRenderer, generate_noise_phase_map
    )
    HAS_CRYSTALLINE_MATH = True
except ImportError:
    HAS_CRYSTALLINE_MATH = False


class AlloyUnifiedTable(QWidget):
    """Main widget for visualizing alloys"""

    # Signals
    alloy_selected = Signal(dict)
    alloy_hovered = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        # Data
        self.loader = AlloyDataLoader()
        self.base_alloys = self.loader.load_all_alloys()
        self.positioned_alloys = []

        # State
        self.layout_mode = AlloyLayoutMode.CATEGORY
        self.hovered_alloy = None
        self.selected_alloy = None

        # Filters
        self.category_filter = None
        self.structure_filter = None
        self.element_filter = None

        # Visual settings
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.scroll_offset_y = 0

        # Scatter plot settings
        self.scatter_x_property = 'density'
        self.scatter_y_property = 'tensile_strength'

        # Layout renderers
        self.layouts = {
            AlloyLayoutMode.CATEGORY: AlloyCategoryLayout(self.width(), self.height()),
            AlloyLayoutMode.PROPERTY_SCATTER: AlloyPropertyLayout(self.width(), self.height()),
            AlloyLayoutMode.COMPOSITION: AlloyCompositionLayout(self.width(), self.height()),
            AlloyLayoutMode.LATTICE: AlloyLatticeLayout(self.width(), self.height()),
        }

        # Initialize layout
        self._update_layout()

    def set_layout_mode(self, mode):
        """Set the layout mode"""
        if isinstance(mode, str):
            mode = AlloyLayoutMode.from_string(mode)
        self.layout_mode = mode
        self._update_layout()
        self.update()

    def set_category_filter(self, category):
        """Set category filter"""
        self.category_filter = category
        self._update_layout()
        self.update()

    def set_structure_filter(self, structure):
        """Set crystal structure filter"""
        self.structure_filter = structure
        self._update_layout()
        self.update()

    def set_element_filter(self, element):
        """Set primary element filter"""
        self.element_filter = element
        self._update_layout()
        self.update()

    def set_scatter_properties(self, x_prop, y_prop):
        """Set properties for scatter plot axes"""
        self.scatter_x_property = x_prop
        self.scatter_y_property = y_prop
        layout = self.layouts.get(AlloyLayoutMode.PROPERTY_SCATTER)
        if layout:
            layout.set_x_property(x_prop)
            layout.set_y_property(y_prop)
        if self.layout_mode == AlloyLayoutMode.PROPERTY_SCATTER:
            self._update_layout()
            self.update()

    def _get_filtered_alloys(self):
        """Get alloys after applying filters"""
        alloys = self.base_alloys.copy()

        if self.category_filter:
            alloys = [a for a in alloys if a.get('category', '').lower() == self.category_filter.lower()]

        if self.structure_filter:
            alloys = [a for a in alloys if a.get('crystal_structure', '').upper() == self.structure_filter.upper()]

        if self.element_filter:
            alloys = [a for a in alloys if a.get('primary_element') == self.element_filter]

        return alloys

    def _update_layout(self):
        """Recalculate positions for all alloys"""
        alloys = self._get_filtered_alloys()
        layout = self.layouts.get(self.layout_mode)

        if layout:
            layout.update_dimensions(self.width(), self.height())
            self.positioned_alloys = layout.calculate_layout(alloys)

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        for layout in self.layouts.values():
            layout.update_dimensions(self.width(), self.height())
        self._update_layout()

    def paintEvent(self, event):
        """Paint the alloy visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        self._draw_background(painter)

        # Apply transformations
        painter.translate(self.pan_x, self.pan_y - self.scroll_offset_y)
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw based on layout mode
        if self.layout_mode == AlloyLayoutMode.PROPERTY_SCATTER:
            self._draw_scatter_plot(painter)
        else:
            # Draw group headers if applicable
            self._draw_group_headers(painter)
            # Draw alloy cards
            for alloy in self.positioned_alloys:
                self._draw_alloy_card(painter, alloy)

        painter.end()

    def _draw_background(self, painter):
        """Draw the dark gradient background"""
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(15, 15, 30))
        gradient.setColorAt(1, QColor(30, 30, 50))
        painter.fillRect(self.rect(), QBrush(gradient))

    def _draw_group_headers(self, painter):
        """Draw group section headers"""
        layout = self.layouts.get(self.layout_mode)
        if not hasattr(layout, 'get_group_headers'):
            return

        headers = layout.get_group_headers(self.positioned_alloys)

        for header in headers:
            y = header.get('y', 0)
            name = header.get('name', '')
            color = header.get('color', '#FFFFFF')
            count = header.get('count', 0)
            description = header.get('description', '')

            # Draw header background
            header_rect = QRectF(20, y, self.width() - 40, 40)
            painter.setPen(Qt.PenStyle.NoPen)

            header_color = QColor(color)
            header_color.setAlpha(50)
            painter.setBrush(QBrush(header_color))
            painter.drawRoundedRect(header_rect, 8, 8)

            # Draw header text
            painter.setPen(QPen(QColor(color)))
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            text = f"{name} ({count})"
            painter.drawText(header_rect.adjusted(15, 0, 0, -5 if description else 0),
                           Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                           text)

            # Draw description if present
            if description:
                painter.setFont(QFont("Arial", 9))
                painter.setPen(QPen(QColor(200, 200, 200, 180)))
                desc_rect = QRectF(header_rect.left() + 15, header_rect.bottom() - 18,
                                   header_rect.width() - 30, 15)
                # Truncate description
                short_desc = description[:80] + '...' if len(description) > 80 else description
                painter.drawText(desc_rect, Qt.AlignmentFlag.AlignLeft, short_desc)

            # Draw accent line
            painter.setPen(QPen(QColor(color), 3))
            painter.drawLine(int(header_rect.left() + 5), int(header_rect.bottom() + 2),
                           int(header_rect.left() + 100), int(header_rect.bottom() + 2))

    def _draw_scatter_plot(self, painter):
        """Draw scatter plot visualization"""
        layout = self.layouts.get(AlloyLayoutMode.PROPERTY_SCATTER)
        axis_info = layout.get_axis_info()
        ticks = layout.get_axis_ticks()

        if not axis_info:
            return

        # Draw axes
        painter.setPen(QPen(QColor(100, 100, 120), 2))

        # X axis
        painter.drawLine(int(axis_info['plot_left']), int(axis_info['plot_bottom']),
                        int(axis_info['plot_right']), int(axis_info['plot_bottom']))

        # Y axis
        painter.drawLine(int(axis_info['plot_left']), int(axis_info['plot_bottom']),
                        int(axis_info['plot_left']), int(axis_info['plot_top']))

        # Draw tick marks and labels
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QPen(QColor(150, 150, 170)))

        for tick in ticks['x_ticks']:
            x = tick['position']
            y = axis_info['plot_bottom']
            painter.drawLine(int(x), int(y), int(x), int(y + 5))
            label = f"{tick['value']:.1f}" if tick['value'] < 100 else f"{int(tick['value'])}"
            painter.drawText(int(x - 20), int(y + 20), label)

        for tick in ticks['y_ticks']:
            x = axis_info['plot_left']
            y = tick['position']
            painter.drawLine(int(x - 5), int(y), int(x), int(y))
            label = f"{tick['value']:.0f}" if tick['value'] >= 10 else f"{tick['value']:.1f}"
            painter.drawText(int(x - 50), int(y + 5), label)

        # Draw axis labels
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(180, 180, 200)))

        x_label = AlloyProperty.get_display_name(axis_info['x_property'])
        x_unit = AlloyProperty.get_unit(axis_info['x_property'])
        painter.drawText(int((axis_info['plot_left'] + axis_info['plot_right']) / 2 - 50),
                        int(axis_info['plot_bottom'] + 45),
                        f"{x_label} ({x_unit})")

        # Y axis label (rotated)
        painter.save()
        painter.translate(20, (axis_info['plot_top'] + axis_info['plot_bottom']) / 2)
        painter.rotate(-90)
        y_label = AlloyProperty.get_display_name(axis_info['y_property'])
        y_unit = AlloyProperty.get_unit(axis_info['y_property'])
        painter.drawText(-50, 0, f"{y_label} ({y_unit})")
        painter.restore()

        # Draw data points
        for alloy in self.positioned_alloys:
            self._draw_scatter_point(painter, alloy)

    def _draw_scatter_point(self, painter, alloy):
        """Draw a single point in the scatter plot"""
        x = alloy.get('x', 0)
        y = alloy.get('y', 0)
        size = alloy.get('width', 60)

        is_hovered = alloy == self.hovered_alloy
        is_selected = alloy == self.selected_alloy

        category_color = QColor(alloy.get('category_color', '#C0C0C0'))

        # Draw glow for hover/selection
        if is_hovered or is_selected:
            glow_color = QColor(category_color)
            glow_color.setAlpha(100)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x + size/2, y + size/2), size * 0.8, size * 0.8)

        # Draw point
        gradient = QRadialGradient(x + size/2, y + size/2, size/2)
        gradient.setColorAt(0, category_color.lighter(130))
        gradient.setColorAt(0.7, category_color)
        gradient.setColorAt(1, category_color.darker(120))

        painter.setBrush(QBrush(gradient))
        if is_selected:
            painter.setPen(QPen(QColor(255, 255, 255), 3))
        elif is_hovered:
            painter.setPen(QPen(category_color.lighter(150), 2))
        else:
            painter.setPen(QPen(category_color.darker(120), 1))

        painter.drawEllipse(QPointF(x + size/2, y + size/2), size/2 - 2, size/2 - 2)

        # Draw label on hover
        if is_hovered or is_selected:
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            name = alloy.get('name', '')[:15]
            painter.drawText(int(x + size + 5), int(y + size/2 + 5), name)

    def _draw_alloy_card(self, painter, alloy):
        """Draw a single alloy card"""
        x = alloy.get('x', 0)
        y = alloy.get('y', 0)
        width = alloy.get('width', 160)
        height = alloy.get('height', 180)

        is_hovered = alloy == self.hovered_alloy
        is_selected = alloy == self.selected_alloy

        # Card background
        card_rect = QRectF(x, y, width, height)

        # Get category color
        category_color = QColor(AlloyCategory.get_color(alloy.get('category', 'Other')))

        # Gradient background
        gradient = QLinearGradient(x, y, x, y + height)
        if is_selected:
            gradient.setColorAt(0, QColor(80, 80, 100, 230))
            gradient.setColorAt(1, QColor(60, 60, 80, 230))
        elif is_hovered:
            gradient.setColorAt(0, QColor(70, 70, 90, 210))
            gradient.setColorAt(1, QColor(50, 50, 70, 210))
        else:
            gradient.setColorAt(0, QColor(55, 55, 75, 190))
            gradient.setColorAt(1, QColor(40, 40, 55, 190))

        painter.setBrush(QBrush(gradient))

        # Border
        if is_selected:
            painter.setPen(QPen(category_color, 3))
        elif is_hovered:
            painter.setPen(QPen(category_color.lighter(120), 2))
        else:
            painter.setPen(QPen(category_color.darker(120), 1))

        painter.drawRoundedRect(card_rect, 10, 10)

        # Draw microstructure preview
        self._draw_microstructure_preview(painter, alloy, x + 10, y + 10, width - 20, 70)

        # Draw alloy info
        self._draw_alloy_info(painter, alloy, x, y, width, height)

    def _draw_microstructure_preview(self, painter, alloy, x, y, width, height):
        """Draw a simplified microstructure preview"""
        # Draw background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 40)))
        painter.drawRoundedRect(QRectF(x, y, width, height), 5, 5)

        # Draw simplified Voronoi-like grain structure
        structure = alloy.get('crystal_structure', 'FCC')
        structure_color = QColor(CrystalStructure.get_color(structure))

        # Generate some pseudo-random grain centers based on alloy name
        seed = sum(ord(c) for c in alloy.get('name', 'alloy'))
        num_grains = 8 + (seed % 5)

        grain_centers = []
        for i in range(num_grains):
            gx = x + 10 + ((seed * (i + 1) * 17) % int(width - 20))
            gy = y + 10 + ((seed * (i + 1) * 23) % int(height - 20))
            grain_centers.append((gx, gy))

        # Draw grains as colored regions
        for i, (gx, gy) in enumerate(grain_centers):
            # Color variation based on IPF-like coloring
            hue = (seed + i * 30) % 360
            grain_color = QColor.fromHsv(hue, 120, 180, 150)

            # Draw gradient grain
            grain_gradient = QRadialGradient(gx, gy, 25)
            grain_gradient.setColorAt(0, grain_color)
            grain_gradient.setColorAt(1, grain_color.darker(150))

            painter.setBrush(QBrush(grain_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(gx, gy), 15, 12)

        # Draw grain boundaries
        painter.setPen(QPen(QColor(20, 20, 30), 1))
        for i, (gx, gy) in enumerate(grain_centers):
            painter.drawEllipse(QPointF(gx, gy), 15, 12)

        # Draw structure label
        painter.setPen(QPen(structure_color))
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(int(x + 3), int(y + height - 3), structure)

    def _draw_alloy_info(self, painter, alloy, x, y, width, height):
        """Draw alloy text information"""
        # Name
        name = alloy.get('name', '')
        painter.setPen(QPen(QColor(220, 220, 240)))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_rect = QRectF(x + 5, y + 85, width - 10, 20)
        # Truncate long names
        display_name = name[:18] + '...' if len(name) > 18 else name
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, display_name)

        # Formula
        formula = alloy.get('formula', '')
        category_color = QColor(AlloyCategory.get_color(alloy.get('category', 'Other')))
        painter.setPen(QPen(category_color))
        painter.setFont(QFont("Arial", 9))
        formula_rect = QRectF(x + 5, y + 103, width - 10, 16)
        painter.drawText(formula_rect, Qt.AlignmentFlag.AlignCenter, formula)

        # Properties
        painter.setPen(QPen(QColor(180, 180, 200, 200)))
        painter.setFont(QFont("Arial", 8))

        # Density
        density = alloy.get('density', 0)
        density_rect = QRectF(x + 5, y + 122, width - 10, 14)
        painter.drawText(density_rect, Qt.AlignmentFlag.AlignCenter, f"{density:.2f} g/cm³")

        # Tensile strength
        tensile = alloy.get('tensile_strength', 0)
        tensile_rect = QRectF(x + 5, y + 136, width - 10, 14)
        painter.drawText(tensile_rect, Qt.AlignmentFlag.AlignCenter, f"{tensile:.0f} MPa")

        # Category badge
        category = alloy.get('category', 'Other')
        badge_rect = QRectF(x + width - 50, y + height - 22, 45, 16)
        painter.setBrush(QBrush(category_color.darker(120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 3, 3)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 7))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, category[:8])

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        # Transform mouse position
        x = (event.position().x() - self.pan_x) / self.zoom_level
        y = (event.position().y() - self.pan_y + self.scroll_offset_y) / self.zoom_level

        layout = self.layouts.get(self.layout_mode)
        if layout:
            alloy = layout.get_alloy_at_position(x, y, self.positioned_alloys)

            if alloy != self.hovered_alloy:
                self.hovered_alloy = alloy
                if alloy:
                    self.alloy_hovered.emit(alloy)
                self.update()

    def mousePressEvent(self, event):
        """Handle mouse click for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.hovered_alloy:
                self.selected_alloy = self.hovered_alloy
                self.alloy_selected.emit(self.selected_alloy)
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
            return layout.get_content_height(self.positioned_alloys)
        return self.height()

    def reload_data(self):
        """Reload alloy data from files"""
        self.base_alloys = self.loader.load_all_alloys()
        self._update_layout()
        self.update()
