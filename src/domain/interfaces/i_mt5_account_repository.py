"""
MT5 Account Repository interface.
Part of the domain layer - defines contract for infrastructure implementation.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.entities.mt5_account import MT5Account, EnvironmentType, AvailabilityStatus
from src.domain.entities.mt5_account_audit_log import MT5AccountAuditLog
from src.domain.entities.mt5_account_validation_log import MT5AccountValidationLog


class IMT5AccountRepository(ABC):
    """
    Repository interface for MT5 Account management.
    
    Defines the contract for persisting and retrieving MT5 account configurations.
    Infrastructure layer (PostgreSQL) will implement this interface.
    """
    
    @abstractmethod
    async def create(self, account: MT5Account) -> MT5Account:
        """
        Create a new MT5 account.
        
        Args:
            account: MT5Account entity to create
            
        Returns:
            Created MT5Account with ID populated
        """
        ...
    
    @abstractmethod
    async def get_by_id(self, account_id: UUID) -> Optional[MT5Account]:
        """
        Get account by ID.
        
        Args:
            account_id: Unique identifier of the account
            
        Returns:
            MT5Account if found, None otherwise
        """
        ...
    
    @abstractmethod
    async def get_all(self) -> List[MT5Account]:
        """
        Get all MT5 accounts.
        
        Returns:
            List of all MT5 accounts
        """
        ...
    
    @abstractmethod
    async def get_by_environment(
        self, 
        environment: EnvironmentType,
        enabled_only: bool = False
    ) -> List[MT5Account]:
        """
        Get accounts by environment type.
        
        Args:
            environment: Environment type to filter by
            enabled_only: If True, only return enabled accounts
            
        Returns:
            List of MT5 accounts in the specified environment
        """
        ...
    
    @abstractmethod
    async def get_default_for_environment(
        self, 
        environment: EnvironmentType
    ) -> Optional[MT5Account]:
        """
        Get the default account for an environment.
        
        Args:
            environment: Environment type
            
        Returns:
            Default MT5Account for the environment, or None if not set
        """
        ...
    
    @abstractmethod
    async def get_operational_accounts(self) -> List[MT5Account]:
        """
        Get all accounts that are operational (enabled, available, active).
        
        Returns:
            List of operational MT5 accounts
        """
        ...
    
    @abstractmethod
    async def update(self, account: MT5Account) -> MT5Account:
        """
        Update an existing MT5 account.
        
        Args:
            account: MT5Account entity with updates
            
        Returns:
            Updated MT5Account
        """
        ...
    
    @abstractmethod
    async def delete(self, account_id: UUID) -> bool:
        """
        Soft delete (archive) an MT5 account.
        
        Args:
            account_id: ID of account to archive
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_audit_logs(
        self, 
        account_id: UUID,
        limit: int = 100
    ) -> List[MT5AccountAuditLog]:
        """
        Get audit logs for an account.
        
        Args:
            account_id: Account ID
            limit: Maximum number of logs to return
            
        Returns:
            List of audit logs, most recent first
        """
        ...
    
    @abstractmethod
    async def log_audit(self, audit_log: MT5AccountAuditLog) -> MT5AccountAuditLog:
        """
        Create an audit log entry.
        
        Args:
            audit_log: Audit log to persist
            
        Returns:
            Persisted audit log
        """
        ...
    
    @abstractmethod
    async def log_validation(
        self, 
        validation_log: MT5AccountValidationLog
    ) -> MT5AccountValidationLog:
        """
        Create a validation log entry.
        
        Args:
            validation_log: Validation log to persist
            
        Returns:
            Persisted validation log
        """
        ...
    
    @abstractmethod
    async def get_validation_logs(
        self, 
        account_id: UUID,
        limit: int = 50
    ) -> List[MT5AccountValidationLog]:
        """
        Get validation logs for an account.
        
        Args:
            account_id: Account ID
            limit: Maximum number of logs to return
            
        Returns:
            List of validation logs, most recent first
        """
        ...
