"""
MT5 Account Service - Application layer service for managing MT5 accounts.
Implements use cases for account creation, validation, enablement, etc.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.entities.mt5_account import (
    MT5Account,
    EnvironmentType,
    AvailabilityStatus,
    LifecycleStatus,
    ValidationStatus,
)
from src.domain.entities.mt5_account_audit_log import MT5AccountAuditLog
from src.domain.entities.mt5_account_validation_log import MT5AccountValidationLog
from src.domain.interfaces.i_mt5_account_repository import IMT5AccountRepository
from src.domain.interfaces.i_mt5_gateway import IMT5Gateway

logger = logging.getLogger(__name__)


class MT5AccountService:
    """
    Application service for MT5 Account management.
    
    Implements the use cases defined in ADR-002:
    - Create account
    - Edit account
    - Validate account connection
    - Enable/disable account
    - Archive account
    - Set default for environment
    - Query accounts
    """
    
    def __init__(
        self,
        account_repository: IMT5AccountRepository,
        mt5_gateway: IMT5Gateway
    ):
        """
        Initialize service with dependencies.
        
        Args:
            account_repository: Repository for account persistence
            mt5_gateway: Gateway for MT5 connection testing
        """
        self._account_repository = account_repository
        self._mt5_gateway = mt5_gateway
    
    async def create_account(
        self,
        account_name: str,
        broker_name: str,
        server_name: str,
        login: str,
        password_secret_ref: str,
        terminal_path: str,
        environment_type: EnvironmentType,
        created_by: Optional[str] = None
    ) -> MT5Account:
        """
        Create a new MT5 account.
        
        The account starts in:
        - lifecycle_status: ACTIVE
        - availability_status: UNKNOWN
        - is_enabled: false
        
        Args:
            account_name: Display name for the account
            broker_name: Name of the broker
            server_name: MT5 server name
            login: MT5 account login
            password_secret_ref: Reference to encrypted password
            terminal_path: Path to MT5 terminal
            environment_type: Type of environment
            created_by: User or system creating the account
            
        Returns:
            Created MT5Account
        """
        logger.info(f"Creating MT5 account: {account_name}")
        
        # Create account with initial state
        account = MT5Account(
            account_name=account_name,
            broker_name=broker_name,
            server_name=server_name,
            login=login,
            password_secret_ref=password_secret_ref,
            terminal_path=terminal_path,
            environment_type=environment_type,
            is_enabled=False,
            availability_status=AvailabilityStatus.UNKNOWN,
            lifecycle_status=LifecycleStatus.ACTIVE,
        )
        
        # Persist account
        created_account = await self._account_repository.create(account)
        
        # Audit log
        await self._audit_account(
            account_id=created_account.id,
            action="CREATED",
            new_value=json.dumps({
                "account_name": account_name,
                "broker_name": broker_name,
                "environment_type": environment_type.value,
            }),
            changed_by=created_by,
            reason="Account created via UI"
        )
        
        logger.info(f"MT5 account created: {created_account.id}")
        return created_account
    
    async def validate_account(
        self,
        account_id: UUID,
        password: str,
        validated_by: Optional[str] = None
    ) -> MT5Account:
        """
        Validate account connection to MT5.
        
        Tests the connection and updates availability status.
        
        Args:
            account_id: ID of account to validate
            password: MT5 account password (plaintext for validation)
            validated_by: User or system performing validation
            
        Returns:
            Updated MT5Account with validation results
        """
        logger.info(f"Validating MT5 account: {account_id}")
        
        # Get account
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        if account.lifecycle_status == LifecycleStatus.ARCHIVED:
            raise ValueError("Cannot validate archived account")
        
        # Create validation log
        validation_log = MT5AccountValidationLog(
            account_id=account_id,
            status="PENDING"
        )
        
        try:
            # Test connection via MT5 gateway
            result = await self._mt5_gateway.test_connection(
                login=account.login,
                password=password,
                server=account.server_name,
                terminal_path=account.terminal_path
            )
            
            # Update validation log
            validation_log.complete(
                status="SUCCESS" if result.success else "FAILED",
                error_message=result.error_message,
                broker_response_summary=json.dumps({
                    "broker_name": result.broker_name,
                    "server_name": result.server_name,
                    "account_type": result.account_type,
                    "currency": result.currency,
                }) if result.success else None
            )
            
            # Update account status
            if result.success:
                account.validate_account(ValidationStatus.SUCCESS)
                logger.info(f"Account validation successful: {account_id}")
            else:
                account.validate_account(ValidationStatus.FAILED)
                account.availability_status = AvailabilityStatus.INVALID_CREDENTIALS
                logger.warning(f"Account validation failed: {account_id} - {result.error_message}")
            
        except FileNotFoundError:
            validation_log.complete(
                status="FAILED",
                error_message="Terminal not found at specified path"
            )
            account.availability_status = AvailabilityStatus.TERMINAL_NOT_FOUND
            logger.warning(f"Terminal not found for account: {account_id}")
            
        except Exception as e:
            validation_log.complete(
                status="FAILED",
                error_message=str(e)
            )
            account.availability_status = AvailabilityStatus.CONNECTION_ERROR
            logger.error(f"Account validation error: {account_id} - {e}")
        
        # Persist validation log
        await self._account_repository.log_validation(validation_log)
        
        # Update account
        updated_account = await self._account_repository.update(account)
        
        # Audit log
        await self._audit_account(
            account_id=account_id,
            action="VALIDATED",
            old_value=json.dumps({
                "availability_status": account.availability_status.value,
                "last_validation_status": account.last_validation_status.value if account.last_validation_status else None,
            }),
            new_value=json.dumps({
                "availability_status": updated_account.availability_status.value,
                "last_validation_status": updated_account.last_validation_status.value if updated_account.last_validation_status else None,
            }),
            changed_by=validated_by,
            reason="Account validation performed"
        )
        
        return updated_account
    
    async def enable_account(
        self,
        account_id: UUID,
        enabled_by: Optional[str] = None
    ) -> MT5Account:
        """
        Enable account for operational use.
        
        Account must be available (validated successfully) to be enabled.
        
        Args:
            account_id: ID of account to enable
            enabled_by: User or system enabling the account
            
        Returns:
            Updated MT5Account
            
        Raises:
            ValueError: If account is not available for enabling
        """
        logger.info(f"Enabling MT5 account: {account_id}")
        
        # Get account
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        # Try to enable
        success = account.enable()
        if not success:
            raise ValueError(
                f"Account cannot be enabled. "
                f"Availability: {account.availability_status.value}, "
                f"Lifecycle: {account.lifecycle_status.value}"
            )
        
        # Update account
        updated_account = await self._account_repository.update(account)
        
        # Audit log
        await self._audit_account(
            account_id=account_id,
            action="ENABLED",
            old_value=json.dumps({"is_enabled": False}),
            new_value=json.dumps({"is_enabled": True}),
            changed_by=enabled_by,
            reason="Account enabled for operations"
        )
        
        logger.info(f"MT5 account enabled: {account_id}")
        return updated_account
    
    async def disable_account(
        self,
        account_id: UUID,
        disabled_by: Optional[str] = None
    ) -> MT5Account:
        """
        Disable account for operational use.
        
        Args:
            account_id: ID of account to disable
            disabled_by: User or system disabling the account
            
        Returns:
            Updated MT5Account
        """
        logger.info(f"Disabling MT5 account: {account_id}")
        
        # Get account
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        old_value = json.dumps({"is_enabled": account.is_enabled})
        
        # Disable
        account.disable()
        
        # Update account
        updated_account = await self._account_repository.update(account)
        
        # Audit log
        await self._audit_account(
            account_id=account_id,
            action="DISABLED",
            old_value=old_value,
            new_value=json.dumps({"is_enabled": False}),
            changed_by=disabled_by,
            reason="Account disabled"
        )
        
        logger.info(f"MT5 account disabled: {account_id}")
        return updated_account
    
    async def archive_account(
        self,
        account_id: UUID,
        archived_by: Optional[str] = None
    ) -> MT5Account:
        """
        Archive account (soft delete).
        
        Archived accounts cannot be used for operations but remain
        in the database for audit and historical purposes.
        
        Args:
            account_id: ID of account to archive
            archived_by: User or system archiving the account
            
        Returns:
            Updated MT5Account
        """
        logger.info(f"Archiving MT5 account: {account_id}")
        
        # Get account
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        old_value = json.dumps({
            "lifecycle_status": account.lifecycle_status.value,
            "is_enabled": account.is_enabled,
        })
        
        # Archive
        account.archive()
        
        # Update account
        updated_account = await self._account_repository.update(account)
        
        # Audit log
        await self._audit_account(
            account_id=account_id,
            action="ARCHIVED",
            old_value=old_value,
            new_value=json.dumps({
                "lifecycle_status": "ARCHIVED",
                "is_enabled": False,
                "archived_at": updated_account.archived_at.isoformat() if updated_account.archived_at else None,
            }),
            changed_by=archived_by,
            reason="Account archived"
        )
        
        logger.info(f"MT5 account archived: {account_id}")
        return updated_account
    
    async def set_default_for_environment(
        self,
        account_id: UUID,
        set_by: Optional[str] = None
    ) -> MT5Account:
        """
        Set account as default for its environment.
        
        This will unset any other default account for the same environment.
        
        Args:
            account_id: ID of account to set as default
            set_by: User or system setting the default
            
        Returns:
            Updated MT5Account
        """
        logger.info(f"Setting default MT5 account for environment: {account_id}")
        
        # Get account
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        if account.lifecycle_status != LifecycleStatus.ACTIVE:
            raise ValueError("Cannot set inactive or archived account as default")
        
        # Unset other defaults for the same environment
        accounts_in_env = await self._account_repository.get_by_environment(
            account.environment_type,
            enabled_only=False
        )
        
        for other_account in accounts_in_env:
            if other_account.id != account_id and other_account.is_default_for_environment:
                other_account.unset_default_for_environment()
                await self._account_repository.update(other_account)
                
                await self._audit_account(
                    account_id=other_account.id,
                    action="UNSET_DEFAULT",
                    old_value=json.dumps({"is_default_for_environment": True}),
                    new_value=json.dumps({"is_default_for_environment": False}),
                    changed_by=set_by,
                    reason=f"Default replaced by account {account_id}"
                )
        
        # Set this account as default
        account.set_default_for_environment()
        updated_account = await self._account_repository.update(account)
        
        # Audit log
        await self._audit_account(
            account_id=account_id,
            action="SET_DEFAULT",
            old_value=json.dumps({"is_default_for_environment": False}),
            new_value=json.dumps({"is_default_for_environment": True}),
            changed_by=set_by,
            reason="Account set as default for environment"
        )
        
        logger.info(f"MT5 account set as default for {account.environment_type.value}: {account_id}")
        return updated_account
    
    async def get_account(self, account_id: UUID) -> Optional[MT5Account]:
        """
        Get account by ID.
        
        Args:
            account_id: ID of account
            
        Returns:
            MT5Account if found, None otherwise
        """
        return await self._account_repository.get_by_id(account_id)
    
    async def get_all_accounts(self) -> List[MT5Account]:
        """
        Get all MT5 accounts.
        
        Returns:
            List of all accounts
        """
        return await self._account_repository.get_all()
    
    async def get_accounts_by_environment(
        self,
        environment: EnvironmentType,
        enabled_only: bool = False
    ) -> List[MT5Account]:
        """
        Get accounts by environment type.
        
        Args:
            environment: Environment type
            enabled_only: If True, only return enabled accounts
            
        Returns:
            List of accounts in the environment
        """
        return await self._account_repository.get_by_environment(environment, enabled_only)
    
    async def get_operational_accounts(self) -> List[MT5Account]:
        """
        Get all operational accounts (enabled, available, active).
        
        Returns:
            List of operational accounts
        """
        return await self._account_repository.get_operational_accounts()
    
    async def get_default_account_for_environment(
        self,
        environment: EnvironmentType
    ) -> Optional[MT5Account]:
        """
        Get default account for an environment.
        
        Args:
            environment: Environment type
            
        Returns:
            Default account if set, None otherwise
        """
        return await self._account_repository.get_default_for_environment(environment)
    
    async def _audit_account(
        self,
        account_id: UUID,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> MT5AccountAuditLog:
        """
        Create an audit log entry.
        
        Args:
            account_id: Account ID
            action: Action performed
            old_value: Old value(s) as JSON
            new_value: New value(s) as JSON
            changed_by: User or system that made the change
            reason: Reason for the change
            
        Returns:
            Created audit log
        """
        audit_log = MT5AccountAuditLog(
            account_id=account_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )
        return await self._account_repository.log_audit(audit_log)
