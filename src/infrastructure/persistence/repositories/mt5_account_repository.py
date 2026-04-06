"""
MT5 Account Repository implementation using SQLAlchemy.
Infrastructure layer - implements IMT5AccountRepository interface.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.mt5_account import MT5Account, EnvironmentType, AvailabilityStatus, LifecycleStatus, ValidationStatus
from src.domain.entities.mt5_account_audit_log import MT5AccountAuditLog
from src.domain.entities.mt5_account_validation_log import MT5AccountValidationLog
from src.domain.interfaces.i_mt5_account_repository import IMT5AccountRepository
from src.infrastructure.persistence.models.mt5_account_model import (
    MT5AccountModel,
    MT5AccountAuditLogModel,
    MT5AccountValidationLogModel,
    EnvironmentTypeEnum,
    AvailabilityStatusEnum,
    LifecycleStatusEnum,
    ValidationStatusEnum,
)

logger = logging.getLogger(__name__)


class MT5AccountRepository(IMT5AccountRepository):
    """
    SQLAlchemy implementation of MT5Account repository.
    
    Handles persistence and retrieval of MT5 accounts with full audit support.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db_session: Async SQLAlchemy session
        """
        self._db_session = db_session
    
    def _to_entity(self, model: MT5AccountModel) -> MT5Account:
        """Convert SQLAlchemy model to domain entity"""
        return MT5Account(
            id=model.id,
            account_name=model.account_name,
            broker_name=model.broker_name,
            server_name=model.server_name,
            login=model.login,
            password_secret_ref=model.password_secret_ref,
            terminal_path=model.terminal_path,
            environment_type=EnvironmentType(model.environment_type.value),
            is_enabled=model.is_enabled,
            availability_status=AvailabilityStatus(model.availability_status.value),
            lifecycle_status=LifecycleStatus(model.lifecycle_status.value),
            is_default_for_environment=model.is_default_for_environment,
            last_validation_at=model.last_validation_at,
            last_validation_status=ValidationStatus(model.last_validation_status.value) if model.last_validation_status else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )
    
    def _to_model(self, entity: MT5Account) -> MT5AccountModel:
        """Convert domain entity to SQLAlchemy model"""
        return MT5AccountModel(
            id=entity.id,
            account_name=entity.account_name,
            broker_name=entity.broker_name,
            server_name=entity.server_name,
            login=entity.login,
            password_secret_ref=entity.password_secret_ref,
            terminal_path=entity.terminal_path,
            environment_type=EnvironmentTypeEnum(entity.environment_type.value),
            is_enabled=entity.is_enabled,
            availability_status=AvailabilityStatusEnum(entity.availability_status.value),
            lifecycle_status=LifecycleStatusEnum(entity.lifecycle_status.value),
            is_default_for_environment=entity.is_default_for_environment,
            last_validation_at=entity.last_validation_at,
            last_validation_status=ValidationStatusEnum(entity.last_validation_status.value) if entity.last_validation_status else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )
    
    async def create(self, account: MT5Account) -> MT5Account:
        """Create a new MT5 account"""
        model = self._to_model(account)
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        logger.info(f"Created MT5 account: {model.id}")
        return self._to_entity(model)
    
    async def get_by_id(self, account_id: UUID) -> Optional[MT5Account]:
        """Get account by ID"""
        stmt = select(MT5AccountModel).where(MT5AccountModel.id == account_id)
        result = await self._db_session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_entity(model)
        return None
    
    async def get_all(self) -> List[MT5Account]:
        """Get all MT5 accounts"""
        stmt = select(MT5AccountModel).order_by(MT5AccountModel.created_at.desc())
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_by_environment(
        self,
        environment: EnvironmentType,
        enabled_only: bool = False
    ) -> List[MT5Account]:
        """Get accounts by environment type"""
        stmt = select(MT5AccountModel).where(
            MT5AccountModel.environment_type == EnvironmentTypeEnum(environment.value)
        )
        
        if enabled_only:
            stmt = stmt.where(MT5AccountModel.is_enabled == True)
            stmt = stmt.where(MT5AccountModel.lifecycle_status == LifecycleStatusEnum.ACTIVE)
        
        stmt = stmt.order_by(MT5AccountModel.account_name)
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_default_for_environment(
        self,
        environment: EnvironmentType
    ) -> Optional[MT5Account]:
        """Get the default account for an environment"""
        stmt = select(MT5AccountModel).where(
            and_(
                MT5AccountModel.environment_type == EnvironmentTypeEnum(environment.value),
                MT5AccountModel.is_default_for_environment == True,
                MT5AccountModel.lifecycle_status == LifecycleStatusEnum.ACTIVE,
            )
        )
        result = await self._db_session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_entity(model)
        return None
    
    async def get_operational_accounts(self) -> List[MT5Account]:
        """Get all accounts that are operational"""
        stmt = select(MT5AccountModel).where(
            and_(
                MT5AccountModel.is_enabled == True,
                MT5AccountModel.availability_status == AvailabilityStatusEnum.AVAILABLE,
                MT5AccountModel.lifecycle_status == LifecycleStatusEnum.ACTIVE,
            )
        ).order_by(MT5AccountModel.account_name)
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def update(self, account: MT5Account) -> MT5Account:
        """Update an existing MT5 account"""
        account.updated_at = datetime.utcnow()
        
        stmt = (
            update(MT5AccountModel)
            .where(MT5AccountModel.id == account.id)
            .values(
                account_name=account.account_name,
                broker_name=account.broker_name,
                server_name=account.server_name,
                login=account.login,
                password_secret_ref=account.password_secret_ref,
                terminal_path=account.terminal_path,
                environment_type=EnvironmentTypeEnum(account.environment_type.value),
                is_enabled=account.is_enabled,
                availability_status=AvailabilityStatusEnum(account.availability_status.value),
                lifecycle_status=LifecycleStatusEnum(account.lifecycle_status.value),
                is_default_for_environment=account.is_default_for_environment,
                last_validation_at=account.last_validation_at,
                last_validation_status=ValidationStatusEnum(account.last_validation_status.value) if account.last_validation_status else None,
                updated_at=account.updated_at,
                archived_at=account.archived_at,
            )
        )
        
        await self._db_session.execute(stmt)
        await self._db_session.flush()
        
        logger.info(f"Updated MT5 account: {account.id}")
        return account
    
    async def delete(self, account_id: UUID) -> bool:
        """Soft delete (archive) an MT5 account"""
        account = await self.get_by_id(account_id)
        if not account:
            return False
        
        account.archive()
        await self.update(account)
        
        logger.info(f"Archived MT5 account: {account_id}")
        return True
    
    async def get_audit_logs(
        self,
        account_id: UUID,
        limit: int = 100
    ) -> List[MT5AccountAuditLog]:
        """Get audit logs for an account"""
        stmt = (
            select(MT5AccountAuditLogModel)
            .where(MT5AccountAuditLogModel.account_id == account_id)
            .order_by(MT5AccountAuditLogModel.changed_at.desc())
            .limit(limit)
        )
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [
            MT5AccountAuditLog(
                id=model.id,
                account_id=model.account_id,
                action=model.action,
                old_value=model.old_value,
                new_value=model.new_value,
                changed_by=model.changed_by,
                changed_at=model.changed_at,
                reason=model.reason,
            )
            for model in models
        ]
    
    async def log_audit(self, audit_log: MT5AccountAuditLog) -> MT5AccountAuditLog:
        """Create an audit log entry"""
        model = MT5AccountAuditLogModel(
            account_id=audit_log.account_id,
            action=audit_log.action,
            old_value=audit_log.old_value,
            new_value=audit_log.new_value,
            changed_by=audit_log.changed_by,
            reason=audit_log.reason,
        )
        
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        return MT5AccountAuditLog(
            id=model.id,
            account_id=model.account_id,
            action=model.action,
            old_value=model.old_value,
            new_value=model.new_value,
            changed_by=model.changed_by,
            changed_at=model.changed_at,
            reason=model.reason,
        )
    
    async def log_validation(
        self,
        validation_log: MT5AccountValidationLog
    ) -> MT5AccountValidationLog:
        """Create a validation log entry"""
        model = MT5AccountValidationLogModel(
            account_id=validation_log.account_id,
            validation_started_at=validation_log.validation_started_at,
            validation_finished_at=validation_log.validation_finished_at,
            status=validation_log.status,
            error_message=validation_log.error_message,
            broker_response_summary=validation_log.broker_response_summary,
        )
        
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        return MT5AccountValidationLog(
            id=model.id,
            account_id=model.account_id,
            validation_started_at=model.validation_started_at,
            validation_finished_at=model.validation_finished_at,
            status=model.status,
            error_message=model.error_message,
            broker_response_summary=model.broker_response_summary,
        )
    
    async def get_validation_logs(
        self,
        account_id: UUID,
        limit: int = 50
    ) -> List[MT5AccountValidationLog]:
        """Get validation logs for an account"""
        stmt = (
            select(MT5AccountValidationLogModel)
            .where(MT5AccountValidationLogModel.account_id == account_id)
            .order_by(MT5AccountValidationLogModel.validation_started_at.desc())
            .limit(limit)
        )
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [
            MT5AccountValidationLog(
                id=model.id,
                account_id=model.account_id,
                validation_started_at=model.validation_started_at,
                validation_finished_at=model.validation_finished_at,
                status=model.status,
                error_message=model.error_message,
                broker_response_summary=model.broker_response_summary,
            )
            for model in models
        ]
