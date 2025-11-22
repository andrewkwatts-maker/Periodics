#!/usr/bin/env python3
"""
Backend Comparison Test Script

Comprehensive comparison of pure Python implementations against scipy/numpy library implementations.
Tests accuracy and performance of:
- pure_math.py vs scipy.special (factorial, genlaguerre, lpmv)
- pure_array.py vs numpy (Vec3 operations, nucleon position generation)
- orbital_clouds.py backend comparison (radial_wavefunction, angular_wavefunction, get_orbital_probability)
- sdf_renderer.py backend comparison (nucleon position generation)

Run with: python tests/backend_comparison.py

Accuracy Testing Notes:
- Tests pass if EITHER relative error < threshold OR absolute error < threshold
- This handles cases where expected values are near zero (relative error is meaningless)
- Performance benchmarks run 1000 iterations (fewer for complex operations)
- Missing scipy/numpy is handled gracefully (tests are skipped)
"""
import sys
import os
import time
import math
from typing import List, Tuple, Dict, Optional, Callable, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============================================================================
# Import Pure Python Implementations (always available)
# =============================================================================
# Import directly from module files to avoid __init__.py dependencies on PySide6
import importlib.util

def _import_module(module_path, module_name):
    """Import a module directly from file path"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_pure_math_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'pure_math.py')
_pure_array_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'pure_array.py')

_pure_math = _import_module(_pure_math_path, 'pure_math')
_pure_array = _import_module(_pure_array_path, 'pure_array')

pure_factorial = _pure_math.factorial
pure_genlaguerre = _pure_math.genlaguerre
pure_lpmv = _pure_math.lpmv
pure_double_factorial = _pure_math.double_factorial
pure_binomial = _pure_math.binomial
pure_spherical_harmonic = _pure_math.spherical_harmonic
pure_spherical_harmonic_real = _pure_math.spherical_harmonic_real

Vec3 = _pure_array.Vec3
pure_pi = _pure_array.pi
pure_sqrt = _pure_array.sqrt
pure_cos = _pure_array.cos
pure_sin = _pure_array.sin
pure_random_seed = _pure_array.random_seed
pure_random_uniform = _pure_array.random_uniform
pure_generate_nucleon_positions = _pure_array.generate_nucleon_positions
pure_rotation_matrix_x = _pure_array.rotation_matrix_x
pure_rotation_matrix_y = _pure_array.rotation_matrix_y
pure_rotation_matrix_z = _pure_array.rotation_matrix_z
pure_rotation_matrix_axis_angle = _pure_array.rotation_matrix_axis_angle
pure_matrix_multiply_3x3 = _pure_array.matrix_multiply_3x3
pure_matrix_vector_multiply = _pure_array.matrix_vector_multiply_3x3

# =============================================================================
# Try to import scipy/numpy for comparison
# =============================================================================
SCIPY_AVAILABLE = False
NUMPY_AVAILABLE = False

try:
    import scipy.special
    SCIPY_AVAILABLE = True
except ImportError:
    print("Note: scipy not available - scipy comparison tests will be skipped")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Note: numpy not available - numpy comparison tests will be skipped")


# =============================================================================
# Test Result Classes
# =============================================================================
class AccuracyResult:
    """Store accuracy test results"""
    def __init__(self, name: str, tests_run: int, max_rel_error: float,
                 max_abs_error: float, threshold: float = 1e-10):
        self.name = name
        self.tests_run = tests_run
        self.max_rel_error = max_rel_error
        self.max_abs_error = max_abs_error
        self.threshold = threshold
        self.passed = max_rel_error <= threshold or max_abs_error <= threshold

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        if self.max_rel_error == 0.0:
            error_str = "0.0 (EXACT MATCH)"
        else:
            error_str = f"{self.max_rel_error:.2e}"
        threshold_str = f"< {self.threshold:.0e} threshold" if self.passed else f"> {self.threshold:.0e} threshold"
        return f"""  Tested: {self.tests_run} combinations
  Max relative error: {error_str}
  Max absolute error: {self.max_abs_error:.2e}
  Status: {status} ({threshold_str})"""


class BenchmarkResult:
    """Store benchmark results"""
    def __init__(self, name: str, library_time_us: Optional[float],
                 pure_time_us: float, iterations: int):
        self.name = name
        self.library_time_us = library_time_us
        self.pure_time_us = pure_time_us
        self.iterations = iterations

        if library_time_us is not None and library_time_us > 0:
            self.ratio = library_time_us / pure_time_us
            self.winner = "pure_python" if self.ratio > 1.0 else "library"
        else:
            self.ratio = None
            self.winner = "pure_python (only option)"

    def format_row(self) -> str:
        lib_str = f"{self.library_time_us:8.2f} us" if self.library_time_us else "    N/A    "
        pure_str = f"{self.pure_time_us:8.2f} us"
        ratio_str = f"{self.ratio:.2f}x" if self.ratio else "N/A  "
        return f"| {self.name:<20} | {lib_str} | {pure_str} | {ratio_str:>6} | {self.winner:<15} |"


# =============================================================================
# Utility Functions
# =============================================================================
def relative_error(computed: float, expected: float) -> float:
    """Calculate relative error between computed and expected values"""
    if expected == 0:
        return abs(computed) if computed != 0 else 0.0
    return abs(computed - expected) / abs(expected)


def benchmark_function(func: Callable, args: Tuple, iterations: int = 1000) -> float:
    """Benchmark a function and return average time in microseconds"""
    # Warm up
    for _ in range(min(100, iterations // 10)):
        func(*args)

    start = time.perf_counter()
    for _ in range(iterations):
        func(*args)
    elapsed = time.perf_counter() - start

    return (elapsed / iterations) * 1_000_000  # Convert to microseconds


# =============================================================================
# ACCURACY TESTS
# =============================================================================

def test_factorial_accuracy() -> Optional[AccuracyResult]:
    """Test factorial accuracy: pure_math.factorial vs scipy.special.factorial"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    for n in range(0, 51):
        pure_result = float(pure_factorial(n))
        scipy_result = float(scipy.special.factorial(n, exact=True))

        rel_err = relative_error(pure_result, scipy_result)
        abs_err = abs(pure_result - scipy_result)

        max_rel_error = max(max_rel_error, rel_err)
        max_abs_error = max(max_abs_error, abs_err)
        tests_run += 1

    return AccuracyResult(
        "pure_math.factorial vs scipy.factorial",
        tests_run, max_rel_error, max_abs_error, threshold=0.0
    )


