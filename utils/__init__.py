"""Utility functions for calculations and helpers."""

from utils.physics_calculator import (
    PhysicsConstants,
    AtomCalculator,
    SubatomicCalculator,
    MoleculeCalculator
)

# Simulation schema for data-driven physics
from utils.simulation_schema import (
    # Enums
    ParticleType, SpinType, LatticeType,
    # Constants
    SimulationConstants,
    # Base dataclasses
    Position3D, Momentum3D, QuantumState, FormFactors,
    # Particle dataclasses
    QuarkSimulationData, HadronSimulationData, AtomSimulationData,
    MoleculeSimulationData, AlloySimulationData,
    # Propagation functions
    propagate_quark_to_hadron, propagate_hadrons_to_atom,
    propagate_atoms_to_molecule, propagate_elements_to_alloy,
    # Utility converters
    dict_to_quark, dict_to_atom,
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
    # Simulation schema exports
    'ParticleType', 'SpinType', 'LatticeType',
    'SimulationConstants',
    'Position3D', 'Momentum3D', 'QuantumState', 'FormFactors',
    'QuarkSimulationData', 'HadronSimulationData', 'AtomSimulationData',
    'MoleculeSimulationData', 'AlloySimulationData',
    'propagate_quark_to_hadron', 'propagate_hadrons_to_atom',
    'propagate_atoms_to_molecule', 'propagate_elements_to_alloy',
    'dict_to_quark', 'dict_to_atom',
]
