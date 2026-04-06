"""
Asset Catalog Service - Application layer service for managing the Watchlist.
Implements use cases for asset discovery, synchronization, and management.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.application.asset_catalog.services.asset_classifier import CompositeAssetClassifier
from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.domain.entities.asset_audit_log import AssetAuditLog
from src.domain.entities.asset_sync_log import AssetSyncLog
from src.domain.interfaces.i_asset_catalog_repository import IAssetCatalogRepository
from src.domain.interfaces.i_mt5_gateway import IMT5Gateway

logger = logging.getLogger(__name__)


class AssetCatalogService:
    """
    Application service for Asset Catalog / Watchlist management.
    
    Implements the use cases defined in ADR-001:
    - Load watchlist
    - Synchronize with MT5
    - Enable asset
    - Disable asset
    - Query assets
    """
    
    def __init__(
        self,
        asset_repository: IAssetCatalogRepository,
        mt5_gateway: IMT5Gateway
    ):
        """
        Initialize service with dependencies.
        
        Args:
            asset_repository: Repository for asset persistence
            mt5_gateway: Gateway for MT5 symbol discovery
        """
        self._asset_repository = asset_repository
        self._mt5_gateway = mt5_gateway
        self._classifier = CompositeAssetClassifier()
    
    async def load_watchlist(
        self,
        asset_type: Optional[AssetType] = None,
        enabled_only: bool = False
    ) -> List[Asset]:
        """
        Load watchlist from local database.
        
        If asset_type is provided, filters by type.
        If enabled_only is True, only returns enabled assets.
        
        Args:
            asset_type: Optional asset type filter
            enabled_only: If True, only return enabled assets
            
        Returns:
            List of assets matching filters
        """
        logger.info("Loading watchlist from local database")
        
        if asset_type:
            assets = await self._asset_repository.get_by_type(asset_type, enabled_only)
        else:
            assets = await self._asset_repository.get_all()
        
        logger.info(f"Loaded {len(assets)} assets from watchlist")
        return assets
    
    async def load_watchlist_grouped(self) -> Dict[AssetType, List[Asset]]:
        """
        Load watchlist grouped by asset type.
        
        Returns:
            Dictionary mapping asset types to lists of assets
        """
        logger.info("Loading watchlist grouped by type")
        grouped = await self._asset_repository.get_grouped_by_type()
        logger.info(f"Loaded assets grouped into {len(grouped)} categories")
        return grouped
    
    async def synchronize_with_mt5(self, synced_by: Optional[str] = None) -> AssetSyncLog:
        """
        Synchronize local asset catalog with MT5.
        
        Performs incremental sync:
        - Inserts new symbols from MT5
        - Updates existing symbols (marks as DISPONIBLE)
        - Marks absent symbols as NO_DISPONIBLE
        
        Args:
            synced_by: User or system performing sync
            
        Returns:
            AssetSyncLog with synchronization results
        """
        logger.info("Starting watchlist synchronization with MT5")
        
        # Create sync log
        sync_log = AssetSyncLog(status="IN_PROGRESS")
        
        try:
            # Get symbols from MT5
            mt5_symbols = await self._mt5_gateway.get_available_symbols()
            mt5_symbol_set = {s.symbol for s in mt5_symbols}
            logger.info(f"Retrieved {len(mt5_symbols)} symbols from MT5")
            
            # Get local assets
            local_assets = await self._asset_repository.get_all()
            local_symbol_map = {asset.symbol: asset for asset in local_assets}
            
            inserted_count = 0
            updated_count = 0
            unavailable_count = 0
            
            # Process MT5 symbols
            for symbol_info in mt5_symbols:
                if symbol_info.symbol in local_symbol_map:
                    # Update existing asset
                    asset = local_symbol_map[symbol_info.symbol]
                    old_status = asset.availability_status
                    asset.mark_available()
                    
                    # Update classification if unknown
                    if asset.asset_type == AssetType.UNKNOWN:
                        asset_type = self._classifier.classify(symbol_info)
                        asset.update_classification(asset_type)
                    
                    await self._asset_repository.update(asset)
                    updated_count += 1
                    
                    # Audit if status changed
                    if old_status != asset.availability_status:
                        await self._audit_asset(
                            asset_id=asset.id,
                            action="SYNC_UPDATED",
                            old_value=json.dumps({"availability_status": old_status.value}),
                            new_value=json.dumps({"availability_status": asset.availability_status.value}),
                            changed_by=synced_by,
                            reason="Asset marked available during sync"
                        )
                else:
                    # Insert new asset
                    asset_type = self._classifier.classify(symbol_info)
                    asset = Asset(
                        symbol=symbol_info.symbol,
                        display_name=symbol_info.description,
                        asset_type=asset_type,
                        availability_status=AvailabilityStatus.DISPONIBLE,
                        is_enabled=False,
                        source="MT5"
                    )
                    
                    created_asset = await self._asset_repository.create(asset)
                    inserted_count += 1
                    
                    # Audit
                    await self._audit_asset(
                        asset_id=created_asset.id,
                        action="SYNC_INSERTED",
                        new_value=json.dumps({
                            "symbol": symbol_info.symbol,
                            "asset_type": asset_type.value,
                        }),
                        changed_by=synced_by,
                        reason="New asset discovered and inserted during sync"
                    )
            
            # Mark absent assets as unavailable
            for symbol, asset in local_symbol_map.items():
                if symbol not in mt5_symbol_set:
                    if asset.availability_status == AvailabilityStatus.DISPONIBLE:
                        old_status = asset.availability_status
                        asset.mark_unavailable()
                        await self._asset_repository.update(asset)
                        unavailable_count += 1
                        
                        # Audit
                        await self._audit_asset(
                            asset_id=asset.id,
                            action="SYNC_MARKED_UNAVAILABLE",
                            old_value=json.dumps({"availability_status": old_status.value}),
                            new_value=json.dumps({"availability_status": asset.availability_status.value}),
                            changed_by=synced_by,
                            reason="Asset no longer available in MT5"
                        )
            
            # Complete sync log
            sync_log.complete(
                status="SUCCESS",
                inserted_count=inserted_count,
                updated_count=updated_count,
                unavailable_count=unavailable_count
            )
            
            logger.info(
                f"Synchronization complete: "
                f"{inserted_count} inserted, "
                f"{updated_count} updated, "
                f"{unavailable_count} marked unavailable"
            )
            
        except Exception as e:
            error_msg = f"Synchronization failed: {e}"
            logger.error(error_msg)
            sync_log.complete(status="FAILED", error_message=error_msg)
        
        # Persist sync log
        await self._asset_repository.log_sync(sync_log)
        
        return sync_log
    
    async def enable_asset(
        self,
        asset_id: UUID,
        enabled_by: Optional[str] = None
    ) -> Asset:
        """
        Enable asset for radar monitoring.
        
        Asset must be available (DISPONIBLE) to be enabled.
        
        Args:
            asset_id: ID of asset to enable
            enabled_by: User or system enabling the asset
            
        Returns:
            Updated Asset
            
        Raises:
            ValueError: If asset is not available for enabling
        """
        logger.info(f"Enabling asset: {asset_id}")
        
        # Get asset
        asset = await self._asset_repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        # Try to enable
        success = asset.enable()
        if not success:
            raise ValueError(
                f"Asset cannot be enabled. "
                f"Availability: {asset.availability_status.value}"
            )
        
        # Update asset
        updated_asset = await self._asset_repository.update(asset)
        
        # Audit log
        await self._audit_asset(
            asset_id=asset_id,
            action="ENABLED",
            old_value=json.dumps({"is_enabled": False}),
            new_value=json.dumps({"is_enabled": True}),
            changed_by=enabled_by,
            reason="Asset enabled for radar monitoring"
        )
        
        logger.info(f"Asset enabled: {asset_id} ({asset.symbol})")
        return updated_asset
    
    async def disable_asset(
        self,
        asset_id: UUID,
        disabled_by: Optional[str] = None
    ) -> Asset:
        """
        Disable asset from radar monitoring.
        
        Args:
            asset_id: ID of asset to disable
            disabled_by: User or system disabling the asset
            
        Returns:
            Updated Asset
        """
        logger.info(f"Disabling asset: {asset_id}")
        
        # Get asset
        asset = await self._asset_repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        old_value = json.dumps({"is_enabled": asset.is_enabled})
        
        # Disable
        asset.disable()
        
        # Update asset
        updated_asset = await self._asset_repository.update(asset)
        
        # Audit log
        await self._audit_asset(
            asset_id=asset_id,
            action="DISABLED",
            old_value=old_value,
            new_value=json.dumps({"is_enabled": False}),
            changed_by=disabled_by,
            reason="Asset disabled"
        )
        
        logger.info(f"Asset disabled: {asset_id} ({asset.symbol})")
        return updated_asset
    
    async def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        """
        Get asset by ID.
        
        Args:
            asset_id: ID of asset
            
        Returns:
            Asset if found, None otherwise
        """
        return await self._asset_repository.get_by_id(asset_id)
    
    async def get_operational_assets(self) -> List[Asset]:
        """
        Get all operational assets (available and enabled).
        
        Returns:
            List of operational assets
        """
        return await self._asset_repository.get_operational_assets()
    
    async def get_sync_logs(self, limit: int = 50) -> List[AssetSyncLog]:
        """
        Get recent synchronization logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of sync logs
        """
        return await self._asset_repository.get_sync_logs(limit)
    
    async def _audit_asset(
        self,
        asset_id: UUID,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> AssetAuditLog:
        """
        Create an audit log entry.
        
        Args:
            asset_id: Asset ID
            action: Action performed
            old_value: Old value(s) as JSON
            new_value: New value(s) as JSON
            changed_by: User or system that made the change
            reason: Reason for the change
            
        Returns:
            Created audit log
        """
        audit_log = AssetAuditLog(
            asset_id=asset_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )
        return await self._asset_repository.log_audit(audit_log)