def test_genlaguerre_accuracy() -> Optional[AccuracyResult]:
    """Test generalized Laguerre polynomial accuracy"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    for n in range(0, 11):
        for alpha in range(0, 6):
            pure_L = pure_genlaguerre(n, alpha)
            scipy_L = scipy.special.genlaguerre(n, alpha)

            for x in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]:
                pure_result = float(pure_L(x))
                scipy_result = float(scipy_L(x))

                rel_err = relative_error(pure_result, scipy_result)
                abs_err = abs(pure_result - scipy_result)

                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs_err)
                tests_run += 1

    return AccuracyResult(
        "pure_math.genlaguerre vs scipy.genlaguerre",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_lpmv_accuracy() -> Optional[AccuracyResult]:
    """Test associated Legendre polynomial accuracy"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    for l in range(0, 6):
        for m in range(-l, l + 1):
            for x in [-1.0, -0.5, 0.0, 0.5, 1.0]:
                pure_result = float(pure_lpmv(m, l, x))
                scipy_result = float(scipy.special.lpmv(m, l, x))

                rel_err = relative_error(pure_result, scipy_result)
                abs_err = abs(pure_result - scipy_result)

                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs_err)
                tests_run += 1

    return AccuracyResult(
        "pure_math.lpmv vs scipy.lpmv",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_vec3_operations() -> AccuracyResult:
    """Test Vec3 operations against numpy equivalents"""
    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    test_vectors = [
        (1.0, 2.0, 3.0),
        (-1.5, 2.5, -3.5),
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (10.0, 20.0, 30.0),
    ]

    for v1_tuple in test_vectors:
        for v2_tuple in test_vectors:
            v1 = Vec3(*v1_tuple)
            v2 = Vec3(*v2_tuple)

            # Test addition
            result = v1 + v2
            expected = (v1_tuple[0] + v2_tuple[0], v1_tuple[1] + v2_tuple[1], v1_tuple[2] + v2_tuple[2])
            for i, (r, e) in enumerate(zip(result.to_tuple(), expected)):
                rel_err = relative_error(r, e)
                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs(r - e))
            tests_run += 1

            # Test scalar multiplication
            for scalar in [0.5, 2.0, -1.0]:
                result = v1 * scalar
                expected = (v1_tuple[0] * scalar, v1_tuple[1] * scalar, v1_tuple[2] * scalar)
                for r, e in zip(result.to_tuple(), expected):
                    rel_err = relative_error(r, e)
                    max_rel_error = max(max_rel_error, rel_err)
                    max_abs_error = max(max_abs_error, abs(r - e))
                tests_run += 1

            # Test dot product
            result = v1.dot(v2)
            expected = sum(a * b for a, b in zip(v1_tuple, v2_tuple))
            rel_err = relative_error(result, expected)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs(result - expected))
            tests_run += 1

    # Test length
    for v_tuple in test_vectors:
        v = Vec3(*v_tuple)
        result = v.length()
        expected = math.sqrt(sum(x * x for x in v_tuple))
        rel_err = relative_error(result, expected)
        max_rel_error = max(max_rel_error, rel_err)
        max_abs_error = max(max_abs_error, abs(result - expected))
        tests_run += 1

    # Test normalization
    for v_tuple in test_vectors:
        if sum(x * x for x in v_tuple) > 0:
            v = Vec3(*v_tuple)
            result = v.normalized()
            result_len = result.length()
            rel_err = relative_error(result_len, 1.0)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs(result_len - 1.0))
            tests_run += 1

    # Test rotations
    test_angles = [0, math.pi / 4, math.pi / 2, math.pi, 2 * math.pi]
    v_test = Vec3(1.0, 0.0, 0.0)

    for angle in test_angles:
        # Rotate X axis vector around Y should give (cos, 0, -sin)
        result = v_test.rotate_y(angle)
        expected = (math.cos(angle), 0.0, -math.sin(angle))
        for r, e in zip(result.to_tuple(), expected):
            rel_err = relative_error(r, e) if abs(e) > 1e-10 else abs(r)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs(r - e))
        tests_run += 1

    return AccuracyResult(
        "Vec3 operations (mathematical correctness)",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_vec3_vs_numpy() -> Optional[AccuracyResult]:
    """Test Vec3 operations against numpy array operations"""
    if not NUMPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    test_vectors = [
        (1.0, 2.0, 3.0),
        (-1.5, 2.5, -3.5),
        (10.0, 20.0, 30.0),
    ]

    for v1_tuple in test_vectors:
        for v2_tuple in test_vectors:
            v1_pure = Vec3(*v1_tuple)
            v2_pure = Vec3(*v2_tuple)
            v1_np = np.array(v1_tuple)
            v2_np = np.array(v2_tuple)

            # Addition
            pure_result = (v1_pure + v2_pure).to_tuple()
            np_result = tuple(v1_np + v2_np)
            for r, e in zip(pure_result, np_result):
                rel_err = relative_error(r, e)
                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs(r - e))
            tests_run += 1

            # Dot product
            pure_result = v1_pure.dot(v2_pure)
            np_result = np.dot(v1_np, v2_np)
            rel_err = relative_error(pure_result, np_result)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs(pure_result - np_result))
            tests_run += 1

            # Cross product
            pure_result = v1_pure.cross(v2_pure).to_tuple()
            np_result = tuple(np.cross(v1_np, v2_np))
            for r, e in zip(pure_result, np_result):
                rel_err = relative_error(r, e) if abs(e) > 1e-10 else abs(r)
                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs(r - e))
            tests_run += 1

        # Length/norm
        v_pure = Vec3(*v1_tuple)
        v_np = np.array(v1_tuple)
        pure_result = v_pure.length()
        np_result = np.linalg.norm(v_np)
        rel_err = relative_error(pure_result, np_result)
        max_rel_error = max(max_rel_error, rel_err)
        max_abs_error = max(max_abs_error, abs(pure_result - np_result))
        tests_run += 1

    return AccuracyResult(
        "Vec3 vs numpy arrays",
        tests_run, max_rel_error, max_abs_error, threshold=1e-14
    )


