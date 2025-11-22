#!/usr/bin/env python3
"""
Test script for the new UnifiedPropertyControl widget
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QPalette, QColor
from ui.components import UnifiedPropertyControl

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Property Control Test")
        self.setGeometry(100, 100, 500, 400)

        # Set dark background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 40))
        self.setPalette(palette)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)

        # Test color property (ionization)
        self.color_control = UnifiedPropertyControl(
            title="Ionization Energy",
            property_name="ionization",
            property_type="color"
        )
        self.color_control.set_value_range(3.5, 25.0)
        self.color_control.color_range_changed.connect(self.on_color_range_changed)
        self.color_control.filter_range_changed.connect(self.on_filter_range_changed)
        self.color_control.filter_changed.connect(self.on_filter_changed)
        layout.addWidget(self.color_control)

        # Test spectrum property
        self.spectrum_control = UnifiedPropertyControl(
            title="Spectrum",
            property_name="spectrum",
            property_type="color"
        )
        self.spectrum_control.set_value_range(380, 750)
        layout.addWidget(self.spectrum_control)

        # Test size property (border)
        self.size_control = UnifiedPropertyControl(
            title="Border Thickness",
            property_name="border",
            property_type="size"
        )
        self.size_control.set_value_range(0, 10)
        layout.addWidget(self.size_control)

        layout.addStretch()

    def on_color_range_changed(self, min_val, max_val):
        print(f"Color range changed: {min_val:.2f} - {max_val:.2f}")

    def on_filter_range_changed(self, min_val, max_val):
        print(f"Filter range changed: {min_val:.2f} - {max_val:.2f}")

    def on_filter_changed(self, enabled):
        print(f"Filter enabled: {enabled}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
