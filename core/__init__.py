#====== Playtow/PeriodicTable2/core/__init__.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

"""
Core application classes
"""

from core.unified_table import UnifiedTable
from core.molecule_unified_table import MoleculeUnifiedTable
from core.molecule_enums import (MoleculeLayoutMode, MoleculeProperty, BondType,
                                  MolecularGeometry, MoleculePolarity, MoleculeCategory,
                                  MoleculeState, get_element_color)

# Quark/Particle visualization
from core.quark_unified_table import QuarkUnifiedTable
from core.quark_enums import (QuarkLayoutMode, QuarkProperty, ParticleType,
                               QuarkGeneration, InteractionForce)

# Subatomic particle visualization
from core.subatomic_unified_table import SubatomicUnifiedTable
from core.subatomic_enums import (SubatomicLayoutMode, SubatomicProperty, ParticleCategory,
                                   QuarkType, PARTICLE_COLORS, get_particle_family_color)

__all__ = [
    'UnifiedTable',
    'MoleculeUnifiedTable',
    'MoleculeLayoutMode',
    'MoleculeProperty',
    'BondType',
    'MolecularGeometry',
    'MoleculePolarity',
    'MoleculeCategory',
    'MoleculeState',
    'get_element_color',
    # Quark exports
    'QuarkUnifiedTable',
    'QuarkLayoutMode',
    'QuarkProperty',
    'ParticleType',
    'QuarkGeneration',
    'InteractionForce',
    # Subatomic exports
    'SubatomicUnifiedTable',
    'SubatomicLayoutMode',
    'SubatomicProperty',
    'ParticleCategory',
    'QuarkType',
    'PARTICLE_COLORS',
    'get_particle_family_color'
]
