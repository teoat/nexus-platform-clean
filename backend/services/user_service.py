#!/usr/bin/env python3
"""
NEXUS Platform - User Service
Business logic for user management
"""

import logging
import os
import sys
from datetime import datetime, timezone
from typing import List, Optional

from schemas.user import (UserCreate, UserPreferencesUpdate, UserProfileUpdate,
                          UserSettingsUpdate, UserUpdate)
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (User, UserPreferences, UserProfile,
                                      UserRole, UserSettings)

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations"""

    def __init__(self):
        # Initialize audit logging
        self.audit_engine = AuditLogQueryEngine()

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """Get users with filtering and pagination"""
        try:
            query = db.query(User)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.full_name.ilike(search_term),
                    )
                )

            if role:
                query = query.filter(User.role == role)

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            raise

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise

    def create_user(
        self, db: Session, user_data: UserCreate, hashed_password: str
    ) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_email(db, user_data.email):
                raise ValueError("User with this email already exists")

            if self.get_user_by_username(db, user_data.username):
                raise ValueError("User with this username already exists")

            # Create user
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True,
                role=UserRole.USER,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            # Create default profile, settings, and preferences
            self._create_default_user_data(db, user.id)

            # Audit log user creation
            try:
                await self.audit_engine.log_operation(
                    operation=OperationType.CREATE.value,
                    entity_type="User",
                    entity_id=str(user.id),
                    details={
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role.value,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "user_data": user_data.dict(),
                    },
                    performed_by="system",  # Could be the registering user if available
                    context="user_management",
                    log_level=AuditLogLevel.INFO,
                )
            except Exception as audit_e:
                logger.error(f"Failed to audit log user creation: {audit_e}")

            return user
        except Exception as e:
            # Audit log failed user creation
            try:
                await self.audit_engine.log_operation(
                    operation=OperationType.CREATE.value,
                    entity_type="User",
                    entity_id=user_data.email,
                    details={
                        "creation_result": "failed",
                        "error": str(e),
                        "username": user_data.username,
                        "email": user_data.email,
                        "full_name": user_data.full_name,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    performed_by="system",
                    context="user_management",
                    log_level=AuditLogLevel.ERROR,
                )
            except Exception as audit_e:
                logger.error(f"Failed to audit log failed user creation: {audit_e}")

            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")

            # Check for email conflicts
            if user_data.email and user_data.email != user.email:
                existing_user = self.get_user_by_email(db, user_data.email)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("User with this email already exists")

            # Check for username conflicts
            if user_data.username and user_data.username != user.username:
                existing_user = self.get_user_by_username(db, user_data.username)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("User with this username already exists")

            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            db.commit()
            db.refresh(user)

            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")

            user.is_active = False
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    def activate_user(self, db: Session, user_id: int) -> bool:
        """Activate user"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")

            user.is_active = True
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error activating user {user_id}: {e}")
            raise

    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate user"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")

            user.is_active = False
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise

    def get_user_profile(self, db: Session, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            raise

    def update_user_profile(
        self, db: Session, user_id: int, profile_data: UserProfileUpdate
    ) -> UserProfile:
        """Update user profile"""
        try:
            profile = self.get_user_profile(db, user_id)
            if not profile:
                # Create new profile
                profile = UserProfile(user_id=user_id)
                db.add(profile)

            # Update fields
            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(profile, field, value)

            db.commit()
            db.refresh(profile)

            return profile
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user profile {user_id}: {e}")
            raise

    def get_user_settings(self, db: Session, user_id: int) -> Optional[UserSettings]:
        """Get user settings"""
        try:
            return (
                db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            )
        except Exception as e:
            logger.error(f"Error getting user settings {user_id}: {e}")
            raise

    def update_user_settings(
        self, db: Session, user_id: int, settings_data: UserSettingsUpdate
    ) -> UserSettings:
        """Update user settings"""
        try:
            settings = self.get_user_settings(db, user_id)
            if not settings:
                # Create new settings
                settings = UserSettings(user_id=user_id)
                db.add(settings)

            # Update fields
            update_data = settings_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(settings, field, value)

            db.commit()
            db.refresh(settings)

            return settings
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user settings {user_id}: {e}")
            raise

    def get_user_preferences(
        self, db: Session, user_id: int
    ) -> Optional[UserPreferences]:
        """Get user preferences"""
        try:
            return (
                db.query(UserPreferences)
                .filter(UserPreferences.user_id == user_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting user preferences {user_id}: {e}")
            raise

    def update_user_preferences(
        self, db: Session, user_id: int, preferences_data: UserPreferencesUpdate
    ) -> UserPreferences:
        """Update user preferences"""
        try:
            preferences = self.get_user_preferences(db, user_id)
            if not preferences:
                # Create new preferences
                preferences = UserPreferences(user_id=user_id)
                db.add(preferences)

            # Update fields
            update_data = preferences_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(preferences, field, value)

            db.commit()
            db.refresh(preferences)

            return preferences
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user preferences {user_id}: {e}")
            raise

    def _create_default_user_data(self, db: Session, user_id: int):
        """Create default profile, settings, and preferences for new user"""
        try:
            # Create default profile
            profile = UserProfile(user_id=user_id)
            db.add(profile)

            # Create default settings
            settings = UserSettings(user_id=user_id)
            db.add(settings)

            # Create default preferences
            preferences = UserPreferences(user_id=user_id)
            db.add(preferences)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default user data for {user_id}: {e}")
            raise


# Create service instance
user_service = UserService()
