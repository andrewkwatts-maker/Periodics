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
                'ThermalExpansion_per_K': cls._calculate_thermal_expansion(elements, weight_fractions) * 1e-6,
                'ElectricalResistivity_Ohm_m': electrical_resistivity,
                'SpecificHeat_J_kgK': cls._calculate_specific_heat(elements, weight_fractions),
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

            'PhaseComposition': cls._estimate_phase_composition(elements, weight_fractions, lattice_type),

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

            'CorrosionResistance': cls._calculate_corrosion_resistance(elements, weight_fractions),

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

    @classmethod
    def _calculate_thermal_expansion(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate coefficient of thermal expansion using rule of mixtures.

        CTE_alloy ≈ Σ(w_i × CTE_i)

        Args:
            elements: List of element symbols
            weight_fractions: Weight fractions

        Returns:
            Thermal expansion coefficient in per K (×10^-6)
        """
        # Thermal expansion coefficients for elements (×10^-6 /K)
        element_cte = {
            'Fe': 11.8, 'Al': 23.1, 'Cu': 16.5, 'Ni': 13.4, 'Cr': 4.9,
            'Ti': 8.6, 'Zn': 30.2, 'Sn': 22.0, 'Mn': 21.7, 'Mo': 4.8,
            'W': 4.5, 'V': 8.4, 'Co': 13.0, 'Nb': 7.3, 'Si': 2.6,
            'Ag': 18.9, 'Au': 14.2, 'Pb': 28.9, 'C': 1.0, 'Mg': 24.8
        }

        weighted_cte = 0
        for elem, wf in zip(elements, weight_fractions):
            cte = element_cte.get(elem, 12.0)  # Default 12 ppm/K
            weighted_cte += wf * cte

        return round(weighted_cte, 1)

    @classmethod
    def _calculate_specific_heat(cls, elements: List[str], weight_fractions: List[float]) -> float:
        """
        Calculate specific heat capacity using Kopp-Neumann rule.

        Cp_alloy ≈ Σ(w_i × Cp_i)

        For metals, Dulong-Petit law gives ~25 J/(mol·K) per atom
        Cp (J/kg·K) = 25 / M × 1000

        Args:
            elements: List of element symbols
            weight_fractions: Weight fractions

        Returns:
            Specific heat in J/(kg·K)
        """
        # Specific heat capacities (J/kg·K)
        element_cp = {
            'Fe': 449, 'Al': 897, 'Cu': 385, 'Ni': 444, 'Cr': 449,
            'Ti': 523, 'Zn': 388, 'Sn': 228, 'Mn': 479, 'Mo': 251,
            'W': 132, 'V': 489, 'Co': 421, 'Nb': 265, 'Si': 705,
            'Ag': 235, 'Au': 129, 'Pb': 129, 'C': 709, 'Mg': 1023, 'N': 1040
        }

        weighted_cp = 0
        for elem, wf in zip(elements, weight_fractions):
            cp = element_cp.get(elem, 450)  # Default 450 J/kg·K
            weighted_cp += wf * cp

        return round(weighted_cp, 0)

    @classmethod
    def _calculate_corrosion_resistance(cls, elements: List[str], weight_fractions: List[float]) -> Dict:
        """
        Calculate corrosion resistance metrics.

        PREN (Pitting Resistance Equivalent Number):
        PREN = %Cr + 3.3×%Mo + 16×%N

        Higher PREN = better pitting corrosion resistance
        PREN > 40 is considered highly corrosion resistant

        Args:
            elements: List of element symbols
            weight_fractions: Weight fractions

        Returns:
            Dict with PREN, passivation film, and corrosion rating
        """
        # Get element percentages
        elem_percent = {elem: wf * 100 for elem, wf in zip(elements, weight_fractions)}

        cr_pct = elem_percent.get('Cr', 0)
        mo_pct = elem_percent.get('Mo', 0)
        n_pct = elem_percent.get('N', 0)
        ni_pct = elem_percent.get('Ni', 0)

        # Calculate PREN
        pren = cr_pct + 3.3 * mo_pct + 16 * n_pct

        # Determine passivation film composition
        if cr_pct >= 10.5:
            passivation_film = "Cr2O3"
        elif elem_percent.get('Al', 0) > 1:
            passivation_film = "Al2O3"
        elif elem_percent.get('Ti', 0) > 1:
            passivation_film = "TiO2"
        else:
            passivation_film = "FeO/Fe2O3"

        # Pitting potential estimate (mV vs SCE)
        if pren > 40:
            pitting_potential = 400 + (pren - 40) * 5
            rating = "Excellent"
        elif pren > 25:
            pitting_potential = 200 + (pren - 25) * 13
            rating = "Good"
        elif pren > 15:
            pitting_potential = 50 + (pren - 15) * 15
            rating = "Moderate"
        else:
            pitting_potential = pren * 3
            rating = "Poor"

        # Critical pitting temperature (K)
        cpt = 253 + pren * 2  # Rough estimate

        return {
            'PREN': round(pren, 1),
            'PassivationFilmComposition': passivation_film,
            'PittingPotential_mV_SCE': round(pitting_potential, 0),
            'CriticalPittingTemperature_K': round(cpt, 0),
            'CorrosionRating': rating,
            'Details': {
                'Cr_percent': cr_pct,
                'Mo_percent': mo_pct,
                'N_percent': n_pct,
                'formula': 'PREN = %Cr + 3.3×%Mo + 16×%N'
            }
        }

    @classmethod
    def _estimate_phase_composition(cls, elements: List[str], weight_fractions: List[float],
                                     lattice_type: str) -> Dict:
        """
        Estimate phase composition from alloy composition.

        Uses empirical rules:
        - Ni equivalents determine austenite stability
        - Cr equivalents determine ferrite formation
        - Schaeffler diagram concepts for stainless steels

        Ni_eq = %Ni + 30×%C + 0.5×%Mn
        Cr_eq = %Cr + %Mo + 1.5×%Si + 0.5×%Nb

        Args:
            elements: List of element symbols
            weight_fractions: Weight fractions
            lattice_type: Primary lattice structure

        Returns:
            Dict with phases and their volume fractions
        """
        # Get element percentages
        elem_pct = {elem: wf * 100 for elem, wf in zip(elements, weight_fractions)}

        ni_pct = elem_pct.get('Ni', 0)
        cr_pct = elem_pct.get('Cr', 0)
        c_pct = elem_pct.get('C', 0)
        mn_pct = elem_pct.get('Mn', 0)
        mo_pct = elem_pct.get('Mo', 0)
        si_pct = elem_pct.get('Si', 0)
        nb_pct = elem_pct.get('Nb', 0)

        # Calculate Schaeffler equivalents
        ni_eq = ni_pct + 30 * c_pct + 0.5 * mn_pct
        cr_eq = cr_pct + mo_pct + 1.5 * si_pct + 0.5 * nb_pct

        phases = []

        # Determine phases using Schaeffler-like approach
        if 'Fe' in elements and cr_pct > 10:
            # Stainless steel - use Schaeffler diagram logic
            if ni_eq > 12 and cr_eq < 25:
                # Austenitic region
                phases.append({
                    'Name': 'Austenite',
                    'Symbol': 'gamma',
                    'Structure': 'FCC',
                    'VolumePercent': 95,
                    'Magnetic': False,
                    'Hardness_HV': 180
                })
                if cr_eq > 18:
                    phases.append({
                        'Name': 'Delta Ferrite',
                        'Symbol': 'delta',
                        'Structure': 'BCC',
                        'VolumePercent': 5,
                        'Magnetic': True,
                        'Hardness_HV': 200
                    })
            elif cr_eq > 18 and ni_eq < 8:
                # Ferritic region
                phases.append({
                    'Name': 'Ferrite',
                    'Symbol': 'alpha',
                    'Structure': 'BCC',
                    'VolumePercent': 100,
                    'Magnetic': True,
                    'Hardness_HV': 200
                })
            elif ni_eq > 8 and ni_eq < 12:
                # Duplex region
                austenite_pct = min(70, max(30, ni_eq * 5))
                phases.extend([
                    {
                        'Name': 'Austenite',
                        'Symbol': 'gamma',
                        'Structure': 'FCC',
                        'VolumePercent': int(austenite_pct),
                        'Magnetic': False,
                        'Hardness_HV': 180
                    },
                    {
                        'Name': 'Ferrite',
                        'Symbol': 'alpha',
                        'Structure': 'BCC',
                        'VolumePercent': int(100 - austenite_pct),
                        'Magnetic': True,
                        'Hardness_HV': 200
                    }
                ])
            else:
                # Martensitic or mixed
                phases.append({
                    'Name': 'Martensite',
                    'Symbol': 'alpha_prime',
                    'Structure': 'BCT',
                    'VolumePercent': 90,
                    'Magnetic': True,
                    'Hardness_HV': 300 + c_pct * 500
                })
        elif 'Al' in elements and elem_pct.get('Al', 0) > 80:
            # Aluminum alloys
            phases.append({
                'Name': 'Alpha Aluminum',
                'Symbol': 'alpha',
                'Structure': 'FCC',
                'VolumePercent': 95,
                'Magnetic': False,
                'Hardness_HV': 50
            })
            if elem_pct.get('Cu', 0) > 2:
                phases.append({
                    'Name': 'Theta (Al2Cu)',
                    'Symbol': 'theta',
                    'Structure': 'Tetragonal',
                    'VolumePercent': 5,
                    'Magnetic': False,
                    'Hardness_HV': 200
                })
        elif 'Cu' in elements and elem_pct.get('Cu', 0) > 50:
            # Copper alloys
            phases.append({
                'Name': 'Alpha Copper',
                'Symbol': 'alpha',
                'Structure': 'FCC',
                'VolumePercent': 100,
                'Magnetic': False,
                'Hardness_HV': 80
            })
        elif 'Ti' in elements and elem_pct.get('Ti', 0) > 70:
            # Titanium alloys
            al_pct = elem_pct.get('Al', 0)
            v_pct = elem_pct.get('V', 0)
            if v_pct > 3:
                # Alpha-beta alloy
                beta_pct = min(40, v_pct * 8)
                phases.extend([
                    {
                        'Name': 'Alpha Titanium',
                        'Symbol': 'alpha',
                        'Structure': 'HCP',
                        'VolumePercent': int(100 - beta_pct),
                        'Magnetic': False,
                        'Hardness_HV': 300
                    },
                    {
                        'Name': 'Beta Titanium',
                        'Symbol': 'beta',
                        'Structure': 'BCC',
                        'VolumePercent': int(beta_pct),
                        'Magnetic': False,
                        'Hardness_HV': 350
                    }
                ])
            else:
                phases.append({
                    'Name': 'Alpha Titanium',
                    'Symbol': 'alpha',
                    'Structure': 'HCP',
                    'VolumePercent': 100,
                    'Magnetic': False,
                    'Hardness_HV': 300
                })
        else:
            # Generic single phase
            phases.append({
                'Name': 'Matrix',
                'Symbol': 'matrix',
                'Structure': lattice_type,
                'VolumePercent': 100,
                'Magnetic': 'Fe' in elements or 'Ni' in elements or 'Co' in elements,
                'Hardness_HV': 150
            })

        return {
            'Phases': phases,
            'NickelEquivalent': round(ni_eq, 1),
            'ChromiumEquivalent': round(cr_eq, 1),
            'TransformationTemperatures': {
                'Ms_K': 273 + 500 - 350 * c_pct - 35 * mn_pct if c_pct > 0 else None,
                'Mf_K': 273 + 350 - 350 * c_pct - 35 * mn_pct if c_pct > 0 else None
            }
        }


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
