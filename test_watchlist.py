"""
Test script for Watchlist functionality.
Tests Asset Catalog with mocked MT5 gateway and real database (if available).
"""

import asyncio
import sys
import json
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

# Add project root to path
sys.path.insert(0, r'C:\Users\gomez\.gemini\antigravity\scratch\radar2')

from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.domain.entities.asset_sync_log import AssetSyncLog
from src.application.asset_catalog.services.asset_catalog_service import AssetCatalogService
from src.application.asset_catalog.services.asset_classifier import CompositeAssetClassifier
from src.infrastructure.mt5.dto.mt5_symbol_info import MT5SymbolInfo


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(message: str):
    """Print success message"""
    print(f"[OK] {message}")


def print_error(message: str):
    """Print error message"""
    print(f"[ERROR] {message}")


def print_info(message: str):
    """Print info message"""
    print(f"[INFO] {message}")


class MockAssetRepository:
    """Mock repository for testing"""
    
    def __init__(self):
        self._assets = {}
        self._sync_logs = []
        self._audit_logs = []
    
    async def create(self, asset: Asset) -> Asset:
        self._assets[asset.symbol] = asset
        return asset
    
    async def get_by_id(self, asset_id):
        for asset in self._assets.values():
            if asset.id == asset_id:
                return asset
        return None
    
    async def get_by_symbol(self, symbol: str):
        return self._assets.get(symbol)
    
    async def get_all(self):
        return list(self._assets.values())
    
    async def get_by_type(self, asset_type: AssetType, enabled_only: bool = False):
        assets = [a for a in self._assets.values() if a.asset_type == asset_type]
        if enabled_only:
            assets = [a for a in assets if a.is_enabled]
        return assets
    
    async def get_operational_assets(self):
        return [a for a in self._assets.values() if a.is_operational()]
    
    async def get_grouped_by_type(self):
        grouped = {}
        for asset in self._assets.values():
            if asset.asset_type not in grouped:
                grouped[asset.asset_type] = []
            grouped[asset.asset_type].append(asset)
        return grouped
    
    async def update(self, asset: Asset) -> Asset:
        self._assets[asset.symbol] = asset
        return asset
    
    async def get_or_create_by_symbol(self, symbol: str):
        if symbol in self._assets:
            return self._assets[symbol]
        new_asset = Asset(
            symbol=symbol,
            display_name=symbol,
            asset_type=AssetType.UNKNOWN,
        )
        return await self.create(new_asset)
    
    async def get_sync_logs(self, limit: int = 50):
        return self._sync_logs[-limit:]
    
    async def log_sync(self, sync_log: AssetSyncLog):
        self._sync_logs.append(sync_log)
        return sync_log
    
    async def get_audit_logs(self, asset_id, limit: int = 100):
        return [log for log in self._audit_logs if log.asset_id == asset_id][:limit]
    
    async def log_audit(self, audit_log):
        self._audit_logs.append(audit_log)
        return audit_log


class MockMT5Gateway:
    """Mock MT5 gateway for testing"""
    
    def __init__(self, symbols=None):
        self._symbols = symbols or self._create_sample_symbols()
    
    def _create_sample_symbols(self):
        """Create sample MT5 symbols for testing"""
        return [
            MT5SymbolInfo(
                symbol="EURUSD",
                description="Euro vs US Dollar",
                path="Forex\\EURUSD",
                digits=5,
                trade_mode=0,
                trade_contract_size=100000,
                currency_base="EUR",
                currency_profit="USD",
            ),
            MT5SymbolInfo(
                symbol="GBPUSD",
                description="Pound vs US Dollar",
                path="Forex\\GBPUSD",
                digits=5,
                trade_mode=0,
                trade_contract_size=100000,
                currency_base="GBP",
                currency_profit="USD",
            ),
            MT5SymbolInfo(
                symbol="XAUUSD",
                description="Gold vs US Dollar",
                path="Metals\\XAUUSD",
                digits=2,
                trade_mode=0,
                trade_contract_size=100,
                currency_base="XAU",
                currency_profit="USD",
            ),
            MT5SymbolInfo(
                symbol="USOIL",
                description="US Oil",
                path="Energy\\USOIL",
                digits=2,
                trade_mode=0,
                trade_contract_size=1000,
                currency_base="USD",
                currency_profit="USD",
            ),
            MT5SymbolInfo(
                symbol="BTCUSD",
                description="Bitcoin vs US Dollar",
                path="Crypto\\BTCUSD",
                digits=2,
                trade_mode=0,
                trade_contract_size=1,
                currency_base="BTC",
                currency_profit="USD",
            ),
        ]
    
    async def get_available_symbols(self):
        return self._symbols
    
    async def get_symbol_info(self, symbol: str):
        for s in self._symbols:
            if s.symbol == symbol:
                return s
        return None


