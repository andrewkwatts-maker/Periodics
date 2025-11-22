"""
Comprehensive Simulation Schema
===============================

Defines all properties required for accurate simulation of particles and materials
at every level of the hierarchy:

Quarks → Hadrons → Nucleons → Atoms → Molecules → Alloys/Materials

Each level captures:
1. Intrinsic properties (mass, charge, spin, etc.)
2. Derived properties (calculated from sub-particles)
3. Positional data (location, orientation, velocity)
4. Quantum state (wavefunction, probability distributions)
5. Interaction data (forces, potentials, coupling constants)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import math


# =============================================================================
# Enums for particle classification
# =============================================================================

class ParticleType(Enum):
    QUARK = "quark"
    LEPTON = "lepton"
    BOSON = "boson"
    HADRON = "hadron"
    BARYON = "baryon"
    MESON = "meson"
    ATOM = "atom"
    MOLECULE = "molecule"
    ALLOY = "alloy"


class SpinType(Enum):
    FERMION = "fermion"  # half-integer spin
    BOSON = "boson"      # integer spin


class LatticeType(Enum):
    FCC = "FCC"
    BCC = "BCC"
    HCP = "HCP"
    BCT = "BCT"
    DIAMOND = "Diamond"
    SIMPLE_CUBIC = "SC"


# =============================================================================
# Physical Constants
# =============================================================================

class SimulationConstants:
    """Physical constants for simulation."""
    HBAR = 1.054571817e-34  # J·s
    C = 299792458  # m/s
    E_CHARGE = 1.602176634e-19  # C
    PROTON_MASS_KG = 1.67262192e-27  # kg
    NEUTRON_MASS_KG = 1.67492749e-27  # kg
    ELECTRON_MASS_KG = 9.1093837e-31  # kg
    BOHR_RADIUS_M = 5.29177210903e-11  # m
    FINE_STRUCTURE = 0.0072973525693
    RYDBERG_EV = 13.605693122994  # eV
    AMU_TO_KG = 1.66054e-27
    MEV_TO_KG = 1.78266192e-30
    FM_TO_M = 1e-15
    PM_TO_M = 1e-12
    NM_TO_M = 1e-9


# =============================================================================
# Base position and state classes
# =============================================================================

@dataclass
class Position3D:
    """3D position with uncertainty for quantum particles."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    uncertainty_x: float = 0.0  # Heisenberg uncertainty
    uncertainty_y: float = 0.0
    uncertainty_z: float = 0.0
    unit: str = "fm"  # femtometers for quarks/hadrons, pm for atoms

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def to_dict(self) -> Dict:
        return {
            'x': self.x, 'y': self.y, 'z': self.z,
            'uncertainty_x': self.uncertainty_x,
            'uncertainty_y': self.uncertainty_y,
            'uncertainty_z': self.uncertainty_z,
            'unit': self.unit
        }

    def distance_to(self, other: 'Position3D') -> float:
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )


@dataclass
class Momentum3D:
    """3D momentum with uncertainty."""
    px: float = 0.0
    py: float = 0.0
    pz: float = 0.0
    uncertainty_px: float = 0.0
    uncertainty_py: float = 0.0
    uncertainty_pz: float = 0.0
    unit: str = "MeV/c"

    def magnitude(self) -> float:
        return math.sqrt(self.px**2 + self.py**2 + self.pz**2)

    def to_dict(self) -> Dict:
        return {
            'px': self.px, 'py': self.py, 'pz': self.pz,
            'uncertainty_px': self.uncertainty_px,
            'uncertainty_py': self.uncertainty_py,
            'uncertainty_pz': self.uncertainty_pz,
            'unit': self.unit
        }


@dataclass
class QuantumState:
    """Complete quantum state for a particle."""
    # Principal quantum numbers
    n: Optional[int] = None  # principal
    l: Optional[int] = None  # orbital angular momentum
    m: Optional[int] = None  # magnetic
    s: Optional[float] = None  # spin projection

    # Wavefunction parameters
    wavefunction_type: str = "gaussian"  # or "hydrogen", "slater", etc.
    wavefunction_params: Dict[str, float] = field(default_factory=dict)

    # Probability distribution
    probability_density_type: str = "orbital"
    probability_params: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'n': self.n, 'l': self.l, 'm': self.m, 's': self.s,
            'wavefunction_type': self.wavefunction_type,
            'wavefunction_params': self.wavefunction_params,
            'probability_density_type': self.probability_density_type,
            'probability_params': self.probability_params
        }


@dataclass
class FormFactors:
    """Form factors for particle interactions."""
    # Electric form factor G_E(Q^2)
    electric: Dict[str, float] = field(default_factory=dict)
    # Magnetic form factor G_M(Q^2)
    magnetic: Dict[str, float] = field(default_factory=dict)
    # Axial form factor G_A(Q^2)
    axial: Dict[str, float] = field(default_factory=dict)
    # Scalar form factor
    scalar: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'electric': self.electric,
            'magnetic': self.magnetic,
            'axial': self.axial,
            'scalar': self.scalar
        }


# =============================================================================
# Quark level schema
# =============================================================================

@dataclass
class QuarkSimulationData:
    """Complete quark data for simulation."""
    # Identity
    name: str = ""
    symbol: str = ""
    flavor: str = ""  # up, down, strange, charm, bottom, top
    generation: int = 1  # 1, 2, or 3
    is_antiparticle: bool = False

    # Intrinsic properties (fundamental)
    mass_MeV: float = 0.0
    constituent_mass_MeV: float = 0.0  # Dressed mass
    charge_e: float = 0.0
    spin_hbar: float = 0.5
    color_charge: str = ""  # red, green, blue
    baryon_number: float = 1/3
    isospin: float = 0.0
    isospin_z: float = 0.0
    strangeness: int = 0
    charm: int = 0
    bottomness: int = 0
    topness: int = 0

    # Position and momentum
    position: Position3D = field(default_factory=Position3D)
    momentum: Momentum3D = field(default_factory=Momentum3D)

    # Quantum state
    quantum_state: QuantumState = field(default_factory=QuantumState)

    # Interaction coupling constants
    strong_coupling: float = 1.0  # αs at quark scale
    weak_coupling: float = 0.034  # GF
    em_coupling: float = 0.0  # proportional to charge^2 × α

    # Confinement parameters (for QCD simulation)
    string_tension_GeV_fm: float = 0.9
    confinement_radius_fm: float = 1.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'symbol': self.symbol,
            'flavor': self.flavor,
            'generation': self.generation,
            'is_antiparticle': self.is_antiparticle,
            'mass_MeV': self.mass_MeV,
            'constituent_mass_MeV': self.constituent_mass_MeV,
            'charge_e': self.charge_e,
            'spin_hbar': self.spin_hbar,
            'color_charge': self.color_charge,
            'baryon_number': self.baryon_number,
            'isospin': self.isospin,
            'isospin_z': self.isospin_z,
            'quantum_numbers': {
                'strangeness': self.strangeness,
                'charm': self.charm,
                'bottomness': self.bottomness,
                'topness': self.topness
            },
            'position': self.position.to_dict(),
            'momentum': self.momentum.to_dict(),
            'quantum_state': self.quantum_state.to_dict(),
            'couplings': {
                'strong': self.strong_coupling,
                'weak': self.weak_coupling,
                'em': self.em_coupling
            },
            'confinement': {
                'string_tension_GeV_fm': self.string_tension_GeV_fm,
                'confinement_radius_fm': self.confinement_radius_fm
            }
        }


# =============================================================================
# Hadron level schema
# =============================================================================

