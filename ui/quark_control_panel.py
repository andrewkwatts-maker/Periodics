#!/usr/bin/env python3
"""
Quark Control Panel
Provides UI controls for particle visualization settings.
Polished to match the Atoms tab control panel features.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QSlider, QToolButton, QFrame, QColorDialog)
from PySide6.QtCore import Qt, QPropertyAnimation, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPolygonF
from PySide6.QtCore import QPointF

from core.quark_enums import QuarkLayoutMode, QuarkProperty, ParticleType
from data.data_manager import get_data_manager, DataCategory


class QuarkPropertyName:
    """Property names for quark/particle data mapping"""
    MASS = "Mass_MeVc2"
    CHARGE = "Charge_e"
    SPIN = "Spin_hbar"
    BARYON_NUMBER = "BaryonNumber_B"
    LEPTON_NUMBER = "LeptonNumber_L"
    ISOSPIN = "Isospin_I"
    PARTICLE_TYPE = "particle_type"
    GENERATION = "generation"
    STABILITY = "Stability"
    NONE = "none"

    @classmethod
    def get_display_name(cls, prop):
        """Get display name for property"""
        names = {
            cls.MASS: "Mass (MeV/c2)",
            cls.CHARGE: "Charge (e)",
            cls.SPIN: "Spin (hbar)",
            cls.BARYON_NUMBER: "Baryon Number",
            cls.LEPTON_NUMBER: "Lepton Number",
            cls.ISOSPIN: "Isospin",
            cls.PARTICLE_TYPE: "Particle Type",
            cls.GENERATION: "Generation",
            cls.STABILITY: "Stability",
            cls.NONE: "None"
        }
        return names.get(prop, prop)

    @classmethod
    def get_color_properties(cls):
        """Properties suitable for color encoding"""
        return [
            cls.MASS,
            cls.CHARGE,
            cls.SPIN,
            cls.BARYON_NUMBER,
            cls.LEPTON_NUMBER,
            cls.ISOSPIN,
            cls.PARTICLE_TYPE,
            cls.GENERATION,
            cls.STABILITY,
            cls.NONE
        ]

    @classmethod
    def get_size_properties(cls):
        """Properties suitable for size encoding"""
        return [
            cls.MASS,
            cls.CHARGE,
            cls.SPIN,
            cls.BARYON_NUMBER,
            cls.LEPTON_NUMBER,
            cls.NONE
        ]

    @classmethod
    def get_intensity_properties(cls):
        """Properties suitable for intensity encoding"""
        return [
            cls.MASS,
            cls.SPIN,
            cls.STABILITY,
            cls.NONE
        ]

    @classmethod
    def get_property_range(cls, prop):
        """Get default min/max range for a property"""
        ranges = {
            cls.MASS: (0.0, 175000.0),  # Up quark to top quark (MeV/c2)
            cls.CHARGE: (-1.0, 1.0),  # In units of e
            cls.SPIN: (0.0, 1.0),  # In units of hbar
            cls.BARYON_NUMBER: (-1.0, 1.0),
            cls.LEPTON_NUMBER: (-1.0, 1.0),
            cls.ISOSPIN: (0.0, 1.0),
            cls.GENERATION: (0, 3),
            cls.NONE: (0, 1)
        }
        return ranges.get(prop, (0, 100))


class CollapsibleBox(QWidget):
    """A collapsible widget that can expand/collapse its content"""
    def __init__(self, title="", border_color="#4fc3f7", parent=None):
        super().__init__(parent)
        self.border_color = border_color

        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet(f"""
            QToolButton {{
                border: none;
                color: white;
                font-weight: bold;
                text-align: left;
                padding: 5px;
            }}
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QFrame()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setStyleSheet(f"""
            QFrame {{
                border: none;
                background: transparent;
                padding: 5px;
            }}
        """)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_area.setLayout(self.content_layout)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

        self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(200)

    def on_toggle(self):
        """Toggle the expanded/collapsed state"""
        checked = self.toggle_button.isChecked()
        arrow_type = Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        self.toggle_button.setArrowType(arrow_type)

        if checked:
            # Expand - use animation to grow, then remove max height constraint
            content_height = self.content_area.sizeHint().height()
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(content_height)
            self.toggle_animation.finished.connect(self._on_expand_finished)
            self.toggle_animation.start()
        else:
            # Collapse
            self.content_area.setMaximumHeight(self.content_area.height())
            self.toggle_animation.setStartValue(self.content_area.height())
            self.toggle_animation.setEndValue(0)
            self.toggle_animation.start()

    def _on_expand_finished(self):
        """Remove height constraint after expand animation completes"""
        self.content_area.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
        try:
            self.toggle_animation.finished.disconnect(self._on_expand_finished)
        except RuntimeError:
            pass  # Already disconnected


