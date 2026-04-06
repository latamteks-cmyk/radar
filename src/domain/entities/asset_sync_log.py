"""
Asset Sync Log entity for tracking synchronization attempts with MT5.
Part of the domain layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class AssetSyncLog:
    """
    Sync log for Asset synchronization with MT5.
    
    Records each synchronization attempt with timing and results.
    """
    
    # Required fields first
    status: str  # SUCCESS, PARTIAL, FAILED
    
    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    sync_started_at: datetime = field(default_factory=datetime.utcnow)
    sync_finished_at: Optional[datetime] = None
    inserted_count: int = 0
    updated_count: int = 0
    unavailable_count: int = 0
    error_message: Optional[str] = None
    
    def complete(
        self,
        status: str,
        inserted_count: int = 0,
        updated_count: int = 0,
        unavailable_count: int = 0,
        error_message: Optional[str] = None
    ) -> None:
        """
        Mark synchronization as complete.
        
        Args:
            status: Final status (SUCCESS, PARTIAL, FAILED)
            inserted_count: Number of new symbols inserted
            updated_count: Number of existing symbols updated
            unavailable_count: Number of symbols marked unavailable
            error_message: Error message if sync failed
        """
        self.sync_finished_at = datetime.utcnow()
        self.status = status
        self.inserted_count = inserted_count
        self.updated_count = updated_count
        self.unavailable_count = unavailable_count
        self.error_message = error_message
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.status or not self.status.strip():
            raise ValueError("Status cannot be empty")