@dataclass
class HadronSimulationData:
    """Complete hadron data for simulation."""
    # Identity
    name: str = ""
    symbol: str = ""
    particle_type: str = ""  # baryon, meson, tetraquark, pentaquark
    pdg_id: Optional[int] = None

    # Composition - full quark data preserved
    quarks: List[QuarkSimulationData] = field(default_factory=list)
    quark_content_string: str = ""  # e.g., "uud" for proton

    # Intrinsic properties (derived from quarks)
    mass_MeV: float = 0.0
    mass_uncertainty_MeV: float = 0.0
    charge_e: float = 0.0
    spin_hbar: float = 0.0
    baryon_number: float = 0.0
    isospin: float = 0.0
    isospin_z: float = 0.0
    parity: int = 1
    c_parity: Optional[int] = None
    g_parity: Optional[int] = None

    # Size and structure
    charge_radius_fm: float = 0.0
    magnetic_radius_fm: float = 0.0
    rms_radius_fm: float = 0.0

    # Position and momentum (center of mass)
    position: Position3D = field(default_factory=Position3D)
    momentum: Momentum3D = field(default_factory=Momentum3D)

    # Form factors
    form_factors: FormFactors = field(default_factory=FormFactors)

    # Stability and decay
    is_stable: bool = False
    mean_lifetime_s: Optional[float] = None
    decay_width_MeV: Optional[float] = None
    decay_modes: List[Dict] = field(default_factory=list)

    # Magnetic properties
    magnetic_moment_nuclear_magneton: Optional[float] = None
    gyromagnetic_ratio: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'symbol': self.symbol,
            'particle_type': self.particle_type,
            'pdg_id': self.pdg_id,
            'quark_content': self.quark_content_string,
            'quarks': [q.to_dict() for q in self.quarks],
            'mass_MeV': self.mass_MeV,
            'mass_uncertainty_MeV': self.mass_uncertainty_MeV,
            'charge_e': self.charge_e,
            'spin_hbar': self.spin_hbar,
            'baryon_number': self.baryon_number,
            'isospin': {'I': self.isospin, 'I3': self.isospin_z},
            'parity': self.parity,
            'c_parity': self.c_parity,
            'g_parity': self.g_parity,
            'structure': {
                'charge_radius_fm': self.charge_radius_fm,
                'magnetic_radius_fm': self.magnetic_radius_fm,
                'rms_radius_fm': self.rms_radius_fm
            },
            'position': self.position.to_dict(),
            'momentum': self.momentum.to_dict(),
            'form_factors': self.form_factors.to_dict(),
            'stability': {
                'is_stable': self.is_stable,
                'mean_lifetime_s': self.mean_lifetime_s,
                'decay_width_MeV': self.decay_width_MeV,
                'decay_modes': self.decay_modes
            },
            'magnetic': {
                'moment_nuclear_magneton': self.magnetic_moment_nuclear_magneton,
                'gyromagnetic_ratio': self.gyromagnetic_ratio
            }
        }


# =============================================================================
# Atom level schema
# =============================================================================