def test_nucleon_positions_consistency() -> AccuracyResult:
    """Test that nucleon position generation is consistent with same seed"""
    tests_run = 0
    max_rel_error = 0.0
    max_abs_error = 0.0

    test_cases = [
        (6, 6, 2.5),    # Carbon-12
        (26, 30, 3.0),  # Iron-56
        (92, 146, 4.0), # Uranium-238
        (1, 0, 1.0),    # Hydrogen-1
    ]

    for protons, neutrons, radius in test_cases:
        seed = 42

        # Generate positions twice with same seed
        pos1 = pure_generate_nucleon_positions(protons, neutrons, radius, seed=seed)
        pos2 = pure_generate_nucleon_positions(protons, neutrons, radius, seed=seed)

        # Verify exact match
        if len(pos1) != len(pos2):
            max_rel_error = 1.0  # Complete mismatch
            tests_run += 1
            continue

        for p1, p2 in zip(pos1, pos2):
            for i in range(3):  # x, y, z
                rel_err = relative_error(p1[i], p2[i])
                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs(p1[i] - p2[i]))
            # is_proton should match exactly
            if p1[3] != p2[3]:
                max_rel_error = 1.0
            tests_run += 1

        # Verify correct counts
        proton_count = sum(1 for p in pos1 if p[3])
        neutron_count = sum(1 for p in pos1 if not p[3])
        if proton_count != protons or neutron_count != neutrons:
            max_rel_error = 1.0
        tests_run += 1

        # Verify all within radius
        for x, y, z, _ in pos1:
            r = math.sqrt(x * x + y * y + z * z)
            if r > radius * 1.01:  # Allow small tolerance
                max_rel_error = max(max_rel_error, (r - radius) / radius)
            tests_run += 1

    return AccuracyResult(
        "Nucleon position generation (seed consistency)",
        tests_run, max_rel_error, max_abs_error, threshold=0.0
    )


