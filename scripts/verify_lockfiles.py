#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Lockfile Verifier
Checks that lockfiles exist, are valid JSON, and reference declared SSOT anchors
"""

import json
import sys
from pathlib import Path
from typing import List

from ssot_utils import SSOTError, SSOTUtils


def load_json(path: Path):
    """Load and parse JSON file"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")
        return None


def validate_lockfile_structure(data: dict, file_path: str) -> List[str]:
    """Validate lockfile structure"""
    errors = []

    # Required fields
    required_fields = {"lock_version", "generated_at", "anchors"}
    missing_fields = required_fields - data.keys()
    if missing_fields:
        errors.append(
            f"{file_path} missing required fields: {', '.join(missing_fields)}"
        )

    # Validate lock_version
    if "lock_version" in data:
        if not isinstance(data["lock_version"], int) or data["lock_version"] != 1:
            errors.append(
                f"{file_path} invalid lock_version: {data['lock_version']} (expected 1)"
            )

    # Validate generated_at
    if "generated_at" in data:
        if not isinstance(data["generated_at"], str):
            errors.append(f"{file_path} generated_at must be a string")

    # Validate workflow (optional)
    if "workflow" in data:
        if (
            not isinstance(data["workflow"], str)
            or not data["workflow"].replace("_", "").replace("-", "").isalnum()
        ):
            errors.append(f"{file_path} invalid workflow format: '{data['workflow']}'")

    # Validate anchors
    if "anchors" in data:
        if not isinstance(data["anchors"], dict):
            errors.append(f"{file_path} anchors field must be a dictionary")
        else:
            # Validate each anchor entry
            for anchor_id, anchor_data in data["anchors"].items():
                if not isinstance(anchor_data, dict):
                    errors.append(
                        f"{file_path} anchor '{anchor_id}' must be a dictionary"
                    )
                    continue

                # Check required anchor fields
                required_anchor_fields = {"version", "sha256"}
                missing_anchor_fields = required_anchor_fields - anchor_data.keys()
                if missing_anchor_fields:
                    errors.append(
                        f"{file_path} anchor '{anchor_id}' missing fields: {', '.join(missing_anchor_fields)}"
                    )

                # Validate version format
                if "version" in anchor_data:
                    version = anchor_data["version"]
                    if not isinstance(version, str) or not version.startswith("v"):
                        errors.append(
                            f"{file_path} anchor '{anchor_id}' invalid version format: '{version}'"
                        )

                # Validate SHA256 format
                if "sha256" in anchor_data:
                    sha256 = anchor_data["sha256"]
                    if (
                        not isinstance(sha256, str)
                        or len(sha256) != 64
                        or not all(c in "0123456789abcdef" for c in sha256.lower())
                    ):
                        errors.append(
                            f"{file_path} anchor '{anchor_id}' invalid SHA256 format: '{sha256}'"
                        )

    return errors


def check_lockfile_consistency_with_ssot(
    lockfiles: List[Path], ssot_utils: SSOTUtils
) -> List[str]:
    """Check consistency between lockfiles and SSOT manifest"""
    errors = []

    # Get anchor IDs from SSOT manifest
    try:
        manifest_data = ssot_utils.load_ssot_manifest()
        ssot_anchor_ids = {
            anchor["id"]
            for anchor in manifest_data.get("anchors", [])
            if isinstance(anchor, dict)
        }
    except SSOTError as e:
        errors.append(f"Could not load SSOT manifest: {e}")
        return errors

    # Check each lockfile
    for lockfile_path in lockfiles:
        data = load_json(lockfile_path)
        if not data:
            continue

        if "anchors" in data:
            lockfile_anchor_ids = set(data["anchors"].keys())

            # Check for anchors in lockfile but not in SSOT manifest
            unknown_anchors = lockfile_anchor_ids - ssot_anchor_ids
            if unknown_anchors:
                errors.append(
                    f"{lockfile_path.name} references unknown anchors: {', '.join(unknown_anchors)}"
                )

            # Check for anchors in SSOT manifest but not in lockfile (warning only)
            missing_anchors = ssot_anchor_ids - lockfile_anchor_ids
            if missing_anchors:
                print(
                    f"⚠️  {lockfile_path.name} missing anchors: {', '.join(missing_anchors)}"
                )

            # Validate anchor data consistency
            for anchor_id in lockfile_anchor_ids:
                if anchor_id in ssot_anchor_ids:
                    ssot_anchor = ssot_utils.get_anchor_by_id(anchor_id)
                    if ssot_anchor:
                        # Check if the file exists and hash is current
                        lockfile_errors = ssot_utils.validate_lockfile_consistency(
                            str(lockfile_path)
                        )
                        errors.extend(
                            [f"{lockfile_path.name}: {err}" for err in lockfile_errors]
                        )

    return errors


def main():
    """Main lockfile verification function"""
    if len(sys.argv) < 2:
        print("Usage: verify_lockfiles.py <lockfiles-directory> [ssot-manifest-path]")
        print("  lockfiles-directory: Directory containing lockfiles to validate")
        print(
            "  ssot-manifest-path: Path to SSOT manifest (default: ssot/modules_index.yaml)"
        )
        sys.exit(1)

    lock_dir = Path(sys.argv[1])
    if not lock_dir.exists():
        print(f"❌ Lockfile directory not found: {lock_dir}")
        sys.exit(1)

    ssot_manifest_path = sys.argv[2] if len(sys.argv) > 2 else "ssot/modules_index.yaml"

    # Initialize SSOT utils
    try:
        ssot_utils = SSOTUtils(ssot_manifest_path)
    except SSOTError as e:
        print(f"❌ SSOT initialization failed: {e}")
        sys.exit(1)

    # Find all JSON lockfiles
    lockfiles = list(lock_dir.glob("*.json"))
    if not lockfiles:
        print("⚠️  No lockfiles found in directory.")
        sys.exit(1)

    print(f"🔍 Found {len(lockfiles)} lockfiles to validate")
    print(f"📋 Using SSOT manifest: {ssot_manifest_path}")

    errors = []

    # Validate each lockfile structure
    print("\n🔒 Validating lockfile structures...")
    for lockfile_path in lockfiles:
        print(f"  Checking {lockfile_path.name}...")
        data = load_json(lockfile_path)
        if data:
            structure_errors = validate_lockfile_structure(data, lockfile_path.name)
            errors.extend(structure_errors)
        else:
            errors.append(f"{lockfile_path.name} is invalid JSON")

    # Check consistency with SSOT manifest
    print("\n🔗 Checking consistency with SSOT manifest...")
    consistency_errors = check_lockfile_consistency_with_ssot(lockfiles, ssot_utils)
    errors.extend(consistency_errors)

    # Report results
    print("\n" + "=" * 50)
    if errors:
        print("❌ Lockfile validation failed with errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ All lockfiles validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
