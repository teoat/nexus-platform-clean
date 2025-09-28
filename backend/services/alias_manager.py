# backend/services/alias_manager.py

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class AliasManager:
    def __init__(self):
        self.aliases: Dict[str, Dict[str, Any]] = {} # Stores active aliases
        self.history: Dict[str, list] = {} # Stores history of alias changes

    def _validate_alias(self, alias_name: str, canonical_name: str, is_new: bool = True):
        if is_new and alias_name in self.aliases:
            raise ValueError(f"Alias '{alias_name}' already exists.")
        
        # Rule: Canonical names should be immutable once set for an alias
        if not is_new and alias_name in self.aliases:
            existing_alias = self.aliases[alias_name]
            if existing_alias["canonical_name"] != canonical_name:
                raise ValueError(f"Canonical name for alias '{alias_name}' cannot be changed.")

        # Rule: Alias names must be unique (already handled by dictionary key)
        # Rule: Canonical names cannot be empty
        if not canonical_name:
            raise ValueError("Canonical name cannot be empty.")

    def create_alias(self, alias_name: str, canonical_name: str, context: str = "global",
                     expires_at: Optional[datetime] = None) -> Dict[str, Any]:
        self._validate_alias(alias_name, canonical_name, is_new=True)

        alias_data = {
            "canonical_name": canonical_name,
            "context": context,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "status": "active"
        }
        self.aliases[alias_name] = alias_data
        self._log_history(alias_name, "created", alias_data)
        return alias_data

    def get_alias(self, alias_name: str) -> Optional[Dict[str, Any]]:
        alias = self.aliases.get(alias_name)
        if alias and alias.get("expires_at") and alias["expires_at"] < datetime.utcnow():
            self._deactivate_alias(alias_name, "expired")
            return None
        return alias

    def resolve_alias(self, alias_name: str, context: str = "global") -> Optional[str]:
        alias_data = self.get_alias(alias_name)
        if not alias_data:
            return None
        
        # Simple context matching: global aliases are always resolved,
        # otherwise context must match exactly.
        if alias_data["context"] == "global" or alias_data["context"] == context:
            return alias_data["canonical_name"]
        return None

    def update_alias(self, alias_name: str, new_canonical_name: Optional[str] = None,
                     new_context: Optional[str] = None, new_expires_at: Optional[datetime] = None) -> Dict[str, Any]:
        if alias_name not in self.aliases:
            raise ValueError(f"Alias '{alias_name}' does not exist.")

        old_data = self.aliases[alias_name].copy()
        
        # Validate potential changes before applying
        if new_canonical_name:
            self._validate_alias(alias_name, new_canonical_name, is_new=False)
            self.aliases[alias_name]["canonical_name"] = new_canonical_name
        if new_context:
            self.aliases[alias_name]["context"] = new_context
        if new_expires_at:
            self.aliases[alias_name]["expires_at"] = new_expires_at
        
        self.aliases[alias_name]["updated_at"] = datetime.utcnow()
        self._log_history(alias_name, "updated", self.aliases[alias_name], old_data)
        return self.aliases[alias_name]

    def deactivate_alias(self, alias_name: str) -> None:
        if alias_name not in self.aliases:
            raise ValueError(f"Alias '{alias_name}' does not exist.")
        self._deactivate_alias(alias_name, "deactivated_by_user")

    def _deactivate_alias(self, alias_name: str, reason: str) -> None:
        old_data = self.aliases[alias_name].copy()
        self.aliases[alias_name]["status"] = "inactive"
        self.aliases[alias_name]["deactivated_at"] = datetime.utcnow()
        self.aliases[alias_name]["deactivation_reason"] = reason
        self._log_history(alias_name, "deactivated", self.aliases[alias_name], old_data)

    def get_alias_history(self, alias_name: str) -> list:
        return self.history.get(alias_name, [])

    def _log_history(self, alias_name: str, action: str, new_data: Dict[str, Any], old_data: Optional[Dict[str, Any]] = None):
        if alias_name not in self.history:
            self.history[alias_name] = []
        self.history[alias_name].append({
            "timestamp": datetime.utcnow(),
            "action": action,
            "new_data": new_data,
            "old_data": old_data
        })

# Example Usage (for testing purposes)
if __name__ == "__main__":
    manager = AliasManager()

    # Create an alias
    try:
        alias1 = manager.create_alias("user_service_v1", "http://localhost:8001/api/v1/users", context="backend")
        print(f"Created alias: {alias1}")
    except ValueError as e:
        print(e)

    # Get an alias
    retrieved_alias = manager.get_alias("user_service_v1")
    print(f"Retrieved alias: {retrieved_alias}")

    # Update an alias
    try:
        updated_alias = manager.update_alias("user_service_v1", new_canonical_name="http://localhost:8002/api/v2/users")
        print(f"Updated alias: {updated_alias}")
    except ValueError as e:
        print(e)

    # Create a temporary alias
    expires_in_5_seconds = datetime.utcnow() + timedelta(seconds=5)
    try:
        temp_alias = manager.create_alias("temp_feature_toggle", "true", expires_at=expires_in_5_seconds)
        print(f"Created temporary alias: {temp_alias}")
    except ValueError as e:
        print(e)

    # Check temporary alias before expiration
    import time
    time.sleep(2)
    print(f"Temporary alias after 2 seconds: {manager.get_alias('temp_feature_toggle')}")

    # Check temporary alias after expiration
    time.sleep(4) # Total 6 seconds sleep
    print(f"Temporary alias after 6 seconds (should be None): {manager.get_alias('temp_feature_toggle')}")

    # Deactivate an alias
    try:
        manager.deactivate_alias("user_service_v1")
        print(f"Deactivated alias: {manager.get_alias('user_service_v1')}")
    except ValueError as e:
        print(e)

    # Get alias history
    print("History for user_service_v1:")
    for entry in manager.get_alias_history("user_service_v1"):
        print(entry)