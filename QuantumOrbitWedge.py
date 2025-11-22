#!/usr/bin/env python3
"""
The Quantum Orbit 2.0: Multi-Layer Scientific Data Visualization
Wedge-based and Serpentine spectroscopic periodic table with layered visual data encoding
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QLabel, QFrame, QSplitter, QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import UI components
from ui import ControlPanel, SpectroscopyPanel

# Import core classes
from core import UnifiedTable

# Import Quark tab components
from core.quark_unified_table import QuarkUnifiedTable
from ui.quark_control_panel import QuarkControlPanel
from ui.quark_info_panel import QuarkInfoPanel

# Import molecule components
from core.molecule_unified_table import MoleculeUnifiedTable
from ui.molecule_control_panel import MoleculeControlPanel
from ui.molecule_info_panel import MoleculeInfoPanel

# Import subatomic particle components
from core.subatomic_unified_table import SubatomicUnifiedTable
from ui.subatomic_control_panel import SubatomicControlPanel
from ui.subatomic_info_panel import SubatomicInfoPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 The Quantum Orbit 2.0 - Multi-Layout Visualization")
        self.resize(1800, 1000)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a1a, stop:1 #1a1a2e);
            }
            QLabel { color: white; }
        """)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        title_bar = QFrame()
        title_bar.setFixedHeight(90)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
            }
        """)
        title_layout = QVBoxLayout(title_bar)
        title_layout.setContentsMargins(30, 15, 30, 15)

        main_title = QLabel("🌌 THE QUANTUM ORBIT 2.0")
        main_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_title.setStyleSheet("background: transparent;")

        subtitle = QLabel("Multi-Layout Visualization • Circular Wedge Spiral & Layered Serpentine Wedges • Isotope Layers")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: rgba(255,255,255,220); background: transparent;")

        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_bar)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(40, 40, 60, 200);
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QTabBar::tab:hover {
                background: rgba(60, 60, 80, 200);
            }
        """)

        # Create Atoms tab (existing periodic table)
        atoms_widget = QWidget()
        atoms_layout = QVBoxLayout(atoms_widget)
        atoms_layout.setContentsMargins(0, 0, 0, 0)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table = UnifiedTable()
        self.control_panel = ControlPanel(self.table)
        # Link the control panel to the table
        self.table.control_panel = self.control_panel
        control_frame = QFrame()
        control_frame.setMinimumWidth(320)
        control_frame.setMaximumWidth(380)
        control_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.control_panel)
        content_splitter.addWidget(control_frame)

        self.table.mousePressEvent = lambda e: self.on_element_click(e)
        content_splitter.addWidget(self.table)

        self.spectro = SpectroscopyPanel()
        info_frame = QFrame()
        info_frame.setMaximumWidth(450)
        info_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(self.spectro)
        content_splitter.addWidget(info_frame)

        content_splitter.setSizes([350, 850, 400])
        atoms_layout.addWidget(content_splitter)

        # Create Quarks tab with three-panel layout
        quarks_widget = QWidget()
        quarks_layout = QVBoxLayout(quarks_widget)
        quarks_layout.setContentsMargins(0, 0, 0, 0)

        quarks_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Quark table (main visualization)
        self.quark_table = QuarkUnifiedTable()

        # Quark control panel (left)
        self.quark_control_panel = QuarkControlPanel(self.quark_table)
        quark_control_frame = QFrame()
        quark_control_frame.setMinimumWidth(280)
        quark_control_frame.setMaximumWidth(340)
        quark_control_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        quark_control_layout = QVBoxLayout(quark_control_frame)
        quark_control_layout.setContentsMargins(0, 0, 0, 0)
        quark_control_layout.addWidget(self.quark_control_panel)
        quarks_splitter.addWidget(quark_control_frame)

        # Add main table
        quarks_splitter.addWidget(self.quark_table)

        # Quark info panel (right)
        self.quark_info_panel = QuarkInfoPanel()
        quark_info_frame = QFrame()
        quark_info_frame.setMaximumWidth(420)
        quark_info_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        quark_info_layout = QVBoxLayout(quark_info_frame)
        quark_info_layout.setContentsMargins(0, 0, 0, 0)
        quark_info_layout.addWidget(self.quark_info_panel)
        quarks_splitter.addWidget(quark_info_frame)

        # Connect quark selection signal to info panel
        self.quark_table.particle_selected.connect(self.quark_info_panel.update_particle)

        quarks_splitter.setSizes([320, 850, 380])
        quarks_layout.addWidget(quarks_splitter)

        # Create Subatomic tab with three-panel layout
        subatomic_widget = QWidget()
        subatomic_layout = QVBoxLayout(subatomic_widget)
        subatomic_layout.setContentsMargins(0, 0, 0, 0)

        subatomic_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Subatomic table (main visualization)
        self.subatomic_table = SubatomicUnifiedTable()

        # Subatomic control panel (left)
        self.subatomic_control_panel = SubatomicControlPanel(self.subatomic_table)
        subatomic_control_frame = QFrame()
        subatomic_control_frame.setMinimumWidth(280)
        subatomic_control_frame.setMaximumWidth(340)
        subatomic_control_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        subatomic_control_layout = QVBoxLayout(subatomic_control_frame)
        subatomic_control_layout.setContentsMargins(0, 0, 0, 0)
        subatomic_control_layout.addWidget(self.subatomic_control_panel)
        subatomic_splitter.addWidget(subatomic_control_frame)

        # Add main table
        subatomic_splitter.addWidget(self.subatomic_table)

        # Subatomic info panel (right)
        self.subatomic_info_panel = SubatomicInfoPanel()
        subatomic_info_frame = QFrame()
        subatomic_info_frame.setMaximumWidth(450)
        subatomic_info_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        subatomic_info_layout = QVBoxLayout(subatomic_info_frame)
        subatomic_info_layout.setContentsMargins(0, 0, 0, 0)
        subatomic_info_layout.addWidget(self.subatomic_info_panel)
        subatomic_splitter.addWidget(subatomic_info_frame)

        # Connect subatomic selection signal to info panel
        self.subatomic_table.particle_selected.connect(self.subatomic_info_panel.update_particle)

        subatomic_splitter.setSizes([320, 850, 430])
        subatomic_layout.addWidget(subatomic_splitter)

        # Create Molecules tab with three-panel layout
        molecules_widget = QWidget()
        molecules_layout = QVBoxLayout(molecules_widget)
        molecules_layout.setContentsMargins(0, 0, 0, 0)

        molecules_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Molecule table (main visualization)
        self.molecule_table = MoleculeUnifiedTable()

        # Molecule control panel (left)
        self.molecule_control_panel = MoleculeControlPanel(self.molecule_table)
        molecule_control_frame = QFrame()
        molecule_control_frame.setMinimumWidth(280)
        molecule_control_frame.setMaximumWidth(340)
        molecule_control_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        molecule_control_layout = QVBoxLayout(molecule_control_frame)
        molecule_control_layout.setContentsMargins(0, 0, 0, 0)
        molecule_control_layout.addWidget(self.molecule_control_panel)
        molecules_splitter.addWidget(molecule_control_frame)

        # Add main table
        molecules_splitter.addWidget(self.molecule_table)

        # Molecule info panel (right)
        self.molecule_info_panel = MoleculeInfoPanel()
        molecule_info_frame = QFrame()
        molecule_info_frame.setMaximumWidth(450)
        molecule_info_frame.setStyleSheet("background: rgba(20, 20, 35, 200); border-radius: 10px;")
        molecule_info_layout = QVBoxLayout(molecule_info_frame)
        molecule_info_layout.setContentsMargins(0, 0, 0, 0)
        molecule_info_layout.addWidget(self.molecule_info_panel)
        molecules_splitter.addWidget(molecule_info_frame)

        # Connect molecule selection signal to info panel
        self.molecule_table.molecule_selected.connect(self.molecule_info_panel.update_molecule)

        molecules_splitter.setSizes([320, 850, 430])
        molecules_layout.addWidget(molecules_splitter)

        # Add tabs
        self.tab_widget.addTab(atoms_widget, "Atoms")
        self.tab_widget.addTab(quarks_widget, "Quarks")
        self.tab_widget.addTab(subatomic_widget, "Subatomic")
        self.tab_widget.addTab(molecules_widget, "Molecules")

        main_layout.addWidget(self.tab_widget, 1)

        self.setCentralWidget(central)

    def on_element_click(self, event):
        if self.table.hovered_element:
            self.table.selected_element = self.table.hovered_element
            self.spectro.update_element(self.table.hovered_element)
            self.table.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
