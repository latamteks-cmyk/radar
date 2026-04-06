"""
Asset Catalog / Watchlist API routes.
Presentation layer - HTTP endpoints for watchlist management.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.asset_catalog.services.asset_catalog_service import AssetCatalogService
from src.domain.entities.asset import AssetType
from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.repositories.asset_catalog_repository import AssetCatalogRepository
from src.infrastructure.mt5.adapter.mt5_gateway import MT5Gateway
from src.presentation.api.schemas.asset_schema import (
    AssetResponse,
    AssetSyncLogResponse,
    AssetAuditLogResponse,
    WatchlistResponse,
    WatchlistSyncResponse,
    MessageResponse,
    AvailabilityStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])


def get_asset_catalog_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> AssetCatalogService:
    """Dependency to get asset catalog service"""
    repository = AssetCatalogRepository(db_session)
    gateway = MT5Gateway()
    return AssetCatalogService(repository, gateway)


def asset_to_response(asset) -> AssetResponse:
    """Convert domain asset to API response"""
    return AssetResponse(
        id=asset.id,
        symbol=asset.symbol,
        display_name=asset.display_name,
        asset_type=asset.asset_type.value,
        availability_status=asset.availability_status.value,
        is_enabled=asset.is_enabled,
        source=asset.source,
        first_seen_at=asset.first_seen_at,
        last_seen_at=asset.last_seen_at,
        updated_at=asset.updated_at,
    )


@router.get("/", response_model=WatchlistResponse)
async def get_watchlist(
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    enabled_only: bool = Query(False, description="Show only enabled assets"),
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Get watchlist with optional filtering.
    
    Returns assets grouped by type.
    """
    try:
        if asset_type or enabled_only:
            assets = await service.load_watchlist(asset_type, enabled_only)
            # Group manually
            grouped = {}
            for asset in assets:
                type_key = asset.asset_type.value
                if type_key not in grouped:
                    grouped[type_key] = []
                grouped[type_key].append(asset)
        else:
            grouped = await service.load_watchlist_grouped()
        
        # Convert to response format
        grouped_response = {
            type_key: [asset_to_response(a) for a in assets]
            for type_key, assets in grouped.items()
        }
        
        total = sum(len(assets) for assets in grouped.values())
        
        return WatchlistResponse(
            assets=grouped_response,
            total=total
        )
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operational", response_model=List[AssetResponse])
async def get_operational_assets(
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Get all operational assets (available and enabled).
    """
    try:
        assets = await service.get_operational_assets()
        return [asset_to_response(a) for a in assets]
    except Exception as e:
        logger.error(f"Error getting operational assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=WatchlistSyncResponse)
async def sync_watchlist(
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Synchronize watchlist with MT5.
    
    Performs incremental sync:
    - Inserts new symbols
    - Updates existing symbols
    - Marks absent symbols as unavailable
    """
    try:
        sync_log = await service.synchronize_with_mt5(synced_by="api_user")
        
        return WatchlistSyncResponse(
            sync_id=sync_log.id,
            status=sync_log.status,
            inserted_count=sync_log.inserted_count,
            updated_count=sync_log.updated_count,
            unavailable_count=sync_log.unavailable_count,
            sync_started_at=sync_log.sync_started_at,
            sync_finished_at=sync_log.sync_finished_at,
            error_message=sync_log.error_message
        )
    except Exception as e:
        logger.error(f"Error syncing watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Get asset by ID.
    """
    try:
        asset = await service.get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset_to_response(asset)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/enable", response_model=AssetResponse)
async def enable_asset(
    asset_id: UUID,
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Enable asset for radar monitoring.
    
    Asset must be available (DISPONIBLE) before enabling.
    """
    try:
        asset = await service.enable_asset(
            asset_id=asset_id,
            enabled_by="api_user"
        )
        return asset_to_response(asset)
    except ValueError as e:
        raise HTTPException(status_code=400 if "cannot be enabled" in str(e).lower() else 404, detail=str(e))
    except Exception as e:
        logger.error(f"Error enabling asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/disable", response_model=AssetResponse)
async def disable_asset(
    asset_id: UUID,
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Disable asset from radar monitoring.
    """
    try:
        asset = await service.disable_asset(
            asset_id=asset_id,
            disabled_by="api_user"
        )
        return asset_to_response(asset)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error disabling asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/sync", response_model=List[AssetSyncLogResponse])
async def get_sync_logs(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of logs to return"),
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Get recent synchronization logs.
    """
    try:
        logs = await service.get_sync_logs(limit)
        return [
            AssetSyncLogResponse(
                id=log.id,
                sync_started_at=log.sync_started_at,
                sync_finished_at=log.sync_finished_at,
                status=log.status,
                inserted_count=log.inserted_count,
                updated_count=log.updated_count,
                unavailable_count=log.unavailable_count,
                error_message=log.error_message
            )
            for log in logs
        ]
    except Exception as e:
        logger.error(f"Error getting sync logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/audit", response_model=List[AssetAuditLogResponse])
async def get_asset_audit_logs(
    asset_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    service: AssetCatalogService = Depends(get_asset_catalog_service)
):
    """
    Get audit logs for an asset.
    """
    try:
        asset = await service.get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Get audit logs directly from repository
        repository = AssetCatalogRepository(service._asset_repository._db_session.__class__())
        logs = await service._asset_repository.get_audit_logs(asset_id, limit)
        
        return [
            AssetAuditLogResponse(
                id=log.id,
                asset_id=log.asset_id,
                action=log.action,
                old_value=log.old_value,
                new_value=log.new_value,
                changed_by=log.changed_by,
                changed_at=log.changed_at,
                reason=log.reason
            )
            for log in logs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
