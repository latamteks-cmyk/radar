"""
SQLAlchemy models for MT5 account management.
Infrastructure layer - database schema definition.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum as SAEnum, Text, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid

from src.infrastructure.persistence.database import Base


class EnvironmentTypeEnum(str, enum.Enum):
    """SQLAlchemy enum for environment types"""
    DEV = "DEV"
    DEMO = "DEMO"
    PAPER = "PAPER"
    LIVE_MICRO = "LIVE_MICRO"
    LIVE = "LIVE"


class AvailabilityStatusEnum(str, enum.Enum):
    """SQLAlchemy enum for availability status"""
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TERMINAL_NOT_FOUND = "TERMINAL_NOT_FOUND"
    CONNECTION_ERROR = "CONNECTION_ERROR"


class LifecycleStatusEnum(str, enum.Enum):
    """SQLAlchemy enum for lifecycle status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class ValidationStatusEnum(str, enum.Enum):
    """SQLAlchemy enum for validation status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class MT5AccountModel(Base):
    """SQLAlchemy model for MT5 accounts"""
    
    __tablename__ = "mt5_accounts"
    __table_args__ = (
        Index("idx_mt5_accounts_environment", "environment_type"),
        Index("idx_mt5_accounts_lifecycle", "lifecycle_status"),
        Index("idx_mt5_accounts_enabled", "is_enabled"),
        Index("idx_mt5_accounts_default_env", "environment_type", "is_default_for_environment"),
    )
    
    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    account_name = Column(String(255), nullable=False, index=True)
    broker_name = Column(String(255), nullable=False)
    server_name = Column(String(255), nullable=False)
    login = Column(String(100), nullable=False)
    password_secret_ref = Column(String(500), nullable=False)  # Reference to secret, not actual password
    terminal_path = Column(String(500), nullable=False)
    
    # Environment and Status
    environment_type = Column(
        SAEnum(EnvironmentTypeEnum),
        nullable=False,
        default=EnvironmentTypeEnum.DEMO
    )
    is_enabled = Column(Boolean, nullable=False, default=False)
    availability_status = Column(
        SAEnum(AvailabilityStatusEnum),
        nullable=False,
        default=AvailabilityStatusEnum.UNKNOWN
    )
    lifecycle_status = Column(
        SAEnum(LifecycleStatusEnum),
        nullable=False,
        default=LifecycleStatusEnum.ACTIVE
    )
    is_default_for_environment = Column(Boolean, nullable=False, default=False)
    
    # Validation metadata
    last_validation_at = Column(DateTime(timezone=True), nullable=True)
    last_validation_status = Column(
        SAEnum(ValidationStatusEnum),
        nullable=True
    )
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<MT5AccountModel(id={self.id}, name={self.account_name}, env={self.environment_type.value})>"


class MT5AccountAuditLogModel(Base):
    """SQLAlchemy model for MT5 account audit logs"""
    
    __tablename__ = "mt5_account_audit_logs"
    __table_args__ = (
        Index("idx_mt5_audit_account_id", "account_id"),
        Index("idx_mt5_audit_changed_at", "changed_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Action metadata
    action = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)  # JSON string
    new_value = Column(Text, nullable=True)  # JSON string
    
    # Audit trail
    changed_by = Column(String(255), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<MT5AccountAuditLogModel(id={self.id}, account={self.account_id}, action={self.action})>"


class MT5AccountValidationLogModel(Base):
    """SQLAlchemy model for MT5 account validation logs"""
    
    __tablename__ = "mt5_account_validation_logs"
    __table_args__ = (
        Index("idx_mt5_validation_account_id", "account_id"),
        Index("idx_mt5_validation_started_at", "validation_started_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Validation timing
    validation_started_at = Column(DateTime(timezone=True), server_default=func.now())
    validation_finished_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    broker_response_summary = Column(Text, nullable=True)  # JSON string (no sensitive data)
    
    def __repr__(self):
        return f"<MT5AccountValidationLogModel(id={self.id}, account={self.account_id}, status={self.status})>"