@dataclass
class AtomSimulationData:
    """Complete atom data for simulation."""
    # Identity
    name: str = ""
    symbol: str = ""
    atomic_number: int = 0
    mass_number: int = 0

    # Nucleus - preserved hadron data
    proton_count: int = 0
    neutron_count: int = 0
    nuclear_spin: float = 0.0
    nuclear_parity: int = 1

    # Nuclear properties
    nuclear_mass_amu: float = 0.0
    nuclear_radius_fm: float = 0.0
    nuclear_binding_energy_MeV: float = 0.0
    nuclear_magnetic_moment: float = 0.0
    nuclear_quadrupole_moment: float = 0.0

    # Electron configuration
    electron_count: int = 0
    electron_configuration: str = ""
    electron_shells: List[int] = field(default_factory=list)
    block: str = ""  # s, p, d, f
    period: int = 0
    group: Optional[int] = None

    # Electron orbital data
    electron_orbitals: List[QuantumState] = field(default_factory=list)

    # Atomic properties
    atomic_mass_amu: float = 0.0
    ionization_energy_eV: float = 0.0
    electron_affinity_eV: float = 0.0
    electronegativity: float = 0.0
    atomic_radius_pm: float = 0.0
    covalent_radius_pm: float = 0.0
    van_der_waals_radius_pm: float = 0.0

    # Physical properties
    melting_point_K: Optional[float] = None
    boiling_point_K: Optional[float] = None
    density_g_cm3: Optional[float] = None

    # Spectroscopic data
    emission_wavelength_nm: Optional[float] = None
    emission_lines: List[Dict] = field(default_factory=list)

    # Position (for molecules/crystals)
    position: Position3D = field(default_factory=Position3D)

    # Isotope data
    isotopes: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'symbol': self.symbol,
            'atomic_number': self.atomic_number,
            'mass_number': self.mass_number,
            'nucleus': {
                'protons': self.proton_count,
                'neutrons': self.neutron_count,
                'spin': self.nuclear_spin,
                'parity': self.nuclear_parity,
                'mass_amu': self.nuclear_mass_amu,
                'radius_fm': self.nuclear_radius_fm,
                'binding_energy_MeV': self.nuclear_binding_energy_MeV,
                'magnetic_moment': self.nuclear_magnetic_moment,
                'quadrupole_moment': self.nuclear_quadrupole_moment
            },
            'electrons': {
                'count': self.electron_count,
                'configuration': self.electron_configuration,
                'shells': self.electron_shells,
                'orbitals': [o.to_dict() for o in self.electron_orbitals]
            },
            'classification': {
                'block': self.block,
                'period': self.period,
                'group': self.group
            },
            'properties': {
                'atomic_mass_amu': self.atomic_mass_amu,
                'ionization_energy_eV': self.ionization_energy_eV,
                'electron_affinity_eV': self.electron_affinity_eV,
                'electronegativity': self.electronegativity,
                'atomic_radius_pm': self.atomic_radius_pm,
                'covalent_radius_pm': self.covalent_radius_pm,
                'van_der_waals_radius_pm': self.van_der_waals_radius_pm,
                'melting_point_K': self.melting_point_K,
                'boiling_point_K': self.boiling_point_K,
                'density_g_cm3': self.density_g_cm3
            },
            'spectroscopy': {
                'emission_wavelength_nm': self.emission_wavelength_nm,
                'emission_lines': self.emission_lines
            },
            'position': self.position.to_dict(),
            'isotopes': self.isotopes
        }


# =============================================================================
# Molecule level schema
# =============================================================================

@dataclass
class MoleculeSimulationData:
    """Complete molecule data for simulation."""
    # Identity
    name: str = ""
    formula: str = ""
    iupac_name: str = ""

    # Composition - preserved atom data
    atoms: List[AtomSimulationData] = field(default_factory=list)
    atom_count: int = 0

    # Structure
    geometry: str = ""  # linear, bent, trigonal planar, etc.
    point_group: str = ""  # C2v, D3h, etc.
    bond_order: float = 0.0

    # Bonding
    bonds: List[Dict] = field(default_factory=list)  # [{atom1, atom2, type, length, energy}]
    bond_angles: List[Dict] = field(default_factory=list)
    dihedral_angles: List[Dict] = field(default_factory=list)

    # Electronic structure
    total_electrons: int = 0
    homo_energy_eV: Optional[float] = None
    lumo_energy_eV: Optional[float] = None
    homo_lumo_gap_eV: Optional[float] = None

    # Physical properties
    molecular_mass_amu: float = 0.0
    dipole_moment_D: float = 0.0
    polarizability: float = 0.0

    # Thermodynamic properties
    melting_point_K: Optional[float] = None
    boiling_point_K: Optional[float] = None
    density_g_cm3: Optional[float] = None

    # Vibrational data
    vibrational_modes: List[Dict] = field(default_factory=list)
    rotational_constants: Dict[str, float] = field(default_factory=dict)

    # Position and orientation
    center_of_mass: Position3D = field(default_factory=Position3D)
    orientation: Dict[str, float] = field(default_factory=dict)  # Euler angles

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'formula': self.formula,
            'iupac_name': self.iupac_name,
            'composition': {
                'atoms': [a.to_dict() for a in self.atoms],
                'atom_count': self.atom_count
            },
            'structure': {
                'geometry': self.geometry,
                'point_group': self.point_group,
                'bond_order': self.bond_order,
                'bonds': self.bonds,
                'bond_angles': self.bond_angles,
                'dihedral_angles': self.dihedral_angles
            },
            'electronic': {
                'total_electrons': self.total_electrons,
                'homo_eV': self.homo_energy_eV,
                'lumo_eV': self.lumo_energy_eV,
                'homo_lumo_gap_eV': self.homo_lumo_gap_eV
            },
            'properties': {
                'molecular_mass_amu': self.molecular_mass_amu,
                'dipole_moment_D': self.dipole_moment_D,
                'polarizability': self.polarizability,
                'melting_point_K': self.melting_point_K,
                'boiling_point_K': self.boiling_point_K,
                'density_g_cm3': self.density_g_cm3
            },
            'spectroscopy': {
                'vibrational_modes': self.vibrational_modes,
                'rotational_constants': self.rotational_constants
            },
            'position': {
                'center_of_mass': self.center_of_mass.to_dict(),
                'orientation': self.orientation
            }
        }


