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

# Import quark viewer
from ui.quark_viewer import QuarkViewer


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

        # Create Quarks tab
        self.quark_viewer = QuarkViewer()

        # Create Molecules tab (placeholder)
        molecules_widget = QWidget()
        molecules_layout = QVBoxLayout(molecules_widget)
        molecules_layout.setContentsMargins(20, 20, 20, 20)
        molecules_label = QLabel("Molecules viewer coming soon...")
        molecules_label.setStyleSheet("color: white; font-size: 16px;")
        molecules_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        molecules_layout.addWidget(molecules_label)

        # Add tabs
        self.tab_widget.addTab(atoms_widget, "Atoms")
        self.tab_widget.addTab(self.quark_viewer, "Quarks")
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
