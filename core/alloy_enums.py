"""
Enums for alloy visualization properties and encodings.
Centralizes all alloy-related property checking to prevent typos and improve maintainability.
"""

from enum import Enum, auto


class AlloyLayoutMode(Enum):
    """Layout modes for alloy visualization"""
    CATEGORY = "category"
    PROPERTY_SCATTER = "property_scatter"
    COMPOSITION = "composition"
    LATTICE = "lattice"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        for member in cls:
            if member.value == value:
                return member
        return cls.CATEGORY  # Default to category

    @classmethod
    def get_display_name(cls, mode):
        """Get UI display name for a layout mode"""
        if isinstance(mode, str):
            mode = cls.from_string(mode)

        display_names = {
            cls.CATEGORY: "By Category",
            cls.PROPERTY_SCATTER: "Property Plot",
            cls.COMPOSITION: "By Primary Element",
            cls.LATTICE: "By Crystal Structure"
        }
        return display_names.get(mode, "Unknown")


class AlloyCategory(Enum):
    """Categories of alloys"""
    STEEL = "Steel"
    ALUMINUM = "Aluminum"
    BRONZE = "Bronze"
    BRASS = "Brass"
    COPPER = "Copper"
    TITANIUM = "Titanium"
    NICKEL = "Nickel"
    PRECIOUS = "Precious"
    SOLDER = "Solder"
    SUPERALLOY = "Superalloy"
    OTHER = "Other"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        if value is None:
            return cls.OTHER
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.OTHER

    @classmethod
    def get_color(cls, category):
        """Get color for a category"""
        if isinstance(category, str):
            category = cls.from_string(category)

        colors = {
            cls.STEEL: "#607D8B",       # Blue Grey
            cls.ALUMINUM: "#90CAF9",    # Light Blue
            cls.BRONZE: "#CD7F32",      # Bronze
            cls.BRASS: "#D4AF37",       # Brass gold
            cls.COPPER: "#B87333",      # Copper
            cls.TITANIUM: "#8E8E8E",    # Grey
            cls.NICKEL: "#A8A8A8",      # Light Grey
            cls.PRECIOUS: "#FFD700",    # Gold
            cls.SOLDER: "#708090",      # Slate Grey
            cls.SUPERALLOY: "#FF6B35",  # Orange
            cls.OTHER: "#9E9E9E"        # Grey
        }
        return colors.get(category, "#9E9E9E")


class CrystalStructure(Enum):
    """Crystal structure types for alloys"""
    FCC = "FCC"      # Face-Centered Cubic
    BCC = "BCC"      # Body-Centered Cubic
    HCP = "HCP"      # Hexagonal Close-Packed
    BCT = "BCT"      # Body-Centered Tetragonal
    ORTHORHOMBIC = "Orthorhombic"
    TETRAGONAL = "Tetragonal"
    MIXED = "Mixed"
    UNKNOWN = "Unknown"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        if value is None:
            return cls.UNKNOWN
        for member in cls:
            if member.value.upper() == value.upper():
                return member
        return cls.UNKNOWN

    @classmethod
    def get_color(cls, structure):
        """Get color for a crystal structure"""
        if isinstance(structure, str):
            structure = cls.from_string(structure)

        colors = {
            cls.FCC: "#4CAF50",         # Green
            cls.BCC: "#2196F3",         # Blue
            cls.HCP: "#9C27B0",         # Purple
            cls.BCT: "#FF9800",         # Orange
            cls.ORTHORHOMBIC: "#E91E63", # Pink
            cls.TETRAGONAL: "#00BCD4",  # Cyan
            cls.MIXED: "#795548",       # Brown
            cls.UNKNOWN: "#9E9E9E"      # Grey
        }
        return colors.get(structure, "#9E9E9E")

    @classmethod
    def get_description(cls, structure):
        """Get description for a crystal structure"""
        if isinstance(structure, str):
            structure = cls.from_string(structure)

        descriptions = {
            cls.FCC: "Face-Centered Cubic - High ductility, common in austenitic steels and aluminum",
            cls.BCC: "Body-Centered Cubic - High strength at room temperature, common in ferritic steels",
            cls.HCP: "Hexagonal Close-Packed - Limited slip systems, common in titanium and zinc",
            cls.BCT: "Body-Centered Tetragonal - Martensitic structure, very hard",
            cls.ORTHORHOMBIC: "Orthorhombic - Less symmetric structure",
            cls.TETRAGONAL: "Tetragonal - Stretched cubic structure",
            cls.MIXED: "Multiple crystal structures present",
            cls.UNKNOWN: "Unknown crystal structure"
        }
        return descriptions.get(structure, "Unknown crystal structure")


