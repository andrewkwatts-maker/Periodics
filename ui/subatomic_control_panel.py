"""
Control Panel for Subatomic Particles Tab
Provides UI controls for layout mode, property mappings, and filters
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.subatomic_enums import SubatomicLayoutMode, SubatomicProperty, ParticleCategory
from data.data_manager import get_data_manager, DataCategory


class SubatomicControlPanel(QWidget):
    """Control panel for subatomic particle visualization settings"""

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
                background: rgba(79, 195, 247, 150);
                border-radius: 5px;
            }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        title = QLabel("Subatomic Controls")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #4fc3f7;")
        layout.addWidget(title)

        # Layout Mode Selection
        layout.addWidget(self._create_layout_mode_group())

        # Particle Type Filters
        layout.addWidget(self._create_filter_group())

        # Visual Property Encodings
        layout.addWidget(self._create_visual_properties_group())

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
        layout_group = QGroupBox("Layout Mode")
        layout_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #667eea;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout_box = QVBoxLayout()

        radio_style = """
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

        self.baryon_meson_radio = QRadioButton("Baryon/Meson Groups")
        self.baryon_meson_radio.setStyleSheet(radio_style)
        self.baryon_meson_radio.setChecked(True)
        self.baryon_meson_radio.toggled.connect(
            lambda: self._on_layout_changed(SubatomicLayoutMode.BARYON_MESON) if self.baryon_meson_radio.isChecked() else None)

        self.mass_radio = QRadioButton("Mass Order")
        self.mass_radio.setStyleSheet(radio_style)
        self.mass_radio.toggled.connect(
            lambda: self._on_layout_changed(SubatomicLayoutMode.MASS_ORDER) if self.mass_radio.isChecked() else None)

        self.charge_radio = QRadioButton("Charge Order")
        self.charge_radio.setStyleSheet(radio_style)
        self.charge_radio.toggled.connect(
            lambda: self._on_layout_changed(SubatomicLayoutMode.CHARGE_ORDER) if self.charge_radio.isChecked() else None)

        self.decay_radio = QRadioButton("Decay Chains")
        self.decay_radio.setStyleSheet(radio_style)
        self.decay_radio.toggled.connect(
            lambda: self._on_layout_changed(SubatomicLayoutMode.DECAY_CHAIN) if self.decay_radio.isChecked() else None)

        self.quark_radio = QRadioButton("Quark Content")
        self.quark_radio.setStyleSheet(radio_style)
        self.quark_radio.toggled.connect(
            lambda: self._on_layout_changed(SubatomicLayoutMode.QUARK_CONTENT) if self.quark_radio.isChecked() else None)

        layout_box.addWidget(self.baryon_meson_radio)
        layout_box.addWidget(self.mass_radio)
        layout_box.addWidget(self.charge_radio)
        layout_box.addWidget(self.decay_radio)
        layout_box.addWidget(self.quark_radio)

        layout_group.setLayout(layout_box)
        return layout_group

    def _create_filter_group(self):
        """Create particle type filter group"""
        filter_group = QGroupBox("Particle Filters")
        filter_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #764ba2;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()

        checkbox_style = """
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #764ba2;
                border-radius: 4px;
                background: rgba(40, 40, 60, 200);
            }
            QCheckBox::indicator:checked {
                background: #764ba2;
            }
        """

        # Particle type checkboxes
        self.show_baryons_check = QCheckBox("Show Baryons")
        self.show_baryons_check.setStyleSheet(checkbox_style)
        self.show_baryons_check.setChecked(True)
        self.show_baryons_check.toggled.connect(self._on_filter_changed)

        self.show_mesons_check = QCheckBox("Show Mesons")
        self.show_mesons_check.setStyleSheet(checkbox_style)
        self.show_mesons_check.setChecked(True)
        self.show_mesons_check.toggled.connect(self._on_filter_changed)

        layout.addWidget(self.show_baryons_check)
        layout.addWidget(self.show_mesons_check)

        # Charge filter
        charge_layout = QHBoxLayout()
        charge_label = QLabel("Charge Filter:")
        charge_label.setStyleSheet("color: white;")
        charge_layout.addWidget(charge_label)

        self.charge_combo = QComboBox()
        self.charge_combo.addItems(["All", "+2", "+1", "0", "-1"])
        self.charge_combo.setStyleSheet("""
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #764ba2;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #764ba2;
            }
        """)
        self.charge_combo.currentIndexChanged.connect(self._on_charge_filter_changed)
        charge_layout.addWidget(self.charge_combo)

        layout.addLayout(charge_layout)

        filter_group.setLayout(layout)
        return filter_group

    def _create_visual_properties_group(self):
        """Create visual property encoding controls"""
        props_group = QGroupBox("Visual Encodings")
        props_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #f093fb;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()

        combo_style = """
            QComboBox {
                background: rgba(40, 40, 60, 200);
                color: white;
                border: 1px solid #f093fb;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #f093fb;
            }
        """

        # Property options
        property_options = ["Mass", "Charge", "Spin", "Half-Life", "Stability", "None"]

        # Card Color encoding
        color_layout = QHBoxLayout()
        color_label = QLabel("Card Glow:")
        color_label.setStyleSheet("color: white; min-width: 80px;")
        color_layout.addWidget(color_label)

        self.color_combo = QComboBox()
        self.color_combo.addItems(property_options)
        self.color_combo.setCurrentIndex(4)  # Stability
        self.color_combo.setStyleSheet(combo_style)
        self.color_combo.currentIndexChanged.connect(self._on_visual_property_changed)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        # Border encoding
        border_layout = QHBoxLayout()
        border_label = QLabel("Border:")
        border_label.setStyleSheet("color: white; min-width: 80px;")
        border_layout.addWidget(border_label)

        self.border_combo = QComboBox()
        self.border_combo.addItems(property_options)
        self.border_combo.setCurrentIndex(1)  # Charge
        self.border_combo.setStyleSheet(combo_style)
        self.border_combo.currentIndexChanged.connect(self._on_visual_property_changed)
        border_layout.addWidget(self.border_combo)
        layout.addLayout(border_layout)

        # Info text
        info_label = QLabel("Particles are automatically colored by their family type (Delta, Sigma, Pion, etc.)")
        info_label.setStyleSheet("color: rgba(255,255,255,150); font-size: 9px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        props_group.setLayout(layout)
        return props_group

    def _create_view_controls_group(self):
        """Create view control buttons"""
        view_group = QGroupBox("View Controls")
        view_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #4fc3f7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()

        button_style = """
            QPushButton {
                background: rgba(79, 195, 247, 150);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 200);
            }
        """

        # Reset view button
        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet(button_style)
        reset_btn.clicked.connect(self._on_reset_view)
        layout.addWidget(reset_btn)

        # Zoom info
        zoom_info = QLabel("Scroll: Zoom\nMiddle-click: Pan")
        zoom_info.setStyleSheet("color: rgba(255,255,255,150); font-size: 9px;")
        layout.addWidget(zoom_info)

        view_group.setLayout(layout)
        return view_group

    def _on_layout_changed(self, mode):
        """Handle layout mode change"""
        self.table.set_layout_mode(mode)

    def _on_filter_changed(self):
        """Handle filter checkbox change"""
        self.table.set_filter(
            show_baryons=self.show_baryons_check.isChecked(),
            show_mesons=self.show_mesons_check.isChecked(),
            charge=self._get_charge_filter()
        )

    def _on_charge_filter_changed(self, index):
        """Handle charge filter combo change"""
        self.table.set_filter(
            show_baryons=self.show_baryons_check.isChecked(),
            show_mesons=self.show_mesons_check.isChecked(),
            charge=self._get_charge_filter()
        )

    def _get_charge_filter(self):
        """Get current charge filter value"""
        charge_text = self.charge_combo.currentText()
        if charge_text == "All":
            return None
        elif charge_text == "+2":
            return 2
        elif charge_text == "+1":
            return 1
        elif charge_text == "0":
            return 0
        elif charge_text == "-1":
            return -1
        return None

    def _on_visual_property_changed(self):
        """Handle visual property encoding change"""
        # Update table visual properties
        glow_text = self.color_combo.currentText().lower().replace("-", "_")
        border_text = self.border_combo.currentText().lower().replace("-", "_")

        self.table.glow_property = SubatomicProperty.from_string(glow_text)
        self.table.border_property = SubatomicProperty.from_string(border_text)
        self.table.update()

    def _on_reset_view(self):
        """Reset view to default"""
        self.table.reset_view()

    def _create_data_management_group(self):
        """Create data management controls group"""
        group = QGroupBox("Data Management")
        group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #26a69a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
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

        # Create button (for creating from sub-components)
        self.create_btn = QPushButton("Create from Quarks")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #764ba2, stop:1 #667eea);
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

    def set_item_selected(self, selected):
        """Enable/disable edit and remove buttons based on selection state"""
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)

    def update_item_count(self, count):
        """Update the item count label"""
        self.item_count_label.setText(f"Items: {count}")
