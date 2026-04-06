# 001_MT_config.md - MT5 Account Configuration Flows

**Date:** 2026-04-05
**Author:** Software Architect
**Status:** Implementation Document

---

## Overview

This document describes the flows, inputs, processes, and outputs for the MT5 Account Configuration module as defined in ADR-002.

---

## 1. Flow Diagrams

### 1.1 Account Creation Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Input: Account details
       │ (name, broker, server, login, password, terminal_path, environment)
       ▼
┌──────────────────────────────┐
│ 1. Validate Input Format     │
│    - Required fields         │
│    - Terminal path (.exe)    │
│    - Environment type valid  │
└──────┬───────────────────────┘
       │
       │ Valid? ──── NO ────► Return 400 Error
       │
       YES
       ▼
┌──────────────────────────────┐
│ 2. Create Account Entity     │
│    - Generate UUID           │
│    - Set initial state:      │
│      lifecycle = ACTIVE      │
│      availability = UNKNOWN  │
│      is_enabled = false      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Store Password Securely   │
│    - Encrypt password        │
│    - Store secret reference  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Persist to Database       │
│    - Insert mt5_accounts     │
│    - Return created account  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 5. Create Audit Log          │
│    - Action: CREATED         │
│    - Record who, when, why   │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Account    │
│  (201)      │
└─────────────┘
```

### 1.2 Account Validation Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Input: account_id, password
       ▼
┌──────────────────────────────┐
│ 1. Get Account by ID         │
│    - Query database           │
│    - Check if archived        │
└──────┬───────────────────────┘
       │
       │ Found? ──── NO ────► Return 404 Error
       │
       YES
       │
       │ Archived? ──── YES ────► Return 400 Error
       │
       NO
       ▼
┌──────────────────────────────┐
│ 2. Create Validation Log     │
│    - Status: PENDING         │
│    - Record start time        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Test MT5 Connection       │
│    - Initialize MT5          │
│    - Login with credentials  │
│    - Get account info         │
│    - Shutdown MT5            │
└──────┬───────────────────────┘
       │
       │ Success? ──── NO ────► Set status: FAILED
       │                         Set availability: ERROR
       │                         Log error message
       │
       YES
       ▼
┌──────────────────────────────┐
│ 4. Update Account Status     │
│    - availability = AVAILABLE│
│    - validation = SUCCESS    │
│    - Update timestamp         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 5. Persist Changes           │
│    - Update account           │
│    - Save validation log      │
│    - Create audit log         │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Account    │
│  (200)      │
└─────────────┘
```

### 1.3 Account Enablement Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Input: account_id
       ▼
┌──────────────────────────────┐
│ 1. Get Account by ID         │
│    - Query database           │
└──────┬───────────────────────┘
       │
       │ Found? ──── NO ────► Return 404 Error
       │
       YES
       ▼
┌──────────────────────────────┐
│ 2. Check Prerequisites       │
│    - availability = AVAILABLE│
│    - lifecycle = ACTIVE      │
└──────┬───────────────────────┘
       │
       │ Valid? ──── NO ────► Return 400 Error
       │                      (Account not validated or archived)
       YES
       ▼
┌──────────────────────────────┐
│ 3. Enable Account            │
│    - is_enabled = true       │
│    - Update timestamp         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Persist Changes           │
│    - Update account           │
│    - Create audit log         │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Account    │
│  (200)      │
└─────────────┘
```

### 1.4 Set Default for Environment Flow

```
┌─────────────┐
│    User     │
│  (UI/API)   │
└──────┬──────┘
       │
       │ Input: account_id
       ▼
┌──────────────────────────────┐
│ 1. Get Account by ID         │
│    - Query database           │
│    - Check lifecycle status   │
└──────┬───────────────────────┘
       │
       │ Found & Active? ──── NO ────► Return 400 Error
       │
       YES
       ▼
