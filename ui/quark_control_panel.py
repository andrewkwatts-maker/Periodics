#!/usr/bin/env python3
"""
Quark Control Panel
Provides UI controls for particle visualization settings.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.quark_enums import QuarkLayoutMode, QuarkProperty
from data.data_manager import get_data_manager, DataCategory


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

        # Visual Property Encodings
        layout.addWidget(self._create_visual_properties_group())

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
        self.standard_radio.setStyleSheet(radio_style)
        self.linear_radio.setStyleSheet(radio_style)
        self.circular_radio.setStyleSheet(radio_style)
        self.alternative_radio.setStyleSheet(radio_style)
        self.force_network_radio.setStyleSheet(radio_style)
        self.mass_spiral_radio.setStyleSheet(radio_style)
        self.fermion_boson_radio.setStyleSheet(radio_style)
        self.charge_mass_radio.setStyleSheet(radio_style)

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
        """Create visual property encoding controls"""
        group = QGroupBox("Visual Encodings")
        group.setStyleSheet(self._get_group_style("#764ba2"))
        layout = QVBoxLayout()

        # Fill Color property
        fill_layout = QHBoxLayout()
        fill_label = QLabel("Fill Color:")
        fill_label.setStyleSheet("color: white; font-size: 10px; min-width: 80px;")
        fill_layout.addWidget(fill_label)

        self.fill_combo = QComboBox()
        self.fill_combo.addItems([
            "Particle Type", "Mass", "Charge", "Spin",
            "Generation", "Stability", "Interaction"
        ])
        self.fill_combo.setStyleSheet(self._get_combo_style())
        self.fill_combo.currentIndexChanged.connect(self._on_fill_changed)
        fill_layout.addWidget(self.fill_combo)
        layout.addLayout(fill_layout)

        # Border Color property
        border_layout = QHBoxLayout()
        border_label = QLabel("Border Color:")
        border_label.setStyleSheet("color: white; font-size: 10px; min-width: 80px;")
        border_layout.addWidget(border_label)

        self.border_combo = QComboBox()
        self.border_combo.addItems([
            "Charge", "Particle Type", "Mass", "Spin",
            "Generation", "Stability"
        ])
        self.border_combo.setStyleSheet(self._get_combo_style())
        self.border_combo.currentIndexChanged.connect(self._on_border_changed)
        border_layout.addWidget(self.border_combo)
        layout.addLayout(border_layout)

        # Glow Effect property
        glow_layout = QHBoxLayout()
        glow_label = QLabel("Glow Effect:")
        glow_label.setStyleSheet("color: white; font-size: 10px; min-width: 80px;")
        glow_layout.addWidget(glow_label)

        self.glow_combo = QComboBox()
        self.glow_combo.addItems([
            "Mass", "Spin", "Stability", "None"
        ])
        self.glow_combo.setStyleSheet(self._get_combo_style())
        self.glow_combo.currentIndexChanged.connect(self._on_glow_changed)
        glow_layout.addWidget(self.glow_combo)
        layout.addLayout(glow_layout)

        group.setLayout(layout)
        return group

    def _create_display_options_group(self):
        """Create display options controls"""
        group = QGroupBox("Display Options")
        group.setStyleSheet(self._get_group_style("#f093fb"))
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

    def _on_fill_changed(self, index):
        """Handle fill property change"""
        props = ['particle_type', 'mass', 'charge', 'spin', 'generation', 'stability', 'interaction']
        if index < len(props):
            self.table.set_fill_property(props[index])

    def _on_border_changed(self, index):
        """Handle border property change"""
        props = ['charge', 'particle_type', 'mass', 'spin', 'generation', 'stability']
        if index < len(props):
            self.table.set_border_property(props[index])

    def _on_glow_changed(self, index):
        """Handle glow property change"""
        props = ['mass', 'spin', 'stability', 'none']
        if index < len(props):
            self.table.set_glow_property(props[index])

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

    def set_item_selected(self, selected):
        """Enable/disable edit and remove buttons based on selection state"""
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)

    def update_item_count(self, count):
        """Update the item count label"""
        self.item_count_label.setText(f"Items: {count}")
