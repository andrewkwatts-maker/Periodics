#!/usr/bin/env python3
"""
Master Test Runner for Periodics
================================

Runs all physics prediction tests and generates a comprehensive report.
Tests the complete prediction chain: Quarks -> Hadrons -> Atoms -> Molecules -> Alloys

Usage:
    python tests/run_all_tests.py
    python tests/run_all_tests.py --verbose
    python tests/run_all_tests.py --quick  # Run only core tests
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class TestResult:
    """Result of running a single test file."""
    name: str
    passed: int
    total: int
    pass_rate: float
    time_seconds: float
    status: str  # "PASS", "PARTIAL", "FAIL", "ERROR"
    output: str


def run_test_file(test_file: str, name: str) -> TestResult:
    """Run a single test file and parse its output."""
    import time

    test_path = Path(__file__).parent / test_file
    if not test_path.exists():
        return TestResult(
            name=name,
            passed=0,
            total=0,
            pass_rate=0.0,
            time_seconds=0.0,
            status="ERROR",
            output=f"Test file not found: {test_file}"
        )

    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return TestResult(
            name=name,
            passed=0,
            total=0,
            pass_rate=0.0,
            time_seconds=300.0,
            status="ERROR",
            output="Test timed out after 5 minutes"
        )
    except Exception as e:
        return TestResult(
            name=name,
            passed=0,
            total=0,
            pass_rate=0.0,
            time_seconds=time.time() - start_time,
            status="ERROR",
            output=str(e)
        )

    elapsed = time.time() - start_time

    # Parse output to extract test results
    passed, total = parse_test_output(output)

    if total == 0:
        pass_rate = 0.0
        status = "ERROR"
    else:
        pass_rate = (passed / total) * 100
        if pass_rate == 100:
            status = "PASS"
        elif pass_rate >= 80:
            status = "PARTIAL"
        else:
            status = "FAIL"

    return TestResult(
        name=name,
        passed=passed,
        total=total,
        pass_rate=pass_rate,
        time_seconds=elapsed,
        status=status,
        output=output
    )


def parse_test_output(output: str) -> Tuple[int, int]:
    """Parse test output to extract passed/total counts."""
    import re

    # Try different patterns (order matters - more specific first)
    patterns = [
        # "Overall property pass rate: 62/88 (70.5%)" - quark tests
        (r'Overall property pass rate:\s*(\d+)/(\d+)', None),
        # "Molecules passed: X" and "Total molecules tested: Y"
        (r'Molecules passed:\s*(\d+)', r'Total molecules tested:\s*(\d+)'),
        # "Passed: X" and "Total: Y"
        (r'Passed:\s*(\d+)', r'Total:\s*(\d+)'),
        # "X/Y passed" or "X/Y pass"
        (r'(\d+)/(\d+)\s+pass', None),
        # "Pass Rate: X.X%" pattern with Total
        (r'Pass Rate:\s*([\d.]+)%', r'Total:\s*(\d+)'),
        # "PASS: X" and "Total property comparisons: Y"
        (r'PASS:\s*(\d+)', r'Total property comparisons:\s*(\d+)'),
        # Validation pattern
        (r'Validations Passed:\s*(\d+)', r'Total Property Validations:\s*(\d+)'),
        # Particles pattern
        (r'Particles:\s*(\d+)/(\d+)', None),
    ]

    for pattern in patterns:
        if pattern[1] is None:
            # Combined pattern like "X/Y passed"
            match = re.search(pattern[0], output, re.IGNORECASE)
            if match:
                return int(match.group(1)), int(match.group(2))
        else:
            # Separate patterns
            passed_match = re.search(pattern[0], output, re.IGNORECASE)
            total_match = re.search(pattern[1], output, re.IGNORECASE)
            if passed_match and total_match:
                if '%' in pattern[0]:
                    # Handle percentage pattern
                    pass_rate = float(passed_match.group(1))
                    total = int(total_match.group(1))
                    passed = int(total * pass_rate / 100)
                else:
                    passed = int(passed_match.group(1))
                    total = int(total_match.group(1))
                return passed, total

    return 0, 0


def print_header():
    """Print test runner header."""
    print("=" * 80)
    print("PERIODICS COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print()


def print_results(results: List[TestResult]):
    """Print test results summary."""
    print()
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Status symbols
    status_symbols = {
        "PASS": "[PASS]",
        "PARTIAL": "[OK]",
        "FAIL": "[FAIL]",
        "ERROR": "[ERR]"
    }

    print(f"{'Test Name':<40} {'Status':^8} {'Pass Rate':>10} {'Time':>10}")
    print("-" * 80)

    total_passed = 0
    total_tests = 0
    total_time = 0.0

    for r in results:
        symbol = status_symbols.get(r.status, "[???]")
        rate_str = f"{r.pass_rate:.1f}%" if r.total > 0 else "N/A"
        time_str = f"{r.time_seconds:.2f}s"
        print(f"{r.name:<40} {symbol:^8} {rate_str:>10} {time_str:>10}")

        total_passed += r.passed
        total_tests += r.total
        total_time += r.time_seconds

    print("-" * 80)

    # Overall summary
    if total_tests > 0:
        overall_rate = (total_passed / total_tests) * 100
    else:
        overall_rate = 0.0

    print(f"{'OVERALL':<40} {'':^8} {overall_rate:>9.1f}% {total_time:>9.2f}s")
    print()

    # Detailed statistics
    print("DETAILED STATISTICS")
    print("-" * 40)
    print(f"  Total Test Suites: {len(results)}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Total Passed: {total_passed}")
    print(f"  Total Failed: {total_tests - total_passed}")
    print(f"  Overall Pass Rate: {overall_rate:.1f}%")
    print(f"  Total Time: {total_time:.2f}s")
    print()

    # Test layer coverage
    print("PREDICTION LAYER COVERAGE")
    print("-" * 40)
    layers = {
        "Quarks": next((r for r in results if "quark" in r.name.lower()), None),
        "Hadrons (Subatomic)": next((r for r in results if "subatomic" in r.name.lower()), None),
        "Atoms (Elements)": next((r for r in results if "element" in r.name.lower()), None),
        "Molecules": next((r for r in results if "molecule" in r.name.lower()), None),
        "Full Chain": next((r for r in results if "chain" in r.name.lower()), None),
    }

    for layer_name, result in layers.items():
        if result:
            status = "VALIDATED" if result.pass_rate >= 80 else "NEEDS WORK"
            print(f"  {layer_name}: {result.pass_rate:.1f}% [{status}]")
        else:
            print(f"  {layer_name}: NOT TESTED")
    print()

    return overall_rate >= 80.0


def main():
    """Run all tests and generate report."""
    import argparse

    parser = argparse.ArgumentParser(description="Run all Periodics tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Run only core tests")
    args = parser.parse_args()

    print_header()

    # Define test files
    if args.quick:
        test_files = [
            ("test_prediction_chain.py", "Prediction Chain Tests"),
            ("test_subatomic_complete.py", "Subatomic Particle Tests"),
        ]
    else:
        test_files = [
            ("test_prediction_chain.py", "Prediction Chain (Quarks->Alloys)"),
            ("test_quark_to_hadron_complete.py", "Quark to Hadron Layer"),
            ("test_subatomic_complete.py", "Subatomic Particle Validation"),
            ("test_all_118_elements.py", "All 118 Elements"),
            ("test_molecules_complete.py", "Molecule Validation"),
        ]

    results = []
    for test_file, name in test_files:
        print(f"Running {name}...", end=" ", flush=True)
        result = run_test_file(test_file, name)
        print(f"{result.status} ({result.pass_rate:.1f}%)")
        results.append(result)

        if args.verbose and result.status != "PASS":
            print(f"\n  Output excerpt:\n")
            lines = result.output.split('\n')
            for line in lines[-20:]:
                print(f"    {line}")
            print()

    success = print_results(results)

    print("=" * 80)
    if success:
        print("OVERALL STATUS: PASS (All critical tests passing)")
    else:
        print("OVERALL STATUS: NEEDS ATTENTION (Some tests below 80%)")
    print("=" * 80)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
