#!/usr/bin/env python3
"""
NEXUS Platform - Role-Based Access Control (RBAC) Service
Implements comprehensive access control with user ID extraction from JWT tokens
"""

import logging
import os
from typing import Any, Dict, List, Optional, Set

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# JWT token scheme
security = HTTPBearer()


class Permission:
    """Permission constants"""
    # User permissions
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Transaction permissions
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_CREATE = "transaction:create"
    TRANSACTION_UPDATE = "transaction:update"
    TRANSACTION_DELETE = "transaction:delete"

    # Account permissions
    ACCOUNT_READ = "account:read"
    ACCOUNT_CREATE = "account:create"
    ACCOUNT_UPDATE = "account:update"
    ACCOUNT_DELETE = "account:delete"

    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"

    # Admin permissions
    ADMIN_USER_MANAGE = "admin:user:manage"
    ADMIN_SYSTEM_CONFIG = "admin:system:config"
    ADMIN_AUDIT_READ = "admin:audit:read"


class Role:
    """Role definitions with associated permissions"""

    USER = {
        "name": "user",
        "permissions": {
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.TRANSACTION_READ,
            Permission.TRANSACTION_CREATE,
            Permission.TRANSACTION_UPDATE,
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_CREATE,
            Permission.ACCOUNT_UPDATE,
            Permission.ANALYTICS_READ,
        }
    }

    PREMIUM_USER = {
        "name": "premium_user",
        "permissions": {
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.TRANSACTION_READ,
            Permission.TRANSACTION_CREATE,
            Permission.TRANSACTION_UPDATE,
            Permission.TRANSACTION_DELETE,
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_CREATE,
            Permission.ACCOUNT_UPDATE,
            Permission.ACCOUNT_DELETE,
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_EXPORT,
        }
    }

    ADMIN = {
        "name": "admin",
        "permissions": {
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.USER_DELETE,
            Permission.TRANSACTION_READ,
            Permission.TRANSACTION_CREATE,
            Permission.TRANSACTION_UPDATE,
            Permission.TRANSACTION_DELETE,
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_CREATE,
            Permission.ACCOUNT_UPDATE,
            Permission.ACCOUNT_DELETE,
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_EXPORT,
            Permission.ADMIN_USER_MANAGE,
            Permission.ADMIN_SYSTEM_CONFIG,
            Permission.ADMIN_AUDIT_READ,
        }
    }


class RBACService:
    """Role-Based Access Control Service"""

    def __init__(self):
        self.roles = {
            "user": Role.USER,
            "premium_user": Role.PREMIUM_USER,
            "admin": Role.ADMIN,
        }

    def _get_current_user_id(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Get current user ID from JWT token in request context"""
        try:
            # Extract token from Authorization header
            token = credentials.credentials

            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Extract user ID from token payload
            user_id = payload.get("sub") or payload.get("user_id")

            if not user_id:
                raise ValueError("Invalid token: no user_id found")

            return str(user_id)

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except Exception as e:
            logger.error(f"Error extracting user ID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to extract user ID from authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user based on their role"""
        # In a real implementation, this would fetch the user's role from the database
        # For now, we'll return default user permissions
        user_role = self.roles.get("user", Role.USER)
        return user_role["permissions"]

    def has_permission(self, user_id: str, required_permission: str) -> bool:
        """Check if a user has a specific permission"""
        user_permissions = self.get_user_permissions(user_id)
        return required_permission in user_permissions

    def has_any_permission(self, user_id: str, required_permissions: List[str]) -> bool:
        """Check if a user has any of the required permissions"""
        user_permissions = self.get_user_permissions(user_id)
        return any(perm in user_permissions for perm in required_permissions)

    def has_all_permissions(self, user_id: str, required_permissions: List[str]) -> bool:
        """Check if a user has all of the required permissions"""
        user_permissions = self.get_user_permissions(user_id)
        return all(perm in user_permissions for perm in required_permissions)

    def require_permission(self, required_permission: str):
        """Dependency function to require a specific permission"""
        async def permission_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
            user_id = self._get_current_user_id(credentials)
            if not self.has_permission(user_id, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permission}"
                )
            return user_id
        return permission_checker

    def require_any_permission(self, required_permissions: List[str]):
        """Dependency function to require any of the specified permissions"""
        async def permission_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
            user_id = self._get_current_user_id(credentials)
            if not self.has_any_permission(user_id, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required any of: {required_permissions}"
                )
            return user_id
        return permission_checker

    def require_all_permissions(self, required_permissions: List[str]):
        """Dependency function to require all of the specified permissions"""
        async def permission_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
            user_id = self._get_current_user_id(credentials)
            if not self.has_all_permissions(user_id, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required all of: {required_permissions}"
                )
            return user_id
        return permission_checker

    def require_admin(self):
        """Dependency function to require admin permissions"""
        return self.require_permission(Permission.ADMIN_USER_MANAGE)

    def require_user_owner(self, resource_user_id: str):
        """Check if the current user owns the resource or has admin permissions"""
        async def ownership_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
            user_id = self._get_current_user_id(credentials)
            if user_id == resource_user_id or self.has_permission(user_id, Permission.ADMIN_USER_MANAGE):
                return user_id
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: resource ownership required"
            )
        return ownership_checker


# Global RBAC service instance
rbac_service = RBACService()


# Dependency functions for use in route handlers
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from JWT token"""
    return rbac_service._get_current_user_id(credentials)


def require_permission(permission: str):
    """Require a specific permission"""
    return rbac_service.require_permission(permission)


def require_admin():
    """Require admin permissions"""
    return rbac_service.require_admin()


def require_user_owner(resource_user_id: str):
    """Require resource ownership or admin permissions"""
    return rbac_service.require_user_owner(resource_user_id)