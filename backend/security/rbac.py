"""
Role-Based Access Control (RBAC) System for NEXUS Platform
Advanced RBAC with role hierarchies, granular permissions, and resource-based access control
"""

import logging
import contextvars
from typing import Dict, List, Set, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class Permission(str, Enum):
    """System permissions enumeration"""
    # User Management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Transaction Management
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_WRITE = "transaction:write"
    TRANSACTION_DELETE = "transaction:delete"
    TRANSACTION_APPROVE = "transaction:approve"

    # Report Management
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    REPORT_DELETE = "report:delete"
    REPORT_EXPORT = "report:export"

    # System Management
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_DELETE = "system:delete"
    SYSTEM_CONFIG = "system:config"

    # Audit & Compliance
    AUDIT_READ = "audit:read"
    AUDIT_WRITE = "audit:write"
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_WRITE = "compliance:write"

    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_WRITE = "analytics:write"

    # API Access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"

class Role(str, Enum):
    """System roles enumeration"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCIAL_ANALYST = "financial_analyst"
    AUDITOR = "auditor"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"
    GUEST = "guest"

@dataclass
class RoleDefinition:
    """Role definition with permissions and metadata"""
    name: str
    permissions: Set[Permission]
    description: str
    level: int  # Hierarchy level (higher = more permissions)
    inherits_from: Optional[List[str]] = None  # Roles this role inherits from

@dataclass
class ResourcePermission:
    """Resource-specific permission"""
    resource_type: str
    resource_id: Optional[str]
    permissions: Set[str]
    conditions: Optional[Dict[str, Any]] = None

# Context variable for current user ID
user_id_context: contextvars.ContextVar[str] = contextvars.ContextVar('user_id')

class RBACService:
    """Advanced Role-Based Access Control Service"""

    def __init__(self):
        self.roles: Dict[str, RoleDefinition] = {}
        self.role_hierarchy: Dict[str, Set[str]] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.user_permissions: Dict[str, Set[Permission]] = {}
        self.resource_permissions: Dict[str, List[ResourcePermission]] = {}

        self._initialize_roles()
        self._build_hierarchy()

    def _initialize_roles(self):
        """Initialize system roles with permissions"""
        self.roles = {
            Role.SUPER_ADMIN: RoleDefinition(
                name="Super Administrator",
                permissions=set(Permission),
                description="Full system access",
                level=100,
                inherits_from=[]
            ),
            Role.ADMIN: RoleDefinition(
                name="Administrator",
                permissions={
                    Permission.USER_READ, Permission.USER_WRITE, Permission.USER_MANAGE,
                    Permission.TRANSACTION_READ, Permission.TRANSACTION_WRITE, Permission.TRANSACTION_DELETE,
                    Permission.REPORT_READ, Permission.REPORT_WRITE, Permission.REPORT_DELETE,
                    Permission.SYSTEM_READ, Permission.SYSTEM_WRITE, Permission.SYSTEM_CONFIG,
                    Permission.AUDIT_READ, Permission.AUDIT_WRITE,
                    Permission.API_READ, Permission.API_WRITE, Permission.API_ADMIN
                },
                description="Administrative access to most system functions",
                level=80,
                inherits_from=[]
            ),
            Role.COMPLIANCE_OFFICER: RoleDefinition(
                name="Compliance Officer",
                permissions={
                    Permission.USER_READ,
                    Permission.TRANSACTION_READ, Permission.TRANSACTION_WRITE,
                    Permission.REPORT_READ, Permission.REPORT_WRITE,
                    Permission.COMPLIANCE_READ, Permission.COMPLIANCE_WRITE,
                    Permission.AUDIT_READ,
                    Permission.API_READ
                },
                description="Compliance and regulatory oversight",
                level=70,
                inherits_from=[]
            ),
            Role.FINANCIAL_ANALYST: RoleDefinition(
                name="Financial Analyst",
                permissions={
                    Permission.TRANSACTION_READ, Permission.TRANSACTION_WRITE,
                    Permission.REPORT_READ, Permission.REPORT_WRITE, Permission.REPORT_EXPORT,
                    Permission.ANALYTICS_READ, Permission.ANALYTICS_WRITE,
                    Permission.API_READ
                },
                description="Financial analysis and reporting",
                level=60,
                inherits_from=[]
            ),
            Role.AUDITOR: RoleDefinition(
                name="Auditor",
                permissions={
                    Permission.TRANSACTION_READ,
                    Permission.REPORT_READ,
                    Permission.AUDIT_READ,
                    Permission.COMPLIANCE_READ,
                    Permission.API_READ
                },
                description="Audit and review access",
                level=50,
                inherits_from=[]
            ),
            Role.MANAGER: RoleDefinition(
                name="Manager",
                permissions={
                    Permission.USER_READ, Permission.USER_WRITE,
                    Permission.TRANSACTION_READ, Permission.TRANSACTION_WRITE,
                    Permission.REPORT_READ, Permission.REPORT_WRITE,
                    Permission.ANALYTICS_READ,
                    Permission.API_READ, Permission.API_WRITE
                },
                description="Management level access",
                level=40,
                inherits_from=[]
            ),
            Role.USER: RoleDefinition(
                name="User",
                permissions={
                    Permission.TRANSACTION_READ, Permission.TRANSACTION_WRITE,
                    Permission.REPORT_READ,
                    Permission.API_READ
                },
                description="Standard user access",
                level=30,
                inherits_from=[]
            ),
            Role.VIEWER: RoleDefinition(
                name="Viewer",
                permissions={
                    Permission.TRANSACTION_READ,
                    Permission.REPORT_READ,
                    Permission.API_READ
                },
                description="Read-only access",
                level=20,
                inherits_from=[]
            ),
            Role.GUEST: RoleDefinition(
                name="Guest",
                permissions={
                    Permission.API_READ
                },
                description="Limited guest access",
                level=10,
                inherits_from=[]
            )
        }

    def _build_hierarchy(self):
        """Build role hierarchy cache"""
        for role_name, role_def in self.roles.items():
            self.role_hierarchy[role_name] = self._get_inherited_permissions(role_name)

    def _get_inherited_permissions(self, role_name: str) -> Set[Permission]:
        """Get all permissions for a role including inherited ones"""
        if role_name not in self.roles:
            return set()

        role_def = self.roles[role_name]
        permissions = role_def.permissions.copy()

        # Add permissions from inherited roles
        if role_def.inherits_from:
            for inherited_role in role_def.inherits_from:
                if inherited_role in self.roles:
                    permissions.update(self._get_inherited_permissions(inherited_role))

        return permissions

    def assign_role_to_user(self, user_id: str, role: Union[str, Role]):
        """Assign a role to a user"""
        role_str = role.value if isinstance(role, Role) else role

        if role_str not in self.roles:
            raise ValueError(f"Role '{role_str}' does not exist")

        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()

        self.user_roles[user_id].add(role_str)
        self._update_user_permissions(user_id)

        logger.info(f"Assigned role '{role_str}' to user '{user_id}'")

    def remove_role_from_user(self, user_id: str, role: Union[str, Role]):
        """Remove a role from a user"""
        role_str = role.value if isinstance(role, Role) else role

        if user_id in self.user_roles and role_str in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_str)
            self._update_user_permissions(user_id)
            logger.info(f"Removed role '{role_str}' from user '{user_id}'")

    def _update_user_permissions(self, user_id: str):
        """Update cached permissions for a user"""
        if user_id not in self.user_roles:
            self.user_permissions[user_id] = set()
            return

        all_permissions = set()
        for role_name in self.user_roles[user_id]:
            all_permissions.update(self.role_hierarchy.get(role_name, set()))

        self.user_permissions[user_id] = all_permissions

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get all roles assigned to a user"""
        return self.user_roles.get(user_id, set()).copy()

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        return self.user_permissions.get(user_id, set()).copy()

    def has_permission(self, user_id: str, permission: Union[str, Permission]) -> bool:
        """Check if user has a specific permission"""
        perm_str = permission.value if isinstance(permission, Permission) else permission
        user_perms = self.get_user_permissions(user_id)

        # Check exact permission match
        if Permission(perm_str) in user_perms:
            return True

        # Check wildcard permissions (e.g., "user:*" covers "user:read", "user:write", etc.)
        perm_parts = perm_str.split(':')
        if len(perm_parts) == 2:
            wildcard_perm = f"{perm_parts[0]}:*"
            if Permission(wildcard_perm) in user_perms:
                return True

        return False

    def has_any_permission(self, user_id: str, permissions: List[Union[str, Permission]]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(user_id, perm) for perm in permissions)

    def has_all_permissions(self, user_id: str, permissions: List[Union[str, Permission]]) -> bool:
        """Check if user has all of the specified permissions"""
        return all(self.has_permission(user_id, perm) for perm in permissions)

    def has_role(self, user_id: str, role: Union[str, Role]) -> bool:
        """Check if user has a specific role"""
        role_str = role.value if isinstance(role, Role) else role
        return role_str in self.get_user_roles(user_id)

    def has_any_role(self, user_id: str, roles: List[Union[str, Role]]) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = self.get_user_roles(user_id)
        return any(
            role.value if isinstance(role, Role) else role in user_roles
            for role in roles
        )

    def can_access_resource(self, user_id: str, resource_type: str,
                          resource_id: Optional[str] = None,
                          action: str = "read") -> bool:
        """Check if user can access a specific resource"""
        # Check general permissions first
        permission = f"{resource_type}:{action}"
        if self.has_permission(user_id, permission):
            return True

        # Check resource-specific permissions
        if user_id in self.resource_permissions:
            for resource_perm in self.resource_permissions[user_id]:
                if resource_perm.resource_type == resource_type:
                    if resource_id is None or resource_perm.resource_id == resource_id:
                        if action in resource_perm.permissions:
                            # Check conditions if any
                            if resource_perm.conditions:
                                if self._evaluate_conditions(user_id, resource_perm.conditions):
                                    return True
                            else:
                                return True

        return False

    def grant_resource_permission(self, user_id: str, resource_type: str,
                                resource_id: Optional[str], permissions: List[str],
                                conditions: Optional[Dict[str, Any]] = None):
        """Grant resource-specific permissions to a user"""
        if user_id not in self.resource_permissions:
            self.resource_permissions[user_id] = []

        resource_perm = ResourcePermission(
            resource_type=resource_type,
            resource_id=resource_id,
            permissions=set(permissions),
            conditions=conditions
        )

        self.resource_permissions[user_id].append(resource_perm)
        logger.info(f"Granted resource permissions to user '{user_id}': {resource_type}:{resource_id}")

    def revoke_resource_permission(self, user_id: str, resource_type: str,
                                  resource_id: Optional[str] = None):
        """Revoke resource-specific permissions from a user"""
        if user_id in self.resource_permissions:
            self.resource_permissions[user_id] = [
                rp for rp in self.resource_permissions[user_id]
                if not (rp.resource_type == resource_type and
                       (resource_id is None or rp.resource_id == resource_id))
            ]
            logger.info(f"Revoked resource permissions from user '{user_id}': {resource_type}:{resource_id}")

    def _evaluate_conditions(self, user_id: str, conditions: Dict[str, Any]) -> bool:
        """Evaluate conditional permissions"""
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated condition evaluation
        for key, value in conditions.items():
            if key == "department" and hasattr(self, '_get_user_department'):
                if self._get_user_department(user_id) != value:
                    return False
            elif key == "clearance_level" and hasattr(self, '_get_user_clearance'):
                if self._get_user_clearance(user_id) < value:
                    return False
            # Add more condition types as needed

        return True

    def get_role_level(self, role: Union[str, Role]) -> int:
        """Get the hierarchy level of a role"""
        role_str = role.value if isinstance(role, Role) else role
        if role_str in self.roles:
            return self.roles[role_str].level
        return 0

    def is_role_higher(self, role1: Union[str, Role], role2: Union[str, Role]) -> bool:
        """Check if role1 has higher or equal hierarchy level than role2"""
        return self.get_role_level(role1) >= self.get_role_level(role2)

    def require_permission(self, permission: Union[str, Permission]):
        """Decorator to require specific permission"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract user_id from request context (implementation depends on your framework)
                user_id = self._get_current_user_id()
                if not self.has_permission(user_id, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {permission}"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def require_role(self, role: Union[str, Role]):
        """Decorator to require specific role"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                user_id = self._get_current_user_id()
                if not self.has_role(user_id, role):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient role. Required: {role}"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def require_resource_access(self, resource_type: str, action: str = "read"):
        """Decorator to require resource access"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                user_id = self._get_current_user_id()
                resource_id = kwargs.get('resource_id')  # Assuming resource_id is passed as kwarg
                if not self.can_access_resource(user_id, resource_type, resource_id, action):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied to resource: {resource_type}"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def _get_current_user_id(self) -> str:
        """Get current user ID from request context"""
        try:
            return user_id_context.get()
        except LookupError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

    def set_current_user_id(self, user_id: str):
        """Set the current user ID in context (for use in request lifecycle)"""
        user_id_context.set(user_id)

# Global RBAC service instance
rbac_service = RBACService()

# Export functions and classes
__all__ = [
    "Permission",
    "Role",
    "RoleDefinition",
    "ResourcePermission",
    "RBACService",
    "rbac_service"
]