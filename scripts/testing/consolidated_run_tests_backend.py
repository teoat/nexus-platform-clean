# Consolidated file from run_tests.py
# Generated on 2025-09-24T15:09:04.060525

# === run_tests.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Test Runner
Comprehensive test runner with different test categories
"""

import argparse
import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.stdout:
        print("STDOUT:")
        print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    return result.returncode == 0


def run_unit_tests():
    """Run unit tests."""
    return run_command("python -m pytest tests/ -m unit -v --tb=short", "Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    return run_command(
        "python -m pytest tests/ -m integration -v --tb=short", "Integration Tests"
    )


def run_security_tests():
    """Run security tests."""
    return run_command(
        "python -m pytest tests/test_security.py -v --tb=short", "Security Tests"
    )


def run_auth_tests():
    """Run authentication tests."""
    return run_command(
        "python -m pytest tests/test_auth.py -v --tb=short", "Authentication Tests"
    )


def run_api_tests():
    """Run API endpoint tests."""
    return run_command(
        "python -m pytest tests/test_api_endpoints.py -v --tb=short",
        "API Endpoint Tests",
    )


def run_all_tests():
    """Run all tests."""
    return run_command(
        "python -m pytest tests/ -v --tb=short --cov=app --cov=backend --cov=database --cov-report=html:htmlcov --cov-report=term-missing",
        "All Tests with Coverage",
    )


def run_coverage_report():
    """Generate coverage report."""
    return run_command(
        "python -m pytest tests/ --cov=app --cov=backend --cov=database --cov-report=html:htmlcov --cov-report=term-missing --cov-report=xml",
        "Coverage Report",
    )


def run_security_scan():
    """Run security scanning."""
    return run_command(
        "bandit -r nexus_nexus_backend/ nexus_nexus_backend/ database/ -f json -o security-report.json",
        "Security Scan with Bandit",
    )


def run_dependency_check():
    """Run dependency vulnerability check."""
    return run_command(
        "safety check --json --output safety-report.json",
        "Dependency Vulnerability Check",
    )


def run_performance_tests():
    """Run performance tests."""
    return run_command(
        "python -m pytest tests/ -m performance -v --tb=short", "Performance Tests"
    )


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="NEXUS Platform Test Runner")
    parser.add_argument(
        "--type",
        choices=[
            "unit",
            "integration",
            "security",
            "auth",
            "api",
            "all",
            "coverage",
            "security-scan",
            "deps",
            "performance",
        ],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Change to the app directory
    os.chdir(Path(__file__).parent)

    print("NEXUS Platform - Test Runner")
    print("=" * 60)

    success = True

    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "security":
        success = run_security_tests()
    elif args.type == "auth":
        success = run_auth_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "all":
        success = run_all_tests()
    elif args.type == "coverage":
        success = run_coverage_report()
    elif args.type == "security-scan":
        success = run_security_scan()
    elif args.type == "deps":
        success = run_dependency_check()
    elif args.type == "performance":
        success = run_performance_tests()

    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()


# === run_tests.py ===
#!/usr/bin/env python3
"""
Test Runner for NEXUS Platform Backend
"""

import os
import subprocess
import sys


def run_command(command: List[str], description: str) -> bool:
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")  # Changed to join for display
    print(f"{'='*60}")

    result = subprocess.run(command, shell=False, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print("Output:")
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("Error:")
            print(result.stderr)
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return False

    return True


def main():
    """Main test runner function."""
    print("🚀 NEXUS Platform Backend Test Suite")
    print("=" * 60)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Install test dependencies
    if not run_command(
        ["pip", "install", "-r", "requirements-test.txt"],
        "Installing test dependencies",
    ):
        print("❌ Failed to install test dependencies")
        sys.exit(1)

    # Run different test suites
    test_commands = [
        (["pytest", "tests/test_auth_api.py", "-v"], "Authentication API Tests"),
        (["pytest", "tests/test_accounts_api.py", "-v"], "Accounts API Tests"),
        (["pytest", "tests/test_transactions_api.py", "-v"], "Transactions API Tests"),
        (["pytest", "tests/test_analytics_api.py", "-v"], "Analytics API Tests"),
        (["pytest", "tests/test_monitoring_api.py", "-v"], "Monitoring API Tests"),
        (["pytest", "tests/test_integration.py", "-v"], "Integration Tests"),
        (
            ["pytest", "tests/test_performance.py", "-v", "-m", "not slow"],
            "Performance Tests (Fast)",
        ),
    ]

    all_passed = True

    for command, description in test_commands:
        if not run_command(command, description):
            all_passed = False

    # Run all tests with coverage
    if not run_command(
        [
            "pytest",
            "tests/",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
        ],
        "All Tests with Coverage",
    ):
        all_passed = False

    # Run slow tests separately
    if not run_command(
        ["pytest", "tests/test_performance.py", "-v", "-m", "slow"],
        "Performance Tests (Slow)",
    ):
        all_passed = False

    # Summary
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Backend test suite completed successfully")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔍 Check the output above for details")
        sys.exit(1)

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
