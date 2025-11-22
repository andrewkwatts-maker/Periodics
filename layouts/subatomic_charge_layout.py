"""
Charge Order Layout Renderer for Subatomic Particles
Groups particles by their electric charge
"""


class SubatomicChargeLayout:
    """Layout renderer that groups particles by charge"""

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
        Calculate positions for particles grouped by charge.

        Args:
            particles: List of particle dictionaries

        Returns:
            Dictionary mapping particle names to position data
        """
        layout_data = {}

        # Group by charge
        charge_groups = {}
        for p in particles:
            charge = p.get('Charge_e', 0)
            if charge not in charge_groups:
                charge_groups[charge] = []
            charge_groups[charge].append(p)

        y_offset = self.header_height + 20
        x_start = 50

        # Calculate columns
        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        # Charge colors
        charge_colors = {
            2: (255, 100, 100),    # +2 red
            1: (255, 183, 77),     # +1 orange
            0: (200, 200, 200),    # 0 gray
            -1: (100, 181, 246),   # -1 blue
            -2: (156, 39, 176),    # -2 purple
        }

        # Process charges in order (highest to lowest)
        for charge in sorted(charge_groups.keys(), reverse=True):
            group = charge_groups[charge]
            charge_str = f"+{charge}" if charge > 0 else str(charge)

            color = charge_colors.get(charge, (150, 150, 150))

            # Section header
            layout_data[f'_charge_{charge}_header'] = {
                'type': 'header',
                'x': x_start,
                'y': y_offset,
                'text': f'CHARGE: {charge_str} e',
                'subtitle': f'{len(group)} particle{"s" if len(group) != 1 else ""}',
                'color': color
            }
            y_offset += self.header_height

            # Sort group by mass
            group_sorted = sorted(group, key=lambda p: p.get('Mass_MeVc2', 0))

            for i, particle in enumerate(group_sorted):
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
                    'charge_group': charge
                }

            # Calculate rows for this group
            group_rows = (len(group) + cols - 1) // cols
            y_offset += group_rows * (self.card_height + self.card_spacing) + self.section_spacing

        return layout_data

    def get_content_height(self, particles):
        """Calculate total content height"""
        # Group by charge
        charge_groups = {}
        for p in particles:
            charge = p.get('Charge_e', 0)
            if charge not in charge_groups:
                charge_groups[charge] = []
            charge_groups[charge].append(p)

        available_width = self.widget_width - 100
        cols = max(1, available_width // (self.card_width + self.card_spacing))

        height = self.header_height + 20

        for charge, group in charge_groups.items():
            height += self.header_height
            rows = (len(group) + cols - 1) // cols
            height += rows * (self.card_height + self.card_spacing) + self.section_spacing

        return height + 50

    def update_dimensions(self, width, height):
        """Update layout dimensions"""
        self.widget_width = width
        self.widget_height = height
