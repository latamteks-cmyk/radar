"""
Asset Audit Log entity for tracking all changes to assets.
Part of the domain layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class AssetAuditLog:
    """
    Audit log for Asset changes.
    
    Tracks all administrative actions on assets for compliance
    and troubleshooting.
    """
    
    # Required fields first
    asset_id: UUID
    action: str  # CREATED, UPDATED, ENABLED, DISABLED, SYNC_INSERTED, SYNC_UPDATED, SYNC_MARKED_UNAVAILABLE
    
    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    old_value: Optional[str] = None  # JSON string of old value(s)
    new_value: Optional[str] = None  # JSON string of new value(s)
    changed_by: Optional[str] = None  # User or system that made the change
    changed_at: datetime = field(default_factory=datetime.utcnow)
    reason: Optional[str] = None  # Why the change was made
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.action or not self.action.strip():
            raise ValueError("Action cannot be empty")
        
        if not self.asset_id:
            raise ValueError("Asset ID is required")
