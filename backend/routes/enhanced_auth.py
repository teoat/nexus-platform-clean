#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced Authentication Routes V3.0
API routes for authentication with OAuth and POV support
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from schemas.enhanced_user import (OAuthLoginRequest, POVConfiguration,
                                   POVSelectionRequest, UserCreate,
                                   UserPreferences, UserProfile, UserResponse,
                                   UserSettings)
from services.enhanced_auth_service import enhanced_auth_service
from services.frenly_ai_service import frenly_ai_service
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (AIInterventionLevel, AnalysisMode,
                                      OAuthAccount, POVRole)
from database.schema_normalization import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/auth", tags=["Enhanced Authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with enhanced features"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = enhanced_auth_service.get_password_hash(user_data.password)

        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            role=user_data.role,
            primary_pov_role=user_data.primary_pov_role,
            secondary_pov_roles=[role.value for role in user_data.secondary_pov_roles]
            if user_data.secondary_pov_roles
            else [],
            analysis_mode=user_data.analysis_mode,
            ai_intervention_level=user_data.ai_intervention_level,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create Frenly AI configuration
        await frenly_ai_service._create_default_config(db, user.id)

        return UserResponse.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/login")
async def login_user(email: str, password: str, db: Session = Depends(get_db)):
    """Login user with email and password"""
    try:
        user = enhanced_auth_service.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        tokens = enhanced_auth_service.create_user_tokens(user)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
            "user": UserResponse.from_orm(user),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/oauth/login")
async def oauth_login(oauth_data: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Login user with OAuth provider"""
    try:
        user = await enhanced_auth_service.authenticate_oauth_user(
            db, oauth_data.provider, oauth_data.access_token
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth authentication failed",
            )

        tokens = enhanced_auth_service.create_user_tokens(user)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
            "user": UserResponse.from_orm(user),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OAuth login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        new_tokens = enhanced_auth_service.refresh_access_token(refresh_token)

        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        return new_tokens

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/pov/configure")
async def configure_pov(
    pov_config: POVSelectionRequest,
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Configure user's POV settings"""
    try:
        # Update user's POV configuration
        user = await enhanced_auth_service.update_pov_configuration(
            db, current_user.id, pov_config
        )

        return {
            "message": "POV configuration updated successfully",
            "user": UserResponse.from_orm(user),
        }

    except Exception as e:
        logger.error(f"Error configuring POV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(enhanced_auth_service.get_current_user),
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfile,
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile"""
    try:
        # Update user profile fields
        if profile_data.full_name:
            current_user.full_name = profile_data.full_name
        if profile_data.bio:
            current_user.bio = profile_data.bio
        if profile_data.avatar_url:
            current_user.avatar_url = profile_data.avatar_url
        if profile_data.location:
            current_user.location = profile_data.location
        if profile_data.website:
            current_user.website = profile_data.website

        current_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/settings", response_model=UserResponse)
async def update_settings(
    settings_data: UserSettings,
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Update user settings"""
    try:
        # Update user settings
        if settings_data.language:
            current_user.language = settings_data.language
        if settings_data.timezone:
            current_user.timezone = settings_data.timezone
        if settings_data.currency:
            current_user.currency = settings_data.currency
        if settings_data.date_format:
            current_user.date_format = settings_data.date_format
        if settings_data.notifications_enabled is not None:
            current_user.notifications_enabled = settings_data.notifications_enabled
        if settings_data.email_notifications is not None:
            current_user.email_notifications = settings_data.email_notifications
        if settings_data.sms_notifications is not None:
            current_user.sms_notifications = settings_data.sms_notifications

        current_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/preferences", response_model=UserResponse)
async def update_preferences(
    preferences_data: UserPreferences,
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Update user preferences"""
    try:
        # Update user preferences
        if preferences_data.theme:
            current_user.theme = preferences_data.theme
        if preferences_data.dashboard_layout:
            current_user.dashboard_layout = preferences_data.dashboard_layout
        if preferences_data.default_view:
            current_user.default_view = preferences_data.default_view
        if preferences_data.auto_refresh is not None:
            current_user.auto_refresh = preferences_data.auto_refresh
        if preferences_data.refresh_interval:
            current_user.refresh_interval = preferences_data.refresh_interval

        current_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/oauth/accounts")
async def get_oauth_accounts(
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's OAuth accounts"""
    try:
        oauth_accounts = (
            db.query(OAuthAccount).filter(OAuthAccount.user_id == current_user.id).all()
        )

        return [
            {
                "id": account.id,
                "provider": account.provider.value,
                "email": account.email,
                "name": account.name,
                "avatar_url": account.avatar_url,
                "connected_at": account.connected_at,
                "last_used_at": account.last_used_at,
            }
            for account in oauth_accounts
        ]

    except Exception as e:
        logger.error(f"Error getting OAuth accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/oauth/accounts/{account_id}")
async def disconnect_oauth_account(
    account_id: str,
    current_user: User = Depends(enhanced_auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnect OAuth account"""
    try:
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.id == account_id, OAuthAccount.user_id == current_user.id
            )
            .first()
        )

        if not oauth_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="OAuth account not found"
            )

        db.delete(oauth_account)
        db.commit()

        return {"message": "OAuth account disconnected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting OAuth account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(enhanced_auth_service.get_current_user),
):
    """Logout user (client-side token invalidation)"""
    return {"message": "Logged out successfully"}


@router.get("/pov/roles")
async def get_pov_roles():
    """Get available POV roles"""
    return {
        "roles": [
            {
                "value": role.value,
                "label": role.value.replace("_", " ").title(),
                "description": f"Professional perspective for {role.value.replace('_', ' ')}",
            }
            for role in POVRole
        ]
    }


@router.get("/pov/analysis-modes")
async def get_analysis_modes():
    """Get available analysis modes"""
    return {
        "modes": [
            {
                "value": mode.value,
                "label": mode.value.replace("_", " ").title(),
                "description": f"Analysis mode for {mode.value.replace('_', ' ')}",
            }
            for mode in AnalysisMode
        ]
    }


@router.get("/pov/ai-intervention-levels")
async def get_ai_intervention_levels():
    """Get available AI intervention levels"""
    return {
        "levels": [
            {
                "value": level.value,
                "label": level.value.replace("_", " ").title(),
                "description": f"AI intervention level for {level.value.replace('_', ' ')}",
            }
            for level in AIInterventionLevel
        ]
    }