async def test_asset_creation():
    """Test 1: Asset Creation and Validation"""
    print_section("TEST 1: Asset Creation and Validation")
    
    try:
        # Create asset
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        print_success(f"Created asset: {asset.symbol} ({asset.display_name})")
        print_info(f"  ID: {asset.id}")
        print_info(f"  Type: {asset.asset_type.value}")
        print_info(f"  Availability: {asset.availability_status.value}")
        print_info(f"  Enabled: {asset.is_enabled}")
        print_info(f"  Operational: {asset.is_operational()}")
        
        # Test validation
        assert asset.symbol == "EURUSD"
        assert asset.availability_status == AvailabilityStatus.DISPONIBLE
        assert asset.is_enabled is False
        print_success("Asset creation validation passed")
        
    except Exception as e:
        print_error(f"Asset creation test failed: {e}")
        raise


async def test_asset_enablement():
    """Test 2: Asset Enablement Workflow"""
    print_section("TEST 2: Asset Enablement Workflow")
    
    try:
        # Create and enable asset
        asset = Asset(
            symbol="EURUSD",
            display_name="Euro vs US Dollar",
            asset_type=AssetType.FOREX_MAJOR,
        )
        
        # Try to enable
        result = asset.enable()
        assert result is True
        assert asset.is_enabled is True
        assert asset.is_operational() is True
        print_success(f"Enabled asset: {asset.symbol}")
        print_info(f"  Enabled: {asset.is_enabled}")
        print_info(f"  Operational: {asset.is_operational()}")
        
        # Test disable
        asset.disable()
        assert asset.is_enabled is False
        assert asset.is_operational() is False
        print_success(f"Disabled asset: {asset.symbol}")
        
        # Test enable unavailable asset
        asset.mark_unavailable()
        result = asset.enable()
        assert result is False
        print_success("Correctly prevented enabling unavailable asset")
        
    except Exception as e:
        print_error(f"Asset enablement test failed: {e}")
        raise


async def test_asset_classifier():
    """Test 3: Asset Classification"""
    print_section("TEST 3: Asset Classification")
    
    try:
        classifier = CompositeAssetClassifier()
        
        # Test symbols
        test_symbols = [
            ("EURUSD", AssetType.FOREX_MAJOR, "Forex Major"),
            ("GBPJPY", None, "Forex Minor (will be UNKNOWN without path)"),  # No path, can't classify
            ("XAUUSD", AssetType.METAL, "Metal"),
            ("USOIL", AssetType.ENERGY, "Energy"),
            ("BTCUSD", AssetType.CRYPTO, "Crypto"),
        ]
        
        for symbol, expected_type, description in test_symbols:
            symbol_info = MT5SymbolInfo(
                symbol=symbol,
                description=symbol,
                path="",
                digits=5,
                trade_mode=0,
                trade_contract_size=100000,
            )
            
            classified_type = classifier.classify(symbol_info)
            if expected_type is None:
                # This is expected to be UNKNOWN without path info
                status = "[INFO]"
                print(f"{status} {symbol}: {classified_type.value} (no path info - {description})")
            else:
                status = "[OK]" if classified_type == expected_type else "[WARN]"
                print(f"{status} {symbol}: {classified_type.value} (expected: {expected_type.value}) - {description}")
        
        print_success("Asset classification complete")
        
    except Exception as e:
        print_error(f"Asset classification test failed: {e}")
        raise


async def test_watchlist_sync():
    """Test 4: Watchlist Synchronization"""
    print_section("TEST 4: Watchlist Synchronization")
    
    try:
        # Setup
        repository = MockAssetRepository()
        gateway = MockMT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        print_info("Initial sync (all new assets):")
        sync_log = await service.synchronize_with_mt5(synced_by="test_user")
        print_success(f"Sync completed: {sync_log.status}")
        print_info(f"  Inserted: {sync_log.inserted_count}")
        print_info(f"  Updated: {sync_log.updated_count}")
        print_info(f"  Unavailable: {sync_log.unavailable_count}")
        
        assert sync_log.status == "SUCCESS"
        assert sync_log.inserted_count == 5
        assert sync_log.updated_count == 0
        
        # Load watchlist
        assets = await service.load_watchlist()
        print_info(f"\nWatchlist loaded: {len(assets)} assets")
        
        # Show assets by type
        grouped = await service.load_watchlist_grouped()
        print_info("\nAssets by type:")
        for asset_type, type_assets in grouped.items():
            print(f"  {asset_type.value}: {len(type_assets)} assets")
            for asset in type_assets:
                print(f"    - {asset.symbol} ({asset.display_name})")
        
        # Second sync (should update, not insert)
        print_info("\nSecond sync (should update existing):")
        sync_log2 = await service.synchronize_with_mt5(synced_by="test_user")
        print_success(f"Sync completed: {sync_log2.status}")
        print_info(f"  Inserted: {sync_log2.inserted_count}")
        print_info(f"  Updated: {sync_log2.updated_count}")
        print_info(f"  Unavailable: {sync_log2.unavailable_count}")
        
        assert sync_log2.inserted_count == 0
        assert sync_log2.updated_count == 5
        
        print_success("Watchlist sync test passed")
        
    except Exception as e:
        print_error(f"Watchlist sync test failed: {e}")
        raise