class AlloyProperty(Enum):
    """Alloy properties that can be visualized or used for ordering"""
    # Basic properties
    NAME = "name"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"

    # Physical properties
    DENSITY = "density"
    MELTING_POINT = "melting_point"
    THERMAL_CONDUCTIVITY = "thermal_conductivity"
    ELECTRICAL_RESISTIVITY = "electrical_resistivity"
    SPECIFIC_HEAT = "specific_heat"

    # Mechanical properties
    TENSILE_STRENGTH = "tensile_strength"
    YIELD_STRENGTH = "yield_strength"
    HARDNESS = "hardness"
    ELONGATION = "elongation"
    YOUNGS_MODULUS = "youngs_modulus"

    # Lattice properties
    CRYSTAL_STRUCTURE = "crystal_structure"
    LATTICE_PARAMETER = "lattice_parameter"
    PACKING_FACTOR = "packing_factor"

    # Special value
    NONE = "none"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum, return NONE if not found"""
        if value is None:
            return cls.NONE
        for member in cls:
            if member.value == value:
                return member
        return cls.NONE

    @classmethod
    def get_display_name(cls, prop):
        """Get UI display name for a property"""
        if isinstance(prop, str):
            prop = cls.from_string(prop)

        display_names = {
            cls.NAME: "Name",
            cls.CATEGORY: "Category",
            cls.SUBCATEGORY: "Sub-Category",
            cls.DENSITY: "Density",
            cls.MELTING_POINT: "Melting Point",
            cls.THERMAL_CONDUCTIVITY: "Thermal Conductivity",
            cls.ELECTRICAL_RESISTIVITY: "Electrical Resistivity",
            cls.SPECIFIC_HEAT: "Specific Heat",
            cls.TENSILE_STRENGTH: "Tensile Strength",
            cls.YIELD_STRENGTH: "Yield Strength",
            cls.HARDNESS: "Hardness",
            cls.ELONGATION: "Elongation",
            cls.YOUNGS_MODULUS: "Young's Modulus",
            cls.CRYSTAL_STRUCTURE: "Crystal Structure",
            cls.LATTICE_PARAMETER: "Lattice Parameter",
            cls.PACKING_FACTOR: "Packing Factor",
            cls.NONE: "None"
        }
        return display_names.get(prop, "Unknown")

    @classmethod
    def get_unit(cls, prop):
        """Get unit for a property"""
        if isinstance(prop, str):
            prop = cls.from_string(prop)

        units = {
            cls.DENSITY: "g/cm³",
            cls.MELTING_POINT: "K",
            cls.THERMAL_CONDUCTIVITY: "W/m·K",
            cls.ELECTRICAL_RESISTIVITY: "Ω·m",
            cls.SPECIFIC_HEAT: "J/kg·K",
            cls.TENSILE_STRENGTH: "MPa",
            cls.YIELD_STRENGTH: "MPa",
            cls.HARDNESS: "HB",
            cls.ELONGATION: "%",
            cls.YOUNGS_MODULUS: "GPa",
            cls.LATTICE_PARAMETER: "pm",
            cls.PACKING_FACTOR: ""
        }
        return units.get(prop, "")

    @classmethod
    def get_scatter_x_properties(cls):
        """Get properties suitable for scatter plot X axis"""
        return [
            cls.DENSITY,
            cls.YIELD_STRENGTH,
            cls.TENSILE_STRENGTH,
            cls.HARDNESS,
            cls.YOUNGS_MODULUS,
            cls.MELTING_POINT
        ]

    @classmethod
    def get_scatter_y_properties(cls):
        """Get properties suitable for scatter plot Y axis"""
        return [
            cls.TENSILE_STRENGTH,
            cls.YIELD_STRENGTH,
            cls.ELONGATION,
            cls.HARDNESS,
            cls.THERMAL_CONDUCTIVITY,
            cls.MELTING_POINT
        ]


class ComponentRole(Enum):
    """Roles of component elements in alloys"""
    BASE = "Base"
    STRENGTHENING = "Strengthening"
    CORROSION_RESISTANCE = "Corrosion Resistance"
    STABILIZER = "Stabilizer"
    HARDENING = "Hardening"
    GRAIN_REFINER = "Grain Refiner"
    DEOXIDIZER = "Deoxidizer"
    IMPURITY = "Impurity"
    OTHER = "Other"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        if value is None:
            return cls.OTHER
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        # Handle special cases
        if "austenite" in value.lower():
            return cls.STABILIZER
        if "ferrite" in value.lower():
            return cls.STABILIZER
        return cls.OTHER

    @classmethod
    def get_color(cls, role):
        """Get color for a component role"""
        if isinstance(role, str):
            role = cls.from_string(role)

        colors = {
            cls.BASE: "#607D8B",
            cls.STRENGTHENING: "#F44336",
            cls.CORROSION_RESISTANCE: "#4CAF50",
            cls.STABILIZER: "#2196F3",
            cls.HARDENING: "#FF9800",
            cls.GRAIN_REFINER: "#9C27B0",
            cls.DEOXIDIZER: "#00BCD4",
            cls.IMPURITY: "#9E9E9E",
            cls.OTHER: "#795548"
        }
        return colors.get(role, "#9E9E9E")


# Element colors for alloy composition visualization
ELEMENT_COLORS = {
    "Fe": "#C0C0C0",    # Iron - Silver
    "Cr": "#6699FF",    # Chromium - Blue
    "Ni": "#99FF99",    # Nickel - Light Green
    "C": "#333333",     # Carbon - Dark Grey
    "Mn": "#FF99FF",    # Manganese - Pink
    "Si": "#FFCC00",    # Silicon - Yellow
    "Mo": "#CC99FF",    # Molybdenum - Light Purple
    "V": "#FF6600",     # Vanadium - Orange
    "Al": "#E0E0E0",    # Aluminum - Light Grey
    "Cu": "#B87333",    # Copper - Copper
    "Zn": "#C0C0FF",    # Zinc - Light Blue
    "Ti": "#8E8E8E",    # Titanium - Grey
    "W": "#6666CC",     # Tungsten - Blue-Grey
    "Co": "#3366FF",    # Cobalt - Blue
    "N": "#99CCFF",     # Nitrogen - Light Blue
    "P": "#FF9999",     # Phosphorus - Light Red
    "S": "#FFFF66",     # Sulfur - Yellow
    "Sn": "#B0B0B0",    # Tin - Grey
    "Pb": "#666666",    # Lead - Dark Grey
    "Ag": "#C0C0C0",    # Silver - Silver
    "Au": "#FFD700",    # Gold - Gold
    "Nb": "#99CC99",    # Niobium - Green-Grey
    "default": "#AAAAAA"
}


def get_element_color(symbol):
    """Get color for an element symbol"""
    return ELEMENT_COLORS.get(symbol, ELEMENT_COLORS["default"])


# IPF (Inverse Pole Figure) coloring for crystallographic orientations
def get_ipf_color(orientation):
    """
    Get IPF color for a crystallographic orientation.
    orientation: tuple of (phi1, phi, phi2) Euler angles in degrees
    Returns RGB tuple (0-255)
    """
    phi1, phi, phi2 = orientation

    # Simplified IPF coloring based on Euler angles
    # In reality, this requires proper crystallographic calculations
    r = int((phi1 / 360) * 255)
    g = int((phi / 90) * 255)
    b = int((phi2 / 90) * 255)

    return (r, g, b)
