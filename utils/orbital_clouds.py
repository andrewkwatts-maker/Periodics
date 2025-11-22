#====== Playtow/PeriodicTable2/utils/orbital_clouds.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

"""
Electron orbital probability cloud calculations.
Supports both scipy (high-performance) and pure Python (zero dependencies) backends.
"""
import math

# Backend selection - try scipy first, fall back to pure Python
USE_SCIPY = True  # Set to False to force pure Python

try:
    if USE_SCIPY:
        from scipy.special import genlaguerre as _scipy_genlaguerre
        from scipy.special import lpmv as _scipy_lpmv
        from scipy.special import factorial as _scipy_factorial
        import numpy as np
        _SCIPY_AVAILABLE = True
    else:
        _SCIPY_AVAILABLE = False
except ImportError:
    _SCIPY_AVAILABLE = False

if not _SCIPY_AVAILABLE:
    from utils.pure_math import genlaguerre as _pure_genlaguerre
    from utils.pure_math import lpmv as _pure_lpmv
    from utils.pure_math import factorial as _pure_factorial


# =============================================================================
# Unified API - Backend wrapper functions
# =============================================================================

def _factorial(n):
    """Compute factorial using the active backend."""
    if _SCIPY_AVAILABLE:
        return float(_scipy_factorial(n))
    return float(_pure_factorial(int(n)))


def _genlaguerre(n, alpha):
    """Return generalized Laguerre polynomial function using the active backend."""
    if _SCIPY_AVAILABLE:
        return _scipy_genlaguerre(n, alpha)
    return _pure_genlaguerre(n, alpha)


def _lpmv(m, l, x):
    """Compute associated Legendre polynomial using the active backend."""
    if _SCIPY_AVAILABLE:
        return float(_scipy_lpmv(m, l, x))
    return float(_pure_lpmv(m, l, x))


# =============================================================================
# Backend management functions
# =============================================================================

def set_backend(use_scipy: bool):
    """
    Switch between scipy and pure Python backends.

    Args:
        use_scipy: True to use scipy, False to use pure Python

    Raises:
        ImportError: If scipy is requested but not available
    """
    global USE_SCIPY, _SCIPY_AVAILABLE
    global _scipy_genlaguerre, _scipy_lpmv, _scipy_factorial, np
    global _pure_genlaguerre, _pure_lpmv, _pure_factorial

    if use_scipy:
        # Try to import scipy
        try:
            from scipy.special import genlaguerre as _scipy_genlaguerre
            from scipy.special import lpmv as _scipy_lpmv
            from scipy.special import factorial as _scipy_factorial
            import numpy as np
            _SCIPY_AVAILABLE = True
            USE_SCIPY = True
        except ImportError:
            raise ImportError("scipy is not available")
    else:
        # Switch to pure Python
        from utils.pure_math import genlaguerre as _pure_genlaguerre
        from utils.pure_math import lpmv as _pure_lpmv
        from utils.pure_math import factorial as _pure_factorial
        _SCIPY_AVAILABLE = False
        USE_SCIPY = False


def get_backend() -> str:
    """
    Return the name of the current backend.

    Returns:
        "scipy" if using scipy backend, "pure_python" otherwise
    """
    return "scipy" if _SCIPY_AVAILABLE and USE_SCIPY else "pure_python"


# =============================================================================
# Orbital naming functions
# =============================================================================

def get_orbital_name(n, l, m=0):
    """
    Get the standard orbital name from quantum numbers.

    Args:
        n: Principal quantum number (1, 2, 3, ...)
        l: Angular momentum quantum number (0=s, 1=p, 2=d, 3=f)
        m: Magnetic quantum number (-l to +l)

    Returns:
        String like "1s", "2p", "3d", etc.
    """
    orbital_letters = {0: 's', 1: 'p', 2: 'd', 3: 'f', 4: 'g', 5: 'h'}
    letter = orbital_letters.get(l, '?')

    if l == 0:  # s orbitals are spherically symmetric
        return f"{n}{letter}"
    else:
        # Add subscript for p, d, f orbitals
        subscripts = {
            (1, -1): 'ₓ', (1, 0): 'z', (1, 1): 'y',  # p orbitals
            (2, -2): 'xy', (2, -1): 'yz', (2, 0): 'z²', (2, 1): 'xz', (2, 2): 'x²-y²',  # d orbitals
        }
        sub = subscripts.get((l, m), str(m))
        return f"{n}{letter}{sub}"


# =============================================================================
# Quantum mechanical wavefunction calculations
# =============================================================================

def radial_wavefunction(n, l, r, Z=1):
    """
    Proper radial wavefunction for hydrogen-like atoms.

    Implements: R_{n,l}(r) = sqrt[(2Z/na₀)³ * (n-l-1)! / (2n[(n+l)!]³)] *
                              (2Zr/na₀)^l * exp(-Zr/na₀) * L_{n-l-1}^{2l+1}(2Zr/na₀)

    Args:
        n: Principal quantum number (1, 2, 3, ...)
        l: Angular momentum quantum number (0, 1, ..., n-1)
        r: Radius in Bohr radii (a₀)
        Z: Nuclear charge (default 1 for hydrogen)

    Returns:
        Radial wavefunction value (can be negative)
    """
    if r < 0 or n < 1 or l < 0 or l >= n:
        return 0.0

    a0 = 1.0  # Normalized to Bohr radius
    rho = 2.0 * Z * r / (n * a0)

    # Normalization constant
    norm_factor = math.sqrt(
        (2.0 * Z / (n * a0))**3 *
        _factorial(n - l - 1) /
        (2.0 * n * _factorial(n + l)**3)
    )

    # Associated Laguerre polynomial L_{n-l-1}^{2l+1}(rho)
    laguerre_poly = _genlaguerre(n - l - 1, 2 * l + 1)
    laguerre_value = laguerre_poly(rho)

    # Radial wavefunction
    R_nl = norm_factor * (rho**l) * math.exp(-rho / 2.0) * laguerre_value

    return float(R_nl)


