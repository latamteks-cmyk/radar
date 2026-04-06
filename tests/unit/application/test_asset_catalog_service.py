"""
Unit tests for Asset Catalog Service.
Tests application layer business logic with mocked dependencies.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.asset_catalog.services.asset_catalog_service import AssetCatalogService
from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.domain.entities.asset_sync_log import AssetSyncLog
from src.infrastructure.mt5.dto.mt5_symbol_info import MT5SymbolInfo


@pytest.fixture
def mock_repository():
    """Create mock repository"""
    repository = AsyncMock()
    return repository


@pytest.fixture
def mock_gateway():
    """Create mock gateway"""
    gateway = AsyncMock()
    return gateway


@pytest.fixture
def service(mock_repository, mock_gateway):
    """Create service with mocked dependencies"""
    return AssetCatalogService(mock_repository, mock_gateway)


@pytest.fixture
def sample_asset():
    """Create a sample asset for testing"""
    return Asset(
        id=uuid4(),
        symbol="EURUSD",
        display_name="Euro vs US Dollar",
        asset_type=AssetType.FOREX_MAJOR,
    )


class TestAssetCatalogServiceLoad:
    """Test AssetCatalogService.load_watchlist"""
    
    @pytest.mark.asyncio
    async def test_load_watchlist_all(self, service, mock_repository, sample_asset):
        """Test loading all assets"""
        # Arrange
        mock_repository.get_all = AsyncMock(return_value=[sample_asset])
        
        # Act
        result = await service.load_watchlist()
        
        # Assert
        assert len(result) == 1
        assert result[0] == sample_asset
    
    @pytest.mark.asyncio
    async def test_load_watchlist_by_type(self, service, mock_repository, sample_asset):
        """Test loading assets by type"""
        # Arrange
        mock_repository.get_by_type = AsyncMock(return_value=[sample_asset])
        
        # Act
        result = await service.load_watchlist(asset_type=AssetType.FOREX_MAJOR)
        
        # Assert
        assert len(result) == 1
        mock_repository.get_by_type.assert_called_once_with(AssetType.FOREX_MAJOR, False)


class TestAssetCatalogServiceSync:
    """Test AssetCatalogService.synchronize_with_mt5"""
    
    @pytest.mark.asyncio
    async def test_sync_insert_new_asset(self, service, mock_repository, mock_gateway):
        """Test synchronization inserts new asset"""
        # Arrange
        symbol_info = MT5SymbolInfo(
            symbol="EURUSD",
            description="Euro vs US Dollar",
            path="Forex\\EURUSD",
            digits=5,
            trade_mode=0,
            trade_contract_size=100000,
            currency_base="EUR",
            currency_profit="USD",
        )
        
        mock_gateway.get_available_symbols = AsyncMock(return_value=[symbol_info])
        mock_repository.get_all = AsyncMock(return_value=[])
        mock_repository.create = AsyncMock(return_value=Asset(
            id=uuid4(),
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        ))
        mock_repository.log_sync = AsyncMock()
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.synchronize_with_mt5(synced_by="test_user")
        
        # Assert
        assert result.status == "SUCCESS"
        assert result.inserted_count == 1
        mock_repository.create.assert_called_once()
        mock_repository.log_audit.assert_called()
    
    @pytest.mark.asyncio
    async def test_sync_updates_existing_asset(self, service, mock_repository, mock_gateway, sample_asset):
        """Test synchronization updates existing asset"""
        # Arrange
        symbol_info = MT5SymbolInfo(
            symbol="EURUSD",
            description="Euro vs US Dollar",
            path="Forex\\EURUSD",
            digits=5,
            trade_mode=0,
            trade_contract_size=100000,
            currency_base="EUR",
            currency_profit="USD",
        )
        
        sample_asset.mark_unavailable()  # Simulate was unavailable
        mock_gateway.get_available_symbols = AsyncMock(return_value=[symbol_info])
        mock_repository.get_all = AsyncMock(return_value=[sample_asset])
        mock_repository.update = AsyncMock(return_value=sample_asset)
        mock_repository.log_sync = AsyncMock()
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.synchronize_with_mt5(synced_by="test_user")
        
        # Assert
        assert result.status == "SUCCESS"
        assert result.updated_count == 1
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sync_marks_absent_as_unavailable(self, service, mock_repository, mock_gateway, sample_asset):
        """Test synchronization marks absent assets as unavailable"""
        # Arrange
        mock_gateway.get_available_symbols = AsyncMock(return_value=[])  # No symbols from MT5
        mock_repository.get_all = AsyncMock(return_value=[sample_asset])
        mock_repository.update = AsyncMock(return_value=sample_asset)
        mock_repository.log_sync = AsyncMock()
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.synchronize_with_mt5(synced_by="test_user")
        
        # Assert
        assert result.status == "SUCCESS"
        assert result.unavailable_count == 1
        assert sample_asset.availability_status == AvailabilityStatus.NO_DISPONIBLE
    
    @pytest.mark.asyncio
    async def test_sync_failure(self, service, mock_repository, mock_gateway):
        """Test synchronization handles failure"""
        # Arrange
        mock_gateway.get_available_symbols = AsyncMock(side_effect=Exception("MT5 error"))
        mock_repository.log_sync = AsyncMock()
        
        # Act
        result = await service.synchronize_with_mt5(synced_by="test_user")
        
        # Assert
        assert result.status == "FAILED"
        assert result.error_message is not None


class TestAssetCatalogServiceEnable:
    """Test AssetCatalogService.enable_asset"""
    
    @pytest.mark.asyncio
    async def test_enable_asset_success(self, service, mock_repository, sample_asset):
        """Test enabling asset successfully"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_asset)
        mock_repository.update = AsyncMock(return_value=sample_asset)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.enable_asset(
            asset_id=sample_asset.id,
            enabled_by="test_user"
        )
        
        # Assert
        assert result.is_enabled is True
        mock_repository.log_audit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enable_asset_not_found(self, service, mock_repository):
        """Test enabling non-existent asset raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Asset not found"):
            await service.enable_asset(asset_id=uuid4())
    
    @pytest.mark.asyncio
    async def test_enable_unavailable_asset_fails(self, service, mock_repository, sample_asset):
        """Test enabling unavailable asset raises error"""
        # Arrange
        sample_asset.mark_unavailable()
        mock_repository.get_by_id = AsyncMock(return_value=sample_asset)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Asset cannot be enabled"):
            await service.enable_asset(asset_id=sample_asset.id)


class TestAssetCatalogServiceDisable:
    """Test AssetCatalogService.disable_asset"""
    
    @pytest.mark.asyncio
    async def test_disable_asset_success(self, service, mock_repository, sample_asset):
        """Test disabling asset successfully"""
        # Arrange
        sample_asset.is_enabled = True
        mock_repository.get_by_id = AsyncMock(return_value=sample_asset)
        mock_repository.update = AsyncMock(return_value=sample_asset)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.disable_asset(
            asset_id=sample_asset.id,
            disabled_by="test_user"
        )
        
        # Assert
        assert result.is_enabled is False
    
    @pytest.mark.asyncio
    async def test_disable_asset_not_found(self, service, mock_repository):
        """Test disabling non-existent asset raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Asset not found"):
            await service.disable_asset(asset_id=uuid4())


class TestAssetCatalogServiceQueries:
    """Test AssetCatalogService query methods"""
    
    @pytest.mark.asyncio
    async def test_get_asset(self, service, mock_repository, sample_asset):
        """Test getting asset by ID"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_asset)
        
        # Act
        result = await service.get_asset(sample_asset.id)
        
        # Assert
        assert result == sample_asset
    
    @pytest.mark.asyncio
    async def test_get_operational_assets(self, service, mock_repository):
        """Test getting operational assets"""
        # Arrange
        operational_assets = []
        mock_repository.get_operational_assets = AsyncMock(return_value=operational_assets)
        
        # Act
        result = await service.get_operational_assets()
        
        # Assert
        assert result == operational_assets
    
    @pytest.mark.asyncio
    async def test_get_sync_logs(self, service, mock_repository):
        """Test getting sync logs"""
        # Arrange
        sync_logs = []
        mock_repository.get_sync_logs = AsyncMock(return_value=sync_logs)
        
        # Act
        result = await service.get_sync_logs()
        
        # Assert
        assert result == sync_logs
