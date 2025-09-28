# frenly_ai/backend/ssot_operator.py

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

# Assuming AliasManager is available in the backend services
from backend.services.alias_manager import AliasManager


class OperationType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"


class SSOTQuery:
    def __init__(
        self,
        query_id: str,
        query_type: OperationType,
        parameters: Dict[str, Any],
        user: str,
    ):
        self.query_id = query_id
        self.query_type = query_type
        self.parameters = parameters
        self.user = user


class SSOTOperator:
    def __init__(self, alias_manager: AliasManager):
        self.alias_manager = alias_manager
        self.operator_id = "ssot-operator-v1"
        print(f"SSOT Operator initialized with ID: {self.operator_id}")

    async def execute_operation(
        self, operation_type: OperationType, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SSOT operation"""
        if operation_type == OperationType.CREATE:
            return await self.create_alias(data)
        elif operation_type == OperationType.UPDATE:
            return await self.update_alias(data)
        elif operation_type == OperationType.DELETE:
            return await self.delete_alias(data)
        elif operation_type == OperationType.QUERY:
            return await self.query_alias(data)
        else:
            raise ValueError(f"Unsupported operation type: {operation_type}")

    async def create_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create alias"""
        alias_name = data.get("alias_name")
        canonical_name = data.get("canonical_name")
        context = data.get("context", "global")
        expires_at = data.get("expires_at")

        if not alias_name or not canonical_name:
            raise ValueError("alias_name and canonical_name are required")

        return self.alias_manager.create_alias(
            alias_name, canonical_name, context, expires_at
        )

    async def update_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update alias"""
        alias_name = data.get("alias_name")
        new_canonical_name = data.get("new_canonical_name")
        new_context = data.get("new_context")
        new_expires_at = data.get("new_expires_at")

        if not alias_name:
            raise ValueError("alias_name is required")

        return self.alias_manager.update_alias(
            alias_name, new_canonical_name, new_context, new_expires_at
        )

    async def delete_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete alias"""
        alias_name = data.get("alias_name")

        if not alias_name:
            raise ValueError("alias_name is required")

        self.alias_manager.deactivate_alias(alias_name)
        return {"message": f"Alias '{alias_name}' deactivated"}

    async def query_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query alias"""
        alias_name = data.get("alias_name")

        if not alias_name:
            raise ValueError("alias_name is required")

        alias = self.alias_manager.get_alias(alias_name)
        if not alias:
            raise ValueError(f"Alias '{alias_name}' not found")

        return alias

    async def process_query(self, query: SSOTQuery) -> Dict[str, Any]:
        """Process SSOT query"""
        try:
            result = await self.execute_operation(query.query_type, query.parameters)
            return {
                "success": True,
                "message": "Success",
                "data": result,
                "query_id": query.query_id,
            }
        except Exception as e:
            return {"success": False, "message": str(e), "query_id": query.query_id}


class FrenlyAISSOTOperator:
    def __init__(self, alias_manager: AliasManager):
        self.alias_manager = alias_manager
        self.operator_id = "frenly-ai-ssot-operator-v1"
        print(f"Frenly AI SSOT Operator initialized with ID: {self.operator_id}")

    async def validate_alias_request(
        self, alias_name: str, canonical_name: str, context: str
    ) -> bool:
        """Validates an alias creation/update request based on SSOT rules."""
        print(
            f"Validating alias request: {alias_name} -> {canonical_name} in context {context}"
        )
        # Implement more sophisticated validation logic here
        # For now, basic checks:
        if not alias_name or not canonical_name or not context:
            print("Validation failed: Missing alias_name, canonical_name, or context.")
            return False

        # Check for existing alias with different canonical name (immutability rule)
        existing_alias = self.alias_manager.get_alias(alias_name)
        if existing_alias and existing_alias["canonical_name"] != canonical_name:
            print(
                f"Validation failed: Alias '{alias_name}' already exists with a different canonical name."
            )
            return False

        print("Validation successful.")
        return True

    async def create_ssot_alias(
        self,
        alias_name: str,
        canonical_name: str,
        context: str,
        expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Creates a new SSOT alias via the AliasManager."""
        if not await self.validate_alias_request(alias_name, canonical_name, context):
            raise ValueError("Alias creation failed validation.")

        print(
            f"Creating SSOT alias: {alias_name} -> {canonical_name} in context {context}"
        )
        try:
            alias_data = self.alias_manager.create_alias(
                alias_name, canonical_name, context, expires_at
            )
            print(f"SSOT Alias created: {alias_data}")
            return alias_data
        except ValueError as e:
            print(f"Error creating alias: {e}")
            raise

    async def update_ssot_alias(
        self,
        alias_name: str,
        new_canonical_name: Optional[str] = None,
        new_context: Optional[str] = None,
        new_expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Updates an existing SSOT alias via the AliasManager."""
        # For updates, we might have different validation rules or allow canonical name changes under strict conditions
        # For simplicity, re-validate with current canonical name if not changing it
        current_alias = self.alias_manager.get_alias(alias_name)
        if not current_alias:
            raise ValueError(f"Alias '{alias_name}' not found for update.")

        canonical_to_validate = (
            new_canonical_name
            if new_canonical_name
            else current_alias["canonical_name"]
        )
        context_to_validate = new_context if new_context else current_alias["context"]

        if not await self.validate_alias_request(
            alias_name, canonical_to_validate, context_to_validate
        ):
            raise ValueError("Alias update failed validation.")

        print(f"Updating SSOT alias: {alias_name}")
        try:
            alias_data = self.alias_manager.update_alias(
                alias_name, new_canonical_name, new_context, new_expires_at
            )
            print(f"SSOT Alias updated: {alias_data}")
            return alias_data
        except ValueError as e:
            print(f"Error updating alias: {e}")
            raise

    async def get_ssot_alias(self, alias_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves an SSOT alias from the AliasManager."""
        print(f"Retrieving SSOT alias: {alias_name}")
        return self.alias_manager.get_alias(alias_name)

    async def deactivate_ssot_alias(self, alias_name: str) -> None:
        """Deactivates an SSOT alias via the AliasManager."""
        print(f"Deactivating SSOT alias: {alias_name}")
        try:
            self.alias_manager.deactivate_alias(alias_name)
            print(f"SSOT Alias '{alias_name}' deactivated.")
        except ValueError as e:
            print(f"Error deactivating alias: {e}")
            raise


# Example Usage (for testing purposes)
if __name__ == "__main__":

    async def main():
        # Create a dummy AliasManager for testing
        class MockAliasManager:
            def __init__(self):
                self.aliases = {}
                self.history = {}

            def create_alias(
                self,
                alias_name: str,
                canonical_name: str,
                context: str = "global",
                expires_at: Optional[datetime] = None,
            ):
                if alias_name in self.aliases:
                    raise ValueError("Alias already exists")
                self.aliases[alias_name] = {
                    "canonical_name": canonical_name,
                    "context": context,
                    "created_at": datetime.utcnow(),
                    "expires_at": expires_at,
                    "status": "active",
                }
                return self.aliases[alias_name]

            def get_alias(self, alias_name: str):
                return self.aliases.get(alias_name)

            def update_alias(
                self,
                alias_name: str,
                new_canonical_name: Optional[str] = None,
                new_context: Optional[str] = None,
                new_expires_at: Optional[datetime] = None,
            ):
                if alias_name not in self.aliases:
                    raise ValueError("Alias not found")
                if new_canonical_name:
                    self.aliases[alias_name]["canonical_name"] = new_canonical_name
                if new_context:
                    self.aliases[alias_name]["context"] = new_context
                if new_expires_at:
                    self.aliases[alias_name]["expires_at"] = new_expires_at
                self.aliases[alias_name]["updated_at"] = datetime.utcnow()
                return self.aliases[alias_name]

            def deactivate_alias(self, alias_name: str):
                if alias_name not in self.aliases:
                    raise ValueError("Alias not found")
                self.aliases[alias_name]["status"] = "inactive"
                self.aliases[alias_name]["deactivated_at"] = datetime.utcnow()

        mock_alias_manager = MockAliasManager()
        operator = FrenlyAISSOTOperator(mock_alias_manager)

        # Test alias creation
        try:
            await operator.create_ssot_alias(
                "test_service", "http://test.com", "backend"
            )
            await operator.create_ssot_alias(
                "another_service",
                "http://another.com",
                "frontend",
                expires_at=datetime.utcnow() + timedelta(days=1),
            )
        except ValueError as e:
            print(f"Test Error: {e}")

        # Test alias retrieval
        alias = await operator.get_ssot_alias("test_service")
        print(f"Retrieved alias: {alias}")

        # Test alias update
        try:
            await operator.update_ssot_alias(
                "test_service", new_canonical_name="http://newtest.com"
            )
        except ValueError as e:
            print(f"Test Error: {e}")
        alias = await operator.get_ssot_alias("test_service")
        print(f"Updated alias: {alias}")

        # Test alias deactivation
        try:
            await operator.deactivate_ssot_alias("another_service")
        except ValueError as e:
            print(f"Test Error: {e}")
        alias = await operator.get_ssot_alias("another_service")
        print(f"Deactivated alias: {alias}")

    asyncio.run(main())