class QuarkPropertyMappingWidget(QWidget):
    """
    Unified property mapping widget for quark properties.
    Features:
    - Color gradient bar
    - Yellow draggable tags for color mapping range (min/max)
    - Grey draggable tags for filter range
    - Color picker swatches for customizing gradient
    """

    # Signals for value changes
    filter_changed = Signal(bool)
    color_range_changed = Signal(float, float)
    filter_range_changed = Signal(float, float)
    gradient_colors_changed = Signal(object, object)

    def __init__(self, property_name="Mass_MeVc2", parent=None):
        super().__init__(parent)
        self.property_name = property_name

        # Property value range
        self.min_value, self.max_value = QuarkPropertyName.get_property_range(property_name)

        # Color mapping range (yellow tags)
        self.min_color_map = self.min_value
        self.max_color_map = self.max_value

        # Filter range (grey tags)
        self.min_filter = self.min_value
        self.max_filter = self.max_value

        # Filter enabled state
        self.filter_enabled = True

        # Custom gradient colors
        self.custom_gradient_start = QColor(100, 150, 255)
        self.custom_gradient_end = QColor(255, 100, 100)

        # Dragging state
        self.dragging_tag = None
        self.drag_start_x = 0

        # UI dimensions
        self.bar_margin = 30
        self.bar_y = 35
        self.bar_height = 30
        self.tag_width = 12
        self.tag_height = 15
        self.swatch_size = 16

        self.setMinimumHeight(110)
        self.setMaximumHeight(110)
        self.setMouseTracking(True)

    def set_property(self, property_name):
        """Update the property being visualized"""
        self.property_name = property_name
        self.min_value, self.max_value = QuarkPropertyName.get_property_range(property_name)
        self.min_color_map = self.min_value
        self.max_color_map = self.max_value
        self.min_filter = self.min_value
        self.max_filter = self.max_value
        self.update()

    def set_value_range(self, min_value, max_value):
        """Set the absolute property value range"""
        self.min_value = min_value
        self.max_value = max_value
        self.min_color_map = min_value
        self.max_color_map = max_value
        self.min_filter = min_value
        self.max_filter = max_value
        self.update()

    def _value_to_x(self, value):
        """Convert property value to x position"""
        width = self.width()
        bar_width = width - 2 * self.bar_margin

        if self.max_value == self.min_value:
            return self.bar_margin

        t = (value - self.min_value) / (self.max_value - self.min_value)
        return self.bar_margin + bar_width * t

    def _x_to_value(self, x):
        """Convert x position to property value"""
        width = self.width()
        bar_width = width - 2 * self.bar_margin

        t = (x - self.bar_margin) / bar_width
        t = max(0.0, min(1.0, t))

        return self.min_value + (self.max_value - self.min_value) * t

    def _get_gradient_color(self, value):
        """Get color for a value in the gradient"""
        if self.max_value == self.min_value:
            t = 0.5
        else:
            t = (value - self.min_value) / (self.max_value - self.min_value)
            t = max(0, min(1, t))

        # Lerp between start and end colors
        r = int(self.custom_gradient_start.red() * (1 - t) + self.custom_gradient_end.red() * t)
        g = int(self.custom_gradient_start.green() * (1 - t) + self.custom_gradient_end.green() * t)
        b = int(self.custom_gradient_start.blue() * (1 - t) + self.custom_gradient_end.blue() * t)
        return QColor(r, g, b)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        bar_width = width - 2 * self.bar_margin

        # Draw gradient bar
        segments = 200
        seg_width = bar_width / segments

        for i in range(segments):
            t = i / segments
            value = self.min_value + (self.max_value - self.min_value) * t
            color = self._get_gradient_color(value)
            x = self.bar_margin + i * seg_width
            painter.fillRect(int(x), self.bar_y, int(seg_width + 1), self.bar_height, color)

        # Draw bar border
        painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.bar_margin, self.bar_y, bar_width, self.bar_height)

        # Draw grey filter range tags (above bar)
        self._draw_filter_tag(painter, self.min_filter, "min_filter", is_min=True)
        self._draw_filter_tag(painter, self.max_filter, "max_filter", is_min=False)

        # Draw yellow mapping tags (below bar)
        self._draw_color_tag(painter, self.min_color_map, "min_color", is_min=True)
        self._draw_color_tag(painter, self.max_color_map, "max_color", is_min=False)

        # Draw color picker swatches
        self._draw_color_swatches(painter)

    def _draw_filter_tag(self, painter, value, tag_id, is_min):
        """Draw grey filter tag above the bar"""
        x = self._value_to_x(value)

        # Draw vertical line from tag to bar
        painter.setPen(QPen(QColor(150, 150, 150, 200), 2))
        painter.drawLine(int(x), self.bar_y - self.tag_height - 2, int(x), self.bar_y)

        # Draw triangle tag pointing down
        tag_y = self.bar_y - self.tag_height - 2
        triangle = QPolygonF([
            QPointF(x, tag_y + self.tag_height),
            QPointF(x - self.tag_width / 2, tag_y),
            QPointF(x + self.tag_width / 2, tag_y)
        ])

        if self.dragging_tag == tag_id:
            painter.setBrush(QColor(200, 200, 200))
        else:
            painter.setBrush(QColor(150, 150, 150))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawPolygon(triangle)

        # Draw value label above tag
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Arial", 8))
        label = self._format_value(value)
        text_width = painter.fontMetrics().horizontalAdvance(label)
        painter.drawText(int(x - text_width / 2), tag_y - 3, label)

    def _draw_color_tag(self, painter, value, tag_id, is_min):
        """Draw yellow color mapping tag below the bar"""
        x = self._value_to_x(value)

        # Draw vertical line from bar to tag
        painter.setPen(QPen(QColor(255, 255, 0, 220), 2))
        painter.drawLine(int(x), self.bar_y + self.bar_height, int(x), self.bar_y + self.bar_height + self.tag_height + 2)

        # Draw triangle tag pointing up
        tag_y = self.bar_y + self.bar_height + 2
        triangle = QPolygonF([
            QPointF(x, tag_y),
            QPointF(x - self.tag_width / 2, tag_y + self.tag_height),
            QPointF(x + self.tag_width / 2, tag_y + self.tag_height)
        ])

        if self.dragging_tag == tag_id:
            painter.setBrush(QColor(255, 255, 100))
        else:
            painter.setBrush(QColor(255, 255, 0))
        painter.setPen(QPen(QColor(200, 200, 0), 1))
        painter.drawPolygon(triangle)

        # Draw value label below tag
        painter.setPen(QColor(255, 255, 0))
        painter.setFont(QFont("Arial", 8))
        label = self._format_value(value)
        text_width = painter.fontMetrics().horizontalAdvance(label)
        painter.drawText(int(x - text_width / 2), tag_y + self.tag_height + 12, label)

    def _format_value(self, value):
        """Format value for display based on magnitude"""
        if abs(value) >= 1000:
            return f"{value:.0f}"
        elif abs(value) >= 1:
            return f"{value:.1f}"
        else:
            return f"{value:.3f}"

    def _draw_color_swatches(self, painter):
        """Draw color picker swatches on left and right of gradient bar"""
        # Left swatch (start color)
        left_x = self.bar_margin - self.swatch_size - 6
        swatch_y = self.bar_y + (self.bar_height - self.swatch_size) // 2

        painter.setBrush(QBrush(self.custom_gradient_start))
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        painter.drawRect(int(left_x), int(swatch_y), self.swatch_size, self.swatch_size)

        # Right swatch (end color)
        right_x = self.bar_margin + (self.width() - 2 * self.bar_margin) + 6

        painter.setBrush(QBrush(self.custom_gradient_end))
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        painter.drawRect(int(right_x), int(swatch_y), self.swatch_size, self.swatch_size)

    def _get_swatch_rect(self, swatch_id):
        """Get rectangle for a swatch"""
        swatch_y = self.bar_y + (self.bar_height - self.swatch_size) // 2
        if swatch_id == 'start':
            left_x = self.bar_margin - self.swatch_size - 6
            return (left_x, swatch_y, self.swatch_size, self.swatch_size)
        else:
            right_x = self.bar_margin + (self.width() - 2 * self.bar_margin) + 6
            return (right_x, swatch_y, self.swatch_size, self.swatch_size)

    def mousePressEvent(self, event):
        """Handle mouse press for tag dragging and color swatch clicks"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.position().x()
        y = event.position().y()

        # Check if clicking on color swatches first
        for swatch_id in ['start', 'end']:
            sx, sy, sw, sh = self._get_swatch_rect(swatch_id)
            if sx <= x <= sx + sw and sy <= y <= sy + sh:
                self._open_color_picker(swatch_id)
                return

        # Check if clicking on any tag
        tags = [
            ('min_filter', self._value_to_x(self.min_filter), self.bar_y - self.tag_height - 2, self.tag_height),
            ('max_filter', self._value_to_x(self.max_filter), self.bar_y - self.tag_height - 2, self.tag_height),
            ('min_color', self._value_to_x(self.min_color_map), self.bar_y + self.bar_height + 2, self.tag_height),
            ('max_color', self._value_to_x(self.max_color_map), self.bar_y + self.bar_height + 2, self.tag_height),
        ]

        for tag_id, tag_x, tag_y, tag_h in tags:
            if abs(x - tag_x) < self.tag_width and abs(y - (tag_y + tag_h / 2)) < tag_h:
                self.dragging_tag = tag_id
                self.drag_start_x = x
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.update()
                break

    def _open_color_picker(self, swatch_id):
        """Open color picker dialog"""
        current_color = self.custom_gradient_start if swatch_id == 'start' else self.custom_gradient_end
        color = QColorDialog.getColor(current_color, self, f"Choose Gradient {'Start' if swatch_id == 'start' else 'End'} Color")

        if color.isValid():
            if swatch_id == 'start':
                self.custom_gradient_start = color
            else:
                self.custom_gradient_end = color
            self.gradient_colors_changed.emit(self.custom_gradient_start, self.custom_gradient_end)
            self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move for tag dragging"""
        if self.dragging_tag is None:
            # Update cursor when hovering over tags
            x = event.position().x()
            y = event.position().y()

            tags = [
                (self._value_to_x(self.min_filter), self.bar_y - self.tag_height - 2, self.tag_height),
                (self._value_to_x(self.max_filter), self.bar_y - self.tag_height - 2, self.tag_height),
                (self._value_to_x(self.min_color_map), self.bar_y + self.bar_height + 2, self.tag_height),
                (self._value_to_x(self.max_color_map), self.bar_y + self.bar_height + 2, self.tag_height),
            ]

            hovering = False
            for tag_x, tag_y, tag_h in tags:
                if abs(x - tag_x) < self.tag_width and abs(y - (tag_y + tag_h / 2)) < tag_h:
                    hovering = True
                    break

            self.setCursor(Qt.CursorShape.OpenHandCursor if hovering else Qt.CursorShape.ArrowCursor)
            return

        # Dragging a tag
        x = event.position().x()
        new_value = self._x_to_value(x)

        if self.dragging_tag == 'min_filter':
            self.min_filter = max(self.min_value, min(self.max_filter, new_value))
            self.filter_range_changed.emit(self.min_filter, self.max_filter)
        elif self.dragging_tag == 'max_filter':
            self.max_filter = max(self.min_filter, min(self.max_value, new_value))
            self.filter_range_changed.emit(self.min_filter, self.max_filter)
        elif self.dragging_tag == 'min_color':
            self.min_color_map = max(self.min_value, min(self.max_color_map, new_value))
            self.color_range_changed.emit(self.min_color_map, self.max_color_map)
        elif self.dragging_tag == 'max_color':
            self.max_color_map = max(self.min_color_map, min(self.max_value, new_value))
            self.color_range_changed.emit(self.min_color_map, self.max_color_map)

        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton and self.dragging_tag is not None:
            self.dragging_tag = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()


