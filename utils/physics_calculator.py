"""
Physics Calculations Module
Provides formula-based calculations for creating particles from constituents.
All formulas are physics-based, not hardcoded lookup values.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


# ==================== Physical Constants ====================

class PhysicsConstants:
    """Fundamental physical constants"""
    # Masses in atomic mass units (u) and MeV/c²
    PROTON_MASS_U = 1.007276466621  # u
    NEUTRON_MASS_U = 1.008664915  # u
    ELECTRON_MASS_U = 0.000548579909065  # u

    PROTON_MASS_MEV = 938.27208816  # MeV/c²
    NEUTRON_MASS_MEV = 939.56542052  # MeV/c²
    ELECTRON_MASS_MEV = 0.51099895  # MeV/c²

    # Quark masses (current quark masses in MeV/c²)
    UP_QUARK_MASS_MEV = 2.2
    DOWN_QUARK_MASS_MEV = 4.7
    STRANGE_QUARK_MASS_MEV = 95.0
    CHARM_QUARK_MASS_MEV = 1275.0
    BOTTOM_QUARK_MASS_MEV = 4180.0
    TOP_QUARK_MASS_MEV = 173100.0

    # Quark charges (in units of e)
    UP_QUARK_CHARGE = 2/3
    DOWN_QUARK_CHARGE = -1/3
    STRANGE_QUARK_CHARGE = -1/3
    CHARM_QUARK_CHARGE = 2/3
    BOTTOM_QUARK_CHARGE = -1/3
    TOP_QUARK_CHARGE = 2/3

    # Other constants
    RYDBERG_ENERGY_EV = 13.605693122994  # eV
    BOHR_RADIUS_PM = 52.9177210903  # pm
    FINE_STRUCTURE = 0.0072973525693  # α
    AVOGADRO = 6.02214076e23  # mol⁻¹

    # Nuclear constants
    NUCLEAR_RADIUS_CONST = 1.25  # fm, r₀ for R = r₀ * A^(1/3)
    BINDING_ENERGY_VOLUME = 15.75  # MeV, a_v
    BINDING_ENERGY_SURFACE = 17.8  # MeV, a_s
    BINDING_ENERGY_COULOMB = 0.711  # MeV, a_c
    BINDING_ENERGY_ASYMMETRY = 23.7  # MeV, a_a
    BINDING_ENERGY_PAIRING = 11.2  # MeV, a_p


# ==================== Atom Creation from Nucleons ====================

class AtomCalculator:
    """
    Calculate atomic properties from protons, neutrons, and electrons.
    Uses semi-empirical formulas from nuclear and atomic physics.
    """

    @staticmethod
    def calculate_atomic_mass(protons: int, neutrons: int) -> float:
        """
        Calculate atomic mass using semi-empirical mass formula.
        Mass = Z*m_p + N*m_n - B/c² where B is binding energy

        Args:
            protons: Number of protons (Z)
            neutrons: Number of neutrons (N)

        Returns:
            Atomic mass in atomic mass units (u)
        """
        Z = protons
        N = neutrons
        A = Z + N  # Mass number

        if A == 0:
            return 0.0

        # Calculate binding energy using semi-empirical mass formula (Weizsäcker formula)
        # B = a_v*A - a_s*A^(2/3) - a_c*Z²/A^(1/3) - a_a*(N-Z)²/A + δ

        a_v = PhysicsConstants.BINDING_ENERGY_VOLUME
        a_s = PhysicsConstants.BINDING_ENERGY_SURFACE
        a_c = PhysicsConstants.BINDING_ENERGY_COULOMB
        a_a = PhysicsConstants.BINDING_ENERGY_ASYMMETRY
        a_p = PhysicsConstants.BINDING_ENERGY_PAIRING

        # Volume term
        B = a_v * A

        # Surface term
        B -= a_s * (A ** (2/3))

        # Coulomb term
        if A > 0:
            B -= a_c * (Z ** 2) / (A ** (1/3))

        # Asymmetry term
        B -= a_a * ((N - Z) ** 2) / A

        # Pairing term
        if Z % 2 == 0 and N % 2 == 0:
            delta = a_p / (A ** 0.5)  # Even-even
        elif Z % 2 == 1 and N % 2 == 1:
            delta = -a_p / (A ** 0.5)  # Odd-odd
        else:
            delta = 0  # Even-odd or odd-even
        B += delta

        # Convert binding energy to mass deficit (MeV to u)
        # 1 u = 931.494 MeV/c²
        mass_deficit_u = B / 931.494

        # Total mass
        mass = Z * PhysicsConstants.PROTON_MASS_U + N * PhysicsConstants.NEUTRON_MASS_U - mass_deficit_u

        return round(mass, 6)

    @staticmethod
    def calculate_ionization_energy(protons: int) -> float:
        """
        Estimate first ionization energy using modified Rydberg formula.
        IE ≈ 13.6 * Z_eff² / n² where Z_eff is effective nuclear charge

        Uses Slater's rules for shielding estimation.
        """
        Z = protons
        if Z == 0:
            return 0.0

        # Determine electron configuration and outermost shell
        # Using aufbau principle approximation
        shell_config = AtomCalculator._get_shell_configuration(Z)
        n = shell_config['n']  # Principal quantum number of outermost electron

        # Calculate effective nuclear charge using Slater's rules (simplified)
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        # Ionization energy using hydrogen-like formula with corrections
        IE = PhysicsConstants.RYDBERG_ENERGY_EV * (Z_eff ** 2) / (n ** 2)

        # Apply empirical corrections for many-electron atoms
        # Correction factor based on periodic trends
        correction = 1.0
        if Z > 2:
            # Penetration and screening corrections
            l = shell_config.get('l', 0)
            if l == 0:  # s orbital
                correction = 1.0
            elif l == 1:  # p orbital
                correction = 0.85
            elif l == 2:  # d orbital
                correction = 0.7
            elif l == 3:  # f orbital
                correction = 0.6

        return round(IE * correction, 3)

    @staticmethod
    def calculate_electronegativity(protons: int) -> float:
        """
        Estimate electronegativity using Mulliken scale converted to Pauling.
        χ_Mulliken = (IE + EA) / 2
        χ_Pauling ≈ 0.359 * χ_Mulliken^0.5 + 0.744

        Uses Allred-Rochow formula as alternative:
        χ = 0.359 * Z_eff / r² + 0.744
        """
        Z = protons
        if Z == 0:
            return 0.0

        # Get shell configuration
        shell_config = AtomCalculator._get_shell_configuration(Z)
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        # Calculate covalent radius approximation
        r = AtomCalculator.calculate_atomic_radius(Z)
        if r == 0:
            r = 100  # Default

        # Allred-Rochow formula (r in Angstroms)
        r_angstrom = r / 100  # pm to Angstrom

        if r_angstrom > 0:
            chi = 0.359 * Z_eff / (r_angstrom ** 2) + 0.744
        else:
            chi = 0.0

        # Clamp to reasonable range
        chi = max(0.0, min(4.0, chi))

        # Noble gases have ~0 electronegativity
        if AtomCalculator._is_noble_gas(Z):
            chi = 0.0

        return round(chi, 2)

    @staticmethod
    def calculate_atomic_radius(protons: int) -> int:
        """
        Estimate atomic radius using Slater's rules and quantum mechanical scaling.
        r ≈ a₀ * n² / Z_eff
        """
        Z = protons
        if Z == 0:
            return 0

        shell_config = AtomCalculator._get_shell_configuration(Z)
        n = shell_config['n']
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        if Z_eff <= 0:
            Z_eff = 1

        # Radius formula: r = a₀ * n² / Z_eff
        r = PhysicsConstants.BOHR_RADIUS_PM * (n ** 2) / Z_eff

        # Apply empirical corrections for d and f block
        block = AtomCalculator._get_block(Z)
        if block == 'd':
            r *= 0.8  # d-block contraction
        elif block == 'f':
            r *= 0.75  # lanthanide/actinide contraction

        return int(round(r))

    @staticmethod
    def calculate_melting_point(protons: int, neutrons: int) -> float:
        """
        Estimate melting point using empirical correlations.
        Based on atomic radius, binding energy, and periodic trends.
        """
        Z = protons
        if Z == 0:
            return 0.0

        # Base estimation using cohesive energy correlation
        # Melting point correlates with binding energy and atomic density

        A = Z + neutrons
        radius = AtomCalculator.calculate_atomic_radius(Z)

        if radius == 0:
            radius = 100

        # Empirical formula based on periodic trends
        # Higher Z_eff and smaller radius → higher melting point
        shell_config = AtomCalculator._get_shell_configuration(Z)
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        # Base melting point estimation
        block = AtomCalculator._get_block(Z)

        if block == 's':
            if Z <= 2:  # H, He
                base_mp = 20 * Z
            else:
                base_mp = 300 + 100 * (Z_eff / shell_config['n'])
        elif block == 'p':
            base_mp = 200 + 150 * Z_eff / radius * 10
        elif block == 'd':
            # Transition metals have higher melting points
            base_mp = 1000 + 200 * Z_eff / radius * 10
        elif block == 'f':
            base_mp = 800 + 150 * Z_eff / radius * 10
        else:
            base_mp = 300

        # Apply corrections
        if AtomCalculator._is_noble_gas(Z):
            base_mp = 5 + Z * 3  # Noble gases have very low melting points

        return round(max(0.0, base_mp), 1)

    @staticmethod
    def calculate_boiling_point(protons: int, neutrons: int) -> float:
        """
        Estimate boiling point based on melting point and Trouton's rule.
        For metals: BP ≈ MP * 1.5 to 3
        """
        mp = AtomCalculator.calculate_melting_point(protons, neutrons)

        block = AtomCalculator._get_block(protons)

        if AtomCalculator._is_noble_gas(protons):
            ratio = 1.1
        elif block == 's' and protons <= 2:
            ratio = 1.4
        elif block in ['d', 'f']:
            ratio = 1.8
        else:
            ratio = 1.5

        return round(mp * ratio, 1)

    @staticmethod
    def calculate_density(protons: int, neutrons: int) -> float:
        """
        Estimate density using atomic mass and radius.
        ρ ≈ M / (4/3 * π * r³ * N_A) with packing factor
        """
        Z = protons
        if Z == 0:
            return 0.0

        mass = AtomCalculator.calculate_atomic_mass(protons, neutrons)
        radius = AtomCalculator.calculate_atomic_radius(protons)

        if radius == 0:
            radius = 100

        # Convert radius from pm to cm
        r_cm = radius * 1e-10

        # Volume of atom in cm³
        V_atom = (4/3) * math.pi * (r_cm ** 3)

        # Assume face-centered cubic packing (0.74 packing efficiency)
        packing = 0.74

        # Density in g/cm³
        # mass in u, need to convert to g
        mass_g = mass / PhysicsConstants.AVOGADRO

        if V_atom > 0:
            density = mass_g / V_atom * packing
        else:
            density = 1.0

        # Apply empirical corrections based on actual periodic trends
        block = AtomCalculator._get_block(Z)
        if block == 's' and Z <= 2:
            density *= 0.001  # Gases
        elif AtomCalculator._is_noble_gas(Z):
            density *= 0.001  # Gases

        return round(max(0.0001, density), 4)

    @staticmethod
    def calculate_electron_affinity(protons: int) -> float:
        """
        Estimate electron affinity using periodic trends.
        EA increases across period, decreases down group.
        """
        Z = protons
        if Z == 0:
            return 0.0

        shell_config = AtomCalculator._get_shell_configuration(Z)
        n = shell_config['n']
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        # Base EA from effective nuclear charge
        # EA ≈ k * Z_eff / r²
        r = AtomCalculator.calculate_atomic_radius(Z)
        if r == 0:
            r = 100

        r_angstrom = r / 100

        base_ea = 50 * Z_eff / (r_angstrom ** 2)

        # Corrections based on orbital filling
        block = AtomCalculator._get_block(Z)
        valence = AtomCalculator._get_valence_electrons(Z)

        # Filled and half-filled shells have lower EA
        if block == 's' and valence == 2:
            base_ea *= 0.1  # Filled s shell
        elif block == 'p' and valence == 8:
            base_ea *= 0.0  # Noble gases
        elif block == 'p' and valence == 5:
            base_ea *= 0.5  # Half-filled p
        elif block == 'd' and valence in [5, 10]:
            base_ea *= 0.3  # Half or fully filled d

        # Halogens have high EA
        if block == 'p' and valence == 7:
            base_ea *= 2.0

        return round(max(0.0, min(400.0, base_ea)), 1)

    @staticmethod
    def get_block_period_group(protons: int) -> Tuple[str, int, Optional[int]]:
        """
        Determine block, period, and group from atomic number.
        Uses aufbau principle.
        """
        Z = protons
        if Z == 0:
            return ('s', 1, 1)

        block = AtomCalculator._get_block(Z)
        period = AtomCalculator._get_period(Z)
        group = AtomCalculator._get_group(Z)

        return (block, period, group)

    @staticmethod
    def get_electron_configuration(protons: int) -> str:
        """Generate electron configuration string."""
        Z = protons
        if Z == 0:
            return ""

        # Orbital order following aufbau principle
        orbitals = [
            (1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6),
            (4, 's', 2), (3, 'd', 10), (4, 'p', 6), (5, 's', 2), (4, 'd', 10),
            (5, 'p', 6), (6, 's', 2), (4, 'f', 14), (5, 'd', 10), (6, 'p', 6),
            (7, 's', 2), (5, 'f', 14), (6, 'd', 10), (7, 'p', 6)
        ]

        superscripts = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                       '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}

        config = []
        electrons_remaining = Z

        for n, l, max_e in orbitals:
            if electrons_remaining <= 0:
                break

            e_in_orbital = min(electrons_remaining, max_e)
            electrons_remaining -= e_in_orbital

            # Convert number to superscript
            sup = ''.join(superscripts[c] for c in str(e_in_orbital))
            config.append(f"{n}{l}{sup}")

        return ' '.join(config)

    @staticmethod
    def estimate_primary_emission_wavelength(protons: int) -> float:
        """
        Estimate primary emission wavelength using Rydberg formula.
        λ = hc / ΔE for n=2 to n=1 transition (or similar)
        """
        Z = protons
        if Z == 0:
            return 500.0

        # Use hydrogen-like formula with effective charge
        shell_config = AtomCalculator._get_shell_configuration(Z)
        Z_eff = AtomCalculator._calculate_z_effective(Z, shell_config)

        # Balmer series transition (n=3 to n=2) scaled by Z_eff
        # λ = 91.2 nm / Z_eff² * (1/n₁² - 1/n₂²)⁻¹

        n1, n2 = 2, 3
        factor = 1 / (n1**2) - 1 / (n2**2)

        if factor > 0 and Z_eff > 0:
            wavelength = 91.2 / (Z_eff ** 2 * factor)
        else:
            wavelength = 500.0

        # Clamp to reasonable range
        wavelength = max(100.0, min(1000.0, wavelength))

        return round(wavelength, 1)

    @staticmethod
    def determine_stability(protons: int, neutrons: int) -> Tuple[bool, Optional[str]]:
        """
        Determine if nucleus is stable and estimate half-life if not.
        Uses band of stability calculations.
        """
        Z = protons
        N = neutrons
        A = Z + N

        if A == 0 or Z == 0:
            return (False, None)

        # Ratio of N/Z for stability
        ratio = N / Z if Z > 0 else 0

        # Band of stability parameters
        # For light nuclei: N ≈ Z
        # For heavy nuclei: N ≈ 1.5Z

        if Z <= 20:
            optimal_ratio = 1.0
            tolerance = 0.15
        elif Z <= 40:
            optimal_ratio = 1.0 + 0.015 * (Z - 20)
            tolerance = 0.12
        elif Z <= 82:
            optimal_ratio = 1.3 + 0.005 * (Z - 40)
            tolerance = 0.10
        else:
            optimal_ratio = 1.5
            tolerance = 0.08

        # Check stability
        deviation = abs(ratio - optimal_ratio)
        is_stable = deviation <= tolerance and Z <= 82

        # All elements with Z > 82 are unstable
        if Z > 82:
            is_stable = False

        # Estimate half-life for unstable nuclei
        half_life = None
        if not is_stable:
            if Z > 110:
                half_life = f"{round(0.001 * 1000 / (Z - 110), 1)} milliseconds"
            elif Z > 100:
                half_life = f"{round(100 / (Z - 100), 0)} days"
            elif Z > 82:
                half_life = f"{round(1e6 / (Z - 82), 0)} years"
            elif deviation > tolerance * 2:
                half_life = f"{round(1 / deviation, 1)} seconds"
            else:
                half_life = f"{round(100 / deviation, 0)} years"

        return (is_stable, half_life)

    # ==================== Helper Methods ====================

    @staticmethod
    def _get_shell_configuration(Z: int) -> Dict:
        """Get shell configuration for given Z."""
        # Determine principal quantum number and angular momentum
        if Z <= 2:
            return {'n': 1, 'l': 0, 'electrons_in_shell': Z}
        elif Z <= 10:
            return {'n': 2, 'l': 1 if Z > 4 else 0, 'electrons_in_shell': Z - 2}
        elif Z <= 18:
            return {'n': 3, 'l': 1 if Z > 12 else 0, 'electrons_in_shell': Z - 10}
        elif Z <= 36:
            if Z <= 20:
                return {'n': 4, 'l': 0, 'electrons_in_shell': Z - 18}
            elif Z <= 30:
                return {'n': 3, 'l': 2, 'electrons_in_shell': Z - 18}
            else:
                return {'n': 4, 'l': 1, 'electrons_in_shell': Z - 28}
        elif Z <= 54:
            if Z <= 38:
                return {'n': 5, 'l': 0, 'electrons_in_shell': Z - 36}
            elif Z <= 48:
                return {'n': 4, 'l': 2, 'electrons_in_shell': Z - 36}
            else:
                return {'n': 5, 'l': 1, 'electrons_in_shell': Z - 46}
        elif Z <= 86:
            if Z <= 56:
                return {'n': 6, 'l': 0, 'electrons_in_shell': Z - 54}
            elif Z <= 71:
                return {'n': 4, 'l': 3, 'electrons_in_shell': Z - 54}
            elif Z <= 80:
                return {'n': 5, 'l': 2, 'electrons_in_shell': Z - 54}
            else:
                return {'n': 6, 'l': 1, 'electrons_in_shell': Z - 78}
        else:
            if Z <= 88:
                return {'n': 7, 'l': 0, 'electrons_in_shell': Z - 86}
            elif Z <= 103:
                return {'n': 5, 'l': 3, 'electrons_in_shell': Z - 86}
            elif Z <= 112:
                return {'n': 6, 'l': 2, 'electrons_in_shell': Z - 86}
            else:
                return {'n': 7, 'l': 1, 'electrons_in_shell': Z - 110}

    @staticmethod
    def _calculate_z_effective(Z: int, shell_config: Dict) -> float:
        """Calculate effective nuclear charge using Slater's rules."""
        n = shell_config['n']

        # Simplified Slater's rules
        if n == 1:
            sigma = 0.30 * (Z - 1)  # 1s electrons shield each other
        elif n == 2:
            sigma = 2 * 0.85 + (Z - 3) * 0.35 if Z > 2 else 0
        elif n == 3:
            sigma = 2 * 1.0 + 8 * 0.85 + (Z - 11) * 0.35 if Z > 10 else 0
        else:
            # General approximation for higher shells
            inner_electrons = Z - shell_config.get('electrons_in_shell', 1)
            sigma = inner_electrons * 0.85

        Z_eff = Z - sigma
        return max(1.0, Z_eff)

    @staticmethod
    def _get_block(Z: int) -> str:
        """Determine block from atomic number."""
        if Z == 0:
            return 's'

        # s-block
        s_block = [1, 2, 3, 4, 11, 12, 19, 20, 37, 38, 55, 56, 87, 88]
        if Z in s_block:
            return 's'

        # f-block (lanthanides and actinides)
        if 57 <= Z <= 71 or 89 <= Z <= 103:
            return 'f'

        # d-block
        d_ranges = [(21, 30), (39, 48), (72, 80), (104, 112)]
        for start, end in d_ranges:
            if start <= Z <= end:
                return 'd'

        # p-block (everything else)
        return 'p'

    @staticmethod
    def _get_period(Z: int) -> int:
        """Determine period from atomic number."""
        if Z <= 2:
            return 1
        elif Z <= 10:
            return 2
        elif Z <= 18:
            return 3
        elif Z <= 36:
            return 4
        elif Z <= 54:
            return 5
        elif Z <= 86:
            return 6
        else:
            return 7

    @staticmethod
    def _get_group(Z: int) -> Optional[int]:
        """Determine group from atomic number."""
        block = AtomCalculator._get_block(Z)

        if block == 'f':
            return None  # Lanthanides/actinides don't have group numbers

        period = AtomCalculator._get_period(Z)

        # Calculate position within period
        period_starts = {1: 1, 2: 3, 3: 11, 4: 19, 5: 37, 6: 55, 7: 87}
        start = period_starts.get(period, 1)
        position = Z - start

        if block == 's':
            return position + 1
        elif block == 'd':
            return position + 3 - (2 if period >= 4 else 0)
        elif block == 'p':
            # p-block starts at different positions
            p_starts = {2: 5, 3: 13, 4: 31, 5: 49, 6: 81, 7: 113}
            p_start = p_starts.get(period, start)
            return 13 + (Z - p_start)

        return None

    @staticmethod
    def _get_valence_electrons(Z: int) -> int:
        """Get number of valence electrons."""
        block = AtomCalculator._get_block(Z)
        group = AtomCalculator._get_group(Z)

        if group is not None:
            if group <= 2:
                return group
            elif group >= 13:
                return group - 10
            else:  # d-block
                return group - 2
        else:  # f-block
            period = AtomCalculator._get_period(Z)
            if period == 6:
                return Z - 54  # Lanthanides
            else:
                return Z - 86  # Actinides

    @staticmethod
    def _is_noble_gas(Z: int) -> bool:
        """Check if element is a noble gas."""
        return Z in [2, 10, 18, 36, 54, 86, 118]

    @classmethod
    def create_atom_from_particles(cls, protons: int, neutrons: int, electrons: int,
                                   name: str = None, symbol: str = None) -> Dict:
        """
        Create a complete atom JSON structure from constituent particles.

        Args:
            protons: Number of protons
            neutrons: Number of neutrons
            electrons: Number of electrons (normally equals protons for neutral atom)
            name: Optional custom name
            symbol: Optional custom symbol

        Returns:
            Complete atom data dictionary
        """
        Z = protons
        A = protons + neutrons

        block, period, group = cls.get_block_period_group(Z)
        is_stable, half_life = cls.determine_stability(protons, neutrons)

        # Generate default name and symbol if not provided
        if symbol is None:
            symbol = f"X{Z}"
        if name is None:
            name = f"Element-{Z}"

        atom_data = {
            "symbol": symbol,
            "name": name,
            "atomic_number": Z,
            "atomic_mass": cls.calculate_atomic_mass(protons, neutrons),
            "block": block,
            "period": period,
            "group": group,
            "ionization_energy": cls.calculate_ionization_energy(Z),
            "electronegativity": cls.calculate_electronegativity(Z),
            "atomic_radius": cls.calculate_atomic_radius(Z),
            "melting_point": cls.calculate_melting_point(protons, neutrons),
            "boiling_point": cls.calculate_boiling_point(protons, neutrons),
            "density": cls.calculate_density(protons, neutrons),
            "electron_affinity": cls.calculate_electron_affinity(Z),
            "valence_electrons": cls._get_valence_electrons(Z),
            "electron_configuration": cls.get_electron_configuration(Z),
            "primary_emission_wavelength": cls.estimate_primary_emission_wavelength(Z),
            "visible_emission_wavelength": cls.estimate_primary_emission_wavelength(Z),
            "isotopes": [
                {
                    "mass_number": A,
                    "neutrons": neutrons,
                    "abundance": 100.0,
                    "is_stable": is_stable,
                    "half_life": half_life
                }
            ],
            "_created_from": {
                "protons": protons,
                "neutrons": neutrons,
                "electrons": electrons
            }
        }

        return atom_data