def angular_wavefunction(l, m, theta, phi=0):
    """
    Proper angular wavefunction (spherical harmonics).

    Implements: Y_{l,m}(θ,φ) using associated Legendre polynomials

    Args:
        l: Angular momentum quantum number (0, 1, 2, ...)
        m: Magnetic quantum number (-l, ..., 0, ..., +l)
        theta: Polar angle (0 to π)
        phi: Azimuthal angle (0 to 2π)

    Returns:
        Magnitude squared of spherical harmonic |Y_{l,m}|²
    """
    if l < 0 or abs(m) > l:
        return 0.0

    # Normalization constant for spherical harmonics
    norm = math.sqrt(
        (2 * l + 1) * _factorial(l - abs(m)) /
        (4 * math.pi * _factorial(l + abs(m)))
    )

    # Associated Legendre polynomial P_l^m(cos(theta))
    legendre_value = _lpmv(abs(m), l, math.cos(theta))

    # Spherical harmonic magnitude squared
    # |Y_{l,m}|² = |normalization * P_l^m * e^{imφ}|²
    # Since |e^{imφ}|² = 1, we just need |normalization * P_l^m|²
    Y_lm_squared = (norm * legendre_value)**2

    return float(Y_lm_squared)


def get_orbital_probability(n, l, m, r, theta, phi=0, Z=1):
    """
    Get total probability density |ψ|² at a point in space.

    Implements: |ψ_{n,l,m}(r,θ,φ)|² = |R_{n,l}(r)|² * |Y_{l,m}(θ,φ)|²

    Args:
        n: Principal quantum number
        l: Angular momentum quantum number
        m: Magnetic quantum number
        r: Radius from nucleus in Bohr radii
        theta: Polar angle (0 to π)
        phi: Azimuthal angle (0 to 2π)
        Z: Nuclear charge (for multi-electron approximation)

    Returns:
        Probability density |ψ|²
    """
    radial = radial_wavefunction(n, l, r, Z)
    angular = angular_wavefunction(l, m, theta, phi)

    # Total probability density: |ψ|² = R²(r) * |Y|²(θ,φ)
    return radial**2 * angular


def get_available_orbitals(max_n=4):
    """
    Get list of available orbitals up to principal quantum number max_n.

    Returns:
        List of tuples (n, l, m, name)
    """
    orbitals = []

    for n in range(1, max_n + 1):
        for l in range(n):  # l < n
            if l == 0:  # s orbital - only one
                orbitals.append((n, l, 0, get_orbital_name(n, l, 0)))
            else:
                # Multiple m values for p, d, f
                for m in range(-l, l + 1):
                    orbitals.append((n, l, m, get_orbital_name(n, l, m)))

    return orbitals


# =============================================================================
# Shell radius calculations
# =============================================================================

def get_bohr_radius_for_shell(n, Z=1):
    """
    Calculate the Bohr radius for shell n in a hydrogen-like atom.

    For hydrogen-like atoms:
    r_n = a₀ * n² / Z

    where:
    - a₀ = 0.529 Å (Bohr radius)
    - n = principal quantum number
    - Z = atomic number (nuclear charge)

    For multi-electron atoms, we use effective nuclear charge (Slater's rules approximation).

    Args:
        n: Principal quantum number (shell number)
        Z: Atomic number (protons in nucleus)

    Returns:
        Radius in Angstroms (Å)
    """
    a0 = 0.529177  # Bohr radius in Angstroms

    # For multi-electron atoms, use effective nuclear charge (simplified Slater's rules)
    # This accounts for electron shielding
    if Z == 1:
        Z_eff = 1.0
    else:
        # Simplified shielding: inner electrons shield ~1.0, same shell ~0.35
        if n == 1:
            shielding = 0.3 * (min(Z, 2) - 1)  # Max 2 electrons in n=1
        elif n == 2:
            shielding = 2.0 + 0.85 * (min(Z - 2, 8) - 1) if Z > 2 else 0  # 2 from n=1, rest from n=2
        elif n == 3:
            shielding = 2.0 + 8.0 + 0.35 * (min(Z - 10, 18) - 1) if Z > 10 else 2.0 + min(Z - 2, 8) * 0.85
        else:
            # General approximation for higher shells
            shielding = Z * 0.7  # Rough approximation

        Z_eff = max(1.0, Z - shielding)

    # Bohr radius formula with effective charge
    radius = a0 * n * n / Z_eff

    return radius


def get_real_shell_radii(Z):
    """
    Get real shell radii for an element with atomic number Z.
    Returns list of radii in Angstroms for each occupied shell.

    Args:
        Z: Atomic number

    Returns:
        List of shell radii in Angstroms [r1, r2, r3, ...]
    """
    from data.element_data import get_electron_shell_distribution

    shells = get_electron_shell_distribution(Z)
    radii = []

    for n in range(1, len(shells) + 1):
        radius = get_bohr_radius_for_shell(n, Z)
        radii.append(radius)

    return radii