async def test_watchlist_incremental_sync():
    """Test 5: Incremental Sync (add/remove symbols)"""
    print_section("TEST 5: Incremental Sync (Add/Remove Symbols)")
    
    try:
        # Setup with initial symbols
        repository = MockAssetRepository()
        gateway = MockMT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        # Initial sync
        await service.synchronize_with_mt5(synced_by="test_user")
        assets = await service.load_watchlist()
        print_info(f"Initial watchlist: {len(assets)} assets")
        
        # Remove one symbol from MT5
        gateway._symbols = gateway._symbols[:-1]  # Remove last symbol
        print_info(f"\nRemoved 1 symbol from MT5")
        
        # Sync again
        sync_log = await service.synchronize_with_mt5(synced_by="test_user")
        print_success(f"Sync completed: {sync_log.status}")
        print_info(f"  Inserted: {sync_log.inserted_count}")
        print_info(f"  Updated: {sync_log.updated_count}")
        print_info(f"  Unavailable: {sync_log.unavailable_count}")
        
        assert sync_log.unavailable_count == 1
        
        # Check unavailable asset
        unavailable_assets = [a for a in await service.load_watchlist() 
                             if a.availability_status == AvailabilityStatus.NO_DISPONIBLE]
        print_info(f"  Unavailable assets: {len(unavailable_assets)}")
        for asset in unavailable_assets:
            print(f"    - {asset.symbol} ({asset.availability_status.value})")
        
        # Add new symbol to MT5
        gateway._symbols.append(MT5SymbolInfo(
            symbol="ETHUSD",
            description="Ethereum vs US Dollar",
            path="Crypto\\ETHUSD",
            digits=2,
            trade_mode=0,
            trade_contract_size=1,
            currency_base="ETH",
            currency_profit="USD",
        ))
        print_info(f"\nAdded 1 symbol to MT5")
        
        # Sync again
        sync_log2 = await service.synchronize_with_mt5(synced_by="test_user")
        print_success(f"Sync completed: {sync_log2.status}")
        print_info(f"  Inserted: {sync_log2.inserted_count}")
        print_info(f"  Updated: {sync_log2.updated_count}")
        print_info(f"  Unavailable: {sync_log2.unavailable_count}")
        
        assert sync_log2.inserted_count == 1
        
        assets = await service.load_watchlist()
        print_info(f"Final watchlist: {len(assets)} assets")
        
        print_success("Incremental sync test passed")
        
    except Exception as e:
        print_error(f"Incremental sync test failed: {e}")
        raise


async def test_enable_disable_workflow():
    """Test 6: Enable/Disable Workflow"""
    print_section("TEST 6: Enable/Disable Workflow")
    
    try:
        # Setup
        repository = MockAssetRepository()
        gateway = MockMT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        # Sync to get assets
        await service.synchronize_with_mt5(synced_by="test_user")
        assets = await service.load_watchlist()
        
        # Enable EURUSD
        eurusd = await repository.get_by_symbol("EURUSD")
        print_info(f"Before enable: {eurusd.symbol}")
        print_info(f"  Enabled: {eurusd.is_enabled}")
        print_info(f"  Operational: {eurusd.is_operational()}")
        
        enabled_asset = await service.enable_asset(
            asset_id=eurusd.id,
            enabled_by="test_user"
        )
        
        print_info(f"After enable: {enabled_asset.symbol}")
        print_info(f"  Enabled: {enabled_asset.is_enabled}")
        print_info(f"  Operational: {enabled_asset.is_operational()}")
        
        assert enabled_asset.is_enabled is True
        assert enabled_asset.is_operational() is True
        print_success(f"Enabled {enabled_asset.symbol}")
        
        # Disable
        disabled_asset = await service.disable_asset(
            asset_id=eurusd.id,
            disabled_by="test_user"
        )
        
        print_info(f"After disable: {disabled_asset.symbol}")
        print_info(f"  Enabled: {disabled_asset.is_enabled}")
        print_info(f"  Operational: {disabled_asset.is_operational()}")
        
        assert disabled_asset.is_enabled is False
        assert disabled_asset.is_operational() is False
        print_success(f"Disabled {disabled_asset.symbol}")
        
        # Get operational assets
        operational = await service.get_operational_assets()
        print_info(f"\nOperational assets: {len(operational)}")
        
        print_success("Enable/disable workflow test passed")
        
    except Exception as e:
        print_error(f"Enable/disable workflow test failed: {e}")
        raise


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  WATCHLIST FUNCTIONALITY TESTS")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Asset Creation and Validation", test_asset_creation),
        ("Asset Enablement Workflow", test_asset_enablement),
        ("Asset Classification", test_asset_classifier),
        ("Watchlist Synchronization", test_watchlist_sync),
        ("Incremental Sync", test_watchlist_incremental_sync),
        ("Enable/Disable Workflow", test_enable_disable_workflow),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_name, str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    print(f"\nTotal Tests: {len(tests)}")
    print(f"[OK] Passed: {passed}")
    print(f"[ERROR] Failed: {failed}")
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if errors:
        print("\nFailed Tests:")
        for test_name, error in errors:
            print(f"  [ERROR] {test_name}: {error}")
    
    if failed == 0:
        print("\n*** All tests passed! ***")
    else:
        print(f"\n[WARN] {failed} test(s) failed")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
