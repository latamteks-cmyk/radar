"""
SQLAlchemy models for Asset Catalog / Watchlist.
Infrastructure layer - database schema definition.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum as SAEnum, Text, JSON, Index, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid

from src.infrastructure.persistence.database import Base


class AvailabilityStatusEnum(str, enum.Enum):
    """SQLAlchemy enum for availability status"""
    DISPONIBLE = "DISPONIBLE"
    NO_DISPONIBLE = "NO_DISPONIBLE"


class AssetTypeEnum(str, enum.Enum):
    """SQLAlchemy enum for asset types"""
    FOREX_MAJOR = "FOREX_MAJOR"
    FOREX_MINOR = "FOREX_MINOR"
    METAL = "METAL"
    ENERGY = "ENERGY"
    INDEX = "INDEX"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"
    UNKNOWN = "UNKNOWN"


class AssetModel(Base):
    """SQLAlchemy model for assets/watchlist"""
    
    __tablename__ = "assets"
    __table_args__ = (
        Index("idx_assets_symbol", "symbol", unique=True),
        Index("idx_assets_type", "asset_type"),
        Index("idx_assets_availability", "availability_status"),
        Index("idx_assets_enabled", "is_enabled"),
        Index("idx_assets_last_seen", "last_seen_at"),
    )
    
    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    symbol = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    asset_type = Column(
        SAEnum(AssetTypeEnum),
        nullable=False,
        default=AssetTypeEnum.UNKNOWN
    )
    
    # Status fields
    availability_status = Column(
        SAEnum(AvailabilityStatusEnum),
        nullable=False,
        default=AvailabilityStatusEnum.DISPONIBLE
    )
    is_enabled = Column(Boolean, nullable=False, default=False)
    source = Column(String(50), nullable=False, default="MT5")
    
    # Timestamps
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AssetModel(id={self.id}, symbol={self.symbol}, type={self.asset_type.value})>"


class AssetSyncLogModel(Base):
    """SQLAlchemy model for asset sync logs"""
    
    __tablename__ = "asset_sync_logs"
    __table_args__ = (
        Index("idx_sync_logs_started_at", "sync_started_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Sync timing
    sync_started_at = Column(DateTime(timezone=True), server_default=func.now())
    sync_finished_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    status = Column(String(50), nullable=False)
    inserted_count = Column(Integer, nullable=False, default=0)
    updated_count = Column(Integer, nullable=False, default=0)
    unavailable_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AssetSyncLogModel(id={self.id}, status={self.status})>"


class AssetAuditLogModel(Base):
    """SQLAlchemy model for asset audit logs"""
    
    __tablename__ = "asset_audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_asset_id", "asset_id"),
        Index("idx_audit_logs_changed_at", "changed_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Action metadata
    action = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)  # JSON string
    new_value = Column(Text, nullable=True)  # JSON string
    
    # Audit trail
    changed_by = Column(String(255), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AssetAuditLogModel(id={self.id}, asset={self.asset_id}, action={self.action})>"