┌──────────────────────────────┐
│ 2. Get All Accounts in Env   │
│    - Query by environment     │
│    - Include all statuses     │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Unset Other Defaults      │
│    - For each account in env: │
│      if is_default=true:      │
│        is_default = false     │
│        Update account          │
│        Audit log: UNSET_DEFAULT│
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 4. Set This Account Default  │
│    - is_default = true       │
│    - Update account           │
│    - Audit log: SET_DEFAULT   │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Account    │
│  (200)      │
└─────────────┘
```

---

## 2. Inputs

### 2.1 Create Account Input

| Field | Type | Required | Validation | Example |
|-------|------|----------|------------|---------|
| account_name | string | Yes | 1-255 chars | "Demo Account - MetaQuotes" |
| broker_name | string | Yes | 1-255 chars | "MetaQuotes Software" |
| server_name | string | Yes | 1-255 chars | "MetaQuotes-Demo" |
| login | string | Yes | 1-100 chars, numeric | "105291044" |
| password | string | Yes | 1+ chars, encrypted | "Yq!b7rYn" |
| terminal_path | string | Yes | Valid path, ends with .exe | "C:\Program Files\MetaTrader 5\terminal64.exe" |
| environment_type | enum | Yes | DEV, DEMO, PAPER, LIVE_MICRO, LIVE | "DEMO" |

**Example Request (JSON):**
```json
{
  "account_name": "Demo Account - MetaQuotes",
  "broker_name": "MetaQuotes Software",
  "server_name": "MetaQuotes-Demo",
  "login": "105291044",
  "password": "Yq!b7rYn",
  "terminal_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
  "environment_type": "DEMO"
}
```

### 2.2 Validate Account Input

| Field | Type | Required | Validation | Example |
|-------|------|----------|------------|---------|
| account_id | UUID | Yes | Valid UUID | "550e8400-e29b-41d4-a716-446655440000" |
| password | string | Yes | 1+ chars | "Yq!b7rYn" |

**Example Request (JSON):**
```json
{
  "password": "Yq!b7rYn"
}
```

### 2.3 Enable/Disable/Archive Input

| Field | Type | Required | Validation | Example |
|-------|------|----------|------------|---------|
| account_id | UUID | Yes | Valid UUID | "550e8400-e29b-41d4-a716-446655440000" |

**Example Request:**
```
POST /api/v1/mt5-accounts/{account_id}/enable
POST /api/v1/mt5-accounts/{account_id}/disable
POST /api/v1/mt5-accounts/{account_id}/archive
```

---

## 3. Processes

### 3.1 Account Creation Process

**Service Method:** `MT5AccountService.create_account()`

**Steps:**
1. **Validate Input Format**
   - Check all required fields are present
   - Validate terminal path ends with `.exe`
   - Validate environment type is valid enum

2. **Create Account Entity**
   ```python
   account = MT5Account(
       account_name=account_name,
       broker_name=broker_name,
       server_name=server_name,
       login=login,
       password_secret_ref=password_secret_ref,  # Encrypted
       terminal_path=terminal_path,
       environment_type=environment_type,
       is_enabled=False,
       availability_status=AvailabilityStatus.UNKNOWN,
       lifecycle_status=LifecycleStatus.ACTIVE,
   )
   ```

3. **Store Password Securely**
   - In production: Use secrets manager (AWS Secrets Manager, Azure Key Vault)
   - For now: Store reference in DB, encrypt password separately

4. **Persist to Database**
   ```python
   created_account = await repository.create(account)
   ```

5. **Create Audit Log**
   ```python
   audit_log = MT5AccountAuditLog(
       account_id=created_account.id,
       action="CREATED",
       new_value=json.dumps({
           "account_name": account_name,
           "broker_name": broker_name,
           "environment_type": environment_type.value,
       }),
       changed_by=created_by,
       reason="Account created via UI"
   )
   await repository.log_audit(audit_log)
   ```

6. **Return Created Account**
   - HTTP Status: 201 Created
   - Response: MT5AccountResponse (with masked login)

**Business Rules Applied:**
- RN-MT5-01: Management from Configuration → MT5 Accounts
- RN-MT5-02: Support multiple accounts
- RN-MT5-03: Account associated with environment
- RN-MT5-07: All changes audited

### 3.2 Account Validation Process

**Service Method:** `MT5AccountService.validate_account()`

**Steps:**
1. **Get Account by ID**
   ```python
   account = await repository.get_by_id(account_id)
   if not account:
       raise ValueError(f"Account not found: {account_id}")
   
   if account.lifecycle_status == LifecycleStatus.ARCHIVED:
       raise ValueError("Cannot validate archived account")
   ```

2. **Create Validation Log**
   ```python
   validation_log = MT5AccountValidationLog(
       account_id=account_id,
       status="PENDING"
   )
   ```

3. **Test MT5 Connection**
   ```python
   result = await mt5_gateway.test_connection(
       login=account.login,
       password=password,
       server=account.server_name,
       terminal_path=account.terminal_path
   )
   ```

4. **Update Account Status Based on Result**
   
   **If Success:**
   ```python
   account.validate_account(ValidationStatus.SUCCESS)
   # availability_status = AVAILABLE
   ```

   **If Failed:**
   ```python
   account.validate_account(ValidationStatus.FAILED)
   account.availability_status = AvailabilityStatus.INVALID_CREDENTIALS
   ```

   **If Terminal Not Found:**
   ```python
   account.availability_status = AvailabilityStatus.TERMINAL_NOT_FOUND
   ```

   **If Connection Error:**
   ```python
   account.availability_status = AvailabilityStatus.CONNECTION_ERROR
   ```

5. **Complete Validation Log**
   ```python
   validation_log.complete(
       status="SUCCESS" if result.success else "FAILED",
       error_message=result.error_message,
       broker_response_summary=json.dumps({
           "broker_name": result.broker_name,
           "server_name": result.server_name,
           "account_type": result.account_type,
           "currency": result.currency,
       }) if result.success else None
   )
   ```

6. **Persist Changes**
   ```python
   await repository.log_validation(validation_log)
   updated_account = await repository.update(account)
   ```

7. **Create Audit Log**
   ```python
   await _audit_account(
       account_id=account_id,
       action="VALIDATED",
       old_value=json.dumps({"availability_status": old_status}),
       new_value=json.dumps({"availability_status": new_status}),
       changed_by=validated_by,
       reason="Account validation performed"
   )
   ```

8. **Return Updated Account**
   - HTTP Status: 200 OK
   - Response: MT5AccountResponse with updated status

**Business Rules Applied:**
- RN-MT5-04: Availability and enablement are separate
- RN-MT5-05: Unavailable accounts cannot be used
- RN-MT5-11: Validation allowed before enabling
- RN-MT5-12: Invalid credentials marked with proper status

### 3.3 Account Enablement Process

**Service Method:** `MT5AccountService.enable_account()`

**Steps:**
1. **Get Account by ID**
   ```python
   account = await repository.get_by_id(account_id)
   if not account:
       raise ValueError(f"Account not found: {account_id}")
   ```

2. **Check Prerequisites**
   ```python
   success = account.enable()
   if not success:
       raise ValueError(
           f"Account cannot be enabled. "
           f"Availability: {account.availability_status.value}, "
           f"Lifecycle: {account.lifecycle_status.value}"
       )
   ```
   
   **enable() method checks:**
   - `availability_status == AVAILABLE`
   - `lifecycle_status == ACTIVE`

3. **Update Account**
   ```python
   account.is_enabled = True
   account.updated_at = datetime.utcnow()
   updated_account = await repository.update(account)
   ```

4. **Create Audit Log**
   ```python
   await _audit_account(
       account_id=account_id,
       action="ENABLED",
       old_value=json.dumps({"is_enabled": False}),
       new_value=json.dumps({"is_enabled": True}),
       changed_by=enabled_by,
       reason="Account enabled for operations"
   )
   ```

5. **Return Updated Account**
   - HTTP Status: 200 OK
   - Response: MT5AccountResponse with is_enabled=true

**Business Rules Applied:**
- RN-MT5-04: Availability and enablement are separate
- RN-MT5-05: Unavailable accounts cannot be enabled
- RN-MT5-07: All changes audited

### 3.4 Set Default for Environment Process

**Service Method:** `MT5AccountService.set_default_for_environment()`

**Steps:**
1. **Get Account by ID**
   ```python
   account = await repository.get_by_id(account_id)
   if not account:
       raise ValueError(f"Account not found: {account_id}")
   
   if account.lifecycle_status != LifecycleStatus.ACTIVE:
       raise ValueError("Cannot set inactive or archived account as default")
   ```

2. **Get All Accounts in Same Environment**
   ```python
   accounts_in_env = await repository.get_by_environment(
       account.environment_type,
       enabled_only=False
   )
   ```

3. **Unset Other Defaults**
   ```python
   for other_account in accounts_in_env:
       if other_account.id != account_id and other_account.is_default_for_environment:
           other_account.unset_default_for_environment()
           await repository.update(other_account)
           
           await _audit_account(
               account_id=other_account.id,
               action="UNSET_DEFAULT",
               old_value=json.dumps({"is_default_for_environment": True}),
               new_value=json.dumps({"is_default_for_environment": False}),
               changed_by=set_by,
               reason=f"Default replaced by account {account_id}"
           )
   ```

4. **Set This Account as Default**
   ```python
   account.set_default_for_environment()
   updated_account = await repository.update(account)
   ```

5. **Create Audit Log**
   ```python
   await _audit_account(
       account_id=account_id,
       action="SET_DEFAULT",
       old_value=json.dumps({"is_default_for_environment": False}),
       new_value=json.dumps({"is_default_for_environment": True}),
       changed_by=set_by,
       reason="Account set as default for environment"
   )
   ```

6. **Return Updated Account**
   - HTTP Status: 200 OK
   - Response: MT5AccountResponse with is_default_for_environment=true

**Business Rules Applied:**
- RN-MT5-08: Default account per environment
- RN-MT5-09: Only one default per environment
- RN-MT5-07: All changes audited

### 3.5 Account Archiving Process

**Service Method:** `MT5AccountService.archive_account()`

**Steps:**
1. **Get Account by ID**
   ```python
   account = await repository.get_by_id(account_id)
   if not account:
       raise ValueError(f"Account not found: {account_id}")
   ```

2. **Archive Account**
   ```python
   account.archive()
   # lifecycle_status = ARCHIVED
   # is_enabled = False
   # archived_at = datetime.utcnow()
   ```

3. **Persist Changes**
   ```python
   updated_account = await repository.update(account)
   ```

4. **Create Audit Log**
   ```python
   await _audit_account(
       account_id=account_id,
       action="ARCHIVED",
       old_value=json.dumps({
           "lifecycle_status": old_status,
           "is_enabled": account.is_enabled,
       }),
       new_value=json.dumps({
           "lifecycle_status": "ARCHIVED",
           "is_enabled": False,
           "archived_at": updated_account.archived_at.isoformat(),
       }),
       changed_by=archived_by,
       reason="Account archived"
   )
   ```

5. **Return Success Message**
   - HTTP Status: 200 OK
   - Response: MessageResponse

**Business Rules Applied:**
- RN-MT5-10: Archived accounts cannot be used
- RN-MT5-07: All changes audited
- Soft delete preserves history

---

## 4. Outputs

### 4.1 Account Response (Success)

**HTTP Status:** 200 OK or 201 Created

**Response Schema:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_name": "Demo Account - MetaQuotes",
  "broker_name": "MetaQuotes Software",
  "server_name": "MetaQuotes-Demo",
  "login": "10****44",  // Masked for security
  "terminal_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
  "environment_type": "DEMO",
  "is_enabled": false,
  "availability_status": "AVAILABLE",
  "lifecycle_status": "ACTIVE",
  "is_default_for_environment": true,
  "last_validation_at": "2026-04-05T10:30:00Z",
  "last_validation_status": "SUCCESS",
  "created_at": "2026-04-05T09:00:00Z",
  "updated_at": "2026-04-05T10:30:00Z",
  "archived_at": null
}
```

