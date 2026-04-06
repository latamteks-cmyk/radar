"""
MT5 Account entity for managing MetaTrader 5 account configurations.
Part of the domain layer - represents business rules and state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class EnvironmentType(str, Enum):
    """Type of trading environment"""
    DEV = "DEV"
    DEMO = "DEMO"
    PAPER = "PAPER"
    LIVE_MICRO = "LIVE_MICRO"
    LIVE = "LIVE"


class AvailabilityStatus(str, Enum):
    """Technical availability status of the account"""
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TERMINAL_NOT_FOUND = "TERMINAL_NOT_FOUND"
    CONNECTION_ERROR = "CONNECTION_ERROR"


class LifecycleStatus(str, Enum):
    """Lifecycle status of the account"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class ValidationStatus(str, Enum):
    """Status of validation attempts"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass
class MT5Account:
    """
    MT5 Account entity.
    
    Represents a MetaTrader 5 account configuration with separated concerns:
    - Registration (exists in DB)
    - Availability (technical connection status)
    - Enablement (operational readiness)
    """
    
    # Basic Information (required fields first)
    account_name: str
    broker_name: str
    server_name: str
    login: str
    password_secret_ref: str  # Reference to encrypted password, not plain text
    terminal_path: str
    environment_type: EnvironmentType
    
    # Identity (with defaults)
    id: UUID = field(default_factory=uuid4)
    
    # Environment and Status (with defaults)
    is_enabled: bool = False
    availability_status: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    is_default_for_environment: bool = False
    
    # Validation metadata (with defaults)
    last_validation_at: Optional[datetime] = None
    last_validation_status: Optional[ValidationStatus] = None
    
    # Audit timestamps (with defaults)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None
    
    def validate_account(self, validation_status: ValidationStatus, error_message: Optional[str] = None) -> None:
        """
        Update account validation status.
        
        Args:
            validation_status: Result of validation attempt
            error_message: Optional error message if validation failed
        """
        self.last_validation_at = datetime.utcnow()
        self.last_validation_status = validation_status
        
        if validation_status == ValidationStatus.SUCCESS:
            self.availability_status = AvailabilityStatus.AVAILABLE
        elif validation_status == ValidationStatus.FAILED:
            # Status will be set more specifically by the validation process
            self.availability_status = AvailabilityStatus.UNAVAILABLE
    
    def enable(self) -> bool:
        """
        Enable account for operational use.
        
        Returns:
            True if successfully enabled, False if not available
        """
        if self.availability_status != AvailabilityStatus.AVAILABLE:
            return False
        
        if self.lifecycle_status != LifecycleStatus.ACTIVE:
            return False
        
        self.is_enabled = True
        self.updated_at = datetime.utcnow()
        return True
    
    def disable(self) -> None:
        """Disable account for operational use"""
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive account (soft delete)"""
        self.lifecycle_status = LifecycleStatus.ARCHIVED
        self.is_enabled = False
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate account from inactive state"""
        if self.lifecycle_status == LifecycleStatus.ARCHIVED:
            raise ValueError("Cannot activate an archived account")
        
        self.lifecycle_status = LifecycleStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate account (set to inactive)"""
        self.lifecycle_status = LifecycleStatus.INACTIVE
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
    
    def set_default_for_environment(self) -> None:
        """Mark as default for its environment"""
        self.is_default_for_environment = True
        self.updated_at = datetime.utcnow()
    
    def unset_default_for_environment(self) -> None:
        """Unmark as default for its environment"""
        self.is_default_for_environment = False
        self.updated_at = datetime.utcnow()
    
    def is_operational(self) -> bool:
        """
        Check if account is ready for operations.
        
        Returns:
            True if account is enabled, available, and active
        """
        return (
            self.is_enabled
            and self.availability_status == AvailabilityStatus.AVAILABLE
            and self.lifecycle_status == LifecycleStatus.ACTIVE
        )
    
    def __post_init__(self):
        """Validate entity invariants after initialization"""
        if not self.account_name or not self.account_name.strip():
            raise ValueError("Account name cannot be empty")
        
        if not self.login or not self.login.strip():
            raise ValueError("Login cannot be empty")
        
        if not self.server_name or not self.server_name.strip():
            raise ValueError("Server name cannot be empty")
        
        if not self.terminal_path or not self.terminal_path.strip():
            raise ValueError("Terminal path cannot be empty")