# =============================================================================
# Alloy level schema
# =============================================================================

@dataclass
class AlloySimulationData:
    """Complete alloy data for simulation."""
    # Identity
    name: str = ""
    formula: str = ""
    category: str = ""  # Steel, Aluminum, Titanium, etc.

    # Composition - preserved element data
    elements: List[AtomSimulationData] = field(default_factory=list)
    weight_fractions: List[float] = field(default_factory=list)
    atomic_fractions: List[float] = field(default_factory=list)

    # Crystal structure
    primary_structure: str = ""  # FCC, BCC, HCP
    lattice_parameter_pm: float = 0.0
    unit_cell_volume_pm3: float = 0.0
    packing_factor: float = 0.0
    coordination_number: int = 0
    space_group: str = ""

    # Atom positions in lattice
    atom_positions: List[Dict] = field(default_factory=list)

    # Physical properties
    density_g_cm3: float = 0.0
    melting_point_K: float = 0.0
    thermal_conductivity_W_mK: float = 0.0
    electrical_resistivity_Ohm_m: float = 0.0
    thermal_expansion_per_K: float = 0.0
    specific_heat_J_kgK: float = 0.0

    # Mechanical properties
    tensile_strength_MPa: float = 0.0
    yield_strength_MPa: float = 0.0
    youngs_modulus_GPa: float = 0.0
    shear_modulus_GPa: float = 0.0
    poissons_ratio: float = 0.0
    hardness_HB: float = 0.0
    elongation_percent: float = 0.0

    # Phase composition
    phases: List[Dict] = field(default_factory=list)
    phase_fractions: Dict[str, float] = field(default_factory=dict)

    # Microstructure
    grain_size_um: float = 0.0
    grain_boundary_energy_J_m2: float = 0.0
    dislocation_density_m2: float = 0.0

    # Defect data
    vacancy_concentration: float = 0.0
    interstitial_concentration: float = 0.0
    stacking_fault_energy_mJ_m2: float = 0.0

    # Corrosion
    pren: float = 0.0  # Pitting Resistance Equivalent Number
    corrosion_rating: str = ""

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'formula': self.formula,
            'category': self.category,
            'composition': {
                'elements': [e.to_dict() for e in self.elements],
                'weight_fractions': self.weight_fractions,
                'atomic_fractions': self.atomic_fractions
            },
            'crystal_structure': {
                'primary': self.primary_structure,
                'lattice_parameter_pm': self.lattice_parameter_pm,
                'unit_cell_volume_pm3': self.unit_cell_volume_pm3,
                'packing_factor': self.packing_factor,
                'coordination_number': self.coordination_number,
                'space_group': self.space_group,
                'atom_positions': self.atom_positions
            },
            'physical_properties': {
                'density_g_cm3': self.density_g_cm3,
                'melting_point_K': self.melting_point_K,
                'thermal_conductivity_W_mK': self.thermal_conductivity_W_mK,
                'electrical_resistivity_Ohm_m': self.electrical_resistivity_Ohm_m,
                'thermal_expansion_per_K': self.thermal_expansion_per_K,
                'specific_heat_J_kgK': self.specific_heat_J_kgK
            },
            'mechanical_properties': {
                'tensile_strength_MPa': self.tensile_strength_MPa,
                'yield_strength_MPa': self.yield_strength_MPa,
                'youngs_modulus_GPa': self.youngs_modulus_GPa,
                'shear_modulus_GPa': self.shear_modulus_GPa,
                'poissons_ratio': self.poissons_ratio,
                'hardness_HB': self.hardness_HB,
                'elongation_percent': self.elongation_percent
            },
            'phases': {
                'list': self.phases,
                'fractions': self.phase_fractions
            },
            'microstructure': {
                'grain_size_um': self.grain_size_um,
                'grain_boundary_energy_J_m2': self.grain_boundary_energy_J_m2,
                'dislocation_density_m2': self.dislocation_density_m2
            },
            'defects': {
                'vacancy_concentration': self.vacancy_concentration,
                'interstitial_concentration': self.interstitial_concentration,
                'stacking_fault_energy_mJ_m2': self.stacking_fault_energy_mJ_m2
            },
            'corrosion': {
                'pren': self.pren,
                'rating': self.corrosion_rating
            }
        }