### 4.2 Account List Response

**HTTP Status:** 200 OK

**Response Schema:**
```json
{
  "accounts": [
    { /* MT5AccountResponse */ },
    { /* MT5AccountResponse */ }
  ],
  "total": 2
}
```

### 4.3 Validation Error Response

**HTTP Status:** 400 Bad Request

**Response Schema:**
```json
{
  "detail": "Account cannot be enabled. Availability: UNKNOWN, Lifecycle: ACTIVE"
}
```

### 4.4 Not Found Error Response

**HTTP Status:** 404 Not Found

**Response Schema:**
```json
{
  "detail": "Account not found: 550e8400-e29b-41d4-a716-446655440000"
}
```

### 4.5 Audit Log Response

**HTTP Status:** 200 OK

**Response Schema:**
```json
[
  {
    "id": "audit-log-uuid",
    "account_id": "account-uuid",
    "action": "CREATED",
    "old_value": null,
    "new_value": "{\"account_name\": \"Demo Account\", ...}",
    "changed_by": "api_user",
    "changed_at": "2026-04-05T09:00:00Z",
    "reason": "Account created via UI"
  },
  {
    "id": "audit-log-uuid-2",
    "account_id": "account-uuid",
    "action": "VALIDATED",
    "old_value": "{\"availability_status\": \"UNKNOWN\"}",
    "new_value": "{\"availability_status\": \"AVAILABLE\"}",
    "changed_by": "api_user",
    "changed_at": "2026-04-05T10:30:00Z",
    "reason": "Account validation performed"
  }
]
```

