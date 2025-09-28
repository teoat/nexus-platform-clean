# Manager Pattern Implementation Guide

**Last Updated**: 2025-01-15 23:35:00  
**Version**: 1.0.0  
**Status**: ✅ **ACTIVE SSOT**

## 🎯 **Purpose**

This guide shows how to implement the Manager pattern using NEXUS Platform coding standards, with examples based on your existing codebase.

## 📋 **Base Manager Template**

```python
#!/usr/bin/env python3
"""
Example Manager Implementation for NEXUS Platform
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import NEXUS standards
from NEXUS_app.core.standards import (
    BaseConfig,
    ErrorHandler,
    LoggingUtils,
    ValidationUtils,
    WorkspacePath,
    ProcessingResult
)

class ExampleManagerConfig(BaseConfig):
    """Configuration for ExampleManager"""

    def __init__(
        self,
        workspace_path: WorkspacePath,
        service_name: str,
        port: int = 8080,
        timeout: int = 30,
        max_retries: int = 3,
        enabled: bool = True
    ):
        self.workspace_path = ValidationUtils.validate_workspace_path(workspace_path)
        self.service_name = ValidationUtils.validate_string(service_name, "service_name")
        self.port = ValidationUtils.validate_integer(port, "port", min_value=1, max_value=65535)
        self.timeout = ValidationUtils.validate_integer(timeout, "timeout", min_value=1)
        self.max_retries = ValidationUtils.validate_integer(max_retries, "max_retries", min_value=0)
        self.enabled = ValidationUtils.validate_boolean(enabled, "enabled")
        super().__init__()

class ExampleManager:
    """Example Manager following NEXUS Platform standards"""

    def __init__(self, workspace_path: WorkspacePath, config: Optional[ExampleManagerConfig] = None):
        # Validate workspace path
        self.workspace_path = ValidationUtils.validate_workspace_path(workspace_path)

        # Setup logging
        self.logger = LoggingUtils.setup_tools/utilities/tools/utilities/nexus_logger(workspace_path, f"example_manager")

        # Load or create configuration
        if config is None:
            config = ExampleManagerConfig(workspace_path, "example_service")
        self.config = config

        # Initialize state
        self.status = "initialized"
        self.last_activity = None

        self.logger.info(f"ExampleManager initialized for {self.workspace_path}")

    @ErrorHandler.error_handler("ExampleManager.start")
    def start(self) -> bool:
        """Start the manager service"""
        try:
            self.logger.info("Starting ExampleManager...")

            # Validate configuration
            if not self.config.enabled:
                self.logger.warning("Manager is disabled in configuration")
                return False

            # Start service logic here
            self.status = "running"
            self.last_activity = datetime.now()

            self.logger.info("ExampleManager started successfully")
            return True

        except Exception as e:
            self.logger.error_with_context(e, "Failed to start ExampleManager")
            self.status = "error"
            return False

    @ErrorHandler.safe_method(default_return=False)
    def stop(self) -> bool:
        """Stop the manager service"""
        try:
            self.logger.info("Stopping ExampleManager...")

            # Stop service logic here
            self.status = "stopped"
            self.last_activity = datetime.now()

            self.logger.info("ExampleManager stopped successfully")
            return True

        except Exception as e:
            self.logger.error_with_context(e, "Failed to stop ExampleManager")
            return False

    def process_task(self, task: Dict[str, Any]) -> ProcessingResult:
        """Process a task with proper error handling"""
        result = ProcessingResult(
            success=False,
            output=[],
            timestamp=datetime.now()
        )

        try:
            # Validate input
            ValidationUtils.validate_dict(task, "task", required_keys=["name", "type"])

            task_name = task.get("name", "unknown")
            self.logger.info(f"Processing task: {task_name}")

            # Process task logic here
            result.output.append(f"Task {task_name} processed successfully")
            result.success = True
            result.tasks_processed = 1
            result.tasks_completed = 1

            self.logger.info(f"Task {task_name} completed successfully")

        except ValidationError as e:
            result.error = f"Validation error: {e}"
            result.tasks_failed = 1
            self.logger.error(f"Task validation failed: {e}")

        except Exception as e:
            result.error = f"Processing error: {e}"
            result.tasks_failed = 1
            self.logger.error_with_context(e, f"Task processing failed: {task.get('name', 'unknown')}")

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        return {
            "status": self.status,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "config": self.config.to_dict(),
            "workspace_path": str(self.workspace_path)
        }
```

## 🔧 **Applying to Existing Code**

### **Step 1: Identify Current Manager**

Look at your existing managers like `DockerManager`, `AgentManager`, etc.

### **Step 2: Create Configuration Class**

```python
class DockerManagerConfig(BaseConfig):
    def __init__(self, workspace_path: WorkspacePath, **kwargs):
        self.workspace_path = ValidationUtils.validate_workspace_path(workspace_path)
        # Add other config fields with validation
        super().__init__()
```

### **Step 3: Add Error Handling**

```python
@ErrorHandler.error_handler("DockerManager.start_service")
def start_service(self, service_name: str) -> bool:
    # Your existing logic with proper error handling
    pass
```

### **Step 4: Add Logging**

```python
def __init__(self, workspace_path: WorkspacePath):
    self.workspace_path = ValidationUtils.validate_workspace_path(workspace_path)
    self.logger = LoggingUtils.setup_tools/utilities/tools/utilities/nexus_logger(workspace_path, "docker_manager")
    # Rest of your initialization
```

## 🚀 **Migration Strategy**

### **Phase 1: Low Risk (Immediate)**

1. Add type hints to existing methods
2. Add basic error handling with try-catch
3. Add structured logging
4. Create configuration classes

### **Phase 2: Medium Risk (Next)**

1. Refactor `__init__` methods to use validation
2. Add input validation to public methods
3. Implement proper error handling patterns
4. Add performance logging

### **Phase 3: High Risk (Later)**

1. Full refactor to use base classes
2. Implement comprehensive testing
3. Add monitoring and metrics
4. Optimize performance

## 📊 **Benefits**

- **Consistency**: All managers follow the same patterns
- **Safety**: Proper error handling and validation
- **Maintainability**: Clear structure and documentation
- **Debugging**: Structured logging and error context
- **Testing**: Easier to test with clear interfaces

## 🔍 **Example: Enhancing continuous_todo_automation.py**

```python
# Before (existing code)
def __init__(self, workspace_path: str):
    self.workspace_path = Path(workspace_path)
    # ... rest of initialization

# After (enhanced with standards)
def __init__(self, workspace_path: WorkspacePath):
    self.workspace_path = ValidationUtils.validate_workspace_path(workspace_path)
    self.logger = LoggingUtils.setup_tools/utilities/tools/utilities/nexus_logger(workspace_path, "continuous_automation")
    # ... rest of initialization with proper validation
```

This approach allows you to gradually improve your codebase while maintaining functionality and reducing risk.
