"""
Molecule Polarity Layout
Arranges molecules grouped by polarity (Polar, Nonpolar, Ionic).
"""

from typing import List, Dict
from core.molecule_enums import MoleculePolarity


class MoleculePolarityLayout:
    """Polarity-grouped layout for molecules"""

    def __init__(self, widget_width: int, widget_height: int):
        self.widget_width = widget_width
        self.widget_height = widget_height
        self.card_width = 150
        self.card_height = 170
        self.padding = 30
        self.spacing = 15
        self.group_spacing = 40
        self.header_height = 40

    def calculate_layout(self, molecules: List[Dict]) -> List[Dict]:
        """
        Calculate positions for molecules grouped by polarity.

        Args:
            molecules: List of molecule dictionaries

        Returns:
            List of molecules with position data added
        """
        if not molecules:
            return []

        # Group molecules by polarity
        groups = {
            'Polar': [],
            'Nonpolar': [],
            'Ionic': []
        }

        for mol in molecules:
            polarity = mol.get('polarity', 'Unknown')
            if polarity in groups:
                groups[polarity].append(mol)
            else:
                groups['Nonpolar'].append(mol)  # Default to nonpolar

        positioned_molecules = []
        current_y = self.padding

        # Order of groups
        group_order = ['Polar', 'Nonpolar', 'Ionic']

        for group_name in group_order:
            group_mols = groups.get(group_name, [])
            if not group_mols:
                continue

            # Add group header position info
            group_color = MoleculePolarity.get_color(group_name)

            # Calculate cards per row
            available_width = self.widget_width - 2 * self.padding
            cols = max(1, int(available_width / (self.card_width + self.spacing)))

            # Add space for header
            current_y += self.header_height

            # Position molecules in this group
            for idx, mol in enumerate(group_mols):
                row = idx // cols
                col = idx % cols

                # Center the row
                items_in_row = min(cols, len(group_mols) - row * cols)
                row_width = items_in_row * self.card_width + (items_in_row - 1) * self.spacing
                start_x = (self.widget_width - row_width) / 2

                x = start_x + col * (self.card_width + self.spacing)
                y = current_y + row * (self.card_height + self.spacing)

                mol_copy = mol.copy()
                mol_copy['x'] = x
                mol_copy['y'] = y
                mol_copy['width'] = self.card_width
                mol_copy['height'] = self.card_height
                mol_copy['group'] = group_name
                mol_copy['group_color'] = group_color
                mol_copy['group_header_y'] = current_y - self.header_height
                positioned_molecules.append(mol_copy)

            # Update current_y for next group
            rows = (len(group_mols) + cols - 1) // cols
            current_y += rows * (self.card_height + self.spacing) + self.group_spacing

        return positioned_molecules

    def get_group_headers(self, molecules: List[Dict]) -> List[Dict]:
        """Get group header information for rendering"""
        if not molecules:
            return []

        # Find unique groups from positioned molecules
        headers = {}
        for mol in molecules:
            group = mol.get('group')
            if group and group not in headers:
                headers[group] = {
                    'name': group,
                    'y': mol.get('group_header_y', 0),
                    'color': mol.get('group_color', '#FFFFFF')
                }

        return list(headers.values())

    def get_molecule_at_position(self, x: float, y: float, molecules: List[Dict]) -> Dict:
        """Find molecule at given position."""
        for mol in molecules:
            mx = mol.get('x', 0)
            my = mol.get('y', 0)
            mw = mol.get('width', self.card_width)
            mh = mol.get('height', self.card_height)

            if mx <= x <= mx + mw and my <= y <= my + mh:
                return mol

        return None

    def update_dimensions(self, width: int, height: int):
        """Update widget dimensions"""
        self.widget_width = width
        self.widget_height = height

    def get_content_height(self, molecules: List[Dict]) -> int:
        """Calculate total content height for scrolling"""
        if not molecules:
            return 0

        positioned = self.calculate_layout(molecules)
        if not positioned:
            return 0

        max_y = max(m.get('y', 0) + m.get('height', self.card_height) for m in positioned)
        return int(max_y + self.padding)