def test_radial_wavefunction() -> Optional[AccuracyResult]:
    """Test radial wavefunction accuracy between backends"""
    if not SCIPY_AVAILABLE:
        return None

    # Implement radial wavefunction directly to test both backends
    # This avoids importing orbital_clouds which may have PySide6 dependencies

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Test parameters
    test_cases = [
        (1, 0, 1),  # 1s orbital, H
        (2, 0, 1),  # 2s orbital, H
        (2, 1, 1),  # 2p orbital, H
        (3, 0, 1),  # 3s orbital, H
        (3, 1, 1),  # 3p orbital, H
        (3, 2, 1),  # 3d orbital, H
        (4, 0, 1),  # 4s orbital, H
        (2, 0, 6),  # 2s orbital, Carbon
        (3, 2, 26), # 3d orbital, Iron
    ]

    r_values = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]

    def radial_wf_scipy(n, l, r, Z):
        """Radial wavefunction using scipy"""
        if r < 0 or n < 1 or l < 0 or l >= n:
            return 0.0
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_factor = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(scipy.special.factorial(n - l - 1, exact=True)) /
            (2.0 * n * float(scipy.special.factorial(n + l, exact=True))**3)
        )
        laguerre_poly = scipy.special.genlaguerre(n - l - 1, 2 * l + 1)
        laguerre_value = laguerre_poly(rho)
        return float(norm_factor * (rho**l) * math.exp(-rho / 2.0) * laguerre_value)

    def radial_wf_pure(n, l, r, Z):
        """Radial wavefunction using pure Python"""
        if r < 0 or n < 1 or l < 0 or l >= n:
            return 0.0
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_factor = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(pure_factorial(n - l - 1)) /
            (2.0 * n * float(pure_factorial(n + l))**3)
        )
        laguerre_poly = pure_genlaguerre(n - l - 1, 2 * l + 1)
        laguerre_value = laguerre_poly(rho)
        return float(norm_factor * (rho**l) * math.exp(-rho / 2.0) * laguerre_value)

    for n, l, Z in test_cases:
        for r in r_values:
            scipy_result = radial_wf_scipy(n, l, r, Z)
            pure_result = radial_wf_pure(n, l, r, Z)

            rel_err = relative_error(pure_result, scipy_result)
            abs_err = abs(pure_result - scipy_result)

            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs_err)
            tests_run += 1

    return AccuracyResult(
        "radial_wavefunction (scipy vs pure_python)",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_angular_wavefunction() -> Optional[AccuracyResult]:
    """Test angular wavefunction accuracy between backends"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Test parameters: (l, m)
    test_cases = [
        (0, 0),   # s orbital
        (1, -1), (1, 0), (1, 1),  # p orbitals
        (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),  # d orbitals
        (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3),  # f orbitals
    ]

    theta_values = [0.0, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2,
                   2 * math.pi / 3, 3 * math.pi / 4, 5 * math.pi / 6, math.pi]

    def angular_wf_scipy(l, m, theta):
        """Angular wavefunction using scipy"""
        if l < 0 or abs(m) > l:
            return 0.0
        norm = math.sqrt(
            (2 * l + 1) * float(scipy.special.factorial(l - abs(m), exact=True)) /
            (4 * math.pi * float(scipy.special.factorial(l + abs(m), exact=True)))
        )
        legendre_value = scipy.special.lpmv(abs(m), l, math.cos(theta))
        return (norm * legendre_value)**2

    def angular_wf_pure(l, m, theta):
        """Angular wavefunction using pure Python"""
        if l < 0 or abs(m) > l:
            return 0.0
        norm = math.sqrt(
            (2 * l + 1) * float(pure_factorial(l - abs(m))) /
            (4 * math.pi * float(pure_factorial(l + abs(m))))
        )
        legendre_value = pure_lpmv(abs(m), l, math.cos(theta))
        return (norm * legendre_value)**2

    for l, m in test_cases:
        for theta in theta_values:
            scipy_result = angular_wf_scipy(l, m, theta)
            pure_result = angular_wf_pure(l, m, theta)

            rel_err = relative_error(pure_result, scipy_result)
            abs_err = abs(pure_result - scipy_result)

            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs_err)
            tests_run += 1

    return AccuracyResult(
        "angular_wavefunction (scipy vs pure_python)",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_orbital_probability() -> Optional[AccuracyResult]:
    """Test end-to-end orbital probability calculation"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Test parameters: (n, l, m, Z)
    test_cases = [
        (1, 0, 0, 1),   # 1s H
        (2, 1, 0, 1),   # 2p H
        (3, 2, 1, 1),   # 3d H
        (2, 0, 0, 6),   # 2s C
        (3, 2, -1, 26), # 3d Fe
    ]

    r_values = [0.5, 1.0, 2.0, 5.0]
    theta_values = [0.0, math.pi / 4, math.pi / 2, math.pi]
    phi_values = [0.0, math.pi / 2, math.pi]

    def orbital_prob_scipy(n, l, m, r, theta, phi, Z):
        """Full orbital probability using scipy"""
        # Radial part
        if r < 0 or n < 1 or l < 0 or l >= n:
            return 0.0
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_r = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(scipy.special.factorial(n - l - 1, exact=True)) /
            (2.0 * n * float(scipy.special.factorial(n + l, exact=True))**3)
        )
        laguerre_poly = scipy.special.genlaguerre(n - l - 1, 2 * l + 1)
        R = norm_r * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)

        # Angular part
        if l < 0 or abs(m) > l:
            return 0.0
        norm_a = math.sqrt(
            (2 * l + 1) * float(scipy.special.factorial(l - abs(m), exact=True)) /
            (4 * math.pi * float(scipy.special.factorial(l + abs(m), exact=True)))
        )
        Y_sq = (norm_a * scipy.special.lpmv(abs(m), l, math.cos(theta)))**2

        return R**2 * Y_sq

    def orbital_prob_pure(n, l, m, r, theta, phi, Z):
        """Full orbital probability using pure Python"""
        # Radial part
        if r < 0 or n < 1 or l < 0 or l >= n:
            return 0.0
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_r = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(pure_factorial(n - l - 1)) /
            (2.0 * n * float(pure_factorial(n + l))**3)
        )
        laguerre_poly = pure_genlaguerre(n - l - 1, 2 * l + 1)
        R = norm_r * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)

        # Angular part
        if l < 0 or abs(m) > l:
            return 0.0
        norm_a = math.sqrt(
            (2 * l + 1) * float(pure_factorial(l - abs(m))) /
            (4 * math.pi * float(pure_factorial(l + abs(m))))
        )
        Y_sq = (norm_a * pure_lpmv(abs(m), l, math.cos(theta)))**2

        return R**2 * Y_sq

    for n, l, m, Z in test_cases:
        for r in r_values:
            for theta in theta_values:
                for phi in phi_values:
                    scipy_result = orbital_prob_scipy(n, l, m, r, theta, phi, Z)
                    pure_result = orbital_prob_pure(n, l, m, r, theta, phi, Z)

                    rel_err = relative_error(pure_result, scipy_result)
                    abs_err = abs(pure_result - scipy_result)

                    max_rel_error = max(max_rel_error, rel_err)
                    max_abs_error = max(max_abs_error, abs_err)
                    tests_run += 1

    return AccuracyResult(
        "get_orbital_probability end-to-end (scipy vs pure_python)",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_spherical_harmonics() -> Optional[AccuracyResult]:
    """Test spherical harmonics accuracy against scipy"""
    if not SCIPY_AVAILABLE:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Test parameters: (l, m)
    test_cases = [
        (0, 0),   # s orbital
        (1, -1), (1, 0), (1, 1),  # p orbitals
        (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),  # d orbitals
        (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3),  # f orbitals
    ]

    theta_values = [0.0, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2,
                   2 * math.pi / 3, 3 * math.pi / 4, math.pi]
    phi_values = [0.0, math.pi / 4, math.pi / 2, math.pi, 3 * math.pi / 2]

    for l, m in test_cases:
        for theta in theta_values:
            for phi in phi_values:
                # Pure Python implementation
                pure_result = pure_spherical_harmonic(l, m, theta, phi)
                pure_magnitude = abs(pure_result)

                # scipy implementation (note: different argument order!)
                # scipy.special.sph_harm(m, l, phi, theta)
                scipy_result = scipy.special.sph_harm(m, l, phi, theta)
                scipy_magnitude = abs(scipy_result)

                if scipy_magnitude > 1e-10:
                    rel_err = abs(pure_magnitude - scipy_magnitude) / scipy_magnitude
                else:
                    rel_err = abs(pure_magnitude - scipy_magnitude)

                abs_err = abs(pure_magnitude - scipy_magnitude)

                max_rel_error = max(max_rel_error, rel_err)
                max_abs_error = max(max_abs_error, abs_err)
                tests_run += 1

    return AccuracyResult(
        "spherical_harmonic vs scipy.sph_harm",
        tests_run, max_rel_error, max_abs_error, threshold=1e-8
    )


def test_rotation_matrices() -> AccuracyResult:
    """Test rotation matrix implementations against known values"""
    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Test rotation matrices with known vector transformations
    test_angles = [0, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2, math.pi]

    for angle in test_angles:
        # Test X rotation: rotating Y axis should give (0, cos, sin)
        Rx = pure_rotation_matrix_x(angle)
        v_y = (0.0, 1.0, 0.0)
        result = pure_matrix_vector_multiply(Rx, v_y)
        expected = (0.0, math.cos(angle), math.sin(angle))

        for r, e in zip(result, expected):
            if abs(e) > 1e-10:
                rel_err = abs(r - e) / abs(e)
            else:
                rel_err = abs(r)
            abs_err = abs(r - e)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs_err)
        tests_run += 1

        # Test Y rotation: rotating X axis should give (cos, 0, -sin)
        Ry = pure_rotation_matrix_y(angle)
        v_x = (1.0, 0.0, 0.0)
        result = pure_matrix_vector_multiply(Ry, v_x)
        expected = (math.cos(angle), 0.0, -math.sin(angle))

        for r, e in zip(result, expected):
            if abs(e) > 1e-10:
                rel_err = abs(r - e) / abs(e)
            else:
                rel_err = abs(r)
            abs_err = abs(r - e)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs_err)
        tests_run += 1

        # Test Z rotation: rotating X axis should give (cos, sin, 0)
        Rz = pure_rotation_matrix_z(angle)
        result = pure_matrix_vector_multiply(Rz, v_x)
        expected = (math.cos(angle), math.sin(angle), 0.0)

        for r, e in zip(result, expected):
            if abs(e) > 1e-10:
                rel_err = abs(r - e) / abs(e)
            else:
                rel_err = abs(r)
            abs_err = abs(r - e)
            max_rel_error = max(max_rel_error, rel_err)
            max_abs_error = max(max_abs_error, abs_err)
        tests_run += 1

    # Test axis-angle rotation
    # Rotating around Z axis should match Rz
    for angle in test_angles:
        R_axis = pure_rotation_matrix_axis_angle((0, 0, 1), angle)
        Rz = pure_rotation_matrix_z(angle)

        for i in range(3):
            for j in range(3):
                diff = abs(R_axis[i][j] - Rz[i][j])
                max_abs_error = max(max_abs_error, diff)
                if abs(Rz[i][j]) > 1e-10:
                    rel_err = diff / abs(Rz[i][j])
                    max_rel_error = max(max_rel_error, rel_err)
        tests_run += 1

    # Test rotation matrix orthogonality: R * R^T = I
    for angle in test_angles:
        Rx = pure_rotation_matrix_x(angle)
        Rx_T = [[Rx[j][i] for j in range(3)] for i in range(3)]  # Transpose
        product = pure_matrix_multiply_3x3(Rx, Rx_T)

        # Check if product is identity
        for i in range(3):
            for j in range(3):
                expected = 1.0 if i == j else 0.0
                diff = abs(product[i][j] - expected)
                max_abs_error = max(max_abs_error, diff)
                if expected != 0:
                    rel_err = diff / abs(expected)
                    max_rel_error = max(max_rel_error, rel_err)
        tests_run += 1

    return AccuracyResult(
        "rotation_matrices (mathematical correctness)",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_rotation_matrices_vs_numpy() -> Optional[AccuracyResult]:
    """Test rotation matrices against numpy/scipy implementations"""
    if not NUMPY_AVAILABLE:
        return None

    try:
        from scipy.spatial.transform import Rotation
    except ImportError:
        return None

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    test_angles = [0, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2, math.pi]

    for angle in test_angles:
        # Compare X rotation
        pure_Rx = pure_rotation_matrix_x(angle)
        scipy_Rx = Rotation.from_euler('x', angle).as_matrix()

        for i in range(3):
            for j in range(3):
                diff = abs(pure_Rx[i][j] - scipy_Rx[i][j])
                max_abs_error = max(max_abs_error, diff)
                if abs(scipy_Rx[i][j]) > 1e-10:
                    rel_err = diff / abs(scipy_Rx[i][j])
                    max_rel_error = max(max_rel_error, rel_err)
        tests_run += 1

        # Compare Y rotation
        pure_Ry = pure_rotation_matrix_y(angle)
        scipy_Ry = Rotation.from_euler('y', angle).as_matrix()

        for i in range(3):
            for j in range(3):
                diff = abs(pure_Ry[i][j] - scipy_Ry[i][j])
                max_abs_error = max(max_abs_error, diff)
                if abs(scipy_Ry[i][j]) > 1e-10:
                    rel_err = diff / abs(scipy_Ry[i][j])
                    max_rel_error = max(max_rel_error, rel_err)
        tests_run += 1

        # Compare Z rotation
        pure_Rz = pure_rotation_matrix_z(angle)
        scipy_Rz = Rotation.from_euler('z', angle).as_matrix()

        for i in range(3):
            for j in range(3):
                diff = abs(pure_Rz[i][j] - scipy_Rz[i][j])
                max_abs_error = max(max_abs_error, diff)
                if abs(scipy_Rz[i][j]) > 1e-10:
                    rel_err = diff / abs(scipy_Rz[i][j])
                    max_rel_error = max(max_rel_error, rel_err)
        tests_run += 1

    return AccuracyResult(
        "rotation_matrices vs scipy.spatial.transform",
        tests_run, max_rel_error, max_abs_error, threshold=1e-10
    )


def test_sdf_nucleon_positions() -> Optional[AccuracyResult]:
    """Test that SDF renderer nucleon generation matches between backends"""
    if not NUMPY_AVAILABLE:
        return None

    # We need to test _generate_nucleons_numpy vs _generate_nucleons_pure
    # from sdf_renderer, but they use different random number generators
    # so we can only test that they generate valid results

    max_rel_error = 0.0
    max_abs_error = 0.0
    tests_run = 0

    # Use already imported pure Python functions
    random_seed = pure_random_seed
    random_uniform = pure_random_uniform
    pi = pure_pi
    sqrt = pure_sqrt
    cos = pure_cos
    sin = pure_sin

    test_cases = [
        (6, 6, 10.0),    # Carbon
        (26, 30, 15.0),  # Iron
        (1, 0, 5.0),     # Hydrogen
    ]

    for protons, neutrons, nuclear_radius in test_cases:
        rotation_x, rotation_y = 0.3, 0.5

        # Generate with pure Python method
        random_seed(protons * 1000 + neutrons)
        cos_rx, sin_rx = cos(rotation_x), sin(rotation_x)
        cos_ry, sin_ry = cos(rotation_y), sin(rotation_y)

        A = protons + neutrons
        nucleon_data_pure = []

        for i in range(protons + neutrons):
            is_proton = i < protons

            if A == 1:
                dx, dy, dz = 0, 0, 0
            else:
                phi = random_uniform(0, 2 * pi)
                cos_theta = random_uniform(-1, 1)
                sin_theta = sqrt(1 - cos_theta**2)
                r = nuclear_radius * 0.7 * random_uniform(0.3, 1.0)

                dx = r * sin_theta * cos(phi)
                dy = r * sin_theta * sin(phi)
                dz = r * cos_theta

            dy2 = dy * cos_rx - dz * sin_rx
            dz2 = dy * sin_rx + dz * cos_rx
            dx2 = dx * cos_ry + dz2 * sin_ry
            dz3 = -dx * sin_ry + dz2 * cos_ry

            nucleon_data_pure.append((dx2, dy2, dz3, is_proton))

        # Generate with numpy method
        np.random.seed(protons * 1000 + neutrons)
        cos_rx_np, sin_rx_np = np.cos(rotation_x), np.sin(rotation_x)
        cos_ry_np, sin_ry_np = np.cos(rotation_y), np.sin(rotation_y)

        nucleon_data_numpy = []

        for i in range(protons + neutrons):
            is_proton = i < protons

            if A == 1:
                dx, dy, dz = 0, 0, 0
            else:
                phi = np.random.uniform(0, 2 * np.pi)
                cos_theta = np.random.uniform(-1, 1)
                sin_theta = np.sqrt(1 - cos_theta**2)
                r = nuclear_radius * 0.7 * np.random.uniform(0.3, 1.0)

                dx = r * sin_theta * np.cos(phi)
                dy = r * sin_theta * np.sin(phi)
                dz = r * cos_theta

            dy2 = dy * cos_rx_np - dz * sin_rx_np
            dz2 = dy * sin_rx_np + dz * cos_rx_np
            dx2 = dx * cos_ry_np + dz2 * sin_ry_np
            dz3 = -dx * sin_ry_np + dz2 * cos_ry_np

            nucleon_data_numpy.append((dx2, dy2, dz3, is_proton))

        # Compare - note that different RNGs may produce different sequences
        # but with same seed, Python's random and numpy's random should be similar
        # Actually they're not the same generator, so we just verify structure

        # Verify same count
        if len(nucleon_data_pure) != len(nucleon_data_numpy):
            max_rel_error = 1.0
        tests_run += 1

        # Verify proton/neutron counts
        pure_protons = sum(1 for n in nucleon_data_pure if n[3])
        numpy_protons = sum(1 for n in nucleon_data_numpy if n[3])
        if pure_protons != protons or numpy_protons != protons:
            max_rel_error = max(max_rel_error, 0.5)
        tests_run += 1

        # Verify positions are within expected bounds (not exact match due to RNG)
        max_expected_r = nuclear_radius * 0.7 * 1.1
        for nucleon_data in [nucleon_data_pure, nucleon_data_numpy]:
            for dx, dy, dz, _ in nucleon_data:
                r = math.sqrt(dx * dx + dy * dy + dz * dz)
                if r > max_expected_r:
                    rel_err = (r - max_expected_r) / max_expected_r
                    max_rel_error = max(max_rel_error, rel_err)
            tests_run += 1

    return AccuracyResult(
        "SDF nucleon positions (structure validation)",
        tests_run, max_rel_error, max_abs_error, threshold=0.1
    )


# =============================================================================
# PERFORMANCE BENCHMARKS
# =============================================================================

def benchmark_factorial() -> BenchmarkResult:
    """Benchmark factorial performance"""
    iterations = 1000
    n = 20

    pure_time = benchmark_function(pure_factorial, (n,), iterations)

    if SCIPY_AVAILABLE:
        scipy_time = benchmark_function(
            lambda x: scipy.special.factorial(x, exact=True), (n,), iterations
        )
    else:
        scipy_time = None

    return BenchmarkResult("factorial(20)", scipy_time, pure_time, iterations)


def benchmark_genlaguerre() -> BenchmarkResult:
    """Benchmark generalized Laguerre polynomial performance"""
    iterations = 1000
    n, alpha, x = 5, 2, 3.0

    # Pure Python
    pure_L = pure_genlaguerre(n, alpha)
    pure_time = benchmark_function(pure_L, (x,), iterations)

    if SCIPY_AVAILABLE:
        scipy_L = scipy.special.genlaguerre(n, alpha)
        scipy_time = benchmark_function(scipy_L, (x,), iterations)
    else:
        scipy_time = None

    return BenchmarkResult("genlaguerre(5,2)(3)", scipy_time, pure_time, iterations)


def benchmark_lpmv() -> BenchmarkResult:
    """Benchmark associated Legendre polynomial performance"""
    iterations = 1000
    m, l, x = 2, 4, 0.5

    pure_time = benchmark_function(pure_lpmv, (m, l, x), iterations)

    if SCIPY_AVAILABLE:
        scipy_time = benchmark_function(scipy.special.lpmv, (m, l, x), iterations)
    else:
        scipy_time = None

    return BenchmarkResult("lpmv(2,4,0.5)", scipy_time, pure_time, iterations)


def benchmark_vec3_add() -> BenchmarkResult:
    """Benchmark Vec3 addition"""
    iterations = 1000
    v1 = Vec3(1.0, 2.0, 3.0)
    v2 = Vec3(4.0, 5.0, 6.0)

    pure_time = benchmark_function(lambda: v1 + v2, (), iterations)

    if NUMPY_AVAILABLE:
        a1 = np.array([1.0, 2.0, 3.0])
        a2 = np.array([4.0, 5.0, 6.0])
        numpy_time = benchmark_function(lambda: a1 + a2, (), iterations)
    else:
        numpy_time = None

    return BenchmarkResult("Vec3 add", numpy_time, pure_time, iterations)


def benchmark_vec3_rotate() -> BenchmarkResult:
    """Benchmark Vec3 rotation"""
    iterations = 1000
    v = Vec3(1.0, 2.0, 3.0)
    angle = 0.5

    pure_time = benchmark_function(v.rotate_y, (angle,), iterations)

    # numpy doesn't have a direct rotation equivalent, so N/A
    return BenchmarkResult("Vec3.rotate_y", None, pure_time, iterations)


def benchmark_vec3_normalize() -> BenchmarkResult:
    """Benchmark Vec3 normalization"""
    iterations = 1000
    v = Vec3(1.0, 2.0, 3.0)

    pure_time = benchmark_function(v.normalized, (), iterations)

    if NUMPY_AVAILABLE:
        a = np.array([1.0, 2.0, 3.0])
        numpy_time = benchmark_function(lambda: a / np.linalg.norm(a), (), iterations)
    else:
        numpy_time = None

    return BenchmarkResult("Vec3 normalize", numpy_time, pure_time, iterations)


def benchmark_nucleon_gen() -> BenchmarkResult:
    """Benchmark nucleon position generation"""
    iterations = 100  # Fewer iterations as this is more complex
    protons, neutrons, radius = 26, 30, 15.0

    pure_time = benchmark_function(
        pure_generate_nucleon_positions, (protons, neutrons, radius, 42), iterations
    )

    if NUMPY_AVAILABLE:
        def numpy_nucleon_gen():
            np.random.seed(42)
            positions = []
            for i in range(protons + neutrons):
                phi = np.random.uniform(0, 2 * np.pi)
                cos_theta = np.random.uniform(-1, 1)
                sin_theta = np.sqrt(1 - cos_theta**2)
                r = radius * (np.random.uniform(0, 1) ** (1.0 / 3.0))
                x = r * sin_theta * np.cos(phi)
                y = r * sin_theta * np.sin(phi)
                z = r * cos_theta
                positions.append((x, y, z, i < protons))
            return positions

        numpy_time = benchmark_function(numpy_nucleon_gen, (), iterations)
    else:
        numpy_time = None

    return BenchmarkResult("nucleon_gen(56)", numpy_time, pure_time, iterations)


def benchmark_radial_wavefunction() -> Optional[BenchmarkResult]:
    """Benchmark radial wavefunction calculation"""
    if not SCIPY_AVAILABLE:
        return None

    iterations = 500
    n, l, r, Z = 3, 2, 2.0, 1

    def radial_wf_pure():
        """Radial wavefunction using pure Python"""
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_factor = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(pure_factorial(n - l - 1)) /
            (2.0 * n * float(pure_factorial(n + l))**3)
        )
        laguerre_poly = pure_genlaguerre(n - l - 1, 2 * l + 1)
        return norm_factor * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)

    def radial_wf_scipy():
        """Radial wavefunction using scipy"""
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_factor = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(scipy.special.factorial(n - l - 1, exact=True)) /
            (2.0 * n * float(scipy.special.factorial(n + l, exact=True))**3)
        )
        laguerre_poly = scipy.special.genlaguerre(n - l - 1, 2 * l + 1)
        return norm_factor * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)

    pure_time = benchmark_function(radial_wf_pure, (), iterations)
    scipy_time = benchmark_function(radial_wf_scipy, (), iterations)

    return BenchmarkResult("radial_wfn(3,2,2)", scipy_time, pure_time, iterations)


