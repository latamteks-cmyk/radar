"""
Asset Catalog Repository implementation using SQLAlchemy.
Infrastructure layer - implements IAssetCatalogRepository interface.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.domain.entities.asset_sync_log import AssetSyncLog
from src.domain.entities.asset_audit_log import AssetAuditLog
from src.domain.interfaces.i_asset_catalog_repository import IAssetCatalogRepository
from src.infrastructure.persistence.models.asset_model import (
    AssetModel,
    AssetSyncLogModel,
    AssetAuditLogModel,
    AvailabilityStatusEnum,
    AssetTypeEnum,
)

logger = logging.getLogger(__name__)


class AssetCatalogRepository(IAssetCatalogRepository):
    """
    SQLAlchemy implementation of Asset Catalog repository.
    
    Handles persistence and retrieval of assets with full audit support.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db_session: Async SQLAlchemy session
        """
        self._db_session = db_session
    
    def _to_entity(self, model: AssetModel) -> Asset:
        """Convert SQLAlchemy model to domain entity"""
        return Asset(
            id=model.id,
            symbol=model.symbol,
            display_name=model.display_name,
            asset_type=AssetType(model.asset_type.value),
            availability_status=AvailabilityStatus(model.availability_status.value),
            is_enabled=model.is_enabled,
            source=model.source,
            first_seen_at=model.first_seen_at,
            last_seen_at=model.last_seen_at,
            updated_at=model.updated_at,
        )
    
    def _to_model(self, entity: Asset) -> AssetModel:
        """Convert domain entity to SQLAlchemy model"""
        return AssetModel(
            id=entity.id,
            symbol=entity.symbol,
            display_name=entity.display_name,
            asset_type=AssetTypeEnum(entity.asset_type.value),
            availability_status=AvailabilityStatusEnum(entity.availability_status.value),
            is_enabled=entity.is_enabled,
            source=entity.source,
            first_seen_at=entity.first_seen_at,
            last_seen_at=entity.last_seen_at,
            updated_at=entity.updated_at,
        )
    
    async def create(self, asset: Asset) -> Asset:
        """Create a new asset"""
        model = self._to_model(asset)
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        logger.info(f"Created asset: {model.symbol}")
        return self._to_entity(model)
    
    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """Get asset by ID"""
        stmt = select(AssetModel).where(AssetModel.id == asset_id)
        result = await self._db_session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_entity(model)
        return None
    
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol"""
        stmt = select(AssetModel).where(AssetModel.symbol == symbol)
        result = await self._db_session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_entity(model)
        return None
    
    async def get_all(self) -> List[Asset]:
        """Get all assets"""
        stmt = select(AssetModel).order_by(AssetModel.symbol)
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_by_type(
        self,
        asset_type: AssetType,
        enabled_only: bool = False
    ) -> List[Asset]:
        """Get assets by type"""
        stmt = select(AssetModel).where(
            AssetModel.asset_type == AssetTypeEnum(asset_type.value)
        )
        
        if enabled_only:
            stmt = stmt.where(AssetModel.is_enabled == True)
        
        stmt = stmt.order_by(AssetModel.symbol)
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_operational_assets(self) -> List[Asset]:
        """Get all assets that are operational"""
        stmt = select(AssetModel).where(
            and_(
                AssetModel.is_enabled == True,
                AssetModel.availability_status == AvailabilityStatusEnum.DISPONIBLE,
            )
        ).order_by(AssetModel.symbol)
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_grouped_by_type(self) -> Dict[AssetType, List[Asset]]:
        """Get all assets grouped by type"""
        stmt = select(AssetModel).order_by(AssetModel.asset_type, AssetModel.symbol)
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        grouped: Dict[AssetType, List[Asset]] = {}
        for model in models:
            asset_type = AssetType(model.asset_type.value)
            if asset_type not in grouped:
                grouped[asset_type] = []
            grouped[asset_type].append(self._to_entity(model))
        
        return grouped
    
    async def update(self, asset: Asset) -> Asset:
        """Update an existing asset"""
        asset.updated_at = datetime.utcnow()
        
        stmt = (
            update(AssetModel)
            .where(AssetModel.id == asset.id)
            .values(
                symbol=asset.symbol,
                display_name=asset.display_name,
                asset_type=AssetTypeEnum(asset.asset_type.value),
                availability_status=AvailabilityStatusEnum(asset.availability_status.value),
                is_enabled=asset.is_enabled,
                source=asset.source,
                first_seen_at=asset.first_seen_at,
                last_seen_at=asset.last_seen_at,
                updated_at=asset.updated_at,
            )
        )
        
        await self._db_session.execute(stmt)
        await self._db_session.flush()
        
        logger.info(f"Updated asset: {asset.symbol}")
        return asset
    
    async def get_or_create_by_symbol(self, symbol: str) -> Asset:
        """Get asset by symbol or create if not exists"""
        asset = await self.get_by_symbol(symbol)
        if asset:
            return asset
        
        # Create new asset with minimal info
        new_asset = Asset(
            symbol=symbol,
            display_name=symbol,
            asset_type=AssetType.UNKNOWN,
        )
        return await self.create(new_asset)
    
    async def get_sync_logs(
        self,
        limit: int = 50
    ) -> List[AssetSyncLog]:
        """Get recent synchronization logs"""
        stmt = (
            select(AssetSyncLogModel)
            .order_by(AssetSyncLogModel.sync_started_at.desc())
            .limit(limit)
        )
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [
            AssetSyncLog(
                id=model.id,
                status=model.status,
                sync_started_at=model.sync_started_at,
                sync_finished_at=model.sync_finished_at,
                inserted_count=model.inserted_count,
                updated_count=model.updated_count,
                unavailable_count=model.unavailable_count,
                error_message=model.error_message,
            )
            for model in models
        ]
    
    async def log_sync(self, sync_log: AssetSyncLog) -> AssetSyncLog:
        """Create a sync log entry"""
        model = AssetSyncLogModel(
            status=sync_log.status,
            sync_started_at=sync_log.sync_started_at,
            sync_finished_at=sync_log.sync_finished_at,
            inserted_count=sync_log.inserted_count,
            updated_count=sync_log.updated_count,
            unavailable_count=sync_log.unavailable_count,
            error_message=sync_log.error_message,
        )
        
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        return AssetSyncLog(
            id=model.id,
            status=model.status,
            sync_started_at=model.sync_started_at,
            sync_finished_at=model.sync_finished_at,
            inserted_count=model.inserted_count,
            updated_count=model.updated_count,
            unavailable_count=model.unavailable_count,
            error_message=model.error_message,
        )
    
    async def get_audit_logs(
        self,
        asset_id: UUID,
        limit: int = 100
    ) -> List[AssetAuditLog]:
        """Get audit logs for an asset"""
        stmt = (
            select(AssetAuditLogModel)
            .where(AssetAuditLogModel.asset_id == asset_id)
            .order_by(AssetAuditLogModel.changed_at.desc())
            .limit(limit)
        )
        
        result = await self._db_session.execute(stmt)
        models = result.scalars().all()
        
        return [
            AssetAuditLog(
                id=model.id,
                asset_id=model.asset_id,
                action=model.action,
                old_value=model.old_value,
                new_value=model.new_value,
                changed_by=model.changed_by,
                changed_at=model.changed_at,
                reason=model.reason,
            )
            for model in models
        ]
    
    async def log_audit(self, audit_log: AssetAuditLog) -> AssetAuditLog:
        """Create an audit log entry"""
        model = AssetAuditLogModel(
            asset_id=audit_log.asset_id,
            action=audit_log.action,
            old_value=audit_log.old_value,
            new_value=audit_log.new_value,
            changed_by=audit_log.changed_by,
            reason=audit_log.reason,
        )
        
        self._db_session.add(model)
        await self._db_session.flush()
        await self._db_session.refresh(model)
        
        return AssetAuditLog(
            id=model.id,
            asset_id=model.asset_id,
            action=model.action,
            old_value=model.old_value,
            new_value=model.new_value,
            changed_by=model.changed_by,
            changed_at=model.changed_at,
            reason=model.reason,
        )
