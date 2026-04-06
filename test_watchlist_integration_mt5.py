"""
Integration test for Watchlist with real MT5 data.
Tests Asset Catalog synchronization with actual MT5 symbols.
"""

import asyncio
import sys
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, r'C:\Users\gomez\.gemini\antigravity\scratch\radar2')

# Load environment variables
load_dotenv()

from src.domain.entities.asset import Asset, AssetType, AvailabilityStatus
from src.application.asset_catalog.services.asset_catalog_service import AssetCatalogService
from src.application.asset_catalog.services.asset_classifier import CompositeAssetClassifier
from src.infrastructure.mt5.adapter.mt5_gateway import MT5Gateway
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


def print_warning(message: str):
    """Print warning message"""
    print(f"[WARN] {message}")


class MockRepositoryForIntegration:
    """Mock repository for integration testing (no database required)"""
    
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
    
    async def get_sync_logs(self, limit: int = 50):
        return self._sync_logs[-limit:]
    
    async def log_sync(self, sync_log):
        self._sync_logs.append(sync_log)
        return sync_log
    
    async def get_audit_logs(self, asset_id, limit: int = 100):
        return [log for log in self._audit_logs if log.asset_id == asset_id][:limit]
    
    async def log_audit(self, audit_log):
        self._audit_logs.append(audit_log)
        return audit_log


async def test_mt5_connection():
    """Test 1: MT5 Connection"""
    print_section("TEST 1: MT5 Connection")
    
    try:
        gateway = MT5Gateway()
        
        # Initialize MT5
        import MetaTrader5 as mt5
        if not mt5.initialize():
            print_error("Failed to initialize MT5")
            print_info("Make sure MT5 is installed and running")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print_error("Failed to get account info")
            return False
        
        print_success("MT5 connected successfully")
        print_info(f"Account: {account_info.login}")
        print_info(f"Server: {account_info.server}")
        print_info(f"Broker: {account_info.company}")
        print_info(f"Balance: {account_info.balance} {account_info.currency}")
        
        mt5.shutdown()
        return True
        
    except Exception as e:
        print_error(f"MT5 connection test failed: {e}")
        return False


