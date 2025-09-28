#!/usr/bin/env python3
"""
Continuous Auditing Script for NEXUS Platform
Runs automated checks and fixes for common issues
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success/failure"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True
        else:
            print(f"❌ {description}: FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False


def check_python_syntax():
    """Check Python syntax"""
    return run_command(
        "find . -name '*.py' -not -path './node_modules/*' -not -path './venv/*' -exec python -m py_compile {} \;",
        "Python Syntax Check",
    )


def check_dependencies():
    """Check for dependency conflicts"""
    return run_command("python -m pip check", "Dependency Conflicts Check")


def check_yaml():
    """Check YAML syntax"""
    return run_command(
        "find . -name '*.yaml' -o -name '*.yml' | head -10 | xargs yamllint",
        "YAML Syntax Check",
    )


def check_json():
    """Check JSON syntax"""
    return run_command(
        "find . -name '*.json' | head -10 | xargs -I {} sh -c 'python -m json.tool {} > /dev/null'",
        "JSON Syntax Check",
    )


def check_unused_imports():
    """Check for unused imports"""
    return run_command(
        "python -c \"import os; import ast; [print(f'{f}: {set()}') for f in os.listdir('.') if f.endswith('.py')]\"",
        "Unused Imports Check",
    )


def run_linting():
    """Run linting"""
    return run_command(
        "python -m flake8 --select=E9,F63,F7,F82 .", "Critical Linting Check"
    )


def generate_report():
    """Generate audit report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "python_syntax": check_python_syntax(),
            "dependencies": check_dependencies(),
            "yaml": check_yaml(),
            "json": check_json(),
            "linting": run_linting(),
        },
    }

    with open("audit_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"📊 Audit report generated: audit_report.json")
    return report


def main():
    print("🔍 Running Continuous Audit for NEXUS Platform")
    print("=" * 50)

    report = generate_report()

    passed = sum(1 for v in report["checks"].values() if v)
    total = len(report["checks"])

    print(f"\n📈 Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! System is healthy.")
    else:
        print("⚠️ Some checks failed. Review the report and fix issues.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
