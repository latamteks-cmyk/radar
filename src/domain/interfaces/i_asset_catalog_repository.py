"""
Asset Catalog Repository interface.
Part of the domain layer - defines contract for infrastructure implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from uuid import UUID

from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.domain.entities.asset_sync_log import AssetSyncLog
from src.domain.entities.asset_audit_log import AssetAuditLog


class IAssetCatalogRepository(ABC):
    """
    Repository interface for Asset Catalog management.
    
    Defines the contract for persisting and retrieving assets.
    Infrastructure layer (PostgreSQL) will implement this interface.
    """
    
    @abstractmethod
    async def create(self, asset: Asset) -> Asset:
        """
        Create a new asset.
        
        Args:
            asset: Asset entity to create
            
        Returns:
            Created Asset with ID populated
        """
        ...
    
    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """
        Get asset by ID.
        
        Args:
            asset_id: Unique identifier of the asset
            
        Returns:
            Asset if found, None otherwise
        """
        ...
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """
        Get asset by symbol.
        
        Args:
            symbol: Symbol string
            
        Returns:
            Asset if found, None otherwise
        """
        ...
    
    @abstractmethod
    async def get_all(self) -> List[Asset]:
        """
        Get all assets.
        
        Returns:
            List of all assets
        """
        ...
    
    @abstractmethod
    async def get_by_type(
        self,
        asset_type: AssetType,
        enabled_only: bool = False
    ) -> List[Asset]:
        """
        Get assets by type.
        
        Args:
            asset_type: Asset type to filter by
            enabled_only: If True, only return enabled assets
            
        Returns:
            List of assets of the specified type
        """
        ...
    
    @abstractmethod
    async def get_operational_assets(self) -> List[Asset]:
        """
        Get all assets that are operational (available and enabled).
        
        Returns:
            List of operational assets
        """
        ...
    
    @abstractmethod
    async def get_grouped_by_type(self) -> Dict[AssetType, List[Asset]]:
        """
        Get all assets grouped by type.
        
        Returns:
            Dictionary mapping asset types to lists of assets
        """
        ...
    
    @abstractmethod
    async def update(self, asset: Asset) -> Asset:
        """
        Update an existing asset.
        
        Args:
            asset: Asset entity with updates
            
        Returns:
            Updated Asset
        """
        ...
    
    @abstractmethod
    async def get_or_create_by_symbol(self, symbol: str) -> Asset:
        """
        Get asset by symbol or create if not exists.
        
        Args:
            symbol: Symbol string
            
        Returns:
            Existing or newly created Asset
        """
        ...
    
    @abstractmethod
    async def get_sync_logs(
        self,
        limit: int = 50
    ) -> List[AssetSyncLog]:
        """
        Get recent synchronization logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of sync logs, most recent first
        """
        ...
    
    @abstractmethod
    async def log_sync(self, sync_log: AssetSyncLog) -> AssetSyncLog:
        """
        Create a sync log entry.
        
        Args:
            sync_log: Sync log to persist
            
        Returns:
            Persisted sync log
        """
        ...
    
    @abstractmethod
    async def get_audit_logs(
        self,
        asset_id: UUID,
        limit: int = 100
    ) -> List[AssetAuditLog]:
        """
        Get audit logs for an asset.
        
        Args:
            asset_id: Asset ID
            limit: Maximum number of logs to return
            
        Returns:
            List of audit logs, most recent first
        """
        ...
    
    @abstractmethod
    async def log_audit(self, audit_log: AssetAuditLog) -> AssetAuditLog:
        """
        Create an audit log entry.
        
        Args:
            audit_log: Audit log to persist
            
        Returns:
            Persisted audit log
        """
        ...
