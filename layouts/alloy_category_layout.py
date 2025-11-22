"""
Alloy Category Layout
Arranges alloys in a grid grouped by category (steels, bronzes, etc.).
"""

from typing import List, Dict
from core.alloy_enums import AlloyCategory


class AlloyCategoryLayout:
    """Category-grouped layout for alloys"""

    def __init__(self, widget_width: int, widget_height: int):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 160
        self.card_height = 180
        self.padding = 30
        self.spacing = 15
        self.group_spacing = 40
        self.header_height = 45

    def calculate_layout(self, alloys: List[Dict]) -> List[Dict]:
        """
        Calculate positions for alloys grouped by category.

        Args:
            alloys: List of alloy dictionaries

        Returns:
            List of alloys with position data added
        """
        if not alloys:
            return []

        # Group alloys by category
        groups = {}
        for alloy in alloys:
            category = alloy.get('category', 'Other')
            if category not in groups:
                groups[category] = []
            groups[category].append(alloy)

        positioned_alloys = []
        current_y = self.padding

        # Sort categories by predefined order
        category_order = [
            'Steel', 'Aluminum', 'Bronze', 'Brass', 'Copper',
            'Titanium', 'Nickel', 'Superalloy', 'Precious', 'Solder', 'Other'
        ]

        # Add any categories not in the predefined order
        for cat in sorted(groups.keys()):
            if cat not in category_order:
                category_order.append(cat)

        for category in category_order:
            group_alloys = groups.get(category, [])
            if not group_alloys:
                continue

            group_color = AlloyCategory.get_color(category)

            # Calculate cards per row
            available_width = self.widget_width - 2 * self.padding
            cols = max(1, int(available_width / (self.card_width + self.spacing)))

            # Add space for header
            current_y += self.header_height

            # Position alloys in this group
            for idx, alloy in enumerate(group_alloys):
                row = idx // cols
                col = idx % cols

                # Center the row
                items_in_row = min(cols, len(group_alloys) - row * cols)
                row_width = items_in_row * self.card_width + (items_in_row - 1) * self.spacing
                start_x = (self.widget_width - row_width) / 2

                x = start_x + col * (self.card_width + self.spacing)
                y = current_y + row * (self.card_height + self.spacing)

                alloy_copy = alloy.copy()
                alloy_copy['x'] = x
                alloy_copy['y'] = y
                alloy_copy['width'] = self.card_width
                alloy_copy['height'] = self.card_height
                alloy_copy['group'] = category
                alloy_copy['group_color'] = group_color
                alloy_copy['group_header_y'] = current_y - self.header_height
                positioned_alloys.append(alloy_copy)

            # Update current_y for next group
            rows = (len(group_alloys) + cols - 1) // cols
            current_y += rows * (self.card_height + self.spacing) + self.group_spacing

        return positioned_alloys

    def get_group_headers(self, alloys: List[Dict]) -> List[Dict]:
        """Get group header information for rendering"""
        if not alloys:
            return []

        headers = {}
        for alloy in alloys:
            group = alloy.get('group')
            if group and group not in headers:
                headers[group] = {
                    'name': group,
                    'y': alloy.get('group_header_y', 0),
                    'color': alloy.get('group_color', '#FFFFFF'),
                    'count': sum(1 for a in alloys if a.get('group') == group)
                }

        return list(headers.values())

    def get_alloy_at_position(self, x: float, y: float, alloys: List[Dict]) -> Dict:
        """Find alloy at given position."""
        for alloy in alloys:
            ax = alloy.get('x', 0)
            ay = alloy.get('y', 0)
            aw = alloy.get('width', self.card_width)
            ah = alloy.get('height', self.card_height)

            if ax <= x <= ax + aw and ay <= y <= ay + ah:
                return alloy

        return None

    def update_dimensions(self, width: int, height: int):
        """Update widget dimensions"""
        self.widget_width = width
        self.widget_height = height

    def get_content_height(self, alloys: List[Dict]) -> int:
        """Calculate total content height for scrolling"""
        if not alloys:
            return 0

        positioned = self.calculate_layout(alloys)
        if not positioned:
            return 0

        max_y = max(a.get('y', 0) + a.get('height', self.card_height) for a in positioned)
        return int(max_y + self.padding)
