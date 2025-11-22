"""
Alloy Control Panel
Provides UI controls for alloy visualization settings with visual property encodings,
filters, and data management - matching the Atoms tab feature set.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QFrame, QSlider, QToolButton, QGridLayout)
from PySide6.QtCore import Qt, QPropertyAnimation, Signal
from PySide6.QtGui import QFont, QColor

from core.alloy_enums import AlloyLayoutMode, AlloyCategory, CrystalStructure, AlloyProperty
from data.data_manager import get_data_manager, DataCategory


class AlloyPropertyControl(QWidget):
    """Expandable control for a single visual property with range controls and filtering for alloys"""
    def __init__(self, title, property_key, parent_panel, available_properties, control_type="color", default_index=0):
        super().__init__()
        self.property_key = property_key
        self.parent_panel = parent_panel
        self.control_type = control_type  # "color" or "size"
        self.is_expanded = False
        self.default_index = default_index
        self.user_selected_index = default_index

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
        self.property_combo.addItems(available_properties)
        self.property_combo.setStyleSheet(self._get_combo_style())
        self.property_combo.currentIndexChanged.connect(self.on_property_selection_changed)
        self.available_properties = available_properties
        header_layout.addWidget(self.property_combo, 1)

        # "Use Default" checkbox
        self.use_default_checkbox = QCheckBox("Default")
        self.use_default_checkbox.setStyleSheet("""
            QCheckBox {
                color: rgba(255,255,255,200);
                font-size: 9px;
                spacing: 3px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #B08264;
                border-radius: 3px;
                background: rgba(40, 40, 60, 150);
            }
            QCheckBox::indicator:checked {
                background: #B08264;
            }
        """)
        self.use_default_checkbox.toggled.connect(self.on_use_default_toggled)
        header_layout.addWidget(self.use_default_checkbox)

        main_layout.addWidget(header)

        # Expandable details area
        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(25, 5, 5, 5)
        details_layout.setSpacing(8)

        # Property mapping label
        mapping_label = QLabel("Property Mapping & Filtering:")
        mapping_label.setStyleSheet("color: rgba(255,255,255,200); font-size: 9px; font-weight: bold;")
        details_layout.addWidget(mapping_label)

        # Min/Max filter sliders
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(5)

        # Min filter
        min_row = QWidget()
        min_layout = QHBoxLayout(min_row)
        min_layout.setContentsMargins(0, 0, 0, 0)
        min_layout.setSpacing(5)
        min_label = QLabel("Min:")
        min_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 30px;")
        min_layout.addWidget(min_label)
        self.min_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_slider.setMinimum(0)
        self.min_slider.setMaximum(1000)
        self.min_slider.setValue(0)
        self.min_slider.setStyleSheet(self._get_slider_style())
        self.min_slider.valueChanged.connect(self.on_filter_range_changed)
        min_layout.addWidget(self.min_slider)
        self.min_display = QLabel("0")
        self.min_display.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 50px;")
        min_layout.addWidget(self.min_display)
        filter_layout.addWidget(min_row)

        # Max filter
        max_row = QWidget()
        max_layout = QHBoxLayout(max_row)
        max_layout.setContentsMargins(0, 0, 0, 0)
        max_layout.setSpacing(5)
        max_label = QLabel("Max:")
        max_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 30px;")
        max_layout.addWidget(max_label)
        self.max_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_slider.setMinimum(0)
        self.max_slider.setMaximum(1000)
        self.max_slider.setValue(1000)
        self.max_slider.setStyleSheet(self._get_slider_style())
        self.max_slider.valueChanged.connect(self.on_filter_range_changed)
        max_layout.addWidget(self.max_slider)
        self.max_display = QLabel("100")
        self.max_display.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px; min-width: 50px;")
        max_layout.addWidget(self.max_display)
        filter_layout.addWidget(max_row)

        details_layout.addWidget(filter_container)

        # Gradient color pickers (for color properties only)
        if self.control_type == "color":
            gradient_container = QWidget()
            gradient_layout = QHBoxLayout(gradient_container)
            gradient_layout.setContentsMargins(0, 5, 0, 0)
            gradient_layout.setSpacing(10)

            gradient_label = QLabel("Gradient:")
            gradient_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 9px;")
            gradient_layout.addWidget(gradient_label)

            self.start_color_btn = QPushButton()
            self.start_color_btn.setFixedSize(24, 24)
            self.start_color_btn.setStyleSheet("background: #4080FF; border: 2px solid white; border-radius: 3px;")
            self.start_color_btn.clicked.connect(lambda: self.pick_gradient_color("start"))
            gradient_layout.addWidget(self.start_color_btn)

            arrow_label = QLabel("->")
            arrow_label.setStyleSheet("color: rgba(255,255,255,150); font-size: 9px;")
            gradient_layout.addWidget(arrow_label)

            self.end_color_btn = QPushButton()
            self.end_color_btn.setFixedSize(24, 24)
            self.end_color_btn.setStyleSheet("background: #FF8040; border: 2px solid white; border-radius: 3px;")
            self.end_color_btn.clicked.connect(lambda: self.pick_gradient_color("end"))
            gradient_layout.addWidget(self.end_color_btn)

            gradient_layout.addStretch()
            details_layout.addWidget(gradient_container)

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

        # Initialize values
        self.data_min = 0
        self.data_max = 100
        self.data_unit = ""
        self.current_property_name = "none"
        self.gradient_start_color = QColor(64, 128, 255)
        self.gradient_end_color = QColor(255, 128, 64)

    def pick_gradient_color(self, which):
        """Open color picker for gradient start or end"""
        from PySide6.QtWidgets import QColorDialog
        current = self.gradient_start_color if which == "start" else self.gradient_end_color
        color = QColorDialog.getColor(current, self, f"Choose Gradient {which.title()} Color")
        if color.isValid():
            if which == "start":
                self.gradient_start_color = color
                self.start_color_btn.setStyleSheet(f"background: {color.name()}; border: 2px solid white; border-radius: 3px;")
            else:
                self.gradient_end_color = color
                self.end_color_btn.setStyleSheet(f"background: {color.name()}; border: 2px solid white; border-radius: 3px;")
            self.parent_panel.on_gradient_color_changed(self.property_key, self.gradient_start_color, self.gradient_end_color)

    def on_property_selection_changed(self, idx):
        """Handle property selection change"""
        property_name = self.available_properties[idx]
        self.current_property_name = property_name

        # Get property metadata for setting slider ranges
        metadata = self._get_property_metadata(property_name)
        if metadata:
            self.data_min = metadata.get("min", 0)
            self.data_max = metadata.get("max", 100)
            self.data_unit = metadata.get("unit", "")

        self.update_filter_displays()
        self.parent_panel.on_property_changed(self.property_key, idx)

    def _get_property_metadata(self, property_name):
        """Get min/max/unit metadata for alloy properties"""
        # Comprehensive property metadata for alloy properties
        metadata = {
            "None": {"min": 0, "max": 100, "unit": ""},
            # Physical Properties
            "Density": {"min": 1.0, "max": 25.0, "unit": "g/cm3"},
            "Melting Point": {"min": 300, "max": 4000, "unit": "K"},
            "Thermal Conductivity": {"min": 5, "max": 500, "unit": "W/m-K"},
            "Thermal Expansion": {"min": 1e-6, "max": 30e-6, "unit": "1/K"},
            "Electrical Resistivity": {"min": 1e-8, "max": 1e-5, "unit": "Ohm-m"},
            "Specific Heat": {"min": 100, "max": 1500, "unit": "J/kg-K"},
            # Mechanical Properties - Strength
            "Tensile Strength": {"min": 50, "max": 3000, "unit": "MPa"},
            "Yield Strength": {"min": 20, "max": 2500, "unit": "MPa"},
            "Fatigue Strength": {"min": 50, "max": 1500, "unit": "MPa"},
            # Mechanical Properties - Hardness
            "Hardness": {"min": 10, "max": 800, "unit": "HB"},
            "Hardness (Brinell)": {"min": 10, "max": 800, "unit": "HB"},
            "Hardness (Vickers)": {"min": 50, "max": 2000, "unit": "HV"},
            "Hardness (Rockwell)": {"min": 10, "max": 70, "unit": "HRC"},
            # Mechanical Properties - Ductility
            "Elongation": {"min": 0, "max": 80, "unit": "%"},
            "Reduction of Area": {"min": 0, "max": 90, "unit": "%"},
            "Impact Strength": {"min": 5, "max": 300, "unit": "J"},
            "Fracture Toughness": {"min": 10, "max": 200, "unit": "MPa-m^0.5"},
            # Mechanical Properties - Stiffness
            "Young's Modulus": {"min": 10, "max": 500, "unit": "GPa"},
            "Shear Modulus": {"min": 10, "max": 200, "unit": "GPa"},
            "Poisson's Ratio": {"min": 0.2, "max": 0.5, "unit": ""},
            # Corrosion Properties
            "Corrosion Resistance": {"min": 0, "max": 100, "unit": ""},
            "PREN": {"min": 0, "max": 50, "unit": ""},
            "Pitting Potential": {"min": -500, "max": 1000, "unit": "mV"},
            # Economic Properties
            "Cost per kg": {"min": 0.5, "max": 1000, "unit": "$/kg"},
            # Lattice Properties
            "Lattice Parameter": {"min": 200, "max": 500, "unit": "pm"},
            "Packing Factor": {"min": 0.5, "max": 0.8, "unit": ""},
        }
        return metadata.get(property_name, {"min": 0, "max": 100, "unit": ""})

    def on_filter_range_changed(self):
        """Handle filter range slider changes"""
        self.update_filter_displays()
        # Apply filter to table
        min_val = self.data_min + (self.min_slider.value() / 1000.0) * (self.data_max - self.data_min)
        max_val = self.data_min + (self.max_slider.value() / 1000.0) * (self.data_max - self.data_min)
        self.parent_panel.on_filter_range_changed(self.property_key, min_val, max_val)

    def update_filter_displays(self):
        """Update the filter display labels"""
        min_val = self.data_min + (self.min_slider.value() / 1000.0) * (self.data_max - self.data_min)
        max_val = self.data_min + (self.max_slider.value() / 1000.0) * (self.data_max - self.data_min)

        if abs(self.data_max) > 1000:
            self.min_display.setText(f"{min_val:.0f}")
            self.max_display.setText(f"{max_val:.0f}")
        elif abs(self.data_max) < 1:
            self.min_display.setText(f"{min_val:.2e}")
            self.max_display.setText(f"{max_val:.2e}")
        else:
            self.min_display.setText(f"{min_val:.1f}")
            self.max_display.setText(f"{max_val:.1f}")

    def on_fade_changed(self, value):
        """Handle fade slider change"""
        self.fade_display.setText(f"{value}%")
        self.parent_panel.on_fade_changed(self.property_key, value / 100.0)

    def toggle_expanded(self):
        """Toggle expanded/collapsed state"""
        self.is_expanded = not self.is_expanded
        self.expand_btn.setArrowType(Qt.ArrowType.DownArrow if self.is_expanded else Qt.ArrowType.RightArrow)
        self.details_widget.setVisible(self.is_expanded)

    def on_use_default_toggled(self, checked):
        """Toggle using default value for this property"""
        self.property_combo.setEnabled(not checked)
        if checked:
            self.user_selected_index = self.property_combo.currentIndex()
            self.property_combo.blockSignals(True)
            self.property_combo.setCurrentIndex(self.default_index)
            self.property_combo.blockSignals(False)
            self.on_property_selection_changed(self.default_index)
        else:
            self.property_combo.blockSignals(True)
            self.property_combo.setCurrentIndex(self.user_selected_index)
            self.property_combo.blockSignals(False)
            self.on_property_selection_changed(self.user_selected_index)

    def _get_combo_style(self):
        return """
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #B08264;
                padding: 3px 5px;
                border-radius: 3px;
                font-size: 9px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #B08264;
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
                background: #B08264;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """


