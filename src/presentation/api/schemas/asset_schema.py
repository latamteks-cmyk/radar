"""
Pydantic schemas for Asset Catalog / Watchlist API.
Presentation layer - request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field


class AvailabilityStatus(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    NO_DISPONIBLE = "NO_DISPONIBLE"


class AssetType(str, Enum):
    FOREX_MAJOR = "FOREX_MAJOR"
    FOREX_MINOR = "FOREX_MINOR"
    METAL = "METAL"
    ENERGY = "ENERGY"
    INDEX = "INDEX"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"
    UNKNOWN = "UNKNOWN"


class AssetResponse(BaseModel):
    """Response schema for asset"""
    
    id: UUID
    symbol: str
    display_name: str
    asset_type: AssetType
    availability_status: AvailabilityStatus
    is_enabled: bool
    source: str
    first_seen_at: datetime
    last_seen_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssetSyncLogResponse(BaseModel):
    """Response schema for sync logs"""
    
    id: UUID
    sync_started_at: datetime
    sync_finished_at: Optional[datetime]
    status: str
    inserted_count: int
    updated_count: int
    unavailable_count: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class AssetAuditLogResponse(BaseModel):
    """Response schema for audit logs"""
    
    id: UUID
    asset_id: UUID
    action: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime
    reason: Optional[str]
    
    class Config:
        from_attributes = True


class WatchlistResponse(BaseModel):
    """Response schema for watchlist grouped by type"""
    
    assets: Dict[str, List[AssetResponse]]
    total: int


class WatchlistSyncResponse(BaseModel):
    """Response schema for sync operation"""
    
    sync_id: UUID
    status: str
    inserted_count: int
    updated_count: int
    unavailable_count: int
    sync_started_at: datetime
    sync_finished_at: Optional[datetime]
    error_message: Optional[str]


class MessageResponse(BaseModel):
    """Generic message response"""
    
    message: str
    success: bool
