"""
MT5 Account Validation Log entity for tracking validation attempts.
Part of the domain layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MT5AccountValidationLog:
    """
    Validation log for MT5 Account connection tests.
    
    Records each validation attempt with timing and results.
    """
    
    # Required fields first
    account_id: UUID
    status: str  # PENDING, SUCCESS, FAILED, TIMEOUT
    
    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    validation_started_at: datetime = field(default_factory=datetime.utcnow)
    validation_finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    broker_response_summary: Optional[str] = None  # JSON string (no sensitive data)
    
    def complete(self, status: str, error_message: Optional[str] = None, 
                 broker_response_summary: Optional[str] = None) -> None:
        """
        Mark validation as complete.
        
        Args:
            status: Final status of validation
            error_message: Error message if validation failed
            broker_response_summary: Summary of broker response (no sensitive data)
        """
        self.validation_finished_at = datetime.utcnow()
        self.status = status
        self.error_message = error_message
        self.broker_response_summary = broker_response_summary
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.account_id:
            raise ValueError("Account ID is required")
        
        if not self.status or not self.status.strip():
            raise ValueError("Status cannot be empty")
