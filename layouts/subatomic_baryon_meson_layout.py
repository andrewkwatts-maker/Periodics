"""
Baryon/Meson Layout Renderer for Subatomic Particles
Displays baryons and mesons in separate visual groups
"""

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor


class SubatomicBaryonMesonLayout:
    """Layout renderer that separates baryons and mesons into distinct groups"""

    def __init__(self, widget_width, widget_height):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 140
        self.card_height = 180
        self.card_spacing = 20
        self.section_spacing = 60
        self.header_height = 40

    def calculate_layout(self, particles):
        """
        Calculate positions for all particles.

        Args:
            particles: List of particle dictionaries

        Returns:
            Dictionary mapping particle names to position data
        """
        layout_data = {}

        # Separate particles
        baryons = [p for p in particles if p.get('_is_baryon', False)]
        mesons = [p for p in particles if p.get('_is_meson', False)]

        y_offset = self.header_height + 20
        x_start = 50

        # Calculate columns
        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        # Baryon section
        if baryons:
            layout_data['_baryon_header'] = {
                'type': 'header',
                'x': x_start,
                'y': y_offset,
                'text': 'BARYONS',
                'subtitle': '3 quarks bound by strong force',
                'color': (102, 126, 234)
            }
            y_offset += self.header_height

            # Sort baryons by mass
            baryons_sorted = sorted(baryons, key=lambda p: p.get('Mass_MeVc2', 0))

            for i, particle in enumerate(baryons_sorted):
                row = i // cols
                col = i % cols
                x = x_start + col * (self.card_width + self.card_spacing)
                y = y_offset + row * (self.card_height + self.card_spacing)

                layout_data[particle['Name']] = {
                    'type': 'particle',
                    'x': x,
                    'y': y,
                    'width': self.card_width,
                    'height': self.card_height,
                    'particle': particle
                }

            # Calculate total baryon rows
            baryon_rows = (len(baryons) + cols - 1) // cols
            y_offset += baryon_rows * (self.card_height + self.card_spacing) + self.section_spacing

        # Meson section
        if mesons:
            layout_data['_meson_header'] = {
                'type': 'header',
                'x': x_start,
                'y': y_offset,
                'text': 'MESONS',
                'subtitle': 'quark + antiquark pairs',
                'color': (240, 147, 251)
            }
            y_offset += self.header_height

            # Sort mesons by mass
            mesons_sorted = sorted(mesons, key=lambda p: p.get('Mass_MeVc2', 0))

            for i, particle in enumerate(mesons_sorted):
                row = i // cols
                col = i % cols
                x = x_start + col * (self.card_width + self.card_spacing)
                y = y_offset + row * (self.card_height + self.card_spacing)

                layout_data[particle['Name']] = {
                    'type': 'particle',
                    'x': x,
                    'y': y,
                    'width': self.card_width,
                    'height': self.card_height,
                    'particle': particle
                }

        return layout_data

    def get_content_height(self, particles):
        """Calculate total content height for scrolling"""
        baryons = [p for p in particles if p.get('_is_baryon', False)]
        mesons = [p for p in particles if p.get('_is_meson', False)]

        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        height = self.header_height + 20

        if baryons:
            baryon_rows = (len(baryons) + cols - 1) // cols
            height += self.header_height + baryon_rows * (self.card_height + self.card_spacing) + self.section_spacing

        if mesons:
            meson_rows = (len(mesons) + cols - 1) // cols
            height += self.header_height + meson_rows * (self.card_height + self.card_spacing)

        return height + 50  # Add padding

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
