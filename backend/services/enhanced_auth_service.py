#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced Authentication Service V3.0
Authentication and authorization logic with OAuth and POV support
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from schemas.enhanced_user import OAuthProvider, POVConfiguration
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (AIInterventionLevel, AnalysisMode,
                                      OAuthAccount, POVRole, User)

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth Configuration
OAUTH_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "user_info_url": "https://graph.microsoft.com/v1.0/me",
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "user_info_url": "https://api.linkedin.com/v2/people/~",
    },
}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class EnhancedAuthService:
    """Enhanced service class for authentication operations with OAuth and POV support"""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                )

            to_encode.update({"exp": expire, "type": "access"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    def create_refresh_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            to_encode.update({"exp": expire, "type": "refresh"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            if payload.get("type") != token_type:
                return None

            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None

            return payload
        except JWTError as e:
            logger.error(f"Error verifying token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    async def verify_oauth_token(
        self, provider: OAuthProvider, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Verify OAuth token with provider"""
        try:
            config = OAUTH_CONFIG.get(provider.value)
            if not config:
                return None

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config["user_info_url"],
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"OAuth verification failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error verifying OAuth token: {e}")
            return None

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            if not user.is_active:
                return None

            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    async def authenticate_oauth_user(
        self, db: Session, provider: OAuthProvider, access_token: str
    ) -> Optional[User]:
        """Authenticate a user with OAuth"""
        try:
            # Verify token with provider
            user_info = await self.verify_oauth_token(provider, access_token)
            if not user_info:
                return None

            # Check if OAuth account exists
            oauth_account = (
                db.query(OAuthAccount)
                .filter(
                    OAuthAccount.provider == provider,
                    OAuthAccount.provider_id == str(user_info.get("id", "")),
                )
                .first()
            )

            if oauth_account:
                # Update last used
                oauth_account.last_used_at = datetime.utcnow()
                db.commit()
                return oauth_account.user

            # Check if user exists by email
            user = (
                db.query(User).filter(User.email == user_info.get("email", "")).first()
            )

            if user:
                # Link OAuth account to existing user
                oauth_account = OAuthAccount(
                    user_id=user.id,
                    provider=provider,
                    provider_id=str(user_info.get("id", "")),
                    email=user_info.get("email", ""),
                    name=user_info.get("name", ""),
                    avatar_url=user_info.get("picture", ""),
                    access_token=access_token,
                )
                db.add(oauth_account)
                db.commit()
                return user

            # Create new user
            user = User(
                username=user_info.get("email", "").split("@")[0],
                email=user_info.get("email", ""),
                full_name=user_info.get("name", ""),
                oauth_provider=provider,
                oauth_provider_id=str(user_info.get("id", "")),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create OAuth account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_id=str(user_info.get("id", "")),
                email=user_info.get("email", ""),
                name=user_info.get("name", ""),
                avatar_url=user_info.get("picture", ""),
                access_token=access_token,
            )
            db.add(oauth_account)
            db.commit()

            return user

        except Exception as e:
            logger.error(f"Error authenticating OAuth user: {e}")
            return None

    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
    ) -> User:
        """Get the current authenticated user"""
        try:
            token = credentials.credentials
            payload = self.verify_token(token, "access")

            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_active_user(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        """Get the current active user"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )
        return current_user

    def create_user_tokens(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens for a user"""
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            access_token = self.create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role.value,
                },
                expires_delta=access_token_expires,
            )

            refresh_token = self.create_refresh_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=refresh_token_expires,
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except Exception as e:
            logger.error(f"Error creating user tokens: {e}")
            raise

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh an access token using a refresh token"""
        try:
            payload = self.verify_token(refresh_token, "refresh")
            if payload is None:
                return None

            user_id = payload.get("sub")
            if user_id is None:
                return None

            # Create new access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={
                    "sub": user_id,
                    "email": payload.get("email"),
                    "role": payload.get("role"),
                },
                expires_delta=access_token_expires,
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return None

    def check_permissions(self, user: User, required_role: str) -> bool:
        """Check if user has required role permissions"""
        try:
            role_hierarchy = {"user": 1, "moderator": 2, "admin": 3}

            user_level = role_hierarchy.get(user.role.value, 0)
            required_level = role_hierarchy.get(required_role, 0)

            return user_level >= required_level
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False

    def require_role(self, required_role: str):
        """Dependency to require a specific role"""

        def role_checker(current_user: User = Depends(self.get_current_user)) -> User:
            if not self.check_permissions(current_user, required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return current_user

        return role_checker

    def check_pov_permissions(self, user: User, required_pov_role: POVRole) -> bool:
        """Check if user has required POV role permissions"""
        try:
            if not user.primary_pov_role:
                return False

            # Check if user has the required POV role as primary or secondary
            if user.primary_pov_role == required_pov_role:
                return True

            # Check secondary roles
            if (
                user.secondary_pov_roles
                and required_pov_role.value in user.secondary_pov_roles
            ):
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking POV permissions: {e}")
            return False

    def require_pov_role(self, required_pov_role: POVRole):
        """Dependency to require a specific POV role"""

        def pov_checker(current_user: User = Depends(self.get_current_user)) -> User:
            if not self.check_pov_permissions(current_user, required_pov_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient POV permissions. Required: {required_pov_role.value}",
                )
            return current_user

        return pov_checker

    async def update_pov_configuration(
        self, db: Session, user_id: int, pov_config: POVConfiguration
    ) -> User:
        """Update user's POV configuration"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            user.primary_pov_role = pov_config.primary_role
            user.secondary_pov_roles = [
                role.value for role in pov_config.secondary_roles
            ]
            user.analysis_mode = pov_config.analysis_mode
            user.ai_intervention_level = pov_config.ai_intervention

            db.commit()
            db.refresh(user)

            return user
        except Exception as e:
            logger.error(f"Error updating POV configuration: {e}")
            raise

    def register_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = (
                db.query(User).filter(User.email == user_data["email"]).first()
            )
            if existing_user:
                raise ValueError("User already exists")

            # Create new user
            user = User(
                username=user_data["email"].split("@")[0],
                email=user_data["email"],
                full_name=user_data.get("full_name", ""),
                hashed_password=self.get_password_hash(user_data["password"]),
                is_active=True,
                role=user_data.get("role", "user"),
                primary_pov_role=user_data.get("primary_pov_role"),
                secondary_pov_roles=user_data.get("secondary_pov_roles", []),
                analysis_mode=user_data.get("analysis_mode", "single_pov"),
                ai_intervention_level=user_data.get("ai_intervention_level", "manual"),
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return user
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            db.rollback()
            raise


# Create service instance
enhanced_auth_service = EnhancedAuthService()
