# 002_WL_config.md - Watchlist Configuration Flows

**Date:** 2026-04-05
**Author:** Software Architect
**Status:** Implementation Document

---

## Overview

This document describes the flows, inputs, processes, and outputs for the Watchlist Configuration module as defined in ADR-001, and its integration with ADR-002 (MT5 Account Configuration).

---

## 1. Flow Diagrams

### 1.1 Watchlist Initial Load Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Action: Open Watchlist
       ▼
┌──────────────────────────────┐
│ 1. Load Local Catalog        │
│    - Query assets table       │
│    - Group by asset_type      │
└──────┬───────────────────────┘
       │
       │ Has local data? ──── NO ────► Go to Initial Load Flow
       │
       YES
       ▼
┌──────────────────────────────┐
│ 2. Return Local Catalog      │
│    - Show assets              │
│    - Show status indicators   │
│    - Show last sync time      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Trigger Background Sync   │
│    - Async synchronization    │
│    - Update UI on completion  │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Display    │
│  Watchlist  │
└─────────────┘
```

### 1.2 Initial Load Flow (First Time)

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Action: Open Watchlist (first time)
       ▼
┌──────────────────────────────┐
│ 1. Detect Empty Catalog      │
│    - Query assets table       │
│    - No records found         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 2. Query MT5 Symbols         │
│    - Call MT5Adapter          │
│    - GetAvailableSymbols()    │
└──────┬───────────────────────┘
       │
       │ MT5 Available? ──── NO ────► Show error, retry later
       │
       YES
       ▼
┌──────────────────────────────┐
│ 3. Classify Symbols          │
│    - Forex Majors/Minors      │
│    - Metals, Energy, etc.     │
│    - Crypto, Indices, Stocks  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Insert All Symbols        │
│    - availability = DISPONIBLE│
│    - is_enabled = false       │
│    - source = "MT5"           │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 5. Log Sync & Audit          │
│    - Record sync results      │
│    - Audit each insertion     │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Display    │
│  Watchlist  │
└─────────────┘
```

### 1.3 Incremental Synchronization Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Action: Sync Watchlist
       ▼
┌──────────────────────────────┐
│ 1. Get MT5 Symbols           │
│    - Call MT5Adapter          │
│    - GetAvailableSymbols()    │
│    - Build MT5 symbol set     │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 2. Get Local Assets          │
│    - Query assets table       │
│    - Build local symbol map   │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Compare & Process         │
│                              │
│  For each MT5 symbol:        │
│    - In local?               │
│      YES → Update & DISPONIBLE│
│      NO  → Insert new        │
│                              │
│  For each local asset:       │
│    - In MT5?                 │
│      YES → Skip              │
│      NO  → Mark NO_DISPONIBLE│
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Update Timestamps         │
│    - last_seen_at             │
│    - updated_at               │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 5. Log Results               │
│    - inserted_count           │
│    - updated_count            │
│    - unavailable_count        │
│    - Audit all changes        │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Results    │
└─────────────┘
```

### 1.4 Enable Asset Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Action: Enable Asset (checkbox)
       ▼
┌──────────────────────────────┐
│ 1. Get Asset by ID           │
│    - Query database           │
└──────┬───────────────────────┘
       │
       │ Found? ──── NO ────► Return 404 Error
       │
       YES
       ▼
┌──────────────────────────────┐
│ 2. Check Availability        │
│    - availability_status      │
│      == DISPONIBLE?           │
└──────┬───────────────────────┘
       │
       │ Available? ──── NO ────► Return 400 Error
       │                          "Asset not available in MT5"
       YES
       ▼
┌──────────────────────────────┐
│ 3. Enable Asset              │
│    - is_enabled = true       │
│    - Update timestamp         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Persist & Audit           │
│    - Update database          │
│    - Create audit log         │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Success    │
│  (200)      │
└─────────────┘
```

---

## 2. Inputs

### 2.1 Load Watchlist Input

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| asset_type | enum | No | Filter by asset type | "FOREX_MAJOR" |
| enabled_only | bool | No | Show only enabled | false |

**Example Request:**
```
GET /api/v1/watchlist?asset_type=FOREX_MAJOR&enabled_only=false
```

### 2.2 Sync Watchlist Input

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| (none) | - | - | No parameters required | - |

**Example Request:**
```
POST /api/v1/watchlist/sync
```

### 2.3 Enable/Disable Asset Input

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| asset_id | UUID | Yes | ID of asset to enable/disable | "550e8400-e29b-41d4-a716-446655440000" |

**Example Request:**
```
POST /api/v1/watchlist/{asset_id}/enable
POST /api/v1/watchlist/{asset_id}/disable
```

---

## 3. Processes

