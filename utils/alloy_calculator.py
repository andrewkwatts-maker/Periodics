"""
Alloy Calculator Module
Provides calculations for creating alloys from constituent elements.
Uses physics-based formulas for property estimation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ==================== Physical Constants ====================

class AlloyConstants:
    """Constants for alloy calculations"""

    # Lattice constants for pure elements (pm) at room temperature
    LATTICE_CONSTANTS = {
        'Fe': {'structure': 'BCC', 'a': 286.65},
        'Al': {'structure': 'FCC', 'a': 404.95},
        'Cu': {'structure': 'FCC', 'a': 361.49},
        'Ni': {'structure': 'FCC', 'a': 352.4},
        'Cr': {'structure': 'BCC', 'a': 288.46},
        'Ti': {'structure': 'HCP', 'a': 295.08, 'c': 468.55},
        'Zn': {'structure': 'HCP', 'a': 266.49, 'c': 494.68},
        'Sn': {'structure': 'BCT', 'a': 583.18, 'c': 318.18},
        'Mn': {'structure': 'BCC', 'a': 891.39},
        'Mo': {'structure': 'BCC', 'a': 314.7},
        'W': {'structure': 'BCC', 'a': 316.52},
        'V': {'structure': 'BCC', 'a': 302.4},
        'Co': {'structure': 'HCP', 'a': 250.71, 'c': 406.95},
        'Nb': {'structure': 'BCC', 'a': 330.04},
        'Si': {'structure': 'Diamond', 'a': 543.09},
        'Ag': {'structure': 'FCC', 'a': 408.53},
        'Au': {'structure': 'FCC', 'a': 407.82},
        'Pb': {'structure': 'FCC', 'a': 495.02},
    }

    # Densities of pure elements (g/cm³)
    ELEMENT_DENSITIES = {
        'Fe': 7.874, 'Al': 2.70, 'Cu': 8.96, 'Ni': 8.908, 'Cr': 7.19,
        'Ti': 4.506, 'Zn': 7.14, 'Sn': 7.265, 'Mn': 7.21, 'Mo': 10.28,
        'W': 19.25, 'V': 6.11, 'Co': 8.90, 'Nb': 8.57, 'Si': 2.33,
        'Ag': 10.49, 'Au': 19.30, 'Pb': 11.34, 'C': 2.267, 'N': 1.251,
        'P': 1.823, 'S': 2.07, 'B': 2.34, 'Mg': 1.738
    }

    # Melting points of pure elements (K)
    ELEMENT_MELTING_POINTS = {
        'Fe': 1811, 'Al': 933.5, 'Cu': 1357.8, 'Ni': 1728, 'Cr': 2180,
        'Ti': 1941, 'Zn': 692.7, 'Sn': 505.1, 'Mn': 1519, 'Mo': 2896,
        'W': 3695, 'V': 2183, 'Co': 1768, 'Nb': 2750, 'Si': 1687,
        'Ag': 1234.9, 'Au': 1337.3, 'Pb': 600.6, 'C': 3915, 'N': 63.15,
        'P': 317.3, 'S': 388.4, 'B': 2349, 'Mg': 923
    }

    # Thermal conductivities (W/m·K)
    ELEMENT_THERMAL_CONDUCTIVITY = {
        'Fe': 80.4, 'Al': 237, 'Cu': 401, 'Ni': 90.9, 'Cr': 93.9,
        'Ti': 21.9, 'Zn': 116, 'Sn': 66.8, 'Mn': 7.81, 'Mo': 138,
        'W': 173, 'V': 30.7, 'Co': 100, 'Nb': 53.7, 'Si': 149,
        'Ag': 429, 'Au': 317, 'Pb': 35.3, 'C': 140, 'Mg': 156
    }

    # Electrical resistivities (Ω·m × 10^-8)
    ELEMENT_RESISTIVITY = {
        'Fe': 9.71, 'Al': 2.65, 'Cu': 1.68, 'Ni': 6.99, 'Cr': 12.7,
        'Ti': 42.0, 'Zn': 5.92, 'Sn': 11.5, 'Mn': 144, 'Mo': 5.34,
        'W': 5.28, 'V': 20.1, 'Co': 6.24, 'Nb': 15.2, 'Si': 2300,
        'Ag': 1.59, 'Au': 2.44, 'Pb': 20.6, 'C': 3500
    }

    # Atomic masses (g/mol)
    ATOMIC_MASSES = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'Al': 26.982,
        'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Ti': 47.867, 'V': 50.942,
        'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693,
        'Cu': 63.546, 'Zn': 65.38, 'Nb': 92.906, 'Mo': 95.95, 'Ag': 107.868,
        'Sn': 118.71, 'W': 183.84, 'Au': 196.967, 'Pb': 207.2, 'B': 10.81,
        'Mg': 24.305
    }


# ==================== Alloy Calculator ====================

class AlloyCalculator:
    """
    Calculate alloy properties from constituent elements.
    Uses physics-based formulas including rule of mixtures and Vegard's law.
    """

    @classmethod
    def create_alloy_from_components(
        cls,
        component_data: List[Dict],
        weight_fractions: List[float],
        lattice_type: str = "FCC",
        name: str = None
    ) -> Dict:
        """
        Calculate alloy properties from constituent elements.

        Args:
            component_data: List of element data dictionaries
                           Each should have at least 'symbol' or 'Element'
            weight_fractions: Weight fractions for each component (should sum to 1.0)
            lattice_type: Crystal structure type (FCC, BCC, HCP, etc.)
            name: Optional name for the alloy

        Returns:
            Dictionary containing calculated alloy properties
        """
        if not component_data or not weight_fractions:
            return {}

        if len(component_data) != len(weight_fractions):
            raise ValueError("Component data and weight fractions must have same length")

        # Normalize weight fractions
        total = sum(weight_fractions)
        if total <= 0:
            raise ValueError("Weight fractions must sum to a positive value")
        weight_fractions = [w / total for w in weight_fractions]

        # Extract element symbols
        elements = []
        for comp in component_data:
            sym = comp.get('symbol') or comp.get('Element') or comp.get('Symbol', 'Unknown')
            elements.append(sym)

        # Calculate properties
        density = cls._calculate_density(elements, weight_fractions)
        melting_point = cls._calculate_melting_point(elements, weight_fractions)
        thermal_conductivity = cls._calculate_thermal_conductivity(elements, weight_fractions)
        electrical_resistivity = cls._calculate_electrical_resistivity(elements, weight_fractions)
        lattice_param = cls._calculate_lattice_parameter(elements, weight_fractions, lattice_type)
        estimated_strength = cls._estimate_strength(elements, weight_fractions, density)

        # Build components list
        components = []
        for elem, wf in zip(elements, weight_fractions):
            role = cls._determine_role(elem, wf, elements)
            components.append({
                'Element': elem,
                'MinPercent': wf * 100 * 0.95,  # Allow 5% variation
                'MaxPercent': wf * 100 * 1.05,
                'Role': role
            })

        # Determine primary element (highest weight fraction)
        max_idx = weight_fractions.index(max(weight_fractions))
        primary_element = elements[max_idx]

        # Generate formula
        formula = cls._generate_formula(elements, weight_fractions)

        # Determine category based on primary element
        category = cls._determine_category(primary_element, elements)

        # Build alloy data structure
        alloy_data = {
            'Name': name or f"Custom {category} Alloy",
            'Formula': formula,
            'Category': category,
            'SubCategory': 'Custom',
            'Description': f"Custom alloy created from {', '.join(elements)}",

            'Components': components,

            'PhysicalProperties': {
                'Density_g_cm3': round(density, 3),
                'MeltingPoint_K': round(melting_point, 1),
                'ThermalConductivity_W_mK': round(thermal_conductivity, 1),
                'ThermalExpansion_per_K': 15e-6,  # Typical value
                'ElectricalResistivity_Ohm_m': electrical_resistivity,
                'SpecificHeat_J_kgK': 500,  # Typical for metals
                'YoungsModulus_GPa': round(estimated_strength['youngs_modulus'], 1),
                'ShearModulus_GPa': round(estimated_strength['youngs_modulus'] / 2.6, 1),
                'PoissonsRatio': 0.30,
                'BrinellHardness_HB': round(estimated_strength['hardness'])
            },

            'MechanicalProperties': {
                'TensileStrength_MPa': round(estimated_strength['tensile_strength']),
                'YieldStrength_MPa': round(estimated_strength['yield_strength']),
                'Elongation_percent': round(estimated_strength['elongation']),
                'ReductionOfArea_percent': 50,
                'ImpactStrength_J': 100,
                'FatigueStrength_MPa': round(estimated_strength['tensile_strength'] * 0.45)
            },

            'LatticeProperties': {
                'PrimaryStructure': lattice_type,
                'SecondaryStructures': [],
                'LatticeParameters': {
                    'a_pm': round(lattice_param, 2),
                    'b_pm': round(lattice_param, 2),
                    'c_pm': round(lattice_param * (1.633 if lattice_type == 'HCP' else 1.0), 2),
                    'alpha_deg': 90,
                    'beta_deg': 90,
                    'gamma_deg': 120 if lattice_type == 'HCP' else 90
                },
                'AtomicPackingFactor': cls._get_packing_factor(lattice_type),
                'CoordinationNumber': cls._get_coordination_number(lattice_type)
            },

            'Microstructure': {
                'GrainStructure': {
                    'AverageGrainSize_um': 50,
                    'GrainSizeDistribution': 'LogNormal',
                    'GrainSizeStdDev': 0.35,
                    'ASTMGrainSizeNumber': 5,
                    'VoronoiSeedDensity_per_mm2': 400
                },
                'PhaseDistribution': {
                    'NoiseType': 'Simplex',
                    'NoiseScale': 0.1,
                    'NoiseOctaves': 3,
                    'NoisePersistence': 0.5
                }
            },

            'Applications': [],
            'ProcessingMethods': [],
            'Color': cls._get_alloy_color(primary_element)
        }

        # Add derived properties for easy access
        alloy_data['name'] = alloy_data['Name']
        alloy_data['category'] = alloy_data['Category']
        alloy_data['density'] = alloy_data['PhysicalProperties']['Density_g_cm3']
        alloy_data['melting_point'] = alloy_data['PhysicalProperties']['MeltingPoint_K']
        alloy_data['tensile_strength'] = alloy_data['MechanicalProperties']['TensileStrength_MPa']
        alloy_data['yield_strength'] = alloy_data['MechanicalProperties']['YieldStrength_MPa']
        alloy_data['crystal_structure'] = lattice_type
        alloy_data['primary_element'] = primary_element

        return alloy_data

    @classmethod
    def _calculate_density(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate alloy density using rule of mixtures.
        1/ρ_alloy = Σ(w_i / ρ_i)
        """
        inv_density_sum = 0
        for elem, wf in zip(elements, weight_fractions):
            elem_density = AlloyConstants.ELEMENT_DENSITIES.get(elem, 7.0)
            if elem_density > 0:
                inv_density_sum += wf / elem_density

        return 1.0 / inv_density_sum if inv_density_sum > 0 else 7.0

    @classmethod
    def _calculate_melting_point(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate approximate melting point.
        Uses weighted average with depression factor for multi-component alloys.
        """
        weighted_mp = 0
        for elem, wf in zip(elements, weight_fractions):
            mp = AlloyConstants.ELEMENT_MELTING_POINTS.get(elem, 1500)
            weighted_mp += wf * mp

        # Apply melting point depression for alloys (typically 5-15%)
        num_components = len([wf for wf in weight_fractions if wf > 0.01])
        depression_factor = 1.0 - 0.03 * (num_components - 1)
        depression_factor = max(0.85, min(1.0, depression_factor))

        return weighted_mp * depression_factor

    @classmethod
    def _calculate_thermal_conductivity(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate thermal conductivity.
        Alloys typically have lower thermal conductivity than pure metals.
        """
        weighted_tc = 0
        for elem, wf in zip(elements, weight_fractions):
            tc = AlloyConstants.ELEMENT_THERMAL_CONDUCTIVITY.get(elem, 50)
            weighted_tc += wf * tc

        # Apply reduction factor for alloying (phonon scattering)
        num_components = len([wf for wf in weight_fractions if wf > 0.01])
        reduction = 0.7 ** (num_components - 1)
        reduction = max(0.3, min(1.0, reduction))

        return weighted_tc * reduction

    @classmethod
    def _calculate_electrical_resistivity(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate electrical resistivity.
        Alloying increases resistivity due to electron scattering.
        """
        weighted_res = 0
        for elem, wf in zip(elements, weight_fractions):
            res = AlloyConstants.ELEMENT_RESISTIVITY.get(elem, 10)
            weighted_res += wf * res

        # Matthiessen's rule addition for alloying
        num_components = len([wf for wf in weight_fractions if wf > 0.01])
        alloying_addition = 5 * (num_components - 1)  # Additional resistivity

        return (weighted_res + alloying_addition) * 1e-8

    @classmethod
    def _calculate_lattice_parameter(cls, elements: List[str], weight_fractions: List[float],
                                      lattice_type: str) -> float:
        """
        Calculate lattice parameter using Vegard's law.
        a_alloy = Σ(x_i * a_i)
        """
        # Convert weight fractions to atomic fractions
        atomic_fracs = cls._weight_to_atomic_fractions(elements, weight_fractions)

        weighted_a = 0
        total_frac = 0
        for elem, af in zip(elements, atomic_fracs):
            lattice_info = AlloyConstants.LATTICE_CONSTANTS.get(elem, {})
            a = lattice_info.get('a', 350)  # Default lattice constant
            weighted_a += af * a
            total_frac += af

        return weighted_a / total_frac if total_frac > 0 else 350

    @classmethod
    def _estimate_strength(cls, elements: List[str], weight_fractions: List[float],
                           density: float) -> Dict:
        """
        Estimate mechanical properties using empirical correlations.
        """
        # Base strength from density correlation
        # Higher density metals tend to have higher strength
        base_strength = 100 + density * 40

        # Solid solution strengthening
        num_components = len([wf for wf in weight_fractions if wf > 0.01])
        ss_strengthening = 50 * (num_components - 1)

        # Check for known strengthening elements
        for elem, wf in zip(elements, weight_fractions):
            if elem == 'C' and wf > 0:
                ss_strengthening += wf * 10000  # Carbon is very effective
            elif elem == 'N' and wf > 0:
                ss_strengthening += wf * 8000
            elif elem in ['Mo', 'W', 'V', 'Nb'] and wf > 0:
                ss_strengthening += wf * 500  # Refractory elements
            elif elem == 'Cr' and wf > 0:
                ss_strengthening += wf * 100

        tensile_strength = base_strength + ss_strengthening
        yield_strength = tensile_strength * 0.6  # Typical ratio

        # Elongation decreases with strength (inverse relationship)
        elongation = max(5, 60 - tensile_strength / 20)

        # Young's modulus estimate
        weighted_E = 0
        E_values = {'Fe': 210, 'Al': 69, 'Cu': 130, 'Ni': 200, 'Ti': 116,
                    'Cr': 279, 'Mo': 329, 'W': 411, 'Co': 209}
        for elem, wf in zip(elements, weight_fractions):
            E = E_values.get(elem, 150)
            weighted_E += wf * E

        # Hardness estimate (correlated with strength)
        hardness = tensile_strength / 3 + 50

        return {
            'tensile_strength': tensile_strength,
            'yield_strength': yield_strength,
            'elongation': elongation,
            'youngs_modulus': weighted_E,
            'hardness': hardness
        }

    @classmethod
    def _weight_to_atomic_fractions(cls, elements: List[str], weight_fractions: List[float]) -> List[float]:
        """Convert weight fractions to atomic fractions"""
        molar_fractions = []
        for elem, wf in zip(elements, weight_fractions):
            atomic_mass = AlloyConstants.ATOMIC_MASSES.get(elem, 50)
            molar_fractions.append(wf / atomic_mass)

        total = sum(molar_fractions)
        return [mf / total for mf in molar_fractions] if total > 0 else weight_fractions

    @classmethod
    def _determine_role(cls, element: str, weight_frac: float, all_elements: List[str]) -> str:
        """Determine the role of an element in the alloy"""
        if weight_frac >= max(0.5, max(weight_frac for e in all_elements)):
            return "Base"

        roles = {
            'C': 'Strengthening',
            'N': 'Strengthening',
            'Cr': 'Corrosion Resistance',
            'Ni': 'Stabilizer',
            'Mo': 'Strengthening',
            'V': 'Grain Refiner',
            'Ti': 'Grain Refiner',
            'Mn': 'Deoxidizer',
            'Si': 'Deoxidizer',
            'W': 'Hardening',
            'Co': 'Strengthening',
            'Al': 'Deoxidizer',
            'P': 'Impurity',
            'S': 'Impurity',
            'Cu': 'Corrosion Resistance'
        }
        return roles.get(element, 'Other')

    @classmethod
    def _determine_category(cls, primary_element: str, elements: List[str]) -> str:
        """Determine alloy category from composition"""
        categories = {
            'Fe': 'Steel',
            'Al': 'Aluminum',
            'Cu': 'Copper',
            'Ti': 'Titanium',
            'Ni': 'Nickel',
            'Zn': 'Zinc',
            'Sn': 'Tin',
            'Ag': 'Precious',
            'Au': 'Precious',
            'Pb': 'Lead'
        }

        base_category = categories.get(primary_element, 'Other')

        # Special cases
        if primary_element == 'Cu':
            if 'Zn' in elements:
                return 'Brass'
            if 'Sn' in elements:
                return 'Bronze'

        return base_category

    @classmethod
    def _generate_formula(cls, elements: List[str], weight_fractions: List[float]) -> str:
        """Generate a formula string for the alloy"""
        # Sort by weight fraction (descending)
        sorted_pairs = sorted(zip(elements, weight_fractions), key=lambda x: -x[1])

        # Take top elements with significant fractions
        significant = [(e, wf) for e, wf in sorted_pairs if wf > 0.005]

        if len(significant) <= 3:
            return '-'.join(e for e, _ in significant)
        else:
            return '-'.join(e for e, _ in significant[:3]) + '...'

    @classmethod
    def _get_packing_factor(cls, lattice_type: str) -> float:
        """Get atomic packing factor for a lattice type"""
        factors = {
            'FCC': 0.74,
            'HCP': 0.74,
            'BCC': 0.68,
            'BCT': 0.70,
            'Diamond': 0.34
        }
        return factors.get(lattice_type, 0.68)

    @classmethod
    def _get_coordination_number(cls, lattice_type: str) -> int:
        """Get coordination number for a lattice type"""
        numbers = {
            'FCC': 12,
            'HCP': 12,
            'BCC': 8,
            'BCT': 8,
            'Diamond': 4
        }
        return numbers.get(lattice_type, 8)

    @classmethod
    def _get_alloy_color(cls, primary_element: str) -> str:
        """Get display color for an alloy based on primary element"""
        colors = {
            'Fe': '#C0C0C0',  # Silver
            'Al': '#E8E8E8',  # Light grey
            'Cu': '#B87333',  # Copper
            'Ti': '#8E8E8E',  # Grey
            'Ni': '#A8A8A8',  # Light grey
            'Zn': '#B0B0B0',  # Grey
            'Sn': '#909090',  # Grey
            'Ag': '#C0C0C0',  # Silver
            'Au': '#FFD700',  # Gold
            'Pb': '#666666'   # Dark grey
        }
        return colors.get(primary_element, '#C0C0C0')


# ==================== Convenience Functions ====================

def calculate_alloy_properties(elements: List[str], weight_percents: List[float],
                                lattice: str = 'FCC', name: str = None) -> Dict:
    """
    Convenience function to calculate alloy properties.

    Args:
        elements: List of element symbols (e.g., ['Fe', 'Cr', 'Ni'])
        weight_percents: Weight percentages for each element
        lattice: Crystal structure type
        name: Optional alloy name

    Returns:
        Dictionary containing alloy properties
    """
    # Convert percentages to fractions
    weight_fractions = [wp / 100 for wp in weight_percents]

    # Create simple component data
    component_data = [{'symbol': elem} for elem in elements]

    return AlloyCalculator.create_alloy_from_components(
        component_data, weight_fractions, lattice, name
    )
