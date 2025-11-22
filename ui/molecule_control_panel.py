"""
Molecule Control Panel
Provides UI controls for molecule visualization settings.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                                QScrollArea, QRadioButton, QComboBox, QCheckBox,
                                QPushButton, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.molecule_enums import MoleculeLayoutMode, MoleculeCategory, MoleculePolarity, MoleculeState


class MoleculeControlPanel(QWidget):
    """Control panel for molecule visualization settings"""

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

        title = QLabel("Molecule Controls")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #4fc3f7;")
        layout.addWidget(title)

        # Layout Mode Selection
        layout.addWidget(self._create_layout_mode_group())

        # Category Filter
        layout.addWidget(self._create_category_filter_group())

        # Polarity Filter
        layout.addWidget(self._create_polarity_filter_group())

        # State Filter
        layout.addWidget(self._create_state_filter_group())

        # View Controls
        layout.addWidget(self._create_view_controls_group())

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

        self.grid_radio = QRadioButton("Grid View")
        self.mass_radio = QRadioButton("Mass Order")
        self.polarity_radio = QRadioButton("By Polarity")
        self.bond_radio = QRadioButton("By Bond Type")
        self.geometry_radio = QRadioButton("By Geometry")

        self.grid_radio.setChecked(True)

        radio_style = self._get_radio_style()
        for radio in [self.grid_radio, self.mass_radio, self.polarity_radio,
                      self.bond_radio, self.geometry_radio]:
            radio.setStyleSheet(radio_style)
            layout.addWidget(radio)

        self.grid_radio.toggled.connect(lambda: self._on_layout_changed("grid") if self.grid_radio.isChecked() else None)
        self.mass_radio.toggled.connect(lambda: self._on_layout_changed("mass_order") if self.mass_radio.isChecked() else None)
        self.polarity_radio.toggled.connect(lambda: self._on_layout_changed("polarity") if self.polarity_radio.isChecked() else None)
        self.bond_radio.toggled.connect(lambda: self._on_layout_changed("bond_type") if self.bond_radio.isChecked() else None)
        self.geometry_radio.toggled.connect(lambda: self._on_layout_changed("geometry") if self.geometry_radio.isChecked() else None)

        group.setLayout(layout)
        return group

    def _create_category_filter_group(self):
        """Create category filter group"""
        group = QGroupBox("Category Filter")
        group.setStyleSheet(self._get_group_style("#8BC34A"))
        layout = QVBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories", None)
        self.category_combo.addItem("Organic", "Organic")
        self.category_combo.addItem("Inorganic", "Inorganic")
        self.category_combo.addItem("Ionic", "Ionic")
        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)

        layout.addWidget(self.category_combo)
        group.setLayout(layout)
        return group

    def _create_polarity_filter_group(self):
        """Create polarity filter group"""
        group = QGroupBox("Polarity Filter")
        group.setStyleSheet(self._get_group_style("#2196F3"))
        layout = QVBoxLayout()

        self.polarity_combo = QComboBox()
        self.polarity_combo.addItem("All Polarities", None)
        self.polarity_combo.addItem("Polar", "Polar")
        self.polarity_combo.addItem("Nonpolar", "Nonpolar")
        self.polarity_combo.addItem("Ionic", "Ionic")
        self.polarity_combo.setStyleSheet(self._get_combo_style())
        self.polarity_combo.currentIndexChanged.connect(self._on_polarity_changed)

        layout.addWidget(self.polarity_combo)
        group.setLayout(layout)
        return group

    def _create_state_filter_group(self):
        """Create state filter group"""
        group = QGroupBox("State Filter")
        group.setStyleSheet(self._get_group_style("#FF9800"))
        layout = QVBoxLayout()

        self.state_combo = QComboBox()
        self.state_combo.addItem("All States", None)
        self.state_combo.addItem("Solid", "Solid")
        self.state_combo.addItem("Liquid", "Liquid")
        self.state_combo.addItem("Gas", "Gas")
        self.state_combo.setStyleSheet(self._get_combo_style())
        self.state_combo.currentIndexChanged.connect(self._on_state_changed)

        layout.addWidget(self.state_combo)
        group.setLayout(layout)
        return group

    def _create_view_controls_group(self):
        """Create view control buttons"""
        group = QGroupBox("View Controls")
        group.setStyleSheet(self._get_group_style("#f093fb"))
        layout = QVBoxLayout()

        # Reset view button
        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7688f0, stop:1 #8658b8);
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

    def _on_layout_changed(self, mode):
        """Handle layout mode change"""
        self.table.set_layout_mode(mode)

    def _on_category_changed(self, index):
        """Handle category filter change"""
        category = self.category_combo.itemData(index)
        self.table.set_category_filter(category)

    def _on_polarity_changed(self, index):
        """Handle polarity filter change"""
        polarity = self.polarity_combo.itemData(index)
        self.table.set_polarity_filter(polarity)

    def _on_state_changed(self, index):
        """Handle state filter change"""
        state = self.state_combo.itemData(index)
        self.table.set_state_filter(state)

    def _on_reset_view(self):
        """Reset view to defaults"""
        self.table.reset_view()

    def _on_clear_filters(self):
        """Clear all filters"""
        self.category_combo.setCurrentIndex(0)
        self.polarity_combo.setCurrentIndex(0)
        self.state_combo.setCurrentIndex(0)

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
                border-radius: 5px;
                font-size: 11px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 250);
                color: white;
                selection-background-color: #764ba2;
            }
        """
