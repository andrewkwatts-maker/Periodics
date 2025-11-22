"""
Alloy Control Panel
Provides UI controls for alloy visualization settings.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.alloy_enums import AlloyLayoutMode, AlloyCategory, CrystalStructure, AlloyProperty
from data.data_manager import get_data_manager, DataCategory


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

        # Layout Mode Selection
        layout.addWidget(self._create_layout_mode_group())

        # Category Filter
        layout.addWidget(self._create_category_filter_group())

        # Structure Filter
        layout.addWidget(self._create_structure_filter_group())

        # Primary Element Filter
        layout.addWidget(self._create_element_filter_group())

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

        self.category_radio = QRadioButton("By Category")
        self.scatter_radio = QRadioButton("Property Plot")
        self.composition_radio = QRadioButton("By Primary Element")
        self.lattice_radio = QRadioButton("By Crystal Structure")

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

    def _create_category_filter_group(self):
        """Create category filter group"""
        group = QGroupBox("Category Filter")
        group.setStyleSheet(self._get_group_style("#607D8B"))
        layout = QVBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories", None)

        # Add standard categories
        for cat in ['Steel', 'Aluminum', 'Bronze', 'Brass', 'Copper',
                    'Titanium', 'Nickel', 'Superalloy', 'Precious', 'Solder']:
            self.category_combo.addItem(cat, cat)

        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)

        layout.addWidget(self.category_combo)
        group.setLayout(layout)
        return group

    def _create_structure_filter_group(self):
        """Create crystal structure filter group"""
        group = QGroupBox("Crystal Structure")
        group.setStyleSheet(self._get_group_style("#4CAF50"))
        layout = QVBoxLayout()

        self.structure_combo = QComboBox()
        self.structure_combo.addItem("All Structures", None)

        for struct in ['FCC', 'BCC', 'HCP', 'BCT', 'Mixed']:
            color = CrystalStructure.get_color(struct)
            self.structure_combo.addItem(struct, struct)

        self.structure_combo.setStyleSheet(self._get_combo_style())
        self.structure_combo.currentIndexChanged.connect(self._on_structure_changed)

        layout.addWidget(self.structure_combo)
        group.setLayout(layout)
        return group

    def _create_element_filter_group(self):
        """Create primary element filter group"""
        group = QGroupBox("Primary Element")
        group.setStyleSheet(self._get_group_style("#2196F3"))
        layout = QVBoxLayout()

        self.element_combo = QComboBox()
        self.element_combo.addItem("All Elements", None)

        # Common base elements
        for elem in ['Fe', 'Al', 'Cu', 'Ti', 'Ni', 'Sn', 'Ag', 'Au']:
            self.element_combo.addItem(elem, elem)

        self.element_combo.setStyleSheet(self._get_combo_style())
        self.element_combo.currentIndexChanged.connect(self._on_element_changed)

        layout.addWidget(self.element_combo)
        group.setLayout(layout)
        return group

    def _create_scatter_settings_group(self):
        """Create scatter plot settings group"""
        group = QGroupBox("Property Axes")
        group.setStyleSheet(self._get_group_style("#FF9800"))
        layout = QVBoxLayout()

        # X axis property
        layout.addWidget(QLabel("X Axis:"))
        self.x_prop_combo = QComboBox()
        for prop in AlloyProperty.get_scatter_x_properties():
            self.x_prop_combo.addItem(AlloyProperty.get_display_name(prop), prop.value)
        self.x_prop_combo.setStyleSheet(self._get_combo_style())
        self.x_prop_combo.currentIndexChanged.connect(self._on_scatter_prop_changed)
        layout.addWidget(self.x_prop_combo)

        # Y axis property
        layout.addWidget(QLabel("Y Axis:"))
        self.y_prop_combo = QComboBox()
        for prop in AlloyProperty.get_scatter_y_properties():
            self.y_prop_combo.addItem(AlloyProperty.get_display_name(prop), prop.value)
        self.y_prop_combo.setCurrentIndex(0)  # Default to tensile strength
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

        # Clear filters button
        clear_btn = QPushButton("Clear All Filters")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 87, 34, 180);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 87, 34, 220);
            }
        """)
        clear_btn.clicked.connect(self._on_clear_filters)
        layout.addWidget(clear_btn)

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

        # Create button (for creating from elements)
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

    def _on_layout_changed(self, mode):
        """Handle layout mode change"""
        self.table.set_layout_mode(mode)
        # Show/hide scatter settings
        self.scatter_group.setVisible(mode == "property_scatter")

    def _on_category_changed(self, index):
        """Handle category filter change"""
        category = self.category_combo.itemData(index)
        self.table.set_category_filter(category)

    def _on_structure_changed(self, index):
        """Handle structure filter change"""
        structure = self.structure_combo.itemData(index)
        self.table.set_structure_filter(structure)

    def _on_element_changed(self, index):
        """Handle element filter change"""
        element = self.element_combo.itemData(index)
        self.table.set_element_filter(element)

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
        self.category_combo.setCurrentIndex(0)
        self.structure_combo.setCurrentIndex(0)
        self.element_combo.setCurrentIndex(0)

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

    def set_item_selected(self, selected):
        """Enable/disable edit and remove buttons based on selection state"""
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)

    def update_item_count(self, count):
        """Update the item count label"""
        self.item_count_label.setText(f"Items: {count}")