### 3.1 Asset Classification Process

**Service:** `CompositeAssetClassifier`

Uses Chain of Responsibility pattern with multiple strategies:

**Strategy 1: PathBasedClassifier**
```python
# Classify by MT5 symbol path
if "forex" in path:
    if symbol in MAJORS:
        return AssetType.FOREX_MAJOR
    return AssetType.FOREX_MINOR
if "metal" in path:
    return AssetType.METAL
# etc.
```

**Strategy 2: SymbolBasedClassifier**
```python
# Classify by symbol name patterns
if symbol.startswith("XAU"):  # Gold
    return AssetType.METAL
if symbol in MAJOR_PAIRS:
    return AssetType.FOREX_MAJOR
# etc.
```

### 3.2 Synchronization Process

**Service Method:** `AssetCatalogService.synchronize_with_mt5()`

**Steps:**

1. **Get Symbols from MT5**
   ```python
   mt5_symbols = await mt5_gateway.get_available_symbols()
   mt5_symbol_set = {s.symbol for s in mt5_symbols}
   ```

2. **Get Local Assets**
   ```python
   local_assets = await repository.get_all()
   local_symbol_map = {asset.symbol: asset for asset in local_assets}
   ```

3. **Process MT5 Symbols**
   ```python
   for symbol_info in mt5_symbols:
       if symbol_info.symbol in local_symbol_map:
           # Update existing
           asset.mark_available()
           updated_count += 1
       else:
           # Insert new
           asset = Asset(
               symbol=symbol_info.symbol,
               display_name=symbol_info.description,
               asset_type=classifier.classify(symbol_info),
               is_enabled=False,
           )
           await repository.create(asset)
           inserted_count += 1
   ```

4. **Mark Absent as Unavailable**
   ```python
   for symbol, asset in local_symbol_map.items():
       if symbol not in mt5_symbol_set:
           asset.mark_unavailable()
           unavailable_count += 1
   ```

5. **Log Results**
   ```python
   sync_log.complete(
       status="SUCCESS",
       inserted_count=inserted_count,
       updated_count=updated_count,
       unavailable_count=unavailable_count
   )
   await repository.log_sync(sync_log)
   ```

### 3.3 Enable Asset Process

**Service Method:** `AssetCatalogService.enable_asset()`

**Steps:**

1. **Get Asset**
   ```python
   asset = await repository.get_by_id(asset_id)
   if not asset:
       raise ValueError(f"Asset not found: {asset_id}")
   ```

2. **Validate Availability**
   ```python
   success = asset.enable()
   if not success:
       raise ValueError(
           f"Asset cannot be enabled. "
           f"Availability: {asset.availability_status.value}"
       )
   ```

3. **Update & Audit**
   ```python
   updated_asset = await repository.update(asset)
   await _audit_asset(
       asset_id=asset_id,
       action="ENABLED",
       old_value=json.dumps({"is_enabled": False}),
       new_value=json.dumps({"is_enabled": True}),
       changed_by=enabled_by,
       reason="Asset enabled for radar monitoring"
   )
   ```

---

## 4. Outputs

### 4.1 Watchlist Response

**HTTP Status:** 200 OK

**Response Schema:**
```json
{
  "assets": {
    "FOREX_MAJOR": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "symbol": "EURUSD",
        "display_name": "Euro vs US Dollar",
        "asset_type": "FOREX_MAJOR",
        "availability_status": "DISPONIBLE",
        "is_enabled": true,
        "source": "MT5",
        "first_seen_at": "2026-04-05T09:00:00Z",
        "last_seen_at": "2026-04-05T10:30:00Z",
        "updated_at": "2026-04-05T10:30:00Z"
      }
    ],
    "METAL": [
      {
        "id": "uuid",
        "symbol": "XAUUSD",
        "display_name": "Gold vs US Dollar",
        "asset_type": "METAL",
        "availability_status": "DISPONIBLE",
        "is_enabled": false,
        "source": "MT5",
        "first_seen_at": "2026-04-05T09:00:00Z",
        "last_seen_at": "2026-04-05T10:30:00Z",
        "updated_at": "2026-04-05T10:30:00Z"
      }
    ]
  },
  "total": 2
}
```

### 4.2 Sync Response

**HTTP Status:** 200 OK

**Response Schema:**
```json
{
  "sync_id": "uuid",
  "status": "SUCCESS",
  "inserted_count": 5,
  "updated_count": 150,
  "unavailable_count": 2,
  "sync_started_at": "2026-04-05T10:30:00Z",
  "sync_finished_at": "2026-04-05T10:30:05Z",
  "error_message": null
}
```

### 4.3 Error Responses

