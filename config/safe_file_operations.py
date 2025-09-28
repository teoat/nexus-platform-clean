"""
NEXUS Platform - Safe File Operations
This module provides safe file operations with automatic locking.
"""

import json
import logging
import os
import shutil

import yaml

logger = logging.getLogger(__name__)


class SafeFileOperations:
    """
    Provides safe file operations with automatic locking.
    """

    def __init__(self):
        self.lock_manager = get_file_lock_manager()

    @contextmanager
    def safe_write(
        self, file_path: Union[str, Path], content: str, encoding: str = "utf-8"
    ):
        """
        Safely write content to a file with locking.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
        """
        file_path = Path(file_path)
        with self.lock_manager.exclusive_lock(file_path):
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first
            temp_file = file_path.with_suffix(file_path.suffix + ".tmp")
            try:
                with open(temp_file, "w", encoding=encoding) as f:
                    f.write(content)

                # Atomic move
                temp_file.replace(file_path)
                logger.debug(f"Safely wrote to file: {file_path}")

            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                raise e

    @contextmanager
    def safe_read(self, file_path: Union[str, Path], encoding: str = "utf-8"):
        """
        Safely read content from a file with locking.

        Args:
            file_path: Path to the file
            encoding: File encoding

        Yields:
            File content as string
        """
        file_path = Path(file_path)
        with self.lock_manager.shared_lock(file_path):
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            yield content

    @contextmanager
    def safe_json_write(self, file_path: Union[str, Path], data: Any, indent: int = 2):
        """
        Safely write JSON data to a file with locking.

        Args:
            file_path: Path to the file
            data: Data to serialize as JSON
            indent: JSON indentation
        """
        content = json.dumps(data, indent=indent, default=str)
        with self.safe_write(file_path, content, "utf-8"):
            yield file_path

    @contextmanager
    def safe_json_read(self, file_path: Union[str, Path]):
        """
        Safely read JSON data from a file with locking.

        Args:
            file_path: Path to the file

        Yields:
            Parsed JSON data
        """
        with self.safe_read(file_path) as content:
            data = json.loads(content)
            yield data

    @contextmanager
    def safe_yaml_write(self, file_path: Union[str, Path], data: Any):
        """
        Safely write YAML data to a file with locking.

        Args:
            file_path: Path to the file
            data: Data to serialize as YAML
        """
        content = yaml.dump(data, default_flow_style=False)
        with self.safe_write(file_path, content, "utf-8"):
            yield file_path

    @contextmanager
    def safe_yaml_read(self, file_path: Union[str, Path]):
        """
        Safely read YAML data from a file with locking.

        Args:
            file_path: Path to the file

        Yields:
            Parsed YAML data
        """
        with self.safe_read(file_path) as content:
            data = yaml.safe_load(content)
            yield data

    def safe_copy(self, src_path: Union[str, Path], dst_path: Union[str, Path]):
        """
        Safely copy a file with locking.

        Args:
            src_path: Source file path
            dst_path: Destination file path
        """
        src_path = Path(src_path)
        dst_path = Path(dst_path)

        with self.lock_manager.shared_lock(src_path):
            with self.lock_manager.exclusive_lock(dst_path):
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                logger.debug(f"Safely copied {src_path} to {dst_path}")

    def is_locked(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file is currently locked.

        Args:
            file_path: Path to the file

        Returns:
            True if file is locked, False otherwise
        """
        return self.lock_manager.is_locked(file_path)

    def get_lock_info(self, file_path: Union[str, Path]):
        """
        Get information about the current lock on a file.

        Args:
            file_path: Path to the file

        Returns:
            LockInfo object or None if not locked
        """
        return self.lock_manager.get_lock_info(file_path)

    def list_locks(self) -> Dict[str, Any]:
        """
        Get information about all active locks.

        Returns:
            Dictionary of active locks
        """
        return self.lock_manager.get_all_locks()


# Global instance
_safe_file_ops = SafeFileOperations()


def get_safe_file_operations() -> SafeFileOperations:
    """Get the global safe file operations instance"""
    return _safe_file_ops


# Convenience functions
def safe_write(file_path: Union[str, Path], content: str, encoding: str = "utf-8"):
    """Convenience function for safe file writing"""
    with get_safe_file_operations().safe_write(file_path, content, encoding):
        pass


def safe_read(file_path: Union[str, Path], encoding: str = "utf-8"):
    """Convenience function for safe file reading"""
    with get_safe_file_operations().safe_read(file_path, encoding) as content:
        return content


def safe_json_write(file_path: Union[str, Path], data: Any, indent: int = 2):
    """Convenience function for safe JSON writing"""
    with get_safe_file_operations().safe_json_write(file_path, data, indent):
        pass


def safe_json_read(file_path: Union[str, Path]):
    """Convenience function for safe JSON reading"""
    with get_safe_file_operations().safe_json_read(file_path) as data:
        return data


def safe_yaml_write(file_path: Union[str, Path], data: Any):
    """Convenience function for safe YAML writing"""
    with get_safe_file_operations().safe_yaml_write(file_path, data):
        pass


def safe_yaml_read(file_path: Union[str, Path]):
    """Convenience function for safe YAML reading"""
    with get_safe_file_operations().safe_yaml_read(file_path) as data:
        return data


# Example usage
if __name__ == "__main__":
    import os
    import tempfile

    # Test safe file operations
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        test_file = f.name

    try:
        # Test safe write
        safe_write(test_file, "Test content for safe file operations")
        print("Safe write completed")

        # Test safe read
        content = safe_read(test_file)
        print(f"Safe read content: {content}")

        # Test JSON operations
        json_file = test_file.replace(".txt", ".json")
        test_data = {"test": "data", "number": 42}
        safe_json_write(json_file, test_data)
        print("Safe JSON write completed")

        loaded_data = safe_json_read(json_file)
        print(f"Safe JSON read: {loaded_data}")

        # Test file operations
        copy_file = test_file.replace(".txt", "_copy.txt")
        get_safe_file_operations().safe_copy(test_file, copy_file)
        print("Safe copy completed")

        print(f"File is locked: {get_safe_file_operations().is_locked(test_file)}")
        print(f"All locks: {get_safe_file_operations().list_locks()}")

    finally:
        # Clean up
        for f in [test_file, json_file, copy_file]:
            if os.path.exists(f):
                os.unlink(f)
