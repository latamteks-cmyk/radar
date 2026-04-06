"""
MT5 Account API routes.
Presentation layer - HTTP endpoints for account management.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.configuration.services.mt5_account_service import MT5AccountService
from src.domain.entities.mt5_account import EnvironmentType
from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.repositories.mt5_account_repository import MT5AccountRepository
from src.presentation.api.schemas.mt5_account_schema import (
    MT5AccountCreateRequest,
    MT5AccountResponse,
    MT5AccountUpdateRequest,
    MT5AccountValidationRequest,
    MT5AccountAuditLogResponse,
    MT5AccountValidationLogResponse,
    MT5AccountListResponse,
    MessageResponse,
    AvailabilityStatus,
    LifecycleStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mt5-accounts", tags=["MT5 Accounts"])


def get_mt5_account_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> MT5AccountService:
    """Dependency to get MT5 account service"""
    from src.infrastructure.mt5.adapter.mt5_gateway import MT5Gateway
    
    repository = MT5AccountRepository(db_session)
    gateway = MT5Gateway()
    return MT5AccountService(repository, gateway)


def mask_login(login: str) -> str:
    """Mask login for display (show first 2 and last 2 characters)"""
    if len(login) <= 4:
        return "*" * len(login)
    return login[:2] + "*" * (len(login) - 4) + login[-2:]


def account_to_response(account) -> MT5AccountResponse:
    """Convert domain account to API response with masked login"""
    response_data = {
        "id": account.id,
        "account_name": account.account_name,
        "broker_name": account.broker_name,
        "server_name": account.server_name,
        "login": mask_login(account.login),  # Mask sensitive data
        "terminal_path": account.terminal_path,
        "environment_type": account.environment_type.value,
        "is_enabled": account.is_enabled,
        "availability_status": account.availability_status.value,
        "lifecycle_status": account.lifecycle_status.value,
        "is_default_for_environment": account.is_default_for_environment,
        "last_validation_at": account.last_validation_at,
        "last_validation_status": account.last_validation_status.value if account.last_validation_status else None,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
        "archived_at": account.archived_at,
    }
    return MT5AccountResponse(**response_data)


@router.get("/", response_model=MT5AccountListResponse)
async def list_accounts(
    environment: Optional[EnvironmentType] = Query(None, description="Filter by environment"),
    enabled_only: bool = Query(False, description="Show only enabled accounts"),
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    List all MT5 accounts with optional filtering.
    """
    try:
        if environment:
            accounts = await service.get_accounts_by_environment(environment, enabled_only)
        else:
            accounts = await service.get_all_accounts()
        
        return MT5AccountListResponse(
            accounts=[account_to_response(acc) for acc in accounts],
            total=len(accounts)
        )
    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operational", response_model=List[MT5AccountResponse])
async def list_operational_accounts(
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    List all operational accounts (enabled, available, active).
    """
    try:
        accounts = await service.get_operational_accounts()
        return [account_to_response(acc) for acc in accounts]
    except Exception as e:
        logger.error(f"Error listing operational accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=MT5AccountResponse)
async def get_account(
    account_id: UUID,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Get MT5 account by ID.
    """
    try:
        account = await service.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account_to_response(account)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=MT5AccountResponse, status_code=201)
async def create_account(
    request: MT5AccountCreateRequest,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Create a new MT5 account.
    
    The account will be created with:
    - lifecycle_status: ACTIVE
    - availability_status: UNKNOWN
    - is_enabled: false
    
    After creation, you should validate the connection before enabling.
    """
    try:
        # In production, encrypt password and store reference
        # For now, we'll store as-is (NOT SECURE - just for demo)
        password_secret_ref = request.password  # TODO: Encrypt this!
        
        account = await service.create_account(
            account_name=request.account_name,
            broker_name=request.broker_name,
            server_name=request.server_name,
            login=request.login,
            password_secret_ref=password_secret_ref,
            terminal_path=request.terminal_path,
            environment_type=EnvironmentType(request.environment_type.value),
            created_by="api_user"  # TODO: Get from auth context
        )
        
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/validate", response_model=MT5AccountResponse)
async def validate_account(
    account_id: UUID,
    request: MT5AccountValidationRequest,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Validate account connection to MT5.
    
    Tests the credentials and updates availability status.
    """
    try:
        account = await service.validate_account(
            account_id=account_id,
            password=request.password,
            validated_by="api_user"  # TODO: Get from auth context
        )
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/enable", response_model=MT5AccountResponse)
async def enable_account(
    account_id: UUID,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Enable account for operational use.
    
    Account must be validated (availability_status=AVAILABLE) before enabling.
    """
    try:
        account = await service.enable_account(
            account_id=account_id,
            enabled_by="api_user"  # TODO: Get from auth context
        )
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=400 if "cannot be enabled" in str(e).lower() else 404, detail=str(e))
    except Exception as e:
        logger.error(f"Error enabling account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/disable", response_model=MT5AccountResponse)
async def disable_account(
    account_id: UUID,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Disable account for operational use.
    """
    try:
        account = await service.disable_account(
            account_id=account_id,
            disabled_by="api_user"  # TODO: Get from auth context
        )
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error disabling account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/archive", response_model=MessageResponse)
async def archive_account(
    account_id: UUID,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Archive account (soft delete).
    
    Archived accounts cannot be used for operations but remain
    in the database for audit and historical purposes.
    """
    try:
        await service.archive_account(
            account_id=account_id,
            archived_by="api_user"  # TODO: Get from auth context
        )
        return MessageResponse(
            message=f"Account {account_id} archived successfully",
            success=True
        )
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error archiving account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/set-default", response_model=MT5AccountResponse)
async def set_default_for_environment(
    account_id: UUID,
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Set account as default for its environment.
    
    This will unset any other default account for the same environment.
    """
    try:
        account = await service.set_default_for_environment(
            account_id=account_id,
            set_by="api_user"  # TODO: Get from auth context
        )
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting default account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}/audit-logs", response_model=List[MT5AccountAuditLogResponse])
async def get_account_audit_logs(
    account_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Get audit logs for an account.
    """
    try:
        account = await service.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        logs = await service._account_repository.get_audit_logs(account_id, limit)
        return [
            MT5AccountAuditLogResponse(
                id=log.id,
                account_id=log.account_id,
                action=log.action,
                old_value=log.old_value,
                new_value=log.new_value,
                changed_by=log.changed_by,
                changed_at=log.changed_at,
                reason=log.reason,
            )
            for log in logs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}/validation-logs", response_model=List[MT5AccountValidationLogResponse])
async def get_account_validation_logs(
    account_id: UUID,
    limit: int = Query(50, ge=1, le=500, description="Maximum number of logs to return"),
    service: MT5AccountService = Depends(get_mt5_account_service)
):
    """
    Get validation logs for an account.
    """
    try:
        account = await service.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        logs = await service._account_repository.get_validation_logs(account_id, limit)
        return [
            MT5AccountValidationLogResponse(
                id=log.id,
                account_id=log.account_id,
                validation_started_at=log.validation_started_at,
                validation_finished_at=log.validation_finished_at,
                status=log.status,
                error_message=log.error_message,
                broker_response_summary=log.broker_response_summary,
            )
            for log in logs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting validation logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
