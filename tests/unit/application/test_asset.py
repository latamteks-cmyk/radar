"""
Unit tests for Asset domain entities.
Tests business logic, state transitions, and validation.
"""

import pytest
from datetime import datetime
from uuid import UUID

from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus


class TestAssetCreation:
    """Test Asset entity creation and validation"""
    
    def test_create_asset_with_valid_data(self):
        """Test creating asset with valid data"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        assert asset.symbol == "EURUSD"
        assert asset.display_name == "Euro vs US Dollar"
        assert asset.asset_type == AssetType.FOREX_MAJOR
        assert asset.is_enabled is False
        assert asset.availability_status == AvailabilityStatus.DISPONIBLE
        assert isinstance(asset.id, UUID)
        assert isinstance(asset.first_seen_at, datetime)
        assert isinstance(asset.updated_at, datetime)
    
    def test_create_asset_empty_symbol_fails(self):
        """Test that empty symbol raises error"""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            Asset(
                symbol="",
                display_name="Euro vs US Dollar",
                asset_type=AssetType.FOREX_MAJOR,
            )
    
    def test_create_asset_empty_display_name_fails(self):
        """Test that empty display name raises error"""
        with pytest.raises(ValueError, match="Display name cannot be empty"):
            Asset(
                symbol="EURUSD",
                display_name="",
                asset_type=AssetType.FOREX_MAJOR,
            )


class TestAssetAvailability:
    """Test Asset availability state transitions"""
    
    def test_mark_available(self):
        """Test marking asset as available"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.mark_available()
        
        assert asset.availability_status == AvailabilityStatus.DISPONIBLE
        assert asset.last_seen_at is not None
    
    def test_mark_unavailable(self):
        """Test marking asset as unavailable"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.mark_unavailable()
        
        assert asset.availability_status == AvailabilityStatus.NO_DISPONIBLE


class TestAssetEnablement:
    """Test Asset enable/disable functionality"""
    
    def test_enable_asset_success(self):
        """Test enabling available asset"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        result = asset.enable()
        
        assert result is True
        assert asset.is_enabled is True
    
    def test_enable_unavailable_asset_fails(self):
        """Test enabling unavailable asset fails"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.mark_unavailable()
        result = asset.enable()
        
        assert result is False
        assert asset.is_enabled is False
    
    def test_disable_asset(self):
        """Test disabling asset"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.enable()
        asset.disable()
        
        assert asset.is_enabled is False


class TestAssetOperational:
    """Test Asset operational status checks"""
    
    def test_is_operational_true(self):
        """Test asset is operational when available and enabled"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.enable()
        
        assert asset.is_operational() is True
    
    def test_is_operational_false_when_disabled(self):
        """Test asset is not operational when disabled"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        assert asset.is_operational() is False
    
    def test_is_operational_false_when_unavailable(self):
        """Test asset is not operational when unavailable"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.mark_unavailable()
        
        assert asset.is_operational() is False


class TestAssetClassification:
    """Test Asset classification updates"""
    
    def test_update_classification(self):
        """Test updating asset type"""
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        asset.update_classification(AssetType.FOREX_MINOR)
        
        assert asset.asset_type == AssetType.FOREX_MINOR