### 4.6 Validation Log Response

**HTTP Status:** 200 OK

**Response Schema:**
```json
[
  {
    "id": "validation-log-uuid",
    "account_id": "account-uuid",
    "validation_started_at": "2026-04-05T10:30:00Z",
    "validation_finished_at": "2026-04-05T10:30:05Z",
    "status": "SUCCESS",
    "error_message": null,
    "broker_response_summary": "{\"broker_name\": \"MetaQuotes Software\", \"server_name\": \"MetaQuotes-Demo\", \"account_type\": \"DEMO\", \"currency\": \"USD\"}"
  }
]
```

---

## 5. Error Handling

### 5.1 Validation Errors

| Error | HTTP Status | When |
|-------|-------------|------|
| "Account name cannot be empty" | 400 | Missing required field |
| "Terminal path must be an executable (.exe)" | 400 | Invalid terminal path |
| "Account cannot be enabled. Availability: UNKNOWN" | 400 | Enabling without validation |
| "Cannot validate archived account" | 400 | Operating on archived account |

### 5.2 Not Found Errors

| Error | HTTP Status | When |
|-------|-------------|------|
| "Account not found: {id}" | 404 | Invalid account ID |

### 5.3 Internal Server Errors

| Error | HTTP Status | When |
|-------|-------------|------|
| "Failed to initialize MT5" | 500 | MT5 terminal error |
| "Login failed" | 500 | MT5 authentication error |
| Database errors | 500 | Persistence layer errors |

