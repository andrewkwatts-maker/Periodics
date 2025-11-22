"""
Eightfold Way Layout Renderer for Subatomic Particles
Displays particles in a Strangeness-Isospin (I3 vs Y) plot
Classic particle physics multiplet diagram showing octets and decuplets
"""

import math


class SubatomicEightfoldLayout:
    """Layout renderer for the Eightfold Way (Strangeness-Isospin Plot)"""

    def __init__(self, widget_width, widget_height):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 120
        self.card_height = 150
        self.card_spacing = 15
        self.header_height = 40

        # Plot configuration
        self.plot_margin = 100
        self.axis_label_offset = 30

    def calculate_layout(self, particles):
        """
        Calculate positions for particles in Eightfold Way diagram.
        X-axis: Isospin_I3
        Y-axis: Hypercharge Y = Strangeness + BaryonNumber/2

        Args:
            particles: List of particle dictionaries

        Returns:
            Dictionary mapping particle names to position data
        """
        layout_data = {}

        # Header
        y_header = 30
        layout_data['_eightfold_header'] = {
            'type': 'header',
            'x': 50,
            'y': y_header,
            'text': 'EIGHTFOLD WAY',
            'subtitle': 'Strangeness-Isospin Plot (I3 vs Hypercharge Y)',
            'color': (255, 215, 0)  # Gold
        }

        # Separate baryons and mesons for different multiplet diagrams
        baryons = [p for p in particles if p.get('_is_baryon', False)]
        mesons = [p for p in particles if p.get('_is_meson', False)]

        # Calculate I3 and Y ranges
        all_particles = baryons + mesons
        if not all_particles:
            return layout_data

        # Get I3 and Y values
        particle_coords = []
        for p in all_particles:
            i3 = p.get('Isospin_I3', 0)
            strangeness = p.get('Strangeness', 0)
            baryon_num = p.get('BaryonNumber_B', 0)
            # Hypercharge: Y = S + B (simplified Gell-Mann-Nishijima)
            hypercharge = strangeness + baryon_num
            particle_coords.append((p, i3, hypercharge))

        # Determine plot bounds
        i3_values = [c[1] for c in particle_coords]
        y_values = [c[2] for c in particle_coords]

        i3_min = min(i3_values) if i3_values else -1.5
        i3_max = max(i3_values) if i3_values else 1.5
        y_min = min(y_values) if y_values else -2
        y_max = max(y_values) if y_values else 2

        # Add padding
        i3_range = max(i3_max - i3_min, 3)
        y_range = max(y_max - y_min, 4)

        # Calculate plot area
        plot_left = self.plot_margin + 50
        plot_right = self.widget_width - self.plot_margin
        plot_top = self.header_height + 80
        plot_bottom = plot_top + 500

        plot_width = plot_right - plot_left
        plot_height = plot_bottom - plot_top

        # Store axis info for rendering
        layout_data['_axis_info'] = {
            'type': 'axis',
            'plot_left': plot_left,
            'plot_right': plot_right,
            'plot_top': plot_top,
            'plot_bottom': plot_bottom,
            'i3_min': i3_min - 0.5,
            'i3_max': i3_max + 0.5,
            'y_min': y_min - 0.5,
            'y_max': y_max + 0.5,
            'x_label': 'Isospin I3',
            'y_label': 'Hypercharge Y'
        }

        # Position particles
        def coord_to_pixel(i3, y):
            """Convert I3, Y coordinates to pixel positions"""
            # Normalize to 0-1 range
            x_norm = (i3 - (i3_min - 0.5)) / (i3_range + 1)
            y_norm = (y - (y_min - 0.5)) / (y_range + 1)

            # Convert to pixel coordinates (Y is inverted)
            px = plot_left + x_norm * plot_width
            py = plot_bottom - y_norm * plot_height

            return px, py

        # Track positions to avoid overlap
        position_map = {}

        for p, i3, hypercharge in particle_coords:
            px, py = coord_to_pixel(i3, hypercharge)

            # Adjust for card centering
            px -= self.card_width / 2
            py -= self.card_height / 2

            # Handle overlapping particles (offset slightly)
            key = (round(i3 * 2), round(hypercharge * 2))
            if key in position_map:
                offset = position_map[key] * 25
                px += offset
                position_map[key] += 1
            else:
                position_map[key] = 1

            layout_data[p['Name']] = {
                'type': 'particle',
                'x': px,
                'y': py,
                'width': self.card_width,
                'height': self.card_height,
                'particle': p,
                'i3': i3,
                'hypercharge': hypercharge,
                'multiplet': self._determine_multiplet(p)
            }

        # Add multiplet labels
        layout_data['_baryon_octet_label'] = {
            'type': 'subheader',
            'x': plot_left,
            'y': plot_top - 20,
            'text': 'Baryon Octet & Decuplet',
            'color': (102, 126, 234)
        }

        return layout_data

    def _determine_multiplet(self, particle):
        """Determine which multiplet a particle belongs to"""
        classification = particle.get('Classification', [])
        classification_lower = [c.lower() for c in classification]

        if 'delta' in str(classification_lower):
            return 'decuplet'
        elif 'omega' in str(classification_lower):
            return 'decuplet'
        elif particle.get('_is_baryon'):
            return 'baryon_octet'
        elif particle.get('_is_meson'):
            return 'meson_octet'
        return 'other'

    def get_content_height(self, particles):
        """Calculate total content height"""
        return 700  # Fixed height for the plot diagram

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
