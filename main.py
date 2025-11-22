"""
Periodics - Interactive Periodic Table Application
Main entry point with tabbed interface for different views:
- Atoms (Periodic Table)
- Quarks (Fundamental Particles)
- Subatomic (Hadrons)
- Molecules
- Alloys
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QSplitter, QMessageBox, QStatusBar, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

# Import tab components
# Atoms tab
try:
    from core.unified_table import UnifiedPeriodicTable
    from ui.control_panel import ControlPanel
    from ui.element_info_panel import ElementInfoPanel
    HAS_ATOMS_TAB = True
except ImportError as e:
    print(f"Atoms tab not available: {e}")
    HAS_ATOMS_TAB = False

# Quarks tab
try:
    from core.quark_unified_table import QuarkUnifiedTable
    from ui.quark_control_panel import QuarkControlPanel
    from ui.quark_info_panel import QuarkInfoPanel
    HAS_QUARKS_TAB = True
except ImportError as e:
    print(f"Quarks tab not available: {e}")
    HAS_QUARKS_TAB = False

# Subatomic tab
try:
    from core.subatomic_unified_table import SubatomicUnifiedTable
    from ui.subatomic_control_panel import SubatomicControlPanel
    from ui.subatomic_info_panel import SubatomicInfoPanel
    HAS_SUBATOMIC_TAB = True
except ImportError as e:
    print(f"Subatomic tab not available: {e}")
    HAS_SUBATOMIC_TAB = False

# Molecules tab
try:
    from core.molecule_unified_table import MoleculeUnifiedTable
    from ui.molecule_control_panel import MoleculeControlPanel
    from ui.molecule_info_panel import MoleculeInfoPanel
    HAS_MOLECULES_TAB = True
except ImportError as e:
    print(f"Molecules tab not available: {e}")
    HAS_MOLECULES_TAB = False

# Alloys tab
try:
    from core.alloy_unified_table import AlloyUnifiedTable
    from ui.alloy_control_panel import AlloyControlPanel
    from ui.alloy_info_panel import AlloyInfoPanel
    from ui.alloy_creation_dialog import AlloyCreationDialog
    HAS_ALLOYS_TAB = True
except ImportError as e:
    print(f"Alloys tab not available: {e}")
    HAS_ALLOYS_TAB = False

# Data management
from data.data_manager import get_data_manager, DataCategory
from ui.data_editor_dialog import DataEditorDialog


class PeriodicsMainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Periodics - Interactive Particle Explorer")
        self.setMinimumSize(1400, 900)

        self.setup_ui()
        self.setup_statusbar()
        self.apply_dark_theme()

    def setup_ui(self):
        """Setup the main UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: rgb(20, 20, 35);
            }
            QTabBar::tab {
                background: rgb(45, 45, 65);
                color: white;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(80, 80, 120), stop:1 rgb(60, 60, 90));
            }
            QTabBar::tab:hover:!selected {
                background: rgb(60, 60, 85);
            }
        """)

        # Add tabs
        if HAS_ATOMS_TAB:
            self._add_atoms_tab()

        if HAS_QUARKS_TAB:
            self._add_quarks_tab()

        if HAS_SUBATOMIC_TAB:
            self._add_subatomic_tab()

        if HAS_MOLECULES_TAB:
            self._add_molecules_tab()

        if HAS_ALLOYS_TAB:
            self._add_alloys_tab()

        main_layout.addWidget(self.tabs)

    def _add_atoms_tab(self):
        """Add the Atoms (Periodic Table) tab"""
        atoms_widget = QWidget()
        atoms_layout = QHBoxLayout(atoms_widget)
        atoms_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Control panel
        self.atom_table = UnifiedPeriodicTable()
        self.atom_control = ControlPanel(self.atom_table)
        self.atom_control.setFixedWidth(280)
        splitter.addWidget(self.atom_control)

        # Main table
        splitter.addWidget(self.atom_table)

        # Info panel
        self.atom_info = ElementInfoPanel()
        self.atom_info.setFixedWidth(350)
        splitter.addWidget(self.atom_info)

        # Connect signals
        self.atom_table.element_selected.connect(self._on_atom_selected)
        self.atom_table.element_hovered.connect(lambda e: self.statusBar().showMessage(
            f"Element: {e.get('name', '')} ({e.get('symbol', '')})" if e else ""))

        # Connect data management signals
        self.atom_control.add_requested.connect(self._on_atom_add)
        self.atom_control.edit_requested.connect(self._on_atom_edit)
        self.atom_control.remove_requested.connect(self._on_atom_remove)
        self.atom_control.reset_requested.connect(self._on_atom_reset)
        self.atom_control.create_requested.connect(self._on_atom_create)
        self.atom_info.data_saved.connect(self._on_atom_data_saved)
        self.atom_info.edit_cancelled.connect(lambda: self.atom_info.show_default())

        atoms_layout.addWidget(splitter)
        self.tabs.addTab(atoms_widget, "Atoms")

    def _add_quarks_tab(self):
        """Add the Quarks tab"""
        quarks_widget = QWidget()
        quarks_layout = QHBoxLayout(quarks_widget)
        quarks_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        self.quark_table = QuarkUnifiedTable()
        self.quark_control = QuarkControlPanel(self.quark_table)
        self.quark_control.setFixedWidth(280)
        splitter.addWidget(self.quark_control)

        splitter.addWidget(self.quark_table)

        self.quark_info = QuarkInfoPanel()
        self.quark_info.setFixedWidth(350)
        splitter.addWidget(self.quark_info)

        self.quark_table.quark_selected.connect(self._on_quark_selected)

        # Connect data management signals
        self.quark_control.add_requested.connect(self._on_quark_add)
        self.quark_control.edit_requested.connect(self._on_quark_edit)
        self.quark_control.remove_requested.connect(self._on_quark_remove)
        self.quark_control.reset_requested.connect(self._on_quark_reset)
        self.quark_control.create_requested.connect(self._on_quark_create)
        self.quark_info.data_saved.connect(self._on_quark_data_saved)
        self.quark_info.edit_cancelled.connect(lambda: self.quark_info.show_default())

        quarks_layout.addWidget(splitter)
        self.tabs.addTab(quarks_widget, "Quarks")

    def _add_subatomic_tab(self):
        """Add the Subatomic particles tab"""
        subatomic_widget = QWidget()
        subatomic_layout = QHBoxLayout(subatomic_widget)
        subatomic_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        self.subatomic_table = SubatomicUnifiedTable()
        self.subatomic_control = SubatomicControlPanel(self.subatomic_table)
        self.subatomic_control.setFixedWidth(280)
        splitter.addWidget(self.subatomic_control)

        splitter.addWidget(self.subatomic_table)

        self.subatomic_info = SubatomicInfoPanel()
        self.subatomic_info.setFixedWidth(350)
        splitter.addWidget(self.subatomic_info)

        self.subatomic_table.particle_selected.connect(self._on_subatomic_selected)

        # Connect data management signals
        self.subatomic_control.add_requested.connect(self._on_subatomic_add)
        self.subatomic_control.edit_requested.connect(self._on_subatomic_edit)
        self.subatomic_control.remove_requested.connect(self._on_subatomic_remove)
        self.subatomic_control.reset_requested.connect(self._on_subatomic_reset)
        self.subatomic_control.create_requested.connect(self._on_subatomic_create)
        self.subatomic_info.data_saved.connect(self._on_subatomic_data_saved)
        self.subatomic_info.edit_cancelled.connect(lambda: self.subatomic_info.show_default())

        subatomic_layout.addWidget(splitter)
        self.tabs.addTab(subatomic_widget, "Subatomic")

    def _add_molecules_tab(self):
        """Add the Molecules tab"""
        molecules_widget = QWidget()
        molecules_layout = QHBoxLayout(molecules_widget)
        molecules_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        self.molecule_table = MoleculeUnifiedTable()
        self.molecule_control = MoleculeControlPanel(self.molecule_table)
        self.molecule_control.setFixedWidth(280)
        splitter.addWidget(self.molecule_control)

        splitter.addWidget(self.molecule_table)

        self.molecule_info = MoleculeInfoPanel()
        self.molecule_info.setFixedWidth(350)
        splitter.addWidget(self.molecule_info)

        self.molecule_table.molecule_selected.connect(self._on_molecule_selected)

        # Connect data management signals
        self.molecule_control.add_requested.connect(self._on_molecule_add)
        self.molecule_control.edit_requested.connect(self._on_molecule_edit)
        self.molecule_control.remove_requested.connect(self._on_molecule_remove)
        self.molecule_control.reset_requested.connect(self._on_molecule_reset)
        self.molecule_control.create_requested.connect(self._on_molecule_create)
        self.molecule_info.data_saved.connect(self._on_molecule_data_saved)
        self.molecule_info.edit_cancelled.connect(lambda: self.molecule_info.show_default())

        molecules_layout.addWidget(splitter)
        self.tabs.addTab(molecules_widget, "Molecules")

    def _add_alloys_tab(self):
        """Add the Alloys tab"""
        alloys_widget = QWidget()
        alloys_layout = QHBoxLayout(alloys_widget)
        alloys_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Create alloy table
        self.alloy_table = AlloyUnifiedTable()

        # Control panel
        self.alloy_control = AlloyControlPanel(self.alloy_table)
        self.alloy_control.setFixedWidth(280)
        splitter.addWidget(self.alloy_control)

        # Main visualization
        splitter.addWidget(self.alloy_table)

        # Info panel
        self.alloy_info = AlloyInfoPanel()
        self.alloy_info.setFixedWidth(400)
        splitter.addWidget(self.alloy_info)

        # Connect signals
        self.alloy_table.alloy_selected.connect(self._on_alloy_selected)
        self.alloy_table.alloy_hovered.connect(lambda a: self.statusBar().showMessage(
            f"Alloy: {a.get('name', '')} - {a.get('category', '')}" if a else ""))

        # Connect data management signals
        self.alloy_control.add_requested.connect(self._on_alloy_add)
        self.alloy_control.edit_requested.connect(self._on_alloy_edit)
        self.alloy_control.remove_requested.connect(self._on_alloy_remove)
        self.alloy_control.reset_requested.connect(self._on_alloy_reset)
        self.alloy_control.create_requested.connect(self._on_alloy_create)

        # Update item count
        self.alloy_control.update_item_count(len(self.alloy_table.base_alloys))

        alloys_layout.addWidget(splitter)
        self.tabs.addTab(alloys_widget, "Alloys")

    def _on_alloy_selected(self, alloy):
        """Handle alloy selection"""
        self.alloy_info.update_alloy(alloy)
        self.alloy_control.set_item_selected(alloy is not None)

    def _on_alloy_add(self):
        """Handle alloy add request"""
        dialog = DataEditorDialog(DataCategory.ALLOYS, parent=self)
        if dialog.exec():
            self.alloy_table.reload_data()
            self.alloy_control.update_item_count(len(self.alloy_table.base_alloys))

    def _on_alloy_edit(self):
        """Handle alloy edit request"""
        if self.alloy_table.selected_alloy:
            dialog = DataEditorDialog(
                DataCategory.ALLOYS,
                existing_data=self.alloy_table.selected_alloy,
                parent=self
            )
            if dialog.exec():
                self.alloy_table.reload_data()

    def _on_alloy_remove(self):
        """Handle alloy remove request"""
        if self.alloy_table.selected_alloy:
            name = self.alloy_table.selected_alloy.get('name', 'Unknown')
            reply = QMessageBox.question(
                self, "Remove Alloy",
                f"Are you sure you want to remove '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                manager = get_data_manager()
                filename = self.alloy_table.selected_alloy.get('_filename', name.replace(' ', '_'))
                if manager.remove_item(DataCategory.ALLOYS, filename):
                    self.alloy_table.reload_data()
                    self.alloy_control.update_item_count(len(self.alloy_table.base_alloys))
                    self.alloy_info.show_default()
                    self.alloy_control.set_item_selected(False)

    def _on_alloy_reset(self):
        """Handle alloy reset request"""
        reply = QMessageBox.question(
            self, "Reset Alloys",
            "Are you sure you want to reset all alloys to defaults?\nThis will remove any custom alloys.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            manager = get_data_manager()
            if manager.reset_category(DataCategory.ALLOYS):
                self.alloy_table.reload_data()
                self.alloy_control.update_item_count(len(self.alloy_table.base_alloys))
                self.alloy_info.show_default()
                QMessageBox.information(self, "Success", "Alloys reset to defaults.")

    def _on_alloy_create(self):
        """Handle alloy creation from elements"""
        dialog = AlloyCreationDialog(self)
        dialog.alloy_created.connect(lambda: self._on_alloy_created())
        dialog.exec()

    def _on_alloy_created(self):
        """Called when a new alloy is created"""
        self.alloy_table.reload_data()
        self.alloy_control.update_item_count(len(self.alloy_table.base_alloys))

    # ==================== ATOMS TAB HANDLERS ====================

    def _on_atom_selected(self, element):
        """Handle atom selection"""
        self.atom_info.update_element(element)
        self.atom_control.set_item_selected(element is not None)

    def _on_atom_add(self):
        """Handle atom add request - show inline editor"""
        # Get selected element as template if available
        template = None
        if hasattr(self.atom_table, 'selected_element'):
            template = self.atom_table.selected_element
        self.atom_info.start_add(template)

    def _on_atom_edit(self):
        """Handle atom edit request - show inline editor"""
        if hasattr(self.atom_table, 'selected_element') and self.atom_table.selected_element:
            self.atom_info.start_edit(self.atom_table.selected_element)

    def _on_atom_remove(self):
        """Handle atom remove request"""
        if hasattr(self.atom_table, 'selected_element') and self.atom_table.selected_element:
            elem = self.atom_table.selected_element
            name = elem.get('name', 'Unknown')
            reply = QMessageBox.question(
                self, "Remove Element",
                f"Are you sure you want to remove '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                manager = get_data_manager()
                z = elem.get('atomic_number', 0)
                symbol = elem.get('symbol', 'X')
                filename = f"{z:03d}_{symbol}"
                if manager.remove_item(DataCategory.ELEMENTS, filename):
                    self.atom_table.reload_data()
                    self.atom_info.show_default()
                    self.atom_control.set_item_selected(False)

    def _on_atom_reset(self):
        """Handle atom reset request"""
        reply = QMessageBox.question(
            self, "Reset Elements",
            "Are you sure you want to reset all elements to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            manager = get_data_manager()
            if manager.reset_category(DataCategory.ELEMENTS):
                self.atom_table.reload_data()
                self.atom_info.show_default()
                QMessageBox.information(self, "Success", "Elements reset to defaults.")

    def _on_atom_create(self):
        """Handle atom creation from subatomic particles"""
        from ui.creation_dialog import AtomCreationDialog
        dialog = AtomCreationDialog(self)
        dialog.atom_created.connect(lambda: self._on_atom_data_saved(None))
        dialog.exec()

    def _on_atom_data_saved(self, data):
        """Called when atom data is saved"""
        self.atom_table.reload_data()
        self.atom_info.show_default()

    # ==================== QUARKS TAB HANDLERS ====================

    def _on_quark_selected(self, quark):
        """Handle quark selection"""
        self.quark_info.update_quark(quark)
        self.quark_control.set_item_selected(quark is not None)

    def _on_quark_add(self):
        """Handle quark add request - show inline editor"""
        template = None
        if hasattr(self.quark_table, 'selected_quark'):
            template = self.quark_table.selected_quark
        self.quark_info.start_add(template)

    def _on_quark_edit(self):
        """Handle quark edit request - show inline editor"""
        if hasattr(self.quark_table, 'selected_quark') and self.quark_table.selected_quark:
            self.quark_info.start_edit(self.quark_table.selected_quark)

    def _on_quark_remove(self):
        """Handle quark remove request"""
        if hasattr(self.quark_table, 'selected_quark') and self.quark_table.selected_quark:
            quark = self.quark_table.selected_quark
            name = quark.get('Name', 'Unknown')
            reply = QMessageBox.question(
                self, "Remove Quark",
                f"Are you sure you want to remove '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                manager = get_data_manager()
                filename = name.replace(' ', '_')
                if manager.remove_item(DataCategory.QUARKS, filename):
                    self.quark_table.reload_data()
                    self.quark_info.show_default()
                    self.quark_control.set_item_selected(False)

    def _on_quark_reset(self):
        """Handle quark reset request"""
        reply = QMessageBox.question(
            self, "Reset Quarks",
            "Are you sure you want to reset all quarks to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            manager = get_data_manager()
            if manager.reset_category(DataCategory.QUARKS):
                self.quark_table.reload_data()
                self.quark_info.show_default()
                QMessageBox.information(self, "Success", "Quarks reset to defaults.")

    def _on_quark_create(self):
        """Handle quark creation (quarks are fundamental, so just add)"""
        self.quark_info.start_add(None)

    def _on_quark_data_saved(self, data):
        """Called when quark data is saved"""
        self.quark_table.reload_data()
        self.quark_info.show_default()

    # ==================== SUBATOMIC TAB HANDLERS ====================

    def _on_subatomic_selected(self, particle):
        """Handle subatomic particle selection"""
        self.subatomic_info.update_particle(particle)
        self.subatomic_control.set_item_selected(particle is not None)

    def _on_subatomic_add(self):
        """Handle subatomic add request - show inline editor"""
        template = None
        if hasattr(self.subatomic_table, 'selected_particle'):
            template = self.subatomic_table.selected_particle
        self.subatomic_info.start_add(template)

    def _on_subatomic_edit(self):
        """Handle subatomic edit request - show inline editor"""
        if hasattr(self.subatomic_table, 'selected_particle') and self.subatomic_table.selected_particle:
            self.subatomic_info.start_edit(self.subatomic_table.selected_particle)

    def _on_subatomic_remove(self):
        """Handle subatomic remove request"""
        if hasattr(self.subatomic_table, 'selected_particle') and self.subatomic_table.selected_particle:
            particle = self.subatomic_table.selected_particle
            name = particle.get('Name', 'Unknown')
            reply = QMessageBox.question(
                self, "Remove Particle",
                f"Are you sure you want to remove '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                manager = get_data_manager()
                filename = name.replace(' ', '_')
                if manager.remove_item(DataCategory.SUBATOMIC, filename):
                    self.subatomic_table.reload_data()
                    self.subatomic_info.show_default()
                    self.subatomic_control.set_item_selected(False)

    def _on_subatomic_reset(self):
        """Handle subatomic reset request"""
        reply = QMessageBox.question(
            self, "Reset Subatomic Particles",
            "Are you sure you want to reset all subatomic particles to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            manager = get_data_manager()
            if manager.reset_category(DataCategory.SUBATOMIC):
                self.subatomic_table.reload_data()
                self.subatomic_info.show_default()
                QMessageBox.information(self, "Success", "Subatomic particles reset to defaults.")

    def _on_subatomic_create(self):
        """Handle subatomic creation from quarks"""
        from ui.creation_dialog import SubatomicCreationDialog
        dialog = SubatomicCreationDialog(self)
        dialog.particle_created.connect(lambda: self._on_subatomic_data_saved(None))
        dialog.exec()

    def _on_subatomic_data_saved(self, data):
        """Called when subatomic data is saved"""
        self.subatomic_table.reload_data()
        self.subatomic_info.show_default()

    # ==================== MOLECULES TAB HANDLERS ====================

    def _on_molecule_selected(self, molecule):
        """Handle molecule selection"""
        self.molecule_info.update_molecule(molecule)
        self.molecule_control.set_item_selected(molecule is not None)

    def _on_molecule_add(self):
        """Handle molecule add request - show inline editor"""
        template = None
        if hasattr(self.molecule_table, 'selected_molecule'):
            template = self.molecule_table.selected_molecule
        self.molecule_info.start_add(template)

    def _on_molecule_edit(self):
        """Handle molecule edit request - show inline editor"""
        if hasattr(self.molecule_table, 'selected_molecule') and self.molecule_table.selected_molecule:
            self.molecule_info.start_edit(self.molecule_table.selected_molecule)

    def _on_molecule_remove(self):
        """Handle molecule remove request"""
        if hasattr(self.molecule_table, 'selected_molecule') and self.molecule_table.selected_molecule:
            mol = self.molecule_table.selected_molecule
            name = mol.get('Name', 'Unknown')
            reply = QMessageBox.question(
                self, "Remove Molecule",
                f"Are you sure you want to remove '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                manager = get_data_manager()
                filename = name.replace(' ', '_')
                if manager.remove_item(DataCategory.MOLECULES, filename):
                    self.molecule_table.reload_data()
                    self.molecule_info.show_default()
                    self.molecule_control.set_item_selected(False)

    def _on_molecule_reset(self):
        """Handle molecule reset request"""
        reply = QMessageBox.question(
            self, "Reset Molecules",
            "Are you sure you want to reset all molecules to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            manager = get_data_manager()
            if manager.reset_category(DataCategory.MOLECULES):
                self.molecule_table.reload_data()
                self.molecule_info.show_default()
                QMessageBox.information(self, "Success", "Molecules reset to defaults.")

    def _on_molecule_create(self):
        """Handle molecule creation from atoms"""
        from ui.creation_dialog import MoleculeCreationDialog
        dialog = MoleculeCreationDialog(self)
        dialog.molecule_created.connect(lambda: self._on_molecule_data_saved(None))
        dialog.exec()

    def _on_molecule_data_saved(self, data):
        """Called when molecule data is saved"""
        self.molecule_table.reload_data()
        self.molecule_info.show_default()

    def setup_statusbar(self):
        """Setup the status bar"""
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: rgb(30, 30, 45);
                color: white;
                padding: 5px;
            }
        """)
        self.statusBar().showMessage("Ready")

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(20, 20, 35))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(30, 30, 50))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 60))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(50, 50, 70))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(100, 150, 255))
        palette.setColor(QPalette.Highlight, QColor(100, 100, 150))
        palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(palette)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = PeriodicsMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