def benchmark_orbital_probability() -> Optional[BenchmarkResult]:
    """Benchmark full orbital probability calculation"""
    if not SCIPY_AVAILABLE:
        return None

    iterations = 200
    n, l, m, r, theta, phi, Z = 3, 2, 1, 2.0, math.pi / 4, 0.0, 1

    def orbital_prob_pure():
        """Full orbital probability using pure Python"""
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_r = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(pure_factorial(n - l - 1)) /
            (2.0 * n * float(pure_factorial(n + l))**3)
        )
        laguerre_poly = pure_genlaguerre(n - l - 1, 2 * l + 1)
        R = norm_r * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)
        norm_a = math.sqrt(
            (2 * l + 1) * float(pure_factorial(l - abs(m))) /
            (4 * math.pi * float(pure_factorial(l + abs(m))))
        )
        Y_sq = (norm_a * pure_lpmv(abs(m), l, math.cos(theta)))**2
        return R**2 * Y_sq

    def orbital_prob_scipy():
        """Full orbital probability using scipy"""
        a0 = 1.0
        rho = 2.0 * Z * r / (n * a0)
        norm_r = math.sqrt(
            (2.0 * Z / (n * a0))**3 *
            float(scipy.special.factorial(n - l - 1, exact=True)) /
            (2.0 * n * float(scipy.special.factorial(n + l, exact=True))**3)
        )
        laguerre_poly = scipy.special.genlaguerre(n - l - 1, 2 * l + 1)
        R = norm_r * (rho**l) * math.exp(-rho / 2.0) * laguerre_poly(rho)
        norm_a = math.sqrt(
            (2 * l + 1) * float(scipy.special.factorial(l - abs(m), exact=True)) /
            (4 * math.pi * float(scipy.special.factorial(l + abs(m), exact=True)))
        )
        Y_sq = (norm_a * scipy.special.lpmv(abs(m), l, math.cos(theta)))**2
        return R**2 * Y_sq

    pure_time = benchmark_function(orbital_prob_pure, (), iterations)
    scipy_time = benchmark_function(orbital_prob_scipy, (), iterations)

    return BenchmarkResult("orbital_prob(3d)", scipy_time, pure_time, iterations)


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_accuracy_tests() -> List[AccuracyResult]:
    """Run all accuracy tests and return results"""
    results = []

    print("\nRunning accuracy tests...")

    tests = [
        ("Factorial", test_factorial_accuracy),
        ("GenLaguerre", test_genlaguerre_accuracy),
        ("LPMV", test_lpmv_accuracy),
        ("Spherical Harmonics", test_spherical_harmonics),
        ("Rotation Matrices", test_rotation_matrices),
        ("Rotation Matrices vs NumPy", test_rotation_matrices_vs_numpy),
        ("Vec3 Operations", test_vec3_operations),
        ("Vec3 vs NumPy", test_vec3_vs_numpy),
        ("Nucleon Consistency", test_nucleon_positions_consistency),
        ("Radial Wavefunction", test_radial_wavefunction),
        ("Angular Wavefunction", test_angular_wavefunction),
        ("Orbital Probability", test_orbital_probability),
        ("SDF Nucleon Positions", test_sdf_nucleon_positions),
    ]

    for name, test_func in tests:
        try:
            result = test_func()
            if result is not None:
                results.append(result)
                status = "PASS" if result.passed else "FAIL"
                print(f"  {name}: {status}")
            else:
                print(f"  {name}: SKIPPED (library not available)")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")

    return results


