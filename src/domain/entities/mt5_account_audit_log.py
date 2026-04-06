"""
MT5 Account Audit Log entity for tracking all changes to MT5 accounts.
Part of the domain layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MT5AccountAuditLog:
    """
    Audit log for MT5 Account changes.
    
    Tracks all administrative actions on MT5 accounts for compliance
    and troubleshooting.
    """
    
    # Required fields first
    account_id: UUID
    action: str  # CREATED, UPDATED, ENABLED, DISABLED, ARCHIVED, VALIDATED, etc.
    
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
        
        if not self.account_id:
            raise ValueError("Account ID is required")
