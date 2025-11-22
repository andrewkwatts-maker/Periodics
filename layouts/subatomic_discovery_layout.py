"""
Discovery Timeline Layout Renderer for Subatomic Particles
Displays particles arranged chronologically by discovery year
X-axis: Discovery year
Y-axis: Mass (showing progression of accessible energies)
"""

import math


class SubatomicDiscoveryLayout:
    """Layout renderer showing particle discovery timeline"""

    def __init__(self, widget_width, widget_height):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 120
        self.card_height = 150
        self.card_spacing = 15
        self.header_height = 40
        self.timeline_height = 60

        # Timeline bounds (typical particle physics history)
        self.year_min = 1895  # Near discovery of electron
        self.year_max = 2020
        self.timeline_margin = 100

    def calculate_layout(self, particles):
        """
        Calculate positions for particles on discovery timeline.

        Args:
            particles: List of particle dictionaries

        Returns:
            Dictionary mapping particle names to position data
        """
        layout_data = {}

        y_start = 30
        x_start = 50

        # Header
        layout_data['_discovery_header'] = {
            'type': 'header',
            'x': x_start,
            'y': y_start,
            'text': 'DISCOVERY TIMELINE',
            'subtitle': 'Chronological particle discoveries with mass distribution',
            'color': (255, 152, 0)  # Orange
        }

        # Separate particles with and without discovery dates
        particles_with_date = []
        particles_without_date = []

        for p in particles:
            discovery = p.get('Discovery', {})
            year = discovery.get('Year') if isinstance(discovery, dict) else None

            if year:
                particles_with_date.append((p, year))
            else:
                particles_without_date.append(p)

        # Sort by year
        particles_with_date.sort(key=lambda x: x[1])

        # Calculate timeline area
        timeline_left = self.timeline_margin
        timeline_right = self.widget_width - self.timeline_margin
        timeline_width = timeline_right - timeline_left

        timeline_y = y_start + self.header_height + 40

        # Get actual year range from data
        if particles_with_date:
            actual_min_year = min(p[1] for p in particles_with_date)
            actual_max_year = max(p[1] for p in particles_with_date)
            # Add some padding
            self.year_min = max(1890, actual_min_year - 5)
            self.year_max = min(2025, actual_max_year + 5)

        # Store timeline info for axis rendering
        layout_data['_discovery_timeline'] = {
            'type': 'timeline_axis',
            'left': timeline_left,
            'right': timeline_right,
            'y': timeline_y,
            'year_min': self.year_min,
            'year_max': self.year_max,
            'markers': self._get_era_markers()
        }

        # Position particles on timeline
        plot_top = timeline_y + self.timeline_height + 20
        plot_height = 400  # Space for mass distribution

        def year_to_x(year):
            """Convert year to x position"""
            if year < self.year_min:
                year = self.year_min
            if year > self.year_max:
                year = self.year_max

            normalized = (year - self.year_min) / (self.year_max - self.year_min)
            return timeline_left + normalized * timeline_width

        # Get mass range for Y positioning
        masses = [p.get('Mass_MeVc2', 0) for p, _ in particles_with_date]
        if masses:
            mass_min = min(m for m in masses if m > 0) if any(m > 0 for m in masses) else 1
            mass_max = max(masses)
            # Use log scale for mass
            log_mass_min = math.log10(mass_min) if mass_min > 0 else 0
            log_mass_max = math.log10(mass_max) if mass_max > 0 else 4
        else:
            log_mass_min, log_mass_max = 0, 4

        def mass_to_y(mass):
            """Convert mass to y position (log scale)"""
            if mass <= 0:
                return plot_top + plot_height - 50

            log_mass = math.log10(mass)
            if log_mass_max == log_mass_min:
                normalized = 0.5
            else:
                normalized = (log_mass - log_mass_min) / (log_mass_max - log_mass_min)

            # Invert: higher mass at top
            return plot_top + plot_height - (normalized * (plot_height - 100))

        # Track positions to handle overlap
        position_grid = {}

        # Place particles with discovery dates
        for p, year in particles_with_date:
            mass = p.get('Mass_MeVc2', 100)

            x = year_to_x(year) - self.card_width / 2
            y = mass_to_y(mass) - self.card_height / 2

            # Handle overlapping particles
            grid_key = (round(x / 80), round(y / 100))
            if grid_key in position_grid:
                offset = position_grid[grid_key] * 30
                x += offset % 60
                y += (offset // 2) * 20
                position_grid[grid_key] += 1
            else:
                position_grid[grid_key] = 1

            # Get discovery info
            discovery = p.get('Discovery', {})
            location = discovery.get('Location', 'Unknown') if isinstance(discovery, dict) else 'Unknown'

            layout_data[p['Name']] = {
                'type': 'particle',
                'x': x,
                'y': y,
                'width': self.card_width,
                'height': self.card_height,
                'particle': p,
                'discovery_year': year,
                'discovery_location': location,
                'era': self._get_era(year)
            }

        # Add era bands for visual reference
        layout_data['_eras'] = {
            'type': 'era_bands',
            'eras': [
                {
                    'name': 'Classical Era',
                    'start': 1895,
                    'end': 1932,
                    'color': (100, 100, 150, 50),
                    'y_start': plot_top,
                    'y_end': plot_top + plot_height
                },
                {
                    'name': 'Nuclear Era',
                    'start': 1932,
                    'end': 1947,
                    'color': (100, 150, 100, 50),
                    'y_start': plot_top,
                    'y_end': plot_top + plot_height
                },
                {
                    'name': 'Strange Particles',
                    'start': 1947,
                    'end': 1964,
                    'color': (150, 100, 100, 50),
                    'y_start': plot_top,
                    'y_end': plot_top + plot_height
                },
                {
                    'name': 'Quark Model Era',
                    'start': 1964,
                    'end': 1995,
                    'color': (150, 150, 100, 50),
                    'y_start': plot_top,
                    'y_end': plot_top + plot_height
                },
                {
                    'name': 'Modern Era',
                    'start': 1995,
                    'end': 2020,
                    'color': (100, 150, 150, 50),
                    'y_start': plot_top,
                    'y_end': plot_top + plot_height
                }
            ],
            'timeline_left': timeline_left,
            'timeline_right': timeline_right,
            'year_min': self.year_min,
            'year_max': self.year_max
        }

        # Place particles without discovery dates in a separate section
        if particles_without_date:
            unknown_y = plot_top + plot_height + 80

            layout_data['_unknown_date_header'] = {
                'type': 'subheader',
                'x': x_start,
                'y': unknown_y,
                'text': 'Discovery Date Unknown',
                'color': (150, 150, 150)
            }
            unknown_y += 35

            available_width = self.widget_width - 100
            cols = max(1, available_width // (self.card_width + self.card_spacing))

            for i, p in enumerate(particles_without_date):
                row = i // cols
                col = i % cols
                x = x_start + col * (self.card_width + self.card_spacing)
                y = unknown_y + row * (self.card_height + self.card_spacing)

                layout_data[p['Name']] = {
                    'type': 'particle',
                    'x': x,
                    'y': y,
                    'width': self.card_width,
                    'height': self.card_height,
                    'particle': p,
                    'discovery_year': None,
                    'era': 'unknown'
                }

        return layout_data

    def _get_era_markers(self):
        """Get historical era markers for the timeline"""
        return [
            {'year': 1897, 'label': '1897\nElectron', 'major': True},
            {'year': 1911, 'label': '1911\nNucleus'},
            {'year': 1919, 'label': '1919\nProton', 'major': True},
            {'year': 1932, 'label': '1932\nNeutron', 'major': True},
            {'year': 1947, 'label': '1947\nPion', 'major': True},
            {'year': 1950, 'label': '1950\nStrange'},
            {'year': 1964, 'label': '1964\nQuark Model', 'major': True},
            {'year': 1974, 'label': '1974\nJ/psi', 'major': True},
            {'year': 1977, 'label': '1977\nUpsilon'},
            {'year': 1995, 'label': '1995\nTop Quark', 'major': True},
            {'year': 2012, 'label': '2012\nHiggs', 'major': True},
        ]

    def _get_era(self, year):
        """Determine which era a discovery belongs to"""
        if year < 1932:
            return 'classical'
        elif year < 1947:
            return 'nuclear'
        elif year < 1964:
            return 'strange'
        elif year < 1995:
            return 'quark_model'
        else:
            return 'modern'

    def get_content_height(self, particles):
        """Calculate total content height"""
        # Count particles without dates
        without_date = 0
        for p in particles:
            discovery = p.get('Discovery', {})
            if isinstance(discovery, dict):
                if not discovery.get('Year'):
                    without_date += 1
            else:
                without_date += 1

        height = self.header_height + self.timeline_height + 500  # Main plot area

        if without_date > 0:
            available_width = self.widget_width - 100
            cols = max(1, available_width // (self.card_width + self.card_spacing))
            rows = (without_date + cols - 1) // cols
            height += 100 + rows * (self.card_height + self.card_spacing)

        return max(height, 700)

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
