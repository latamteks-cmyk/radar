"""
Pydantic schemas for MT5 Account API.
Presentation layer - request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class EnvironmentType(str, Enum):
    DEV = "DEV"
    DEMO = "DEMO"
    PAPER = "PAPER"
    LIVE_MICRO = "LIVE_MICRO"
    LIVE = "LIVE"


class AvailabilityStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TERMINAL_NOT_FOUND = "TERMINAL_NOT_FOUND"
    CONNECTION_ERROR = "CONNECTION_ERROR"


class LifecycleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class ValidationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class MT5AccountCreateRequest(BaseModel):
    """Request schema for creating MT5 account"""
    
    account_name: str = Field(..., min_length=1, max_length=255, description="Display name for the account")
    broker_name: str = Field(..., min_length=1, max_length=255, description="Name of the broker")
    server_name: str = Field(..., min_length=1, max_length=255, description="MT5 server name")
    login: str = Field(..., min_length=1, max_length=100, description="MT5 account login")
    password: str = Field(..., min_length=1, description="MT5 account password (will be encrypted)")
    terminal_path: str = Field(..., min_length=1, description="Path to MT5 terminal executable")
    environment_type: EnvironmentType = Field(..., description="Type of trading environment")
    
    @validator("terminal_path")
    def validate_terminal_path(cls, v):
        if not v.endswith('.exe'):
            raise ValueError("Terminal path must be an executable (.exe)")
        return v


class MT5AccountResponse(BaseModel):
    """Response schema for MT5 account"""
    
    id: UUID
    account_name: str
    broker_name: str
    server_name: str
    login: str  # Will be masked in responses
    terminal_path: str
    environment_type: EnvironmentType
    is_enabled: bool
    availability_status: AvailabilityStatus
    lifecycle_status: LifecycleStatus
    is_default_for_environment: bool
    last_validation_at: Optional[datetime]
    last_validation_status: Optional[ValidationStatus]
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MT5AccountUpdateRequest(BaseModel):
    """Request schema for updating MT5 account"""
    
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    broker_name: Optional[str] = Field(None, min_length=1, max_length=255)
    server_name: Optional[str] = Field(None, min_length=1, max_length=255)
    login: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1, description="New password (will replace old one)")
    terminal_path: Optional[str] = Field(None, min_length=1)
    environment_type: Optional[EnvironmentType]
    
    @validator("terminal_path")
    def validate_terminal_path(cls, v):
        if v and not v.endswith('.exe'):
            raise ValueError("Terminal path must be an executable (.exe)")
        return v


class MT5AccountValidationRequest(BaseModel):
    """Request schema for validating account connection"""
    
    password: str = Field(..., min_length=1, description="MT5 account password for validation")


class MT5AccountAuditLogResponse(BaseModel):
    """Response schema for audit logs"""
    
    id: UUID
    account_id: UUID
    action: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime
    reason: Optional[str]
    
    class Config:
        from_attributes = True


class MT5AccountValidationLogResponse(BaseModel):
    """Response schema for validation logs"""
    
    id: UUID
    account_id: UUID
    validation_started_at: datetime
    validation_finished_at: Optional[datetime]
    status: str
    error_message: Optional[str]
    broker_response_summary: Optional[str]
    
    class Config:
        from_attributes = True


class MT5AccountListResponse(BaseModel):
    """List response for MT5 accounts"""
    
    accounts: list[MT5AccountResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response"""
    
    message: str
    success: bool