# =============================================================================
# Property propagation functions
# =============================================================================

def propagate_quark_to_hadron(quarks: List[Dict]) -> HadronSimulationData:
    """
    Calculate all hadron properties from constituent quarks.
    Uses constituent quark model with QCD corrections.
    """
    hadron = HadronSimulationData()

    if not quarks:
        return hadron

    # Determine hadron type
    num_quarks = len(quarks)
    if num_quarks == 3:
        hadron.particle_type = "baryon"
    elif num_quarks == 2:
        hadron.particle_type = "meson"
    else:
        hadron.particle_type = "exotic"

    # Sum conserved quantities
    hadron.charge_e = sum(q.get('Charge_e', 0) for q in quarks)
    hadron.baryon_number = sum(q.get('BaryonNumber_B', 1/3) for q in quarks)
    hadron.isospin_z = sum(q.get('Isospin_I3', 0) for q in quarks)

    # Build quark content string
    symbols = [q.get('Symbol', '?') for q in quarks]
    hadron.quark_content_string = ''.join(symbols)

    # Calculate mass using constituent quark model
    total_mass = 0
    for q in quarks:
        current_mass = q.get('Mass_MeVc2', 0)
        # Add QCD dressing
        if current_mass < 10:  # light quarks
            constituent_mass = 336
        elif current_mass < 200:  # strange
            constituent_mass = 486
        else:  # heavy quarks
            constituent_mass = current_mass + 200
        total_mass += constituent_mass

    # Binding correction
    if hadron.particle_type == "baryon":
        hadron.mass_MeV = total_mass - 60
    else:
        hadron.mass_MeV = total_mass - 400

    # Estimate radius
    hadron.rms_radius_fm = 0.8 if hadron.particle_type == "baryon" else 0.6
    hadron.charge_radius_fm = hadron.rms_radius_fm * 0.9

    return hadron


# Tabulated experimental data for light nuclei (A <= 4)
# The Weizsacker semi-empirical mass formula doesn't work well for these
# Format: (Z, N) -> (atomic_mass_amu, binding_energy_MeV)
LIGHT_NUCLEI_DATA = {
    # Hydrogen isotopes
    (1, 0): (1.00783, 0.0),        # H-1 (protium) - single proton, no binding
    (1, 1): (2.01410, 2.22),       # H-2 (deuterium)
    (1, 2): (3.01605, 8.48),       # H-3 (tritium)
    # Helium isotopes
    (2, 1): (3.01603, 7.72),       # He-3
    (2, 2): (4.00260, 28.30),      # He-4 (alpha particle) - doubly magic
    # Lithium isotopes (included for completeness of very light nuclei)
    (3, 3): (6.01512, 31.99),      # Li-6
    (3, 4): (7.01600, 39.24),      # Li-7
    # Beryllium
    (4, 4): (8.00531, 56.50),      # Be-8 (unstable but useful for calculations)
    (4, 5): (9.01218, 58.16),      # Be-9
}