| Error | HTTP Status | When |
|-------|-------------|------|
| "Asset not found: {id}" | 404 | Invalid asset ID |
| "Asset cannot be enabled. Availability: NO_DISPONIBLE" | 400 | Enabling unavailable asset |

---

## 5. Integration with ADR-002 (MT5 Accounts)

### 5.1 Relationship

| Aspect | ADR-001 (Watchlist) | ADR-002 (MT5 Accounts) |
|--------|---------------------|------------------------|
| **Purpose** | Manage symbols to monitor | Manage MT5 account credentials |
| **Entity** | Asset (symbol) | MT5Account |
| **Source** | MT5 symbols | MT5 terminal |
| **Status** | availability_status, is_enabled | availability_status, is_enabled, lifecycle_status |

### 5.2 Shared Patterns

Both modules implement similar patterns:

| Pattern | Watchlist | MT5 Accounts |
|---------|-----------|--------------|
| **Availability Status** | `DISPONIBLE` / `NO_DISPONIBLE` | `AVAILABLE` / `UNAVAILABLE` / etc. |
| **Enablement** | `is_enabled` (user control) | `is_enabled` (user control) |
| **Audit Trail** | `asset_audit_log` | `mt5_account_audit_log` |
| **Sync/Validation** | `asset_sync_log` | `mt5_account_validation_log` |
| **Soft Delete** | Mark as `NO_DISPONIBLE` | Mark as `ARCHIVED` |

### 5.3 Integration Points

**MT5 Gateway:**
```python
# Shared by both modules
class IMT5Gateway:
    async def get_available_symbols() -> List[MT5SymbolInfo]  # For Watchlist
    async def test_connection() -> MT5ConnectionTestResult    # For MT5 Accounts
```

**Asset Catalog ↔ MT5 Accounts:**
- Watchlist uses MT5 Gateway to discover symbols
- MT5 Accounts uses MT5 Gateway to validate credentials
- Both audit their operations

**Operational Dependency:**
```
MT5 Account (validated & enabled)
    ↓
MT5 Gateway (connection established)
    ↓
Watchlist Sync (get_available_symbols)
    ↓
Assets (available & enabled)
    ↓
Radar Engine (monitors enabled assets)
```

### 5.4 Dependency Flow

```
User enables MT5 Account (ADR-002)
    ↓
Account validated & enabled
    ↓
User syncs Watchlist (ADR-001)
    ↓
Symbols discovered from MT5
    ↓
User enables assets
    ↓
Radar monitors enabled assets using enabled MT5 Account
```

---

## 6. Business Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| RN-01 | Watchlist accessed from Configuration → Watchlist | API route: `/api/v1/watchlist` |
| RN-02 | Sync with MT5 on open | `POST /api/v1/watchlist/sync` |
| RN-03 | Build from MT5 if empty | Service checks if empty, calls MT5 |
| RN-04 | Group by asset type | `get_grouped_by_type()` |
| RN-05 | Separate availability & enablement | `availability_status` vs `is_enabled` |
| RN-06 | Mark absent as NO_DISPONIBLE | Sync process marks unavailable |
| RN-07 | NO_DISPONIBLE cannot be used | `enable()` checks availability |
| RN-08 | Audit all changes | `asset_audit_log` for all mutations |
| RN-09 | New symbols inserted disabled | `is_enabled = false` on insert |
| RN-10 | Show last catalog if MT5 fails | Load local first, then sync |

---

## 7. Test Coverage

### Domain Entity Tests

| Test Category | Tests | Status |
|---------------|-------|--------|
| Asset Creation | 3 tests | ✅ |
| Asset Availability | 2 tests | ✅ |
| Asset Enablement | 3 tests | ✅ |
| Asset Operational | 3 tests | ✅ |
| Asset Classification | 1 test | ✅ |
| **Total** | **12 tests** | ✅ |

### Service Layer Tests

| Test Category | Tests | Status |
|---------------|-------|--------|
| Load Watchlist | 2 tests | ✅ |
| Sync Watchlist | 4 tests | ✅ |
| Enable Asset | 3 tests | ✅ |
| Disable Asset | 2 tests | ✅ |
| Query Methods | 3 tests | ✅ |
| **Total** | **14 tests** | ✅ |

### **Total Test Count: 26 tests**

---

## 8. Next Steps

1. **Create Alembic Migration**
   ```bash
   alembic revision --autogenerate -m "add_watchlist_assets_tables"
   alembic upgrade head
   ```

2. **Update main.py**
   - Add assets router to FastAPI app

3. **Frontend UI**
   - Configuration → Watchlist page
   - Implement sync button
   - Implement enable/disable checkboxes

4. **Integration Tests**
   - Test full sync flow with real MT5
   - Test classification accuracy

---

**End of Document**