async def test_mt5_symbol_discovery():
    """Test 2: MT5 Symbol Discovery"""
    print_section("TEST 2: MT5 Symbol Discovery")
    
    try:
        gateway = MT5Gateway()
        
        # Get symbols
        symbols = await gateway.get_available_symbols()
        
        if not symbols:
            print_error("No symbols returned from MT5")
            return False
        
        print_success(f"Retrieved {len(symbols)} symbols from MT5")
        
        # Show first 10 symbols
        print_info("\nFirst 10 symbols:")
        for i, symbol in enumerate(symbols[:10], 1):
            print(f"  {i}. {symbol.symbol:15} {symbol.description:40} {symbol.path}")
        
        # Show statistics
        print_info(f"\nTotal symbols: {len(symbols)}")
        
        # Show symbols by path
        path_counts = {}
        for symbol in symbols:
            path = symbol.path.split('\\')[0] if '\\' in symbol.path else symbol.path
            if path not in path_counts:
                path_counts[path] = 0
            path_counts[path] += 1
        
        print_info("\nSymbols by category:")
        for path, count in sorted(path_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {path:20} {count:5} symbols")
        
        return True
        
    except Exception as e:
        print_error(f"MT5 symbol discovery test failed: {e}")
        return False


async def test_asset_classification_with_real_data():
    """Test 3: Asset Classification with Real MT5 Data"""
    print_section("TEST 3: Asset Classification with Real MT5 Data")
    
    try:
        gateway = MT5Gateway()
        classifier = CompositeAssetClassifier()
        
        # Get symbols from MT5
        symbols = await gateway.get_available_symbols()
        
        if not symbols:
            print_error("No symbols from MT5")
            return False
        
        print_info(f"Classifying {len(symbols)} symbols from MT5...\n")
        
        # Classify all symbols
        classification_counts = {}
        sample_symbols = []
        
        for symbol in symbols:
            asset_type = classifier.classify(symbol)
            
            if asset_type not in classification_counts:
                classification_counts[asset_type] = []
            classification_counts[asset_type].append(symbol)
            
            # Keep sample for display
            if len(classification_counts[asset_type]) <= 3:
                sample_symbols.append((symbol.symbol, asset_type, symbol.path))
        
        # Show results
        print_info("Classification results:")
        for asset_type in AssetType:
            if asset_type in classification_counts:
                count = len(classification_counts[asset_type])
                print(f"  {asset_type.value:20} {count:5} symbols")
        
        # Show samples
        print_info("\nSample classifications:")
        for symbol, asset_type, path in sample_symbols[:15]:
            print(f"  {symbol:15} -> {asset_type.value:20} ({path})")
        
        return True
        
    except Exception as e:
        print_error(f"Asset classification test failed: {e}")
        return False


async def test_watchlist_sync_with_mt5():
    """Test 4: Watchlist Synchronization with Real MT5"""
    print_section("TEST 4: Watchlist Synchronization with Real MT5")
    
    try:
        # Setup
        repository = MockRepositoryForIntegration()
        gateway = MT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        print_info("Starting initial synchronization with MT5...")
        
        # First sync
        sync_log = await service.synchronize_with_mt5(synced_by="integration_test")
        
        print_success(f"Synchronization completed: {sync_log.status}")
        print_info(f"  Inserted: {sync_log.inserted_count}")
        print_info(f"  Updated: {sync_log.updated_count}")
        print_info(f"  Unavailable: {sync_log.unavailable_count}")
        
        if sync_log.status != "SUCCESS":
            print_error(f"Sync failed: {sync_log.error_message}")
            return False
        
        # Load watchlist
        assets = await service.load_watchlist()
        print_info(f"\nWatchlist loaded: {len(assets)} assets")
        
        # Show assets by type
        grouped = await service.load_watchlist_grouped()
        print_info("\nAssets by type:")
        for asset_type, type_assets in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {asset_type.value:20} {len(type_assets):5} assets")
            
            # Show first 3 assets of each type
            for asset in type_assets[:3]:
                print(f"    - {asset.symbol:15} ({asset.display_name})")
            
            if len(type_assets) > 3:
                print(f"    ... and {len(type_assets) - 3} more")
        
        # Second sync (should update only)
        print_info("\nSecond synchronization (should update existing)...")
        sync_log2 = await service.synchronize_with_mt5(synced_by="integration_test")
        
        print_success(f"Second sync completed: {sync_log2.status}")
        print_info(f"  Inserted: {sync_log2.inserted_count}")
        print_info(f"  Updated: {sync_log2.updated_count}")
        print_info(f"  Unavailable: {sync_log2.unavailable_count}")
        
        # Verify no new insertions
        if sync_log2.inserted_count == 0:
            print_success("No duplicate insertions on second sync")
        else:
            print_warning(f"Unexpected insert on second sync: {sync_log2.inserted_count}")
        
        return True
        
    except Exception as e:
        print_error(f"Watchlist sync with MT5 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enable_real_assets():
    """Test 5: Enable Real Assets from MT5"""
    print_section("TEST 5: Enable Real Assets from MT5")
    
    try:
        # Setup
        repository = MockRepositoryForIntegration()
        gateway = MT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        # Sync to get assets
        await service.synchronize_with_mt5(synced_by="integration_test")
        
        # Get some assets
        assets = await service.load_watchlist()
        
        if not assets:
            print_error("No assets in watchlist")
            return False
        
        # Try to enable first available asset
        asset_to_enable = assets[0]
        print_info(f"Attempting to enable: {asset_to_enable.symbol}")
        print_info(f"  Before: enabled={asset_to_enable.is_enabled}, operational={asset_to_enable.is_operational()}")
        
        enabled_asset = await service.enable_asset(
            asset_id=asset_to_enable.id,
            enabled_by="integration_test"
        )
        
        print_success(f"Enabled: {enabled_asset.symbol}")
        print_info(f"  After: enabled={enabled_asset.is_enabled}, operational={enabled_asset.is_operational()}")
        
        # Get operational assets
        operational = await service.get_operational_assets()
        print_info(f"\nOperational assets: {len(operational)}")
        for asset in operational[:5]:
            print(f"  - {asset.symbol:15} ({asset.asset_type.value})")
        
        # Disable it back
        disabled_asset = await service.disable_asset(
            asset_id=asset_to_enable.id,
            disabled_by="integration_test"
        )
        
        print_success(f"Disabled: {disabled_asset.symbol}")
        
        return True
        
    except Exception as e:
        print_error(f"Enable real assets test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_incremental_sync_with_mt5():
    """Test 6: Incremental Sync Simulation with Real MT5 Data"""
    print_section("TEST 6: Incremental Sync Simulation with Real MT5 Data")
    
    try:
        # Setup
        repository = MockRepositoryForIntegration()
        gateway = MT5Gateway()
        service = AssetCatalogService(repository, gateway)
        
        # Initial sync
        print_info("Initial synchronization...")
        await service.synchronize_with_mt5(synced_by="integration_test")
        assets = await service.load_watchlist()
        print_info(f"Initial watchlist: {len(assets)} assets")
        
        # Simulate removing some assets from MT5
        # (we'll manually mark some as unavailable)
        assets_to_remove = assets[:3]  # Remove first 3
        print_info(f"\nSimulating removal of {len(assets_to_remove)} assets from MT5...")
        
        for asset in assets_to_remove:
            asset.mark_unavailable()
            await repository.update(asset)
        
        # Sync again
        print_info("Synchronizing again...")
        sync_log = await service.synchronize_with_mt5(synced_by="integration_test")
        
        print_success(f"Sync completed: {sync_log.status}")
        print_info(f"  Inserted: {sync_log.inserted_count}")
        print_info(f"  Updated: {sync_log.updated_count}")
        print_info(f"  Unavailable: {sync_log.unavailable_count}")
        
        # Check unavailable assets
        unavailable_assets = [a for a in await service.load_watchlist() 
                             if a.availability_status == AvailabilityStatus.NO_DISPONIBLE]
        print_info(f"  Unavailable assets: {len(unavailable_assets)}")
        
        # Restore them (sync again will mark as available if back in MT5)
        print_info("\nRestoring assets (re-syncing)...")
        sync_log2 = await service.synchronize_with_mt5(synced_by="integration_test")
        
        print_success(f"Restore sync completed: {sync_log2.status}")
        print_info(f"  Inserted: {sync_log2.inserted_count}")
        print_info(f"  Updated: {sync_log2.updated_count}")
        print_info(f"  Unavailable: {sync_log2.unavailable_count}")
        
        # Verify all are available again
        unavailable_assets = [a for a in await service.load_watchlist() 
                             if a.availability_status == AvailabilityStatus.NO_DISPONIBLE]
        
        if len(unavailable_assets) == 0:
            print_success("All assets restored to DISPONIBLE status")
        else:
            print_warning(f"{len(unavailable_assets)} assets still unavailable")
        
        return True
        
    except Exception as e:
        print_error(f"Incremental sync simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("  WATCHLIST INTEGRATION TESTS WITH REAL MT5 DATA")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("MT5 Connection", test_mt5_connection),
        ("MT5 Symbol Discovery", test_mt5_symbol_discovery),
        ("Asset Classification with Real Data", test_asset_classification_with_real_data),
        ("Watchlist Synchronization with MT5", test_watchlist_sync_with_mt5),
        ("Enable Real Assets", test_enable_real_assets),
        ("Incremental Sync Simulation", test_incremental_sync_with_mt5),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    errors = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result is True:
                passed += 1
            elif result is False:
                failed += 1
                errors.append((test_name, "Test returned False"))
            else:
                skipped += 1
                errors.append((test_name, "Test skipped"))
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
    print(f"[SKIP] Skipped: {skipped}")
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if errors:
        print("\nFailed/Skipped Tests:")
        for test_name, error in errors:
            print(f"  [ERROR] {test_name}: {error}")
    
    if failed == 0 and skipped == 0:
        print("\n*** All integration tests passed! ***")
    elif failed == 0:
        print(f"\n[WARN] Some tests were skipped")
    else:
        print(f"\n[WARN] {failed} test(s) failed")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
