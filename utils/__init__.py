"""Utility functions for calculations and helpers."""

from utils.physics_calculator import (
    PhysicsConstants,
    AtomCalculator,
    SubatomicCalculator,
    MoleculeCalculator
)

# SDFRenderer requires PySide6, import conditionally
try:
    from utils.sdf_renderer import SDFRenderer
    _SDF_AVAILABLE = True
except ImportError:
    SDFRenderer = None
    _SDF_AVAILABLE = False

# Pure Python math utilities (no external dependencies)
from utils.pure_math import (
    factorial,
    double_factorial,
    genlaguerre,
    lpmv,
    GeneralizedLaguerre,
)

from utils.pure_array import (
    # Constants
    pi,
    # Math functions
    sqrt, cos, sin, acos, atan2,
    # Random utilities
    random_uniform, random_seed,
    # Vector class
    Vec3,
    # Nucleon generation
    generate_nucleon_positions,
    generate_shell_positions,
    # Utility functions
    lerp, clamp, smoothstep, distance,
)

__all__ = [
    'PhysicsConstants',
    'AtomCalculator',
    'SubatomicCalculator',
    'MoleculeCalculator',
    'SDFRenderer',
    # pure_math exports
    'factorial', 'double_factorial', 'genlaguerre', 'lpmv', 'GeneralizedLaguerre',
    # pure_array exports
    'pi',
    'sqrt', 'cos', 'sin', 'acos', 'atan2',
    'random_uniform', 'random_seed',
    'Vec3',
    'generate_nucleon_positions',
    'generate_shell_positions',
    'lerp', 'clamp', 'smoothstep', 'distance',
]
