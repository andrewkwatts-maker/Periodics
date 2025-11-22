#!/usr/bin/env python3
"""
Enums for quark/particle visualization properties and encodings.
Centralizes all string-based property checking for the Quarks tab.
"""

from enum import Enum, auto


class QuarkLayoutMode(Enum):
    """Layout modes for particle visualization"""
    STANDARD_MODEL = "standard_model"  # Standard Model grid layout
    LINEAR = "linear"  # Linear arrangement by property
    CIRCULAR = "circular"  # Circular arrangement with categories
    ALTERNATIVE = "alternative"  # Alternative grouping (by interaction type)

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        for member in cls:
            if member.value == value:
                return member
        return cls.STANDARD_MODEL  # Default

    @classmethod
    def get_display_name(cls, mode):
        """Get display name for layout mode"""
        if isinstance(mode, str):
            mode = cls.from_string(mode)
        names = {
            cls.STANDARD_MODEL: "Standard Model",
            cls.LINEAR: "Linear Arrangement",
            cls.CIRCULAR: "Circular Layout",
            cls.ALTERNATIVE: "Alternative Grouping"
        }
        return names.get(mode, "Unknown")


class ParticleType(Enum):
    """Types of fundamental particles"""
    QUARK = "quark"
    LEPTON = "lepton"
    GAUGE_BOSON = "gauge_boson"
    SCALAR_BOSON = "scalar_boson"
    ANTIPARTICLE = "antiparticle"
    COMPOSITE = "composite"
    UNKNOWN = "unknown"

    @classmethod
    def from_classification(cls, classification_list):
        """Determine particle type from classification list"""
        if not classification_list:
            return cls.UNKNOWN

        classification_lower = [c.lower() for c in classification_list]

        if "quark" in classification_lower:
            return cls.QUARK
        elif "lepton" in classification_lower:
            return cls.LEPTON
        elif "gauge boson" in classification_lower or "force carrier" in classification_lower:
            return cls.GAUGE_BOSON
        elif "scalar boson" in classification_lower:
            return cls.SCALAR_BOSON
        elif any("anti" in c for c in classification_lower):
            return cls.ANTIPARTICLE
        elif "composite" in classification_lower or "hadron" in classification_lower:
            return cls.COMPOSITE
        return cls.UNKNOWN

    @classmethod
    def get_color(cls, particle_type):
        """Get default color for particle type (R, G, B)"""
        if isinstance(particle_type, str):
            particle_type = cls.from_string(particle_type)
        colors = {
            cls.QUARK: (230, 100, 100),  # Red-ish
            cls.LEPTON: (100, 180, 230),  # Blue
            cls.GAUGE_BOSON: (230, 180, 100),  # Orange/Gold
            cls.SCALAR_BOSON: (180, 100, 230),  # Purple
            cls.ANTIPARTICLE: (180, 180, 180),  # Gray
            cls.COMPOSITE: (100, 200, 150),  # Teal
            cls.UNKNOWN: (150, 150, 150)  # Gray
        }
        return colors.get(particle_type, (150, 150, 150))

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN


class QuarkProperty(Enum):
    """Particle properties that can be visualized"""
    MASS = "mass"
    CHARGE = "charge"
    SPIN = "spin"
    PARTICLE_TYPE = "particle_type"
    INTERACTION = "interaction"
    STABILITY = "stability"
    GENERATION = "generation"
    BARYON_NUMBER = "baryon_number"
    LEPTON_NUMBER = "lepton_number"
    ISOSPIN = "isospin"
    NONE = "none"

    @classmethod
    def from_string(cls, value):
        """Convert string to enum"""
        if value is None:
            return cls.NONE
        for member in cls:
            if member.value == value:
                return member
        return cls.NONE

    @classmethod
    def get_display_name(cls, prop):
        """Get display name for property"""
        if isinstance(prop, str):
            prop = cls.from_string(prop)
        names = {
            cls.MASS: "Mass",
            cls.CHARGE: "Charge",
            cls.SPIN: "Spin",
            cls.PARTICLE_TYPE: "Particle Type",
            cls.INTERACTION: "Interaction Forces",
            cls.STABILITY: "Stability",
            cls.GENERATION: "Generation",
            cls.BARYON_NUMBER: "Baryon Number",
            cls.LEPTON_NUMBER: "Lepton Number",
            cls.ISOSPIN: "Isospin",
            cls.NONE: "None"
        }
        return names.get(prop, "Unknown")

    @classmethod
    def get_color_properties(cls):
        """Properties suitable for color encoding"""
        return [
            cls.PARTICLE_TYPE,
            cls.MASS,
            cls.CHARGE,
            cls.SPIN,
            cls.INTERACTION,
            cls.STABILITY,
            cls.GENERATION,
            cls.NONE
        ]

    @classmethod
    def get_size_properties(cls):
        """Properties suitable for size encoding"""
        return [
            cls.MASS,
            cls.CHARGE,
            cls.SPIN,
            cls.BARYON_NUMBER,
            cls.LEPTON_NUMBER,
            cls.NONE
        ]

    @classmethod
    def get_intensity_properties(cls):
        """Properties suitable for intensity encoding"""
        return [
            cls.MASS,
            cls.SPIN,
            cls.STABILITY,
            cls.NONE
        ]


class QuarkGeneration(Enum):
    """Particle generations in the Standard Model"""
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FORCE_CARRIER = 0  # Bosons don't have generations
    UNKNOWN = -1

    @classmethod
    def from_particle_name(cls, name):
        """Determine generation from particle name"""
        name_lower = name.lower()

        # First generation
        first_gen = ['up', 'down', 'electron', 'electron neutrino']
        if any(p in name_lower for p in first_gen):
            return cls.FIRST

        # Second generation
        second_gen = ['charm', 'strange', 'muon']
        if any(p in name_lower for p in second_gen):
            return cls.SECOND

        # Third generation
        third_gen = ['top', 'bottom', 'tau']
        if any(p in name_lower for p in third_gen):
            return cls.THIRD

        # Bosons
        bosons = ['photon', 'gluon', 'w boson', 'z boson', 'higgs']
        if any(p in name_lower for p in bosons):
            return cls.FORCE_CARRIER

        return cls.UNKNOWN


class InteractionForce(Enum):
    """Fundamental forces"""
    STRONG = "Strong"
    ELECTROMAGNETIC = "Electromagnetic"
    WEAK = "Weak"
    GRAVITATIONAL = "Gravitational"

    @classmethod
    def get_color(cls, force):
        """Get color for interaction force"""
        if isinstance(force, str):
            force_map = {
                "Strong": cls.STRONG,
                "Electromagnetic": cls.ELECTROMAGNETIC,
                "Weak": cls.WEAK,
                "Gravitational": cls.GRAVITATIONAL
            }
            force = force_map.get(force, None)
            if force is None:
                return (150, 150, 150)

        colors = {
            cls.STRONG: (255, 100, 100),  # Red
            cls.ELECTROMAGNETIC: (100, 150, 255),  # Blue
            cls.WEAK: (255, 200, 100),  # Orange
            cls.GRAVITATIONAL: (150, 255, 150)  # Green
        }
        return colors.get(force, (150, 150, 150))