---

## 6. Security Considerations

### 6.1 Password Handling

- **NEVER** store passwords in plain text in database
- **NEVER** return passwords in API responses
- **NEVER** log passwords
- **ALWAYS** encrypt passwords before storage
- **ALWAYS** mask login in UI responses

### 6.2 Current Implementation

```python
# TODO: Encrypt password before storing
password_secret_ref = request.password  # NOT SECURE - temporary
```

### 6.3 Production Implementation

```python
# Use secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
from src.infrastructure.config.secrets_manager import SecretsManager

secrets_manager = SecretsManager()
secret_ref = await secrets_manager.store_secret(
    secret_name=f"mt5-account-{account_id}-password",
    secret_value=request.password
)
account.password_secret_ref = secret_ref
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

- [ ] Test account creation with valid data
- [ ] Test account creation with invalid data (missing fields, bad terminal path)
- [ ] Test account validation with successful connection
- [ ] Test account validation with failed connection
- [ ] Test account enablement (success and failure cases)
- [ ] Test account disablement
- [ ] Test account archiving
- [ ] Test set default for environment (with and without existing default)
- [ ] Test audit log creation
- [ ] Test validation log creation

### 7.2 Integration Tests

- [ ] Test full create → validate → enable flow
- [ ] Test create → enable without validation (should fail)
- [ ] Test archive → validate (should fail)
- [ ] Test set default → verify other defaults unset
- [ ] Test MT5 gateway connection test

### 7.3 API Tests

- [ ] Test all endpoints with valid data
- [ ] Test all endpoints with invalid data
- [ ] Test error responses
- [ ] Test login masking in responses
- [ ] Test audit log retrieval
- [ ] Test validation log retrieval

---

## 8. Implementation Checklist

### Domain Layer ✅
- [x] MT5Account entity
- [x] MT5AccountAuditLog entity
- [x] MT5AccountValidationLog entity
- [x] IMT5AccountRepository interface
- [x] IMT5Gateway interface

### Application Layer ✅
- [x] MT5AccountService
  - [x] create_account
  - [x] validate_account
  - [x] enable_account
  - [x] disable_account
  - [x] archive_account
  - [x] set_default_for_environment
  - [x] get_account
  - [x] get_all_accounts
  - [x] get_accounts_by_environment
  - [x] get_operational_accounts
  - [x] get_default_account_for_environment

### Infrastructure Layer ✅
- [x] MT5AccountModel (SQLAlchemy)
- [x] MT5AccountAuditLogModel (SQLAlchemy)
- [x] MT5AccountValidationLogModel (SQLAlchemy)
- [x] MT5AccountRepository implementation
- [x] MT5Gateway implementation

### Presentation Layer ✅
- [x] MT5Account API schemas
- [x] MT5Account API routes
  - [x] GET / (list)
  - [x] GET /operational
  - [x] GET /{account_id}
  - [x] POST / (create)
  - [x] POST /{account_id}/validate
  - [x] POST /{account_id}/enable
  - [x] POST /{account_id}/disable
  - [x] POST /{account_id}/archive
  - [x] POST /{account_id}/set-default
  - [x] GET /{account_id}/audit-logs
  - [x] GET /{account_id}/validation-logs

### Database ✅
- [x] SQLAlchemy models
- [x] Database configuration
- [ ] Alembic migration (to be created)

### Tests ⏳
- [ ] Unit tests
- [ ] Integration tests
- [ ] API tests

---

## 9. Next Steps

1. **Create Alembic Migration**
   ```bash
   alembic revision --autogenerate -m "add_mt5_accounts_tables"
   alembic upgrade head
   ```

2. **Write Unit Tests**
   - Test all service methods
   - Test repository methods
   - Test domain entity methods

3. **Write Integration Tests**
   - Test full flows
   - Test MT5 gateway connection

4. **Update main.py**
   - Add MT5 accounts router to FastAPI app

5. **Create Frontend UI**
   - Configuration → MT5 Accounts page
   - List, create, edit, validate, enable, disable, archive

6. **Implement Secret Storage**
   - Integrate with secrets manager
   - Remove plaintext password storage

---

**End of Document**