def propagate_hadrons_to_atom(
    protons: int,
    neutrons: int,
    electrons: int,
    proton_data: Optional[Dict] = None,
    neutron_data: Optional[Dict] = None
) -> AtomSimulationData:
    """
    Calculate all atomic properties from constituent hadrons.
    Uses tabulated values for light nuclei (A <= 4) and Weizsacker mass
    formula for heavier nuclei.
    """
    atom = AtomSimulationData()

    Z = protons
    N = neutrons
    A = Z + N

    atom.atomic_number = Z
    atom.mass_number = A
    atom.proton_count = Z
    atom.neutron_count = N
    atom.electron_count = electrons

    # Nuclear radius (fm)
    r0 = 1.2  # fm
    atom.nuclear_radius_fm = r0 * (A ** (1/3)) if A > 0 else 0

    # Electron mass constant
    electron_mass = 0.000548579

    # Check if we have tabulated data for light nuclei
    if (Z, N) in LIGHT_NUCLEI_DATA:
        # Use experimental values for light nuclei
        atomic_mass, binding_energy = LIGHT_NUCLEI_DATA[(Z, N)]
        atom.nuclear_binding_energy_MeV = binding_energy
        atom.atomic_mass_amu = atomic_mass
        atom.nuclear_mass_amu = atomic_mass - electrons * electron_mass
    else:
        # Use Weizsacker semi-empirical mass formula for heavier nuclei
        av, as_, ac, aa, ap = 15.75, 17.8, 0.711, 23.7, 11.2

        volume = av * A
        surface = -as_ * (A ** (2/3)) if A > 0 else 0
        coulomb = -ac * Z * (Z - 1) / (A ** (1/3)) if A > 0 else 0
        asymmetry = -aa * ((N - Z) ** 2) / A if A > 0 else 0

        # Pairing term
        if Z % 2 == 0 and N % 2 == 0:
            pairing = ap / (A ** 0.5) if A > 0 else 0
        elif Z % 2 == 1 and N % 2 == 1:
            pairing = -ap / (A ** 0.5) if A > 0 else 0
        else:
            pairing = 0

        atom.nuclear_binding_energy_MeV = volume + surface + coulomb + asymmetry + pairing

        # Atomic mass calculation
        proton_mass = proton_data.get('Mass_amu', 1.007276) if proton_data else 1.007276
        neutron_mass = neutron_data.get('Mass_amu', 1.008665) if neutron_data else 1.008665

        mass_defect = atom.nuclear_binding_energy_MeV / 931.494
        atom.atomic_mass_amu = Z * proton_mass + N * neutron_mass - mass_defect
        atom.nuclear_mass_amu = atom.atomic_mass_amu - electrons * electron_mass

    return atom


def propagate_atoms_to_molecule(
    atoms: List[Dict],
    bonds: List[Dict]
) -> MoleculeSimulationData:
    """
    Calculate all molecular properties from constituent atoms.
    Uses VSEPR and molecular orbital theory.
    """
    molecule = MoleculeSimulationData()

    if not atoms:
        return molecule

    molecule.atom_count = len(atoms)

    # Calculate molecular mass
    molecule.molecular_mass_amu = sum(
        a.get('atomic_mass', a.get('AtomicMass', 0))
        for a in atoms
    )

    # Total electrons
    molecule.total_electrons = sum(
        a.get('atomic_number', a.get('Z', 0))
        for a in atoms
    )

    # Generate formula
    element_counts = {}
    for a in atoms:
        sym = a.get('symbol', a.get('Symbol', '?'))
        element_counts[sym] = element_counts.get(sym, 0) + 1

    formula_parts = []
    for sym in sorted(element_counts.keys()):
        count = element_counts[sym]
        if count == 1:
            formula_parts.append(sym)
        else:
            formula_parts.append(f"{sym}{count}")
    molecule.formula = ''.join(formula_parts)

    molecule.bonds = bonds

    return molecule