class QuarkPropertyControl(QWidget):
    """Expandable control for a single visual property with range controls and filtering"""

    property_changed = Signal(str, int)  # property_key, index

    def __init__(self, title, property_key, parent_panel, available_properties, default_index=0):
        super().__init__()
        self.property_key = property_key
        self.parent_panel = parent_panel
        self.is_expanded = False
        self.default_index = default_index
        self.available_properties = available_properties

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 3, 5, 3)
        main_layout.setSpacing(3)

        # Header with expand/collapse and property selector
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        self.expand_btn = QToolButton()
        self.expand_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.expand_btn.setStyleSheet("QToolButton { border: none; color: white; }")
        self.expand_btn.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.expand_btn)

        title_label = QLabel(title + ":")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px;")
        title_label.setMinimumWidth(110)
        header_layout.addWidget(title_label)

        self.property_combo = QComboBox()
        display_names = [QuarkPropertyName.get_display_name(p) for p in available_properties]
        self.property_combo.addItems(display_names)
        self.property_combo.setCurrentIndex(default_index)
        self.property_combo.setStyleSheet(self._get_combo_style())
        self.property_combo.currentIndexChanged.connect(self.on_property_selection_changed)
        header_layout.addWidget(self.property_combo, 1)

        main_layout.addWidget(header)

        # Expandable details area
        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(25, 5, 5, 5)
        details_layout.setSpacing(8)

        # Property mapping widget
        mapping_label = QLabel("Property Mapping & Filtering:")
        mapping_label.setStyleSheet("color: rgba(255,255,255,200); font-size: 9px; font-weight: bold;")
        details_layout.addWidget(mapping_label)

        current_prop = available_properties[default_index] if default_index < len(available_properties) else QuarkPropertyName.MASS
        self.mapping_widget = QuarkPropertyMappingWidget(current_prop)
        self.mapping_widget.color_range_changed.connect(self.on_color_range_changed)
        self.mapping_widget.filter_range_changed.connect(self.on_filter_range_changed)
        self.mapping_widget.gradient_colors_changed.connect(self.on_gradient_colors_changed)
        details_layout.addWidget(self.mapping_widget)

        # Fade slider
        fade_container = QWidget()
        fade_layout = QHBoxLayout(fade_container)
        fade_layout.setContentsMargins(0, 5, 0, 0)
        fade_layout.setSpacing(5)

        fade_label = QLabel("Fade:")
        fade_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 35px;")
        fade_layout.addWidget(fade_label)

        self.fade_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_slider.setMinimum(0)
        self.fade_slider.setMaximum(100)
        self.fade_slider.setValue(0)
        self.fade_slider.setStyleSheet(self._get_slider_style())
        self.fade_slider.valueChanged.connect(self.on_fade_changed)
        fade_layout.addWidget(self.fade_slider)

        self.fade_display = QLabel("0%")
        self.fade_display.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 35px;")
        fade_layout.addWidget(self.fade_display)

        details_layout.addWidget(fade_container)

        main_layout.addWidget(self.details_widget)

    def toggle_expanded(self):
        """Toggle expanded/collapsed state"""
        self.is_expanded = not self.is_expanded
        self.expand_btn.setArrowType(Qt.ArrowType.DownArrow if self.is_expanded else Qt.ArrowType.RightArrow)
        self.details_widget.setVisible(self.is_expanded)

    def on_property_selection_changed(self, idx):
        """Handle property selection change"""
        if idx < len(self.available_properties):
            prop = self.available_properties[idx]
            self.mapping_widget.set_property(prop)
            self.property_changed.emit(self.property_key, idx)

    def on_color_range_changed(self, min_map, max_map):
        """Handle color mapping range change"""
        if hasattr(self.parent_panel, 'table'):
            attr_map = {
                "fill_color": ("fill_color_range_min", "fill_color_range_max"),
                "border_color": ("border_color_range_min", "border_color_range_max"),
                "glow_color": ("glow_color_range_min", "glow_color_range_max"),
                "symbol_text_color": ("symbol_text_color_range_min", "symbol_text_color_range_max"),
            }
            if self.property_key in attr_map:
                min_attr, max_attr = attr_map[self.property_key]
                if hasattr(self.parent_panel.table, min_attr):
                    setattr(self.parent_panel.table, min_attr, min_map)
                if hasattr(self.parent_panel.table, max_attr):
                    setattr(self.parent_panel.table, max_attr, max_map)
                self.parent_panel.table.update()

    def on_filter_range_changed(self, min_filter, max_filter):
        """Handle filter range change"""
        if hasattr(self.parent_panel, 'table'):
            prop = self.available_properties[self.property_combo.currentIndex()]
            if hasattr(self.parent_panel.table, 'filters'):
                if prop not in self.parent_panel.table.filters:
                    self.parent_panel.table.filters[prop] = {'min': min_filter, 'max': max_filter, 'active': True}
                else:
                    self.parent_panel.table.filters[prop]['min'] = min_filter
                    self.parent_panel.table.filters[prop]['max'] = max_filter
                self.parent_panel.table.update()

    def on_gradient_colors_changed(self, start_color, end_color):
        """Handle gradient color change"""
        if hasattr(self.parent_panel, 'table'):
            gradient_attr_map = {
                "fill_color": ("custom_fill_gradient_start", "custom_fill_gradient_end"),
                "border_color": ("custom_border_gradient_start", "custom_border_gradient_end"),
                "glow_color": ("custom_glow_gradient_start", "custom_glow_gradient_end"),
                "symbol_text_color": ("custom_symbol_text_gradient_start", "custom_symbol_text_gradient_end"),
            }
            if self.property_key in gradient_attr_map:
                start_attr, end_attr = gradient_attr_map[self.property_key]
                if hasattr(self.parent_panel.table, start_attr):
                    setattr(self.parent_panel.table, start_attr, start_color)
                if hasattr(self.parent_panel.table, end_attr):
                    setattr(self.parent_panel.table, end_attr, end_color)
                self.parent_panel.table.update()

    def on_fade_changed(self, value):
        """Handle fade slider change"""
        fade = value / 100.0
        self.fade_display.setText(f"{value}%")
        if hasattr(self.parent_panel, 'table'):
            fade_map = {
                "fill_color": "fill_fade",
                "border_color": "border_color_fade",
                "glow_color": "glow_color_fade",
                "symbol_text_color": "symbol_text_color_fade"
            }
            if self.property_key in fade_map:
                attr = fade_map[self.property_key]
                if hasattr(self.parent_panel.table, attr):
                    setattr(self.parent_panel.table, attr, fade)
                    self.parent_panel.table.update()

    def _get_combo_style(self):
        return """
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #764ba2;
                padding: 3px 5px;
                border-radius: 3px;
                font-size: 9px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #764ba2;
            }
        """

    def _get_slider_style(self):
        return """
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(60, 60, 80, 200);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #764ba2;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """


