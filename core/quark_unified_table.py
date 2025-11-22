#!/usr/bin/env python3
"""
QuarkUnifiedTable - Main visualization widget for particles
Handles all layout modes and user interactions for the Quarks tab.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QFont)

from core.quark_enums import QuarkLayoutMode, QuarkProperty, ParticleType
from data.quark_loader import QuarkDataLoader
from layouts.quark_standard_layout import QuarkStandardLayoutRenderer
from layouts.quark_linear_layout import QuarkLinearLayoutRenderer
from layouts.quark_circular_layout import QuarkCircularLayoutRenderer
from layouts.quark_alternative_layout import QuarkAlternativeLayoutRenderer


class QuarkUnifiedTable(QWidget):
    """Unified widget for displaying particle visualizations in multiple layouts"""

    # Signals
    particle_selected = Signal(dict)  # Emitted when a particle is clicked
    particle_hovered = Signal(dict)   # Emitted when a particle is hovered

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 500)
        self.setMouseTracking(True)

        # Data
        self.loader = QuarkDataLoader()
        self.particles = []
        self.base_particles = []

        # Layout state
        self.layout_mode = QuarkLayoutMode.STANDARD_MODEL
        self.current_renderer = None

        # Interaction state
        self.hovered_particle = None
        self.selected_particle = None

        # Visual property mappings
        self.fill_property = "particle_type"
        self.border_property = "charge"
        self.glow_property = "mass"

        # Linear layout ordering
        self.order_property = "mass"

        # Filters
        self.filters = {
            'mass': {'min': 0, 'max': float('inf'), 'active': False},
            'charge': {'min': -2, 'max': 2, 'active': False},
            'spin': {'min': 0, 'max': 2, 'active': False}
        }

        # Display options
        self.show_antiparticles = False
        self.show_composites = False
        self.show_connections = False

        # Zoom and pan
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Load data
        self.load_particle_data()
        self._create_renderers()

    def load_particle_data(self):
        """Load particle data from JSON files"""
        self.base_particles = self.loader.load_all_particles(
            include_antiparticles=self.show_antiparticles,
            include_composite=self.show_composites
        )
        self._update_layout()

    def _create_renderers(self):
        """Create layout renderer instances"""
        self.renderers = {
            QuarkLayoutMode.STANDARD_MODEL: QuarkStandardLayoutRenderer(self.width(), self.height()),
            QuarkLayoutMode.LINEAR: QuarkLinearLayoutRenderer(self.width(), self.height()),
            QuarkLayoutMode.CIRCULAR: QuarkCircularLayoutRenderer(self.width(), self.height()),
            QuarkLayoutMode.ALTERNATIVE: QuarkAlternativeLayoutRenderer(self.width(), self.height())
        }
        self.current_renderer = self.renderers[self.layout_mode]

    def _update_layout(self):
        """Update particle positions based on current layout mode"""
        if not self.base_particles:
            return

        # Filter particles based on settings
        filtered = self.base_particles.copy()
        if not self.show_antiparticles:
            filtered = [p for p in filtered if not p.get('_is_antiparticle', False)]
        if not self.show_composites:
            filtered = [p for p in filtered if not p.get('is_composite', False)]

        # Create layout
        self.current_renderer = self.renderers.get(self.layout_mode)
        if self.current_renderer:
            self.current_renderer.update_dimensions(self.width(), self.height())
            kwargs = {}
            if self.layout_mode == QuarkLayoutMode.LINEAR:
                kwargs['sort_property'] = self.order_property
            self.particles = self.current_renderer.create_layout(filtered, **kwargs)
        else:
            self.particles = filtered

        self.update()

    def set_layout_mode(self, mode):
        """Set the layout mode"""
        if isinstance(mode, str):
            mode = QuarkLayoutMode.from_string(mode)
        self.layout_mode = mode
        self._update_layout()

    def set_fill_property(self, prop):
        """Set the property for fill color encoding"""
        self.fill_property = prop
        self.update()

    def set_border_property(self, prop):
        """Set the property for border color encoding"""
        self.border_property = prop
        self.update()

    def set_glow_property(self, prop):
        """Set the property for glow effect encoding"""
        self.glow_property = prop
        self.update()

    def set_order_property(self, prop):
        """Set the property for ordering in linear layout"""
        self.order_property = prop
        if self.layout_mode == QuarkLayoutMode.LINEAR:
            self._update_layout()

    def set_show_antiparticles(self, show):
        """Toggle antiparticle display"""
        if self.show_antiparticles != show:
            self.show_antiparticles = show
            self.load_particle_data()

    def set_show_composites(self, show):
        """Toggle composite particle display"""
        if self.show_composites != show:
            self.show_composites = show
            self.load_particle_data()

    def passes_filter(self, particle):
        """Check if a particle passes the current filters"""
        for prop, filter_settings in self.filters.items():
            if not filter_settings.get('active', False):
                continue

            value = None
            if prop == 'mass':
                value = particle.get('Mass_MeVc2', 0)
            elif prop == 'charge':
                value = particle.get('Charge_e', 0)
            elif prop == 'spin':
                value = particle.get('Spin_hbar', 0)

            if value is not None:
                if value < filter_settings['min'] or value > filter_settings['max']:
                    return False
        return True

    def get_table_state(self):
        """Get current visualization state for renderers"""
        return {
            'fill_property': self.fill_property,
            'border_property': self.border_property,
            'glow_property': self.glow_property,
            'order_property': self.order_property,
            'hovered_particle': self.hovered_particle,
            'selected_particle': self.selected_particle,
            'show_connections': self.show_connections
        }

    def paintEvent(self, event):
        """Paint the particle visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(15, 15, 30))

        # Apply zoom and pan
        painter.translate(self.pan_x, self.pan_y)
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw title
        self._draw_title(painter)

        # Draw particles using current renderer
        if self.current_renderer and self.particles:
            table_state = self.get_table_state()
            self.current_renderer.paint(
                painter, self.particles, table_state,
                passes_filter_func=self.passes_filter
            )

        painter.end()

    def _draw_title(self, painter):
        """Draw layout mode title"""
        title = QuarkLayoutMode.get_display_name(self.layout_mode)
        font = QFont('Arial', 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(100, 150, 200), 1))
        painter.drawText(QPointF(20, 30), f"Layout: {title}")

        # Particle count
        font_small = QFont('Arial', 10)
        painter.setFont(font_small)
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawText(QPointF(20, 50), f"Showing {len(self.particles)} particles")

    def resizeEvent(self, event):
        """Handle widget resize"""
        super().resizeEvent(event)
        for renderer in self.renderers.values():
            renderer.update_dimensions(self.width(), self.height())
        self._update_layout()

    def mouseMoveEvent(self, event):
        """Handle mouse move for hover detection"""
        # Transform mouse position
        x = (event.position().x() - self.pan_x) / self.zoom_level
        y = (event.position().y() - self.pan_y) / self.zoom_level

        # Handle panning
        if self.is_panning:
            self.pan_x = event.position().x() - self.pan_start_x
            self.pan_y = event.position().y() - self.pan_start_y
            self.update()
            return

        # Find particle under mouse
        old_hovered = self.hovered_particle
        self.hovered_particle = None

        if self.current_renderer:
            self.hovered_particle = self.current_renderer.get_particle_at_position(
                x, y, self.particles
            )

        if old_hovered != self.hovered_particle:
            if self.hovered_particle:
                self.particle_hovered.emit(self.hovered_particle)
            self.update()

    def mousePressEvent(self, event):
        """Handle mouse press for selection and panning"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning
            self.is_panning = True
            self.pan_start_x = event.position().x() - self.pan_x
            self.pan_start_y = event.position().y() - self.pan_y
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.LeftButton:
            # Select particle
            if self.hovered_particle:
                self.selected_particle = self.hovered_particle
                self.particle_selected.emit(self.selected_particle)
                self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9

        # Zoom toward mouse position
        mouse_x = event.position().x()
        mouse_y = event.position().y()

        # Adjust pan to zoom toward mouse
        self.pan_x = mouse_x - (mouse_x - self.pan_x) * zoom_factor
        self.pan_y = mouse_y - (mouse_y - self.pan_y) * zoom_factor

        self.zoom_level *= zoom_factor
        self.zoom_level = max(0.3, min(3.0, self.zoom_level))
        self.update()

    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.update()