def propagate_elements_to_alloy(
    elements: List[Dict],
    weight_fractions: List[float],
    lattice_type: str = "FCC"
) -> AlloySimulationData:
    """
    Calculate all alloy properties from constituent elements.
    Uses rule of mixtures and Vegard's law.
    """
    alloy = AlloySimulationData()

    if not elements or not weight_fractions:
        return alloy

    alloy.primary_structure = lattice_type
    alloy.weight_fractions = weight_fractions

    # Generate formula
    symbols = []
    for e, wf in zip(elements, weight_fractions):
        sym = e.get('symbol', e.get('Symbol', '?'))
        symbols.append(f"{sym}{int(wf*100)}")
    alloy.formula = '-'.join(symbols)

    # Calculate density (rule of mixtures)
    inv_density = 0
    for e, wf in zip(elements, weight_fractions):
        rho = e.get('density', 7.0)
        if rho > 0:
            inv_density += wf / rho
    alloy.density_g_cm3 = 1 / inv_density if inv_density > 0 else 7.0

    # Calculate melting point (weighted average with depression)
    mp_sum = 0
    for e, wf in zip(elements, weight_fractions):
        mp = e.get('melting_point', 1500)
        mp_sum += wf * mp

    num_components = len([wf for wf in weight_fractions if wf > 0.01])
    depression = 1.0 - 0.03 * (num_components - 1)
    alloy.melting_point_K = mp_sum * max(0.85, depression)

    # Lattice properties
    packing = {'FCC': 0.74, 'BCC': 0.68, 'HCP': 0.74}
    coord = {'FCC': 12, 'BCC': 8, 'HCP': 12}
    alloy.packing_factor = packing.get(lattice_type, 0.68)
    alloy.coordination_number = coord.get(lattice_type, 8)

    return alloy


# =============================================================================
# Utility functions
# =============================================================================

def dict_to_quark(data: Dict) -> QuarkSimulationData:
    """Convert dictionary to QuarkSimulationData."""
    quark = QuarkSimulationData()
    quark.name = data.get('Name', data.get('name', ''))
    quark.symbol = data.get('Symbol', data.get('symbol', ''))
    quark.mass_MeV = data.get('Mass_MeVc2', data.get('mass', 0))
    quark.charge_e = data.get('Charge_e', data.get('charge', 0))
    quark.spin_hbar = data.get('Spin_hbar', data.get('spin', 0.5))
    quark.baryon_number = data.get('BaryonNumber_B', 1/3)
    quark.isospin = data.get('Isospin_I', 0)
    quark.isospin_z = data.get('Isospin_I3', 0)
    quark.color_charge = data.get('ColorCharge', data.get('color', ''))
    return quark


def dict_to_atom(data: Dict) -> AtomSimulationData:
    """Convert dictionary to AtomSimulationData."""
    atom = AtomSimulationData()
    atom.name = data.get('Name', data.get('name', ''))
    atom.symbol = data.get('Symbol', data.get('symbol', ''))
    atom.atomic_number = data.get('Z', data.get('atomic_number', 0))
    atom.mass_number = data.get('A', data.get('mass_number', 0))
    atom.atomic_mass_amu = data.get('AtomicMass', data.get('atomic_mass', 0))
    atom.ionization_energy_eV = data.get('IonizationEnergy', data.get('ionization_energy', 0))
    atom.electronegativity = data.get('Electronegativity', data.get('electronegativity', 0))
    atom.atomic_radius_pm = data.get('AtomicRadius', data.get('atomic_radius', 0))
    return atom
