"""
Element Data Loader
Loads element data from JSON files on application startup.
This replaces hardcoded data with data-driven configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ElementDataLoader:
    """Loads element data from JSON files"""

    def __init__(self, elements_dir: Optional[str] = None):
        """
        Initialize the loader.

        Args:
            elements_dir: Path to directory containing element JSON files.
                         If None, uses default 'data/elements' directory.
        """
        if elements_dir is None:
            # Default to data/elements relative to this file
            base_dir = Path(__file__).parent
            elements_dir = base_dir / "elements"

        self.elements_dir = Path(elements_dir)
        self.elements: List[Dict] = []
        self.elements_by_symbol: Dict[str, Dict] = {}
        self.elements_by_z: Dict[int, Dict] = {}

    def load_all_elements(self) -> List[Dict]:
        """
        Load all element data from JSON files.

        Returns:
            List of element dictionaries sorted by atomic number.
        """
        if not self.elements_dir.exists():
            raise FileNotFoundError(f"Elements directory not found: {self.elements_dir}")

        # Find all JSON files matching pattern: ###_XX.json (e.g., 001_H.json)
        json_files = sorted(self.elements_dir.glob("*.json"))

        if not json_files:
            raise ValueError(f"No element JSON files found in {self.elements_dir}")

        loaded_elements = []

        for json_file in json_files:
            try:
                element_data = self._load_element_file(json_file)
                loaded_elements.append(element_data)
            except Exception as e:
                print(f"Warning: Failed to load {json_file.name}: {e}")
                continue

        # Sort by atomic number
        loaded_elements.sort(key=lambda e: e['atomic_number'])

        # Store in instance variables
        self.elements = loaded_elements
        self.elements_by_symbol = {e['symbol']: e for e in loaded_elements}
        self.elements_by_z = {e['atomic_number']: e for e in loaded_elements}

        return loaded_elements

    def _load_element_file(self, filepath: Path) -> Dict:
        """
        Load a single element JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            Dictionary containing element data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required fields
        required_fields = [
            'symbol', 'name', 'atomic_number', 'block', 'period',
            'ionization_energy', 'atomic_radius', 'density'
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {filepath.name}")

        return data

    def get_element_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get element data by symbol (e.g., 'H', 'C', 'Fe')"""
        return self.elements_by_symbol.get(symbol)

    def get_element_by_z(self, z: int) -> Optional[Dict]:
        """Get element data by atomic number"""
        return self.elements_by_z.get(z)

    def get_all_elements(self) -> List[Dict]:
        """Get all loaded elements"""
        return self.elements

    def get_element_count(self) -> int:
        """Get total number of loaded elements"""
        return len(self.elements)


def create_fallback_element_data():
    """
    Create fallback element data when JSON files are not available.
    This is a temporary bridge during the refactoring process.

    Returns:
        Dictionary with basic element data for testing/fallback
    """
    return {
        'H': {
            'symbol': 'H',
            'name': 'Hydrogen',
            'atomic_number': 1,
            'block': 's',
            'period': 1,
            'group': 1,
            'ionization_energy': 13.598,
            'electronegativity': 2.2,
            'atomic_radius': 53,
            'melting_point': 14.01,
            'boiling_point': 20.28,
            'density': 0.00008988,
            'electron_affinity': 72.8,
            'valence_electrons': 1,
            'isotopes': []
        },
        'C': {
            'symbol': 'C',
            'name': 'Carbon',
            'atomic_number': 6,
            'block': 'p',
            'period': 2,
            'group': 14,
            'ionization_energy': 11.260,
            'electronegativity': 2.55,
            'atomic_radius': 67,
            'melting_point': 3823,
            'boiling_point': 4098,
            'density': 2.267,
            'electron_affinity': 121.9,
            'valence_electrons': 4,
            'isotopes': []
        }
    }