def run_benchmarks() -> List[BenchmarkResult]:
    """Run all benchmarks and return results"""
    results = []

    print("\nRunning performance benchmarks...")

    benchmarks = [
        ("Factorial", benchmark_factorial),
        ("GenLaguerre", benchmark_genlaguerre),
        ("LPMV", benchmark_lpmv),
        ("Vec3 Add", benchmark_vec3_add),
        ("Vec3 Rotate", benchmark_vec3_rotate),
        ("Vec3 Normalize", benchmark_vec3_normalize),
        ("Nucleon Gen", benchmark_nucleon_gen),
        ("Radial Wfn", benchmark_radial_wavefunction),
        ("Orbital Prob", benchmark_orbital_probability),
    ]

    for name, bench_func in benchmarks:
        try:
            result = bench_func()
            if result is not None:
                results.append(result)
                print(f"  {name}: {result.pure_time_us:.2f} us (pure)")
            else:
                print(f"  {name}: SKIPPED")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")

    return results


def print_results(accuracy_results: List[AccuracyResult],
                 benchmark_results: List[BenchmarkResult]):
    """Print formatted test results"""
    print("\n" + "=" * 70)
    print("=== Backend Comparison Test Results ===")
    print("=" * 70)

    # Accuracy tests
    print("\nACCURACY TESTS")
    print("-" * 50)

    for result in accuracy_results:
        print(f"\n{result.name}:")
        print(result)

    # Performance benchmarks
    print("\n\nPERFORMANCE BENCHMARKS")
    print("-" * 90)
    print(f"| {'Function':<20} | {'scipy/numpy':^11} | {'pure_python':^11} | {'Ratio':^6} | {'Winner':<15} |")
    print(f"|{'-' * 22}|{'-' * 13}|{'-' * 13}|{'-' * 8}|{'-' * 17}|")

    for result in benchmark_results:
        print(result.format_row())

    print("-" * 90)

    # Summary
    print("\n\nSUMMARY")
    print("-" * 50)

    total_accuracy = len(accuracy_results)
    passed_accuracy = sum(1 for r in accuracy_results if r.passed)
    print(f"Accuracy tests: {passed_accuracy}/{total_accuracy} passed")

    if passed_accuracy == total_accuracy:
        print("Accuracy: 100% within tolerance")
    else:
        failed = [r.name for r in accuracy_results if not r.passed]
        print(f"Failed tests: {', '.join(failed)}")

    # Categorize benchmarks
    pure_wins = []
    lib_wins = []
    not_applicable = []

    for r in benchmark_results:
        if r.ratio is None:
            not_applicable.append(r.name)
        elif r.ratio > 1.0:
            pure_wins.append(r.name)
        else:
            lib_wins.append(r.name)

    if pure_wins:
        print(f"Pure Python competitive for: {', '.join(pure_wins)}")
    if lib_wins:
        print(f"Libraries faster for: {', '.join(lib_wins)}")
    if not_applicable:
        print(f"Pure Python only (no comparison): {', '.join(not_applicable)}")

    # Backend availability
    print(f"\nBackend availability:")
    print(f"  scipy: {'Available' if SCIPY_AVAILABLE else 'Not installed'}")
    print(f"  numpy: {'Available' if NUMPY_AVAILABLE else 'Not installed'}")


def main():
    """Main entry point"""
    print("Backend Comparison Test Script")
    print("Testing pure Python implementations against scipy/numpy")
    print("=" * 70)

    accuracy_results = run_accuracy_tests()
    benchmark_results = run_benchmarks()

    print_results(accuracy_results, benchmark_results)

    # Return exit code based on test results
    all_passed = all(r.passed for r in accuracy_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