# ==================== Subatomic Particle Creation from Quarks ====================

class SubatomicCalculator:
    """
    Calculate subatomic particle properties from quark composition.
    """

    QUARK_PROPERTIES = {
        'u': {'charge': 2/3, 'mass_mev': 2.2, 'spin': 0.5, 'baryon': 1/3, 'name': 'Up'},
        'd': {'charge': -1/3, 'mass_mev': 4.7, 'spin': 0.5, 'baryon': 1/3, 'name': 'Down'},
        's': {'charge': -1/3, 'mass_mev': 95.0, 'spin': 0.5, 'baryon': 1/3, 'name': 'Strange'},
        'c': {'charge': 2/3, 'mass_mev': 1275.0, 'spin': 0.5, 'baryon': 1/3, 'name': 'Charm'},
        'b': {'charge': -1/3, 'mass_mev': 4180.0, 'spin': 0.5, 'baryon': 1/3, 'name': 'Bottom'},
        't': {'charge': 2/3, 'mass_mev': 173100.0, 'spin': 0.5, 'baryon': 1/3, 'name': 'Top'},
        # Antiquarks
        'u̅': {'charge': -2/3, 'mass_mev': 2.2, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-up'},
        'd̅': {'charge': 1/3, 'mass_mev': 4.7, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-down'},
        's̅': {'charge': 1/3, 'mass_mev': 95.0, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-strange'},
        'c̅': {'charge': -2/3, 'mass_mev': 1275.0, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-charm'},
        'b̅': {'charge': 1/3, 'mass_mev': 4180.0, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-bottom'},
        't̅': {'charge': -2/3, 'mass_mev': 173100.0, 'spin': 0.5, 'baryon': -1/3, 'name': 'Anti-top'},
    }

    @classmethod
    def calculate_charge(cls, quarks: List[str]) -> float:
        """Calculate total charge from quark composition."""
        total = 0.0
        for q in quarks:
            if q in cls.QUARK_PROPERTIES:
                total += cls.QUARK_PROPERTIES[q]['charge']
        return round(total, 6)

    @classmethod
    def calculate_mass(cls, quarks: List[str]) -> float:
        """
        Calculate hadron mass from quarks.
        Note: Actual mass is much higher due to QCD binding energy.
        Uses empirical scaling factors.
        """
        # Sum constituent quark masses
        quark_mass_sum = 0.0
        for q in quarks:
            if q in cls.QUARK_PROPERTIES:
                quark_mass_sum += cls.QUARK_PROPERTIES[q]['mass_mev']

        # QCD binding contribution (empirical)
        # Most of hadron mass comes from gluon field energy
        num_quarks = len(quarks)

        if num_quarks == 3:  # Baryon
            # Binding energy contributes ~300 MeV per quark
            binding_per_quark = 300.0
            mass = quark_mass_sum + num_quarks * binding_per_quark
        elif num_quarks == 2:  # Meson
            # Mesons are lighter
            binding_per_quark = 150.0
            mass = quark_mass_sum + num_quarks * binding_per_quark
        else:
            mass = quark_mass_sum

        return round(mass, 2)

    @classmethod
    def calculate_spin(cls, quarks: List[str], aligned: bool = True) -> float:
        """
        Calculate total spin from quark spins.
        Quarks can be aligned (parallel) or anti-aligned.
        """
        num_quarks = len(quarks)

        if num_quarks == 3:  # Baryon
            # Spin 1/2 (one anti-aligned) or 3/2 (all aligned)
            if aligned:
                return 1.5  # All parallel
            else:
                return 0.5  # Ground state baryons
        elif num_quarks == 2:  # Meson
            # Spin 0 (anti-aligned) or 1 (aligned)
            if aligned:
                return 1.0
            else:
                return 0.0

        return 0.5

    @classmethod
    def calculate_baryon_number(cls, quarks: List[str]) -> float:
        """Calculate baryon number from quarks."""
        total = 0.0
        for q in quarks:
            if q in cls.QUARK_PROPERTIES:
                total += cls.QUARK_PROPERTIES[q]['baryon']
        return round(total)

    @classmethod
    def determine_particle_type(cls, quarks: List[str]) -> str:
        """Determine if particle is baryon, meson, or exotic."""
        num_quarks = len(quarks)
        baryon_num = cls.calculate_baryon_number(quarks)

        if num_quarks == 3 and baryon_num == 1:
            return "Baryon"
        elif num_quarks == 3 and baryon_num == -1:
            return "Antibaryon"
        elif num_quarks == 2 and baryon_num == 0:
            return "Meson"
        elif num_quarks == 4:
            return "Tetraquark"
        elif num_quarks == 5:
            return "Pentaquark"
        else:
            return "Exotic"

    @classmethod
    def estimate_stability(cls, quarks: List[str]) -> Tuple[str, Optional[str]]:
        """
        Estimate stability and half-life.
        Only particles with u and d quarks are stable.
        """
        has_strange = any(q in ['s', 's̅'] for q in quarks)
        has_charm = any(q in ['c', 'c̅'] for q in quarks)
        has_bottom = any(q in ['b', 'b̅'] for q in quarks)
        has_top = any(q in ['t', 't̅'] for q in quarks)

        if has_top:
            return ("Unstable", "5e-25 seconds")
        elif has_bottom:
            return ("Unstable", "1.5e-12 seconds")
        elif has_charm:
            return ("Unstable", "1e-12 seconds")
        elif has_strange:
            return ("Unstable", "1e-10 seconds")
        else:
            # Only u and d quarks - check if it's proton/neutron
            charge = cls.calculate_charge(quarks)
            if abs(charge - 1.0) < 0.01:  # Proton-like
                return ("Stable", None)
            elif abs(charge) < 0.01:  # Neutron-like
                return ("Unstable", "879.4 seconds")
            else:
                return ("Unstable", "1e-8 seconds")

    @classmethod
    def get_interaction_forces(cls, quarks: List[str]) -> List[str]:
        """Determine which forces the particle interacts with."""
        forces = ["Strong", "Gravitational"]

        charge = cls.calculate_charge(quarks)
        if abs(charge) > 0.01:
            forces.append("Electromagnetic")

        # All hadrons interact weakly
        forces.append("Weak")

        return forces

    @classmethod
    def generate_symbol(cls, quarks: List[str]) -> str:
        """Generate a symbol based on quark content."""
        charge = cls.calculate_charge(quarks)

        # Common particle symbols
        if quarks == ['u', 'u', 'd']:
            return 'p'
        elif quarks == ['u', 'd', 'd']:
            return 'n'
        elif sorted(quarks) == ['d', 'u', 'u']:
            return 'p'
        elif sorted(quarks) == ['d', 'd', 'u']:
            return 'n'

        # Generic symbol based on charge
        if charge > 0:
            return f"X⁺{'⁺' * int(charge - 1)}" if charge > 1 else "X⁺"
        elif charge < 0:
            return f"X⁻{'⁻' * int(abs(charge) - 1)}" if charge < -1 else "X⁻"
        else:
            return "X⁰"

    @classmethod
    def create_particle_from_quarks(cls, quarks: List[str], name: str = None,
                                    symbol: str = None, spin_aligned: bool = False) -> Dict:
        """
        Create a complete subatomic particle JSON structure from quarks.

        Args:
            quarks: List of quark symbols (e.g., ['u', 'u', 'd'] for proton)
            name: Optional custom name
            symbol: Optional custom symbol
            spin_aligned: Whether quark spins are aligned (affects total spin)

        Returns:
            Complete particle data dictionary
        """
        charge = cls.calculate_charge(quarks)
        mass = cls.calculate_mass(quarks)
        spin = cls.calculate_spin(quarks, spin_aligned)
        baryon_num = cls.calculate_baryon_number(quarks)
        particle_type = cls.determine_particle_type(quarks)
        stability, half_life = cls.estimate_stability(quarks)

        if symbol is None:
            symbol = cls.generate_symbol(quarks)
        if name is None:
            name = f"Hadron ({','.join(quarks)})"

        # Build composition list
        composition = []
        quark_counts = {}
        for q in quarks:
            quark_counts[q] = quark_counts.get(q, 0) + 1

        for q, count in quark_counts.items():
            if q in cls.QUARK_PROPERTIES:
                composition.append({
                    "Constituent": cls.QUARK_PROPERTIES[q]['name'] + " Quark",
                    "Count": count,
                    "Charge_e": cls.QUARK_PROPERTIES[q]['charge']
                })

        particle_data = {
            "Name": name,
            "Symbol": symbol,
            "Type": "Subatomic Particle",
            "Classification": ["Fermion" if spin % 1 != 0 else "Boson", particle_type, "Hadron", "Composite Particle"],
            "Charge_e": charge,
            "Mass_MeVc2": mass,
            "Mass_kg": mass * 1.78266192e-30,  # MeV/c² to kg
            "Mass_amu": mass / 931.494,
            "Spin_hbar": spin,
            "MagneticDipoleMoment_J_T": None,
            "LeptonNumber_L": 0,
            "BaryonNumber_B": baryon_num,
            "Isospin_I": 0.5 if len(quarks) == 3 else 0,
            "Isospin_I3": (quarks.count('u') - quarks.count('d')) / 2,
            "Parity_P": 1 if particle_type == "Baryon" else -1,
            "Composition": composition,
            "Stability": stability,
            "HalfLife_s": half_life,
            "DecayProducts": [],
            "Antiparticle": {
                "Name": f"Anti-{name}",
                "Symbol": symbol.replace('⁺', '⁻').replace('⁻', '⁺') if '⁺' in symbol or '⁻' in symbol else f"{symbol}̅"
            },
            "InteractionForces": cls.get_interaction_forces(quarks),
            "_created_from": {
                "quarks": quarks,
                "spin_aligned": spin_aligned
            }
        }

        return particle_data


# ==================== Molecule Creation from Atoms ====================

class MoleculeCalculator:
    """
    Calculate molecular properties from atomic composition.
    """

    # Electronegativity values for common elements (Pauling scale)
    ELECTRONEGATIVITIES = {
        'H': 2.20, 'C': 2.55, 'N': 3.04, 'O': 3.44, 'F': 3.98,
        'P': 2.19, 'S': 2.58, 'Cl': 3.16, 'Br': 2.96, 'I': 2.66,
        'Na': 0.93, 'K': 0.82, 'Ca': 1.00, 'Mg': 1.31
    }

    # Covalent radii in pm
    COVALENT_RADII = {
        'H': 31, 'C': 76, 'N': 71, 'O': 66, 'F': 57,
        'P': 107, 'S': 105, 'Cl': 102, 'Br': 120, 'I': 139,
        'Na': 166, 'K': 203, 'Ca': 176, 'Mg': 141
    }

    # Standard atomic masses
    ATOMIC_MASSES = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998,
        'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Br': 79.904, 'I': 126.904,
        'Na': 22.990, 'K': 39.098, 'Ca': 40.078, 'Mg': 24.305
    }

    @classmethod
    def calculate_molecular_mass(cls, composition: List[Dict], atom_data: Dict = None) -> float:
        """
        Calculate molecular mass from atomic composition.

        Args:
            composition: List of {"Element": symbol, "Count": n}
            atom_data: Optional dict mapping symbols to full atom data
        """
        total_mass = 0.0

        for comp in composition:
            element = comp.get('Element', '')
            count = comp.get('Count', 1)

            # Try to get mass from provided atom data first
            if atom_data and element in atom_data:
                mass = atom_data[element].get('atomic_mass', cls.ATOMIC_MASSES.get(element, 0))
            else:
                mass = cls.ATOMIC_MASSES.get(element, 0)

            total_mass += mass * count

        return round(total_mass, 3)

    @classmethod
    def generate_formula(cls, composition: List[Dict]) -> str:
        """Generate molecular formula from composition."""
        subscripts = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                     '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}

        # Sort by Hill system: C first, then H, then alphabetical
        sorted_comp = sorted(composition, key=lambda x: (
            0 if x['Element'] == 'C' else (1 if x['Element'] == 'H' else 2),
            x['Element']
        ))

        formula = ""
        for comp in sorted_comp:
            element = comp.get('Element', '')
            count = comp.get('Count', 1)

            formula += element
            if count > 1:
                for digit in str(count):
                    formula += subscripts.get(digit, digit)

        return formula

    @classmethod
    def determine_bond_type(cls, composition: List[Dict], atom_data: Dict = None) -> str:
        """
        Determine primary bond type based on electronegativity differences.
        """
        if len(composition) < 2:
            return "None"

        electronegativities = []
        for comp in composition:
            element = comp['Element']
            if atom_data and element in atom_data:
                en = atom_data[element].get('electronegativity', cls.ELECTRONEGATIVITIES.get(element, 2.0))
            else:
                en = cls.ELECTRONEGATIVITIES.get(element, 2.0)
            electronegativities.append(en)

        if not electronegativities:
            return "Covalent"

        max_en = max(electronegativities)
        min_en = min(electronegativities)
        diff = max_en - min_en

        if diff > 1.7:
            return "Ionic"
        elif diff > 0.4:
            return "Polar Covalent"
        else:
            return "Covalent"

    @classmethod
    def estimate_polarity(cls, composition: List[Dict], geometry: str = None) -> str:
        """Estimate molecular polarity."""
        bond_type = cls.determine_bond_type(composition)

        if bond_type == "Ionic":
            return "Ionic"

        # Symmetric molecules are nonpolar even with polar bonds
        if geometry in ["Linear", "Trigonal Planar", "Tetrahedral", "Octahedral"]:
            # Check if all atoms are the same (homonuclear)
            elements = set(comp['Element'] for comp in composition)
            if len(elements) == 1:
                return "Nonpolar"

        if bond_type == "Polar Covalent":
            return "Polar"

        return "Nonpolar"

    @classmethod
    def estimate_geometry(cls, composition: List[Dict]) -> str:
        """
        Estimate molecular geometry using VSEPR theory.
        Based on number of atoms and expected bonding.
        """
        total_atoms = sum(comp.get('Count', 1) for comp in composition)
        unique_elements = len(set(comp['Element'] for comp in composition))

        if total_atoms == 2:
            return "Linear"
        elif total_atoms == 3:
            return "Bent" if unique_elements > 1 else "Linear"
        elif total_atoms == 4:
            return "Trigonal Pyramidal"
        elif total_atoms == 5:
            return "Tetrahedral"
        elif total_atoms == 6:
            return "Trigonal Bipyramidal"
        elif total_atoms == 7:
            return "Octahedral"
        else:
            return "Complex"

    @classmethod
    def estimate_bond_angle(cls, geometry: str) -> Optional[float]:
        """Get ideal bond angle for geometry."""
        angles = {
            "Linear": 180.0,
            "Bent": 104.5,
            "Trigonal Planar": 120.0,
            "Trigonal Pyramidal": 107.0,
            "Tetrahedral": 109.5,
            "Trigonal Bipyramidal": 90.0,  # Mixed angles
            "Octahedral": 90.0,
            "Square Planar": 90.0
        }
        return angles.get(geometry)

    @classmethod
    def estimate_melting_point(cls, molecular_mass: float, polarity: str, bond_type: str) -> float:
        """
        Estimate melting point based on molecular properties.
        Uses intermolecular force correlations.
        """
        # Base melting point from molecular mass
        base_mp = 100 + molecular_mass * 2

        # Adjust for polarity
        if polarity == "Ionic":
            base_mp += 500
        elif polarity == "Polar":
            base_mp += 100

        # Adjust for bond type
        if bond_type == "Ionic":
            base_mp *= 1.5

        # Small molecules have lower melting points
        if molecular_mass < 50:
            base_mp *= 0.5

        return round(max(10.0, base_mp), 1)

    @classmethod
    def estimate_boiling_point(cls, melting_point: float, polarity: str) -> float:
        """Estimate boiling point from melting point."""
        ratio = 1.5 if polarity == "Ionic" else (1.3 if polarity == "Polar" else 1.2)
        return round(melting_point * ratio, 1)

    @classmethod
    def estimate_density(cls, molecular_mass: float, composition: List[Dict]) -> float:
        """Estimate density based on molecular mass and composition."""
        # Rough estimation based on typical molecular densities
        total_atoms = sum(comp.get('Count', 1) for comp in composition)

        # Density tends to increase with molecular mass
        base_density = 0.5 + molecular_mass / 100

        # Adjust for atom count (more atoms = denser packing)
        base_density *= (1 + total_atoms * 0.05)

        # Clamp to reasonable range
        return round(max(0.001, min(5.0, base_density)), 3)

    @classmethod
    def estimate_dipole_moment(cls, composition: List[Dict], polarity: str) -> float:
        """Estimate dipole moment in Debye."""
        if polarity == "Nonpolar":
            return 0.0
        elif polarity == "Ionic":
            return round(5.0 + len(composition) * 0.5, 2)
        else:  # Polar
            return round(1.0 + len(composition) * 0.3, 2)

    @classmethod
    def determine_state(cls, melting_point: float, boiling_point: float) -> str:
        """Determine state at STP (298 K, 1 atm)."""
        stp_temp = 298.15  # K

        if melting_point > stp_temp:
            return "Solid"
        elif boiling_point < stp_temp:
            return "Gas"
        else:
            return "Liquid"

    @classmethod
    def estimate_bonds(cls, composition: List[Dict]) -> List[Dict]:
        """Estimate bond information based on composition."""
        bonds = []
        elements = [comp['Element'] for comp in composition for _ in range(comp.get('Count', 1))]

        if len(elements) < 2:
            return bonds

        # Simple estimation: first element bonds to others
        central = elements[0] if len(set(elements)) > 1 else elements[0]
        other_elements = [e for e in set(elements) if e != central or elements.count(e) > 1]

        for other in other_elements:
            # Estimate bond length from covalent radii
            r1 = cls.COVALENT_RADII.get(central, 100)
            r2 = cls.COVALENT_RADII.get(other, 100)
            length = r1 + r2

            bonds.append({
                "From": central,
                "To": other,
                "Type": "Single",  # Simplified
                "Length_pm": length
            })

        return bonds

    @classmethod
    def create_molecule_from_atoms(cls, composition: List[Dict], name: str = None,
                                   atom_data: Dict = None) -> Dict:
        """
        Create a complete molecule JSON structure from atomic composition.

        Args:
            composition: List of {"Element": symbol, "Count": n}
            name: Optional custom name
            atom_data: Optional dict mapping symbols to full atom data

        Returns:
            Complete molecule data dictionary
        """
        formula = cls.generate_formula(composition)
        molecular_mass = cls.calculate_molecular_mass(composition, atom_data)
        bond_type = cls.determine_bond_type(composition, atom_data)
        geometry = cls.estimate_geometry(composition)
        polarity = cls.estimate_polarity(composition, geometry)
        melting_point = cls.estimate_melting_point(molecular_mass, polarity, bond_type)
        boiling_point = cls.estimate_boiling_point(melting_point, polarity)

        if name is None:
            name = f"Compound ({formula})"

        molecule_data = {
            "Name": name,
            "Formula": formula,
            "MolecularMass_amu": molecular_mass,
            "MolecularMass_g_mol": molecular_mass,
            "BondType": bond_type,
            "Geometry": geometry,
            "BondAngle_deg": cls.estimate_bond_angle(geometry),
            "Polarity": polarity,
            "MeltingPoint_K": melting_point,
            "BoilingPoint_K": boiling_point,
            "Density_g_cm3": cls.estimate_density(molecular_mass, composition),
            "State_STP": cls.determine_state(melting_point, boiling_point),
            "Composition": composition,
            "Bonds": cls.estimate_bonds(composition),
            "DipoleMoment_D": cls.estimate_dipole_moment(composition, polarity),
            "Applications": [],
            "IUPAC_Name": name,
            "_created_from": {
                "composition": composition
            }
        }

        return molecule_data