class CollapsibleBox(QWidget):
    """A collapsible widget that can expand/collapse its content"""
    def __init__(self, title="", border_color="#B08264", parent=None):
        super().__init__(parent)

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
            content_height = self.content_area.sizeHint().height()
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(content_height)
            self.toggle_animation.finished.connect(self._on_expand_finished)
            self.toggle_animation.start()
        else:
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
            pass


class AlloyControlPanel(QWidget):
    """Control panel for alloy visualization settings"""

    # Data management signals
    add_requested = Signal()
    edit_requested = Signal()
    remove_requested = Signal()
    reset_requested = Signal()
    create_requested = Signal()

    def __init__(self, table_widget):
        super().__init__()
        self.table = table_widget
        self.setup_ui()

    def setup_ui(self):
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
                background: rgba(176, 130, 100, 150);
                border-radius: 5px;
            }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        title = QLabel("Alloy Controls")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #B08264;")
        layout.addWidget(title)

        # Layout Mode Selection (always expanded)
        layout.addWidget(self._create_layout_mode_group())

        # Visual Property Encodings (collapsible)
        layout.addWidget(self._create_visual_properties_group())

        # Filter Options (collapsible)
        layout.addWidget(self._create_filter_options_group())

        # Scatter Plot Settings (only visible in scatter mode)
        self.scatter_group = self._create_scatter_settings_group()
        layout.addWidget(self.scatter_group)
        self.scatter_group.setVisible(False)

        # View Controls
        layout.addWidget(self._create_view_controls_group())

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
        group.setStyleSheet(self._get_group_style("#B08264"))
        layout = QVBoxLayout()

        self.category_radio = QRadioButton("Category Grid")
        self.scatter_radio = QRadioButton("Property Scatter")
        self.composition_radio = QRadioButton("Composition")
        self.lattice_radio = QRadioButton("Lattice Structure")

        self.category_radio.setChecked(True)

        radio_style = self._get_radio_style()
        for radio in [self.category_radio, self.scatter_radio,
                      self.composition_radio, self.lattice_radio]:
            radio.setStyleSheet(radio_style)
            layout.addWidget(radio)

        self.category_radio.toggled.connect(lambda: self._on_layout_changed("category") if self.category_radio.isChecked() else None)
        self.scatter_radio.toggled.connect(lambda: self._on_layout_changed("property_scatter") if self.scatter_radio.isChecked() else None)
        self.composition_radio.toggled.connect(lambda: self._on_layout_changed("composition") if self.composition_radio.isChecked() else None)
        self.lattice_radio.toggled.connect(lambda: self._on_layout_changed("lattice") if self.lattice_radio.isChecked() else None)

        group.setLayout(layout)
        return group

    def _create_visual_properties_group(self):
        """Create visual property encodings with expandable controls"""
        collapsible = CollapsibleBox("Visual Property Encodings", "#B08264")

        # Comprehensive property options for alloys - matching element tab feature set
        color_properties = [
            "None",
            # Physical Properties
            "Density", "Melting Point", "Thermal Conductivity", "Thermal Expansion",
            "Electrical Resistivity", "Specific Heat",
            # Mechanical Properties - Strength
            "Tensile Strength", "Yield Strength", "Fatigue Strength",
            # Mechanical Properties - Hardness
            "Hardness (Brinell)", "Hardness (Vickers)", "Hardness (Rockwell)",
            # Mechanical Properties - Ductility
            "Elongation", "Reduction of Area", "Impact Strength", "Fracture Toughness",
            # Mechanical Properties - Stiffness
            "Young's Modulus", "Shear Modulus", "Poisson's Ratio",
            # Corrosion Properties
            "Corrosion Resistance", "PREN", "Pitting Potential",
            # Economic Properties
            "Cost per kg"
        ]

        size_properties = [
            "None",
            "Density", "Hardness (Brinell)", "Hardness (Vickers)",
            "Tensile Strength", "Yield Strength",
            "Young's Modulus", "Shear Modulus", "Melting Point",
            "Elongation", "Impact Strength", "Fracture Toughness",
            "PREN", "Cost per kg"
        ]

        intensity_properties = [
            "None",
            "Tensile Strength", "Yield Strength", "Hardness (Brinell)",
            "Melting Point", "Thermal Conductivity",
            "Corrosion Resistance", "PREN",
            "Fatigue Strength", "Fracture Toughness", "Cost per kg"
        ]

        # 1. Fill Colour -> Density
        self.fill_color_control = AlloyPropertyControl(
            "Fill Colour", "fill_color", self, color_properties,
            control_type="color", default_index=1  # Density
        )
        self.fill_color_control.property_combo.setCurrentIndex(1)
        collapsible.content_layout.addWidget(self.fill_color_control)

        # 2. Border Colour -> Melting Point
        self.border_color_control = AlloyPropertyControl(
            "Border Colour", "border_color", self, color_properties,
            control_type="color", default_index=2  # Melting Point
        )
        self.border_color_control.property_combo.setCurrentIndex(2)
        collapsible.content_layout.addWidget(self.border_color_control)

        # 3. Glow Colour -> Tensile Strength
        self.glow_color_control = AlloyPropertyControl(
            "Glow Colour", "glow_color", self, color_properties,
            control_type="color", default_index=7  # Tensile Strength
        )
        self.glow_color_control.property_combo.setCurrentIndex(7)
        collapsible.content_layout.addWidget(self.glow_color_control)

        # 4. Glow Intensity -> Corrosion Resistance (NEW)
        self.glow_intensity_control = AlloyPropertyControl(
            "Glow Intensity", "glow_intensity", self, intensity_properties,
            control_type="size", default_index=6  # Corrosion Resistance
        )
        self.glow_intensity_control.property_combo.setCurrentIndex(6)
        collapsible.content_layout.addWidget(self.glow_intensity_control)

        # 5. Symbol Text Colour -> Young's Modulus
        self.symbol_text_color_control = AlloyPropertyControl(
            "Symbol Text Colour", "symbol_text_color", self, color_properties,
            control_type="color", default_index=17  # Young's Modulus
        )
        self.symbol_text_color_control.property_combo.setCurrentIndex(17)
        collapsible.content_layout.addWidget(self.symbol_text_color_control)

        # 6. Border Size -> Hardness (Brinell)
        self.border_size_control = AlloyPropertyControl(
            "Border Size", "border_size", self, size_properties,
            control_type="size", default_index=2  # Hardness (Brinell)
        )
        self.border_size_control.property_combo.setCurrentIndex(2)
        collapsible.content_layout.addWidget(self.border_size_control)

        # 7. Card Size -> Yield Strength (NEW)
        self.card_size_control = AlloyPropertyControl(
            "Card Size", "card_size", self, size_properties,
            control_type="size", default_index=4  # Yield Strength
        )
        self.card_size_control.property_combo.setCurrentIndex(4)
        collapsible.content_layout.addWidget(self.card_size_control)

        # Reset button to restore default mappings
        reset_button = QPushButton("Reset Property Mappings")
        reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #B08264, stop:1 #8B6547);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #C09274, stop:1 #9B7557);
            }
        """)
        reset_button.clicked.connect(self.reset_property_mappings)
        collapsible.content_layout.addWidget(reset_button)

        # Open by default
        collapsible.toggle_button.setChecked(True)
        collapsible.on_toggle()

        return collapsible

    def _create_filter_options_group(self):
        """Create filter options with category, crystal structure, and corrosion filters"""
        collapsible = CollapsibleBox("Filter Options", "#607D8B")

        # Category Filter Section
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px; margin-top: 5px;")
        collapsible.content_layout.addWidget(category_label)

        category_grid = QWidget()
        category_layout = QGridLayout(category_grid)
        category_layout.setContentsMargins(10, 5, 5, 10)
        category_layout.setSpacing(5)

        self.category_checkboxes = {}
        categories = ["Steel", "Aluminum", "Copper", "Titanium", "Nickel", "Precious"]
        checkbox_style = self._get_checkbox_style("#607D8B")

        for i, cat in enumerate(categories):
            cb = QCheckBox(cat)
            cb.setChecked(True)
            cb.setStyleSheet(checkbox_style)
            cb.stateChanged.connect(self._on_category_filter_changed)
            self.category_checkboxes[cat] = cb
            category_layout.addWidget(cb, i // 3, i % 3)

        collapsible.content_layout.addWidget(category_grid)

        # Select All / Clear All for categories
        cat_btn_row = QWidget()
        cat_btn_layout = QHBoxLayout(cat_btn_row)
        cat_btn_layout.setContentsMargins(10, 0, 5, 10)
        cat_btn_layout.setSpacing(5)

        select_all_cat = QPushButton("Select All")
        select_all_cat.setStyleSheet(self._get_small_button_style())
        select_all_cat.clicked.connect(lambda: self._set_all_category_checkboxes(True))
        cat_btn_layout.addWidget(select_all_cat)

        clear_all_cat = QPushButton("Clear All")
        clear_all_cat.setStyleSheet(self._get_small_button_style())
        clear_all_cat.clicked.connect(lambda: self._set_all_category_checkboxes(False))
        cat_btn_layout.addWidget(clear_all_cat)

        cat_btn_layout.addStretch()
        collapsible.content_layout.addWidget(cat_btn_row)

        # Crystal Structure Filter Section
        structure_label = QLabel("Crystal Structure:")
        structure_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px; margin-top: 5px;")
        collapsible.content_layout.addWidget(structure_label)

        structure_grid = QWidget()
        structure_layout = QHBoxLayout(structure_grid)
        structure_layout.setContentsMargins(10, 5, 5, 10)
        structure_layout.setSpacing(10)

        self.structure_checkboxes = {}
        structures = ["FCC", "BCC", "HCP"]
        structure_colors = {"FCC": "#4CAF50", "BCC": "#2196F3", "HCP": "#9C27B0"}

        for struct in structures:
            cb = QCheckBox(struct)
            cb.setChecked(True)
            cb.setStyleSheet(self._get_checkbox_style(structure_colors.get(struct, "#607D8B")))
            cb.stateChanged.connect(self._on_structure_filter_changed)
            self.structure_checkboxes[struct] = cb
            structure_layout.addWidget(cb)

        structure_layout.addStretch()
        collapsible.content_layout.addWidget(structure_grid)

        # Corrosion Rating Filter Section
        corrosion_label = QLabel("Corrosion Resistance:")
        corrosion_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px; margin-top: 5px;")
        collapsible.content_layout.addWidget(corrosion_label)

        corrosion_grid = QWidget()
        corrosion_layout = QHBoxLayout(corrosion_grid)
        corrosion_layout.setContentsMargins(10, 5, 5, 10)
        corrosion_layout.setSpacing(10)

        self.corrosion_checkboxes = {}
        ratings = ["Excellent", "Good", "Moderate", "Poor"]
        rating_colors = {"Excellent": "#4CAF50", "Good": "#8BC34A", "Moderate": "#FF9800", "Poor": "#F44336"}

        for rating in ratings:
            cb = QCheckBox(rating)
            cb.setChecked(True)
            cb.setStyleSheet(self._get_checkbox_style(rating_colors.get(rating, "#607D8B")))
            cb.stateChanged.connect(self._on_corrosion_filter_changed)
            self.corrosion_checkboxes[rating] = cb
            corrosion_layout.addWidget(cb)

        collapsible.content_layout.addWidget(corrosion_grid)

        # Clear all filters button
        clear_filters_btn = QPushButton("Clear All Filters")
        clear_filters_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 87, 34, 180);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: rgba(255, 87, 34, 220);
            }
        """)
        clear_filters_btn.clicked.connect(self._on_clear_filters)
        collapsible.content_layout.addWidget(clear_filters_btn)

        return collapsible

    def _create_scatter_settings_group(self):
        """Create scatter plot settings group"""
        group = QGroupBox("Property Axes")
        group.setStyleSheet(self._get_group_style("#FF9800"))
        layout = QVBoxLayout()

        # X axis property
        x_label = QLabel("X Axis:")
        x_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(x_label)
        self.x_prop_combo = QComboBox()
        for prop in AlloyProperty.get_scatter_x_properties():
            self.x_prop_combo.addItem(AlloyProperty.get_display_name(prop), prop.value)
        self.x_prop_combo.setStyleSheet(self._get_combo_style())
        self.x_prop_combo.currentIndexChanged.connect(self._on_scatter_prop_changed)
        layout.addWidget(self.x_prop_combo)

        # Y axis property
        y_label = QLabel("Y Axis:")
        y_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(y_label)
        self.y_prop_combo = QComboBox()
        for prop in AlloyProperty.get_scatter_y_properties():
            self.y_prop_combo.addItem(AlloyProperty.get_display_name(prop), prop.value)
        self.y_prop_combo.setCurrentIndex(0)
        self.y_prop_combo.setStyleSheet(self._get_combo_style())
        self.y_prop_combo.currentIndexChanged.connect(self._on_scatter_prop_changed)
        layout.addWidget(self.y_prop_combo)

        group.setLayout(layout)
        return group

    def _create_view_controls_group(self):
        """Create view control buttons"""
        group = QGroupBox("View Controls")
        group.setStyleSheet(self._get_group_style("#9C27B0"))
        layout = QVBoxLayout()

        # Reset view button
        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #B08264, stop:1 #8B6547);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #C09274, stop:1 #9B7557);
            }
        """)
        reset_btn.clicked.connect(self._on_reset_view)
        layout.addWidget(reset_btn)

        # Info label
        info_label = QLabel("Scroll to navigate\nCtrl+Scroll to zoom")
        info_label.setStyleSheet("color: rgba(255,255,255,150); font-size: 9px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

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

        # Create from Elements button
        self.create_btn = QPushButton("Create from Elements")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B08264, stop:1 #8B6547);
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B6547, stop:1 #B08264);
            }
        """)
        self.create_btn.clicked.connect(self.create_requested.emit)
        layout.addWidget(self.create_btn)

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

    # Event handlers
    def _on_layout_changed(self, mode):
        """Handle layout mode change"""
        self.table.set_layout_mode(mode)
        # Show/hide scatter settings
        self.scatter_group.setVisible(mode == "property_scatter")

    def _on_category_filter_changed(self, state):
        """Handle category filter checkbox change"""
        selected = [cat for cat, cb in self.category_checkboxes.items() if cb.isChecked()]
        if hasattr(self.table, 'set_category_filters'):
            self.table.set_category_filters(selected)
        self.table.update()

    def _on_structure_filter_changed(self, state):
        """Handle structure filter checkbox change"""
        selected = [struct for struct, cb in self.structure_checkboxes.items() if cb.isChecked()]
        if hasattr(self.table, 'set_structure_filters'):
            self.table.set_structure_filters(selected)
        self.table.update()

    def _on_corrosion_filter_changed(self, state):
        """Handle corrosion rating filter checkbox change"""
        selected = [rating for rating, cb in self.corrosion_checkboxes.items() if cb.isChecked()]
        if hasattr(self.table, 'set_corrosion_filters'):
            self.table.set_corrosion_filters(selected)
        self.table.update()

    def _set_all_category_checkboxes(self, checked):
        """Set all category checkboxes to checked/unchecked"""
        for cb in self.category_checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(checked)
            cb.blockSignals(False)
        self._on_category_filter_changed(0)

    def _on_scatter_prop_changed(self):
        """Handle scatter property change"""
        x_prop = self.x_prop_combo.currentData()
        y_prop = self.y_prop_combo.currentData()
        self.table.set_scatter_properties(x_prop, y_prop)

    def _on_reset_view(self):
        """Reset view to defaults"""
        self.table.reset_view()

    def _on_clear_filters(self):
        """Clear all filters"""
        # Reset category checkboxes
        for cb in self.category_checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)

        # Reset structure checkboxes
        for cb in self.structure_checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)

        # Reset corrosion checkboxes
        for cb in self.corrosion_checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)

        # Apply changes
        self._on_category_filter_changed(0)
        self._on_structure_filter_changed(0)
        self._on_corrosion_filter_changed(0)

    # Property control callbacks
    def on_property_changed(self, property_key, index):
        """Handle property selection change from AlloyPropertyControl"""
        if hasattr(self.table, 'set_visual_property'):
            property_map = {
                "fill_color": "fill_property",
                "border_color": "border_color_property",
                "glow_color": "glow_property",
                "glow_intensity": "glow_intensity_property",
                "symbol_text_color": "symbol_text_color_property",
                "border_size": "border_size_property",
                "card_size": "card_size_property"
            }
            attr_name = property_map.get(property_key)
            if attr_name:
                # Get the property name from the control
                control = getattr(self, f"{property_key}_control", None)
                if control:
                    prop_name = control.available_properties[index]
                    setattr(self.table, attr_name, prop_name)
                    self.table.update()

    def on_filter_range_changed(self, property_key, min_val, max_val):
        """Handle filter range change from AlloyPropertyControl"""
        if hasattr(self.table, 'set_property_filter'):
            self.table.set_property_filter(property_key, min_val, max_val)
            self.table.update()

    def on_gradient_color_changed(self, property_key, start_color, end_color):
        """Handle gradient color change from AlloyPropertyControl"""
        if hasattr(self.table, 'set_gradient_colors'):
            self.table.set_gradient_colors(property_key, start_color, end_color)
            self.table.update()

    def on_fade_changed(self, property_key, fade_value):
        """Handle fade change from AlloyPropertyControl"""
        if hasattr(self.table, 'set_property_fade'):
            self.table.set_property_fade(property_key, fade_value)
            self.table.update()

    def reset_property_mappings(self):
        """Reset all property controls to their default mappings"""
        # Reset fill color -> Density
        self.fill_color_control.property_combo.setCurrentIndex(1)

        # Reset border color -> Melting Point
        self.border_color_control.property_combo.setCurrentIndex(2)

        # Reset glow color -> Tensile Strength
        self.glow_color_control.property_combo.setCurrentIndex(7)

        # Reset glow intensity -> Corrosion Resistance
        self.glow_intensity_control.property_combo.setCurrentIndex(6)

        # Reset symbol text color -> Young's Modulus
        self.symbol_text_color_control.property_combo.setCurrentIndex(17)

        # Reset border size -> Hardness (Brinell)
        self.border_size_control.property_combo.setCurrentIndex(2)

        # Reset card size -> Yield Strength
        self.card_size_control.property_combo.setCurrentIndex(4)

        self.table.update()

    # Style helpers
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
                border: 2px solid #B08264;
                border-radius: 8px;
                background: rgba(40, 40, 60, 200);
            }
            QRadioButton::indicator:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #B08264, stop:1 rgba(176, 130, 100, 100));
            }
        """

    def _get_combo_style(self):
        return """
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #8B6547;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 11px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #8B6547;
            }
        """

    def _get_checkbox_style(self, color):
        return f"""
            QCheckBox {{
                color: white;
                spacing: 5px;
                font-size: 10px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 2px solid {color};
                border-radius: 3px;
                background: rgba(40, 40, 60, 200);
            }}
            QCheckBox::indicator:checked {{
                background: {color};
            }}
        """

    def _get_small_button_style(self):
        return """
            QPushButton {
                background: rgba(100, 100, 120, 150);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
            }
            QPushButton:hover {
                background: rgba(120, 120, 140, 180);
            }
        """

    # Public interface methods
    def set_item_selected(self, selected):
        """Enable/disable edit and remove buttons based on selection state"""
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)

    def update_item_count(self, count):
        """Update the item count label"""
        self.item_count_label.setText(f"Items: {count}")
