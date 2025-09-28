#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Utilities
Common utilities for SSOT validation and processing
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class SSOTError(Exception):
    """SSOT-related error"""

    pass


class SSOTUtils:
    """Utility class for SSOT operations"""

    def __init__(self, ssot_path: str = "ssot/modules_index.yaml"):
        self.ssot_path = Path(ssot_path)
        self._ssot_data = None

    def load_ssot_manifest(self) -> Dict[str, Any]:
        """Load and cache SSOT manifest"""
        if self._ssot_data is None:
            if not self.ssot_path.exists():
                raise SSOTError(f"SSOT manifest not found: {self.ssot_path}")

            try:
                with open(self.ssot_path, "r") as f:
                    self._ssot_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise SSOTError(f"Failed to parse SSOT manifest: {e}")
            except Exception as e:
                raise SSOTError(f"Error loading SSOT manifest: {e}")

        return self._ssot_data

    def validate_manifest_structure(self) -> List[str]:
        """Validate SSOT manifest structure"""
        errors = []

        try:
            data = self.load_ssot_manifest()
        except SSOTError as e:
            return [str(e)]

        # Check required top-level fields
        required_fields = ["metadata", "anchors"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate metadata
        if "metadata" in data:
            metadata = data["metadata"]
            required_meta_fields = [
                "generated_at",
                "version",
                "platform",
                "total_phases",
            ]
            for field in required_meta_fields:
                if field not in metadata:
                    errors.append(f"Missing metadata field: {field}")

        # Validate anchors
        if "anchors" in data:
            anchors = data["anchors"]
            if not isinstance(anchors, list):
                errors.append("anchors must be a list")
            else:
                for i, anchor in enumerate(anchors):
                    anchor_errors = self._validate_anchor_structure(anchor, i)
                    errors.extend(anchor_errors)

        return errors

    def _validate_anchor_structure(
        self, anchor: Dict[str, Any], index: int
    ) -> List[str]:
        """Validate individual anchor structure"""
        errors = []

        required_fields = [
            "id",
            "family",
            "description",
            "format",
            "owner",
            "version",
            "path",
        ]
        for field in required_fields:
            if field not in anchor:
                errors.append(f"Anchor {index} missing required field: {field}")

        # Validate format
        if "format" in anchor:
            valid_formats = ["yaml", "json", "env", "sql", "conf", "ini", "xml", "toml"]
            if anchor["format"] not in valid_formats:
                errors.append(f"Anchor {index} invalid format: {anchor['format']}")

        # Validate family
        if "family" in anchor:
            valid_families = [
                "api",
                "data",
                "deployment",
                "build",
                "automation",
                "operator",
                "policy",
                "observability",
                "infrastructure",
                "application",
                "security",
                "monitoring",
                "database",
                "networking",
                "storage",
            ]
            if anchor["family"] not in valid_families:
                errors.append(f"Anchor {index} invalid family: {anchor['family']}")

        return errors

    def get_anchor_by_id(self, anchor_id: str) -> Optional[Dict[str, Any]]:
        """Get anchor by ID"""
        try:
            data = self.load_ssot_manifest()
            for anchor in data.get("anchors", []):
                if anchor.get("id") == anchor_id:
                    return anchor
        except SSOTError:
            pass
        return None

    def get_anchors_by_family(self, family: str) -> List[Dict[str, Any]]:
        """Get all anchors in a family"""
        try:
            data = self.load_ssot_manifest()
            return [
                anchor
                for anchor in data.get("anchors", [])
                if anchor.get("family") == family
            ]
        except SSOTError:
            return []

    def validate_anchor_file(self, anchor: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate an anchor file exists and is valid"""
        errors = []
        warnings = []

        anchor_path = Path(anchor.get("path", ""))
        if not anchor_path.exists():
            errors.append(f"Anchor file not found: {anchor_path}")
            return False, errors

        # Check file format matches expected
        expected_format = anchor.get("format", "")
        if expected_format:
            if expected_format == "yaml" and not anchor_path.suffix in [
                ".yaml",
                ".yml",
            ]:
                warnings.append(
                    f"File extension doesn't match expected format: {expected_format}"
                )
            elif expected_format == "json" and anchor_path.suffix != ".json":
                warnings.append(
                    f"File extension doesn't match expected format: {expected_format}"
                )

        # Try to parse file based on format
        try:
            with open(anchor_path, "r") as f:
                content = f.read()

            if expected_format == "yaml":
                yaml.safe_load(content)
            elif expected_format == "json":
                json.loads(content)
            # Add other format validations as needed

        except Exception as e:
            errors.append(f"Failed to parse {expected_format} file {anchor_path}: {e}")
            return False, errors

        return True, warnings

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        if not file_path.exists():
            return ""

        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

    def create_lockfile_entry(self, anchor: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lockfile entry for an anchor"""
        anchor_path = Path(anchor.get("path", ""))
        return {
            "version": anchor.get("version", "v1.0.0"),
            "sha256": self.calculate_file_hash(anchor_path),
            "last_modified": datetime.now().isoformat(),
            "size": anchor_path.stat().st_size if anchor_path.exists() else 0,
        }

    def validate_lockfile_consistency(self, lockfile_path: str) -> List[str]:
        """Validate lockfile consistency with SSOT manifest"""
        errors = []

        if not Path(lockfile_path).exists():
            errors.append(f"Lockfile not found: {lockfile_path}")
            return errors

        try:
            with open(lockfile_path, "r") as f:
                lockfile_data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse lockfile: {e}")
            return errors

        # Check lockfile structure
        required_fields = ["lock_version", "generated_at", "anchors"]
        for field in required_fields:
            if field not in lockfile_data:
                errors.append(f"Lockfile missing required field: {field}")

        if "anchors" not in lockfile_data:
            return errors

        # Validate each anchor in lockfile
        lockfile_anchors = lockfile_data["anchors"]
        ssot_anchors = {
            anchor["id"]: anchor
            for anchor in self.load_ssot_manifest().get("anchors", [])
        }

        for anchor_id, lockfile_entry in lockfile_anchors.items():
            if anchor_id not in ssot_anchors:
                errors.append(f"Lockfile references unknown anchor: {anchor_id}")
                continue

            ssot_anchor = ssot_anchors[anchor_id]

            # Check if file still exists and hash matches
            anchor_path = Path(ssot_anchor.get("path", ""))
            if not anchor_path.exists():
                errors.append(f"Anchor file missing: {anchor_path}")
                continue

            current_hash = self.calculate_file_hash(anchor_path)
            locked_hash = lockfile_entry.get("sha256", "")

            if current_hash != locked_hash:
                errors.append(
                    f"Anchor {anchor_id} has changed since lockfile was created"
                )

        return errors


def main():
    """CLI interface for SSOT utilities"""
    if len(sys.argv) < 2:
        print("Usage: ssot_utils.py <command> [args...]")
        print("Commands:")
        print("  validate-manifest [path]  - Validate SSOT manifest")
        print("  list-anchors [family]     - List anchors, optionally by family")
        print("  validate-anchor <id>      - Validate specific anchor")
        sys.exit(1)

    utils = SSOTUtils()

    command = sys.argv[1]

    if command == "validate-manifest":
        ssot_path = sys.argv[2] if len(sys.argv) > 2 else "ssot/modules_index.yaml"
        utils = SSOTUtils(ssot_path)
        errors = utils.validate_manifest_structure()

        if errors:
            print("❌ SSOT manifest validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✅ SSOT manifest is valid")

    elif command == "list-anchors":
        family = sys.argv[2] if len(sys.argv) > 2 else None

        try:
            if family:
                anchors = utils.get_anchors_by_family(family)
                print(f"Anchors in family '{family}':")
            else:
                data = utils.load_ssot_manifest()
                anchors = data.get("anchors", [])
                print("All anchors:")

            for anchor in anchors:
                print(
                    f"  - {anchor['id']} ({anchor['family']}) - {anchor['description']}"
                )

        except SSOTError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif command == "validate-anchor":
        if len(sys.argv) < 3:
            print("Usage: ssot_utils.py validate-anchor <anchor_id>")
            sys.exit(1)

        anchor_id = sys.argv[2]
        anchor = utils.get_anchor_by_id(anchor_id)

        if not anchor:
            print(f"❌ Anchor not found: {anchor_id}")
            sys.exit(1)

        valid, messages = utils.validate_anchor_file(anchor)

        if valid:
            print(f"✅ Anchor {anchor_id} is valid")
            if messages:
                for msg in messages:
                    print(f"⚠️  {msg}")
        else:
            print(f"❌ Anchor {anchor_id} validation failed:")
            for msg in messages:
                print(f"  - {msg}")
            sys.exit(1)


if __name__ == "__main__":
    main()