class QuarkControlPanel(QWidget):
    """Control panel for the Quark visualization"""

    # Data management signals
    add_requested = Signal()
    edit_requested = Signal()
    remove_requested = Signal()
    reset_requested = Signal()

    def __init__(self, table_widget):
        super().__init__()
        self.table = table_widget
        self.setup_ui()

    def setup_ui(self):
        """Set up the control panel UI"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: rgba(40, 40, 60, 100);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(79, 195, 247, 150);
                border-radius: 5px;
            }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Title
        title = QLabel("Particle Controls")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #4fc3f7;")
        layout.addWidget(title)

        # Layout Mode Selection
        layout.addWidget(self._create_layout_mode_group())

        # Visual Property Encodings (collapsible)
        layout.addWidget(self._create_visual_properties_group())

        # Filter Options (collapsible)
        layout.addWidget(self._create_filter_options_group())

        # Display Options
        layout.addWidget(self._create_display_options_group())

        # Data Management
        layout.addWidget(self._create_data_management_group())

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_layout_mode_group(self):
        """Create layout mode selection group"""
        group = QGroupBox("Layout Mode")
        group.setStyleSheet(self._get_group_style("#667eea"))
        layout = QVBoxLayout()

        # All 8 layout modes
        self.standard_radio = QRadioButton("Standard Model Grid")
        self.linear_radio = QRadioButton("Linear (Sorted)")
        self.circular_radio = QRadioButton("Circular (Rings)")
        self.alternative_radio = QRadioButton("By Interaction Force")
        self.force_network_radio = QRadioButton("Force Network")
        self.mass_spiral_radio = QRadioButton("Mass Spiral")
        self.fermion_boson_radio = QRadioButton("Fermion/Boson Split")
        self.charge_mass_radio = QRadioButton("Charge-Mass Grid")
        self.standard_radio.setChecked(True)

        radio_style = self._get_radio_style()
        for radio in [self.standard_radio, self.linear_radio, self.circular_radio,
                      self.alternative_radio, self.force_network_radio, self.mass_spiral_radio,
                      self.fermion_boson_radio, self.charge_mass_radio]:
            radio.setStyleSheet(radio_style)

        self.standard_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.STANDARD_MODEL) if checked else None)
        self.linear_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.LINEAR) if checked else None)
        self.circular_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.CIRCULAR) if checked else None)
        self.alternative_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.ALTERNATIVE) if checked else None)
        self.force_network_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.FORCE_NETWORK) if checked else None)
        self.mass_spiral_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.MASS_SPIRAL) if checked else None)
        self.fermion_boson_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.FERMION_BOSON) if checked else None)
        self.charge_mass_radio.toggled.connect(
            lambda checked: self._on_layout_changed(QuarkLayoutMode.CHARGE_MASS) if checked else None)

        layout.addWidget(self.standard_radio)
        layout.addWidget(self.linear_radio)
        layout.addWidget(self.circular_radio)
        layout.addWidget(self.alternative_radio)
        layout.addWidget(self.force_network_radio)
        layout.addWidget(self.mass_spiral_radio)
        layout.addWidget(self.fermion_boson_radio)
        layout.addWidget(self.charge_mass_radio)

        # Sort property for linear mode
        self.sort_container = QWidget()
        sort_layout = QHBoxLayout(self.sort_container)
        sort_layout.setContentsMargins(20, 5, 0, 0)

        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 10px;")
        sort_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Mass", "Charge", "Spin", "Generation", "Name"])
        self.sort_combo.setStyleSheet(self._get_combo_style())
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        sort_layout.addWidget(self.sort_combo)

        self.sort_container.setVisible(False)
        layout.addWidget(self.sort_container)

        # Reset view button
        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet(self._get_button_style())
        reset_btn.clicked.connect(self._on_reset_view)
        layout.addWidget(reset_btn)

        group.setLayout(layout)
        return group

    def _create_visual_properties_group(self):
        """Create visual property encodings with expandable controls"""
        collapsible = CollapsibleBox("Visual Property Encodings", "#764ba2")

        # Available properties for color encoding
        color_properties = QuarkPropertyName.get_color_properties()

        # 1. Fill Colour -> Mass_MeVc2
        self.fill_color_control = QuarkPropertyControl(
            "Fill Colour", "fill_color", self, color_properties, default_index=0)
        collapsible.content_layout.addWidget(self.fill_color_control)

        # 2. Border Colour -> Charge_e
        self.border_color_control = QuarkPropertyControl(
            "Border Colour", "border_color", self, color_properties, default_index=1)
        collapsible.content_layout.addWidget(self.border_color_control)

        # 3. Glow Colour -> Spin_hbar
        self.glow_color_control = QuarkPropertyControl(
            "Glow Colour", "glow_color", self, color_properties, default_index=2)
        collapsible.content_layout.addWidget(self.glow_color_control)

        # 4. Symbol Text Colour -> BaryonNumber_B
        self.symbol_text_color_control = QuarkPropertyControl(
            "Symbol Text Colour", "symbol_text_color", self, color_properties, default_index=3)
        collapsible.content_layout.addWidget(self.symbol_text_color_control)

        # Reset button for visual encodings
        reset_visual_btn = QPushButton("Reset Visual Encodings")
        reset_visual_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #7688f0, stop:1 #8658b8);
            }
        """)
        reset_visual_btn.clicked.connect(self._reset_visual_encodings)
        collapsible.content_layout.addWidget(reset_visual_btn)

        # Open by default
        collapsible.toggle_button.setChecked(True)
        collapsible.on_toggle()

        return collapsible

    def _create_filter_options_group(self):
        """Create filter options section"""
        collapsible = CollapsibleBox("Filter Options", "#f093fb")

        # Classification filter
        class_label = QLabel("Classification:")
        class_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px;")
        collapsible.content_layout.addWidget(class_label)

        self.quark_check = QCheckBox("Quarks")
        self.quark_check.setChecked(True)
        self.quark_check.setStyleSheet(self._get_checkbox_style())
        self.quark_check.toggled.connect(self._on_classification_filter_changed)
        collapsible.content_layout.addWidget(self.quark_check)

        self.lepton_check = QCheckBox("Leptons")
        self.lepton_check.setChecked(True)
        self.lepton_check.setStyleSheet(self._get_checkbox_style())
        self.lepton_check.toggled.connect(self._on_classification_filter_changed)
        collapsible.content_layout.addWidget(self.lepton_check)

        self.boson_check = QCheckBox("Bosons")
        self.boson_check.setChecked(True)
        self.boson_check.setStyleSheet(self._get_checkbox_style())
        self.boson_check.toggled.connect(self._on_classification_filter_changed)
        collapsible.content_layout.addWidget(self.boson_check)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setStyleSheet("background: rgba(255,255,255,50);")
        collapsible.content_layout.addWidget(separator1)

        # Generation filter
        gen_label = QLabel("Generation:")
        gen_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px; margin-top: 5px;")
        collapsible.content_layout.addWidget(gen_label)

        self.gen1_check = QCheckBox("1st Generation")
        self.gen1_check.setChecked(True)
        self.gen1_check.setStyleSheet(self._get_checkbox_style())
        self.gen1_check.toggled.connect(self._on_generation_filter_changed)
        collapsible.content_layout.addWidget(self.gen1_check)

        self.gen2_check = QCheckBox("2nd Generation")
        self.gen2_check.setChecked(True)
        self.gen2_check.setStyleSheet(self._get_checkbox_style())
        self.gen2_check.toggled.connect(self._on_generation_filter_changed)
        collapsible.content_layout.addWidget(self.gen2_check)

        self.gen3_check = QCheckBox("3rd Generation")
        self.gen3_check.setChecked(True)
        self.gen3_check.setStyleSheet(self._get_checkbox_style())
        self.gen3_check.toggled.connect(self._on_generation_filter_changed)
        collapsible.content_layout.addWidget(self.gen3_check)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background: rgba(255,255,255,50);")
        collapsible.content_layout.addWidget(separator2)

        # Charge type filter
        charge_label = QLabel("Charge Type:")
        charge_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px; margin-top: 5px;")
        collapsible.content_layout.addWidget(charge_label)

        self.positive_check = QCheckBox("Positive Charge")
        self.positive_check.setChecked(True)
        self.positive_check.setStyleSheet(self._get_checkbox_style())
        self.positive_check.toggled.connect(self._on_charge_filter_changed)
        collapsible.content_layout.addWidget(self.positive_check)

        self.negative_check = QCheckBox("Negative Charge")
        self.negative_check.setChecked(True)
        self.negative_check.setStyleSheet(self._get_checkbox_style())
        self.negative_check.toggled.connect(self._on_charge_filter_changed)
        collapsible.content_layout.addWidget(self.negative_check)

        self.neutral_check = QCheckBox("Neutral")
        self.neutral_check.setChecked(True)
        self.neutral_check.setStyleSheet(self._get_checkbox_style())
        self.neutral_check.toggled.connect(self._on_charge_filter_changed)
        collapsible.content_layout.addWidget(self.neutral_check)

        return collapsible

    def _create_display_options_group(self):
        """Create display options controls"""
        group = QGroupBox("Display Options")
        group.setStyleSheet(self._get_group_style("#4fc3f7"))
        layout = QVBoxLayout()

        # Show antiparticles
        self.antiparticle_check = QCheckBox("Show Antiparticles")
        self.antiparticle_check.setStyleSheet(self._get_checkbox_style())
        self.antiparticle_check.toggled.connect(self._on_antiparticle_toggled)
        layout.addWidget(self.antiparticle_check)

        # Show composite particles
        self.composite_check = QCheckBox("Show Composite Particles")
        self.composite_check.setStyleSheet(self._get_checkbox_style())
        self.composite_check.toggled.connect(self._on_composite_toggled)
        layout.addWidget(self.composite_check)

        # Show connections (for circular mode)
        self.connections_check = QCheckBox("Show Force Connections")
        self.connections_check.setStyleSheet(self._get_checkbox_style())
        self.connections_check.toggled.connect(self._on_connections_toggled)
        layout.addWidget(self.connections_check)

        # Legend info
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background: rgba(40, 40, 60, 150);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setContentsMargins(10, 10, 10, 10)
        legend_layout.setSpacing(5)

        legend_title = QLabel("Particle Types:")
        legend_title.setStyleSheet("color: #4fc3f7; font-size: 10px; font-weight: bold;")
        legend_layout.addWidget(legend_title)

        type_colors = [
            ("Quarks", "#e66464"),
            ("Leptons", "#64b4e6"),
            ("Gauge Bosons", "#e6b464"),
            ("Scalar Boson", "#b464e6")
        ]

        for name, color in type_colors:
            item_layout = QHBoxLayout()
            color_box = QLabel()
            color_box.setFixedSize(12, 12)
            color_box.setStyleSheet(f"background: {color}; border-radius: 2px;")
            item_layout.addWidget(color_box)

            name_label = QLabel(name)
            name_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px;")
            item_layout.addWidget(name_label)
            item_layout.addStretch()

            legend_layout.addLayout(item_layout)

        layout.addWidget(legend_frame)

        group.setLayout(layout)
        return group

    def _create_data_management_group(self):
        """Create data management controls group"""
        group = QGroupBox("Data Management")
        group.setStyleSheet(self._get_group_style("#26a69a"))
        layout = QVBoxLayout()

        # Buttons row
        btn_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                background: rgba(38, 166, 154, 150);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(38, 166, 154, 200);
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 100);
                color: rgba(255, 255, 255, 100);
            }
        """

        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(button_style)
        self.add_btn.clicked.connect(self.add_requested.emit)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet(button_style)
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_requested.emit)
        btn_layout.addWidget(self.edit_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setStyleSheet(button_style)
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_requested.emit)
        btn_layout.addWidget(self.remove_btn)

        layout.addLayout(btn_layout)

        # Reset button
        self.reset_data_btn = QPushButton("Reset to Defaults")
        self.reset_data_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #ef5350, stop:1 #e53935);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #f44336, stop:1 #d32f2f);
            }
        """)
        self.reset_data_btn.clicked.connect(self.reset_requested.emit)
        layout.addWidget(self.reset_data_btn)

        # Item count label
        self.item_count_label = QLabel("Items: 0")
        self.item_count_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 10px; margin-top: 5px;")
        layout.addWidget(self.item_count_label)

        group.setLayout(layout)
        return group

    def _on_layout_changed(self, mode):
        """Handle layout mode change"""
        self.table.set_layout_mode(mode)
        # Show/hide sort controls
        self.sort_container.setVisible(mode == QuarkLayoutMode.LINEAR)

    def _on_sort_changed(self, index):
        """Handle sort property change"""
        props = ['mass', 'charge', 'spin', 'generation', 'name']
        if index < len(props):
            self.table.set_order_property(props[index])

    def _on_classification_filter_changed(self):
        """Handle classification filter change"""
        if hasattr(self.table, 'set_classification_filter'):
            filters = {
                'quark': self.quark_check.isChecked(),
                'lepton': self.lepton_check.isChecked(),
                'boson': self.boson_check.isChecked()
            }
            self.table.set_classification_filter(filters)
        self.table.update()

    def _on_generation_filter_changed(self):
        """Handle generation filter change"""
        if hasattr(self.table, 'set_generation_filter'):
            filters = {
                1: self.gen1_check.isChecked(),
                2: self.gen2_check.isChecked(),
                3: self.gen3_check.isChecked()
            }
            self.table.set_generation_filter(filters)
        self.table.update()

    def _on_charge_filter_changed(self):
        """Handle charge type filter change"""
        if hasattr(self.table, 'set_charge_filter'):
            filters = {
                'positive': self.positive_check.isChecked(),
                'negative': self.negative_check.isChecked(),
                'neutral': self.neutral_check.isChecked()
            }
            self.table.set_charge_filter(filters)
        self.table.update()

    def _reset_visual_encodings(self):
        """Reset all visual property encodings to defaults"""
        # Reset fill color to Mass
        self.fill_color_control.property_combo.setCurrentIndex(0)
        # Reset border color to Charge
        self.border_color_control.property_combo.setCurrentIndex(1)
        # Reset glow color to Spin
        self.glow_color_control.property_combo.setCurrentIndex(2)
        # Reset symbol text color to Baryon Number
        self.symbol_text_color_control.property_combo.setCurrentIndex(3)
        self.table.update()

    def _on_antiparticle_toggled(self, checked):
        """Handle antiparticle visibility toggle"""
        self.table.set_show_antiparticles(checked)

    def _on_composite_toggled(self, checked):
        """Handle composite particle visibility toggle"""
        self.table.set_show_composites(checked)

    def _on_connections_toggled(self, checked):
        """Handle connections visibility toggle"""
        self.table.show_connections = checked
        self.table.update()

    def _on_reset_view(self):
        """Reset view to default"""
        self.table.reset_view()

    def set_item_selected(self, selected):
        """Enable/disable edit and remove buttons based on selection state"""
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)

    def update_item_count(self, count):
        """Update the item count label"""
        self.item_count_label.setText(f"Items: {count}")

    def _get_group_style(self, color):
        return f"""
            QGroupBox {{
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """

    def _get_radio_style(self):
        return """
            QRadioButton {
                color: white;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #667eea;
                border-radius: 8px;
                background: rgba(40, 40, 60, 200);
            }
            QRadioButton::indicator:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #667eea, stop:1 rgba(102, 126, 234, 100));
            }
        """

    def _get_combo_style(self):
        return """
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #764ba2;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 10px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #764ba2;
            }
        """

    def _get_checkbox_style(self):
        return """
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #f093fb;
                border-radius: 4px;
                background: rgba(40, 40, 60, 200);
            }
            QCheckBox::indicator:checked {
                background: #f093fb;
            }
        """

    def _get_button_style(self):
        return """
            QPushButton {
                background: rgba(102, 126, 234, 150);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 200);
            }
        """
