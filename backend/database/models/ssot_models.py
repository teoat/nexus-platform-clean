from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import JSON  # Import generic JSON type
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import \
    JSONB  # Keep for PostgreSQL, but use generic JSON for SQLite
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Import Base from the newly created base.py
from database.base import Base


class SSOTAnchorModel(Base):
    __tablename__ = "ssot_anchors"

    id = Column(String, primary_key=True, index=True)
    family = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    format = Column(String, nullable=False)
    version = Column(String, nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata_ = Column(
        JSON, nullable=True
    )  # Renamed to avoid conflict with Python keyword
    tags = Column(JSON, nullable=True)
    status = Column(String, default="active")

    def __repr__(self):
        return f"<SSOTAnchorModel(id='{self.id}', family='{self.family}')>"


class AliasDefinitionModel(Base):
    __tablename__ = "alias_definitions"

    alias = Column(String, primary_key=True, index=True)
    canonical = Column(String, nullable=False)
    context = Column(
        String, primary_key=True, index=True
    )  # Composite primary key with alias
    alias_type = Column(String, nullable=False)  # Storing enum value as string
    description = Column(Text, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)  # Storing enum value as string
    metadata_ = Column(
        JSON, nullable=True
    )  # Renamed to avoid conflict with Python keyword
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<AliasDefinitionModel(alias='{self.alias}', context='{self.context}')>"


class AuditEntryModel(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action = Column(String, nullable=False)
    user = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    request_id = Column(String, nullable=True)

    def __repr__(self):
        return f"<AuditEntryModel(action='{self.action}', user='{self.user}')>"
