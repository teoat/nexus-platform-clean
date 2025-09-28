#!/usr/bin/env python3
"""
Base Module Class - NEXUS Platform
Foundation for all modular automation components
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModuleResult:
    """Result from a module execution"""

    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: datetime = None
    module_name: str = ""
    function_name: str = ""
    execution_time: float = 0.0
    audit_record: Dict[str, Any] = None


class BaseModule(ABC):
    """Base class for all automation modules"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.config = self._load_config()
        self.audit_log_path = self.base_path / self.config["global"]["audit_log_path"]
        self.audit_log_path.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load module configuration from policies.yaml"""
        config_path = self.base_path / "config" / "policies.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {}

    async def execute_function(self, function_name: str, **kwargs) -> ModuleResult:
        """Execute a module function with audit logging"""
        start_time = datetime.now()

        try:
            # Check if function exists
            if not hasattr(self, function_name):
                return ModuleResult(
                    success=False,
                    data=None,
                    error=f"Function '{function_name}' not found in module {self.__class__.__name__}",
                    timestamp=start_time,
                    module_name=self.__class__.__name__,
                    function_name=function_name,
                )

            # Execute the function
            method = getattr(self, function_name)
            result = await method(**kwargs)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Create audit record
            audit_record = self._create_audit_record(
                function_name, kwargs, result, execution_time, "success"
            )

            # Log audit record
            await self._log_audit_record(audit_record)

            return ModuleResult(
                success=result.success if hasattr(result, "success") else True,
                data=result.data if hasattr(result, "data") else result,
                error=result.error if hasattr(result, "error") else None,
                timestamp=start_time,
                module_name=self.__class__.__name__,
                function_name=function_name,
                execution_time=execution_time,
                audit_record=audit_record,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)

            # Create audit record for failure
            audit_record = self._create_audit_record(
                function_name, kwargs, None, execution_time, "failure", error_msg
            )

            # Log audit record
            await self._log_audit_record(audit_record)

            return ModuleResult(
                success=False,
                data=None,
                error=error_msg,
                timestamp=start_time,
                module_name=self.__class__.__name__,
                function_name=function_name,
                execution_time=execution_time,
                audit_record=audit_record,
            )

    def _create_audit_record(
        self,
        function_name: str,
        inputs: Dict,
        outputs: Any,
        execution_time: float,
        status: str,
        error: str = None,
    ) -> Dict[str, Any]:
        """Create audit record for module execution"""
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "actor": self.__class__.__name__,
            "action": function_name,
            "inputs": inputs,
            "outputs": outputs.data if hasattr(outputs, "data") else outputs,
            "ssot_state": {
                "manifest": str(
                    self.base_path / self.config["global"]["ssot_manifest_path"]
                ),
                "lock_manifest": str(
                    self.base_path / self.config["global"]["lock_manifest_path"]
                ),
            },
            "status": status,
            "trace_id": f"trace-{uuid.uuid4().hex[:8]}",
            "execution_time": execution_time,
            "error": error,
            "notes": f"Module {self.__class__.__name__} executed {function_name}",
        }

    async def _log_audit_record(self, audit_record: Dict[str, Any]):
        """Log audit record to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            audit_file = self.audit_log_path / f"{timestamp}.jsonl"

            # Clean the audit record for JSON serialization
            clean_record = self._clean_for_json(audit_record)

            with open(audit_file, "a") as f:
                f.write(json.dumps(clean_record, default=str) + "\n")

        except Exception as e:
            logger.error(f"Failed to log audit record: {e}")

    def _clean_for_json(self, obj):
        """Recursively clean object for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._clean_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # Convert dataclass or object to dict
            return self._clean_for_json(obj.__dict__)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)

    @abstractmethod
    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        pass

    @abstractmethod
    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        pass


# Example usage and testing
async def main():
    """Test the base module functionality"""

    class TestModule(BaseModule):
        async def get_available_functions(self) -> List[str]:
            return ["test_function"]

        async def get_module_info(self) -> Dict[str, Any]:
            return {
                "name": "TestModule",
                "version": "1.0",
                "functions": await self.get_available_functions(),
            }

        async def test_function(self, message: str = "Hello") -> ModuleResult:
            return ModuleResult(
                success=True,
                data={"message": message, "timestamp": datetime.now().isoformat()},
                timestamp=datetime.now(),
            )

    # Test the module
    module = TestModule()
    result = await module.execute_function("test_function", message="Test message")
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
