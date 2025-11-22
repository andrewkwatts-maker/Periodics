"""
Decay Chain Layout Renderer for Subatomic Particles
Displays particles ordered by stability with decay relationship arrows
"""


class SubatomicDecayLayout:
    """Layout renderer showing decay chains and stability ordering"""

    def __init__(self, widget_width, widget_height):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 140
        self.card_height = 180
        self.card_spacing = 30  # More spacing for arrows
        self.section_spacing = 60
        self.header_height = 40

    def calculate_layout(self, particles):
        """
        Calculate positions for particles ordered by stability.

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
        layout_data['_decay_header'] = {
            'type': 'header',
            'x': x_start,
            'y': y_offset,
            'text': 'STABILITY & DECAY',
            'subtitle': 'Ordered by half-life (most stable first)',
            'color': (129, 199, 132)
        }
        y_offset += self.header_height

        # Sort by stability factor (most stable first)
        sorted_particles = sorted(particles, key=lambda p: -p.get('_stability_factor', 0))

        # Group by stability ranges
        stability_groups = [
            ('stable', 'Stable Particles', (100, 255, 100), lambda p: p.get('Stability') == 'Stable'),
            ('long', 'Long-lived (> 1 ns)', (200, 255, 100), lambda p: p.get('Stability') != 'Stable' and p.get('HalfLife_s', 0) and p.get('HalfLife_s', 0) > 1e-9),
            ('medium', 'Medium (1 ps - 1 ns)', (255, 255, 100), lambda p: p.get('HalfLife_s', 0) and 1e-12 <= p.get('HalfLife_s', 0) <= 1e-9),
            ('short', 'Short-lived (< 1 ps)', (255, 150, 100), lambda p: p.get('HalfLife_s', 0) and p.get('HalfLife_s', 0) < 1e-12),
        ]

        decay_arrows = []

        for group_id, group_name, color, filter_func in stability_groups:
            group_particles = [p for p in sorted_particles if filter_func(p)]

            if not group_particles:
                continue

            # Group header
            layout_data[f'_stability_{group_id}_header'] = {
                'type': 'subheader',
                'x': x_start,
                'y': y_offset,
                'text': group_name,
                'color': color
            }
            y_offset += 30

            for i, particle in enumerate(group_particles):
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
                    'stability_group': group_id
                }

                # Record decay arrows
                decay_products = particle.get('DecayProducts', [])
                for product in decay_products:
                    decay_arrows.append({
                        'from': particle['Name'],
                        'to': product
                    })

            group_rows = (len(group_particles) + cols - 1) // cols
            y_offset += group_rows * (self.card_height + self.card_spacing) + self.section_spacing

        # Store decay arrows for later rendering
        layout_data['_decay_arrows'] = {
            'type': 'arrows',
            'arrows': decay_arrows
        }

        return layout_data

    def get_decay_arrows(self, layout_data):
        """Get list of decay arrows to draw"""
        arrows_data = layout_data.get('_decay_arrows', {})
        return arrows_data.get('arrows', [])

    def get_content_height(self, particles):
        """Calculate total content height"""
        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        # Estimate based on number of particles
        rows = (len(particles) + cols - 1) // cols
        # Add extra for group headers
        height = self.header_height * 6 + 20
        height += rows * (self.card_height + self.card_spacing)
        height += self.section_spacing * 4

        return height + 50

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
