"""
Mass Order Layout Renderer for Subatomic Particles
Displays all particles ordered by their mass
"""


class SubatomicMassLayout:
    """Layout renderer that orders particles by mass"""

    def __init__(self, widget_width, widget_height):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 140
        self.card_height = 180
        self.card_spacing = 20
        self.header_height = 40

    def calculate_layout(self, particles):
        """
        Calculate positions for all particles ordered by mass.

        Args:
            particles: List of particle dictionaries

        Returns:
            Dictionary mapping particle names to position data
        """
        layout_data = {}

        y_offset = self.header_height + 20
        x_start = 50

        # Calculate columns
        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        # Header
        layout_data['_mass_header'] = {
            'type': 'header',
            'x': x_start,
            'y': y_offset,
            'text': 'PARTICLES BY MASS',
            'subtitle': 'Lightest to heaviest (MeV/c^2)',
            'color': (255, 183, 77)
        }
        y_offset += self.header_height

        # Sort by mass
        sorted_particles = sorted(particles, key=lambda p: p.get('Mass_MeVc2', 0))

        # Add mass scale markers
        mass_ranges = [
            (0, 200, 'Light (< 200 MeV)'),
            (200, 1000, 'Medium (200-1000 MeV)'),
            (1000, 2000, 'Heavy (1-2 GeV)'),
            (2000, float('inf'), 'Very Heavy (> 2 GeV)')
        ]

        current_range_idx = 0
        for i, particle in enumerate(sorted_particles):
            mass = particle.get('Mass_MeVc2', 0)

            # Check if we need a new range header
            while current_range_idx < len(mass_ranges):
                min_m, max_m, label = mass_ranges[current_range_idx]
                if min_m <= mass < max_m:
                    break
                current_range_idx += 1

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
                'particle': particle,
                'mass_rank': i + 1
            }

        return layout_data

    def get_content_height(self, particles):
        """Calculate total content height"""
        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        rows = (len(particles) + cols - 1) // cols
        height = self.header_height * 2 + 20
        height += rows * (self.card_height + self.card_spacing)

        return height + 50

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
