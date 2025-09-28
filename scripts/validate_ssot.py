#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Validation Script
Validates SSOT manifest and anchor files
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from ssot_utils import SSOTUtils, SSOTError

def validate_ssot_manifest(ssot_path: str = "ssot/modules_index.yaml") -> Dict[str, Any]:
    """Validate SSOT manifest structure and content"""
    results = {
        "valid": True,
        "manifest_valid": False,
        "anchors_validated": 0,
        "anchors_valid": 0,
        "issues": [],
        "warnings": []
    }

    try:
        utils = SSOTUtils(ssot_path)

        # Validate manifest structure
        manifest_errors = utils.validate_manifest_structure()
        if manifest_errors:
            results["valid"] = False
            results["issues"].extend(manifest_errors)
            return results

        results["manifest_valid"] = True

        # Load manifest data
        manifest_data = utils.load_ssot_manifest()
        anchors = manifest_data.get("anchors", [])

        print(f"Found {len(anchors)} anchors in manifest")

        # Validate each anchor file
        for anchor in anchors:
            anchor_id = anchor.get("id", "unknown")
            results["anchors_validated"] += 1

            print(f"Validating anchor: {anchor_id}")

            valid, messages = utils.validate_anchor_file(anchor)
            if valid:
                results["anchors_valid"] += 1
                if messages:  # warnings
                    results["warnings"].extend([f"{anchor_id}: {msg}" for msg in messages])
            else:
                results["valid"] = False
                results["issues"].extend([f"{anchor_id}: {msg}" for msg in messages])

    except SSOTError as e:
        results["valid"] = False
        results["issues"].append(f"SSOT error: {e}")
    except Exception as e:
        results["valid"] = False
        results["issues"].append(f"Unexpected error: {e}")

    return results

def validate_lockfiles_consistency(ssot_path: str = "ssot/modules_index.yaml", lockfile_dir: str = "ssot/lockfiles/") -> Dict[str, Any]:
    """Validate lockfile consistency"""
    results = {
        "valid": True,
        "lockfiles_checked": 0,
        "issues": [],
        "warnings": []
    }

    lockfile_path_obj = Path(lockfile_dir)
    if not lockfile_path_obj.exists():
        results["warnings"].append(f"Lockfile directory not found: {lockfile_dir}")
        return results

    # Find all lockfiles
    lockfiles = list(lockfile_path_obj.glob("*.json"))
    results["lockfiles_checked"] = len(lockfiles)

    if not lockfiles:
        results["warnings"].append("No lockfiles found")
        return results

    utils = SSOTUtils(ssot_path)

    for lockfile in lockfiles:
        print(f"Checking lockfile: {lockfile.name}")
        errors = utils.validate_lockfile_consistency(str(lockfile))
        if errors:
            results["valid"] = False
            results["issues"].extend([f"{lockfile.name}: {err}" for err in errors])

    return results

def main():
    """Main validation function"""
    print("🔍 NEXUS SSOT Validation")
    print("=" * 50)

    ssot_path = "ssot/modules_index.yaml"

    # Check if SSOT manifest exists
    if not Path(ssot_path).exists():
        print(f"❌ SSOT manifest not found: {ssot_path}")
        print("Run Phase 1 first to create the SSOT manifest")
        sys.exit(1)

    # Validate SSOT manifest and anchors
    print("\n📋 Validating SSOT Manifest and Anchors...")
    manifest_results = validate_ssot_manifest(ssot_path)

    if manifest_results["manifest_valid"]:
        print("✅ SSOT manifest structure is valid")
    else:
        print("❌ SSOT manifest validation failed:")
        for issue in manifest_results["issues"]:
            print(f"  - {issue}")

    if manifest_results["anchors_validated"] > 0:
        print(f"✅ Validated {manifest_results['anchors_valid']}/{manifest_results['anchors_validated']} anchor files")

        if manifest_results["issues"]:
            print("❌ Anchor validation issues:")
            for issue in manifest_results["issues"]:
                print(f"  - {issue}")

        if manifest_results["warnings"]:
            print("⚠️  Anchor validation warnings:")
            for warning in manifest_results["warnings"]:
                print(f"  - {warning}")

    # Validate lockfile consistency
    print("\n🔒 Validating Lockfile Consistency...")
    lockfile_results = validate_lockfiles_consistency(ssot_path)

    if lockfile_results["lockfiles_checked"] > 0:
        if lockfile_results["valid"]:
            print(f"✅ All {lockfile_results['lockfiles_checked']} lockfiles are consistent")
        else:
            print("❌ Lockfile consistency issues:")
            for issue in lockfile_results["issues"]:
                print(f"  - {issue}")

        if lockfile_results["warnings"]:
            print("⚠️  Lockfile warnings:")
            for warning in lockfile_results["warnings"]:
                print(f"  - {warning}")
    else:
        print("⚠️  No lockfiles to validate")

    # Overall result
    overall_valid = manifest_results["valid"] and lockfile_results["valid"]

    print("\n" + "=" * 50)
    if overall_valid:
        print("🎉 SSOT validation completed successfully!")
        sys.exit(0)
    else:
        print("💥 SSOT validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()