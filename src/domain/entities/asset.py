"""
Asset entity representing a tradable symbol in the Watchlist.
Part of the domain layer - represents business rules and state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class AvailabilityStatus(str, Enum):
    """Availability status of the symbol in MT5"""
    DISPONIBLE = "DISPONIBLE"
    NO_DISPONIBLE = "NO_DISPONIBLE"


class AssetType(str, Enum):
    """Type of asset/classification"""
    FOREX_MAJOR = "FOREX_MAJOR"
    FOREX_MINOR = "FOREX_MINOR"
    METAL = "METAL"
    ENERGY = "ENERGY"
    INDEX = "INDEX"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"
    UNKNOWN = "UNKNOWN"


@dataclass
class Asset:
    """
    Asset entity representing a tradable symbol.
    
    Separates concerns:
    - availability_status: whether MT5 exposes this symbol
    - is_enabled: whether user wants to monitor this symbol
    """
    
    # Required fields first
    symbol: str
    display_name: str
    asset_type: AssetType
    
    # Identity (with defaults)
    id: UUID = field(default_factory=uuid4)
    
    # Status fields
    availability_status: AvailabilityStatus = AvailabilityStatus.DISPONIBLE
    is_enabled: bool = False
    source: str = "MT5"
    
    # Timestamps
    first_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_seen_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def mark_available(self) -> None:
        """Mark symbol as available in MT5"""
        self.availability_status = AvailabilityStatus.DISPONIBLE
        self.last_seen_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_unavailable(self) -> None:
        """Mark symbol as no longer available in MT5"""
        self.availability_status = AvailabilityStatus.NO_DISPONIBLE
        self.updated_at = datetime.utcnow()
    
    def enable(self) -> bool:
        """
        Enable symbol for radar monitoring.
        
        Returns:
            True if successfully enabled, False if not available
        """
        if self.availability_status == AvailabilityStatus.NO_DISPONIBLE:
            return False
        
        self.is_enabled = True
        self.updated_at = datetime.utcnow()
        return True
    
    def disable(self) -> None:
        """Disable symbol from radar monitoring"""
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
    
    def is_operational(self) -> bool:
        """
        Check if symbol is ready for radar operations.
        
        Returns:
            True if available and enabled
        """
        return (
            self.availability_status == AvailabilityStatus.DISPONIBLE
            and self.is_enabled
        )
    
    def update_classification(self, asset_type: AssetType) -> None:
        """Update asset type classification"""
        self.asset_type = asset_type
        self.updated_at = datetime.utcnow()
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.symbol or not self.symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        if not self.display_name or not self.display_name.strip():
            raise ValueError("Display name cannot be empty")
