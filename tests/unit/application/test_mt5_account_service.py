"""
Unit tests for MT5 Account Service.
Tests application layer business logic with mocked dependencies.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.configuration.services.mt5_account_service import MT5AccountService
from src.domain.entities.mt5_account import (
    MT5Account,
    EnvironmentType,
    AvailabilityStatus,
    LifecycleStatus,
    ValidationStatus,
)
from src.domain.interfaces.i_mt5_gateway import MT5ConnectionTestResult


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
    return MT5AccountService(mock_repository, mock_gateway)


@pytest.fixture
def sample_account():
    """Create a sample MT5 account for testing"""
    return MT5Account(
        id=uuid4(),
        account_name="Test Demo Account",
        broker_name="MetaQuotes",
        server_name="MetaQuotes-Demo",
        login="12345678",
        password_secret_ref="encrypted_password_ref",
        terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
        environment_type=EnvironmentType.DEMO,
    )


class TestMT5AccountServiceCreate:
    """Test MT5AccountService.create_account"""
    
    @pytest.mark.asyncio
    async def test_create_account_success(self, service, mock_repository):
        """Test creating account successfully"""
        # Arrange
        created_account = MT5Account(
            id=uuid4(),
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        mock_repository.create = AsyncMock(return_value=created_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.create_account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
            created_by="test_user"
        )
        
        # Assert
        assert result == created_account
        mock_repository.create.assert_called_once()
        mock_repository.log_audit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_account_logs_audit(self, service, mock_repository):
        """Test that creating account logs audit entry"""
        # Arrange
        created_account = MT5Account(
            id=uuid4(),
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        mock_repository.create = AsyncMock(return_value=created_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        await service.create_account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
            created_by="test_user"
        )
        
        # Assert
        audit_call = mock_repository.log_audit.call_args
        assert audit_call is not None
        audit_log = audit_call[0][0]
        assert audit_log.action == "CREATED"
        assert audit_log.changed_by == "test_user"


class TestMT5AccountServiceValidate:
    """Test MT5AccountService.validate_account"""
    
    @pytest.mark.asyncio
    async def test_validate_account_success(self, service, mock_repository, mock_gateway, sample_account):
        """Test validating account with successful connection"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_validation = AsyncMock()
        mock_repository.log_audit = AsyncMock()
        
        mock_gateway.test_connection = AsyncMock(return_value=MT5ConnectionTestResult(
            success=True,
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            account_type="DEMO",
            currency="USD",
            balance=10000.0
        ))
        
        # Act
        result = await service.validate_account(
            account_id=sample_account.id,
            password="test_password",
            validated_by="test_user"
        )
        
        # Assert
        assert result.availability_status == AvailabilityStatus.AVAILABLE
        assert result.last_validation_status == ValidationStatus.SUCCESS
        mock_gateway.test_connection.assert_called_once()
        mock_repository.log_validation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_account_not_found(self, service, mock_repository):
        """Test validating non-existent account raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            await service.validate_account(
                account_id=uuid4(),
                password="test_password"
            )
    
    @pytest.mark.asyncio
    async def test_validate_archived_account_fails(self, service, mock_repository, sample_account):
        """Test validating archived account raises error"""
        # Arrange
        sample_account.archive()
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot validate archived account"):
            await service.validate_account(
                account_id=sample_account.id,
                password="test_password"
            )
    
    @pytest.mark.asyncio
    async def test_validate_account_connection_failure(self, service, mock_repository, mock_gateway, sample_account):
        """Test validating account with connection failure"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_validation = AsyncMock()
        mock_repository.log_audit = AsyncMock()
        
        mock_gateway.test_connection = AsyncMock(return_value=MT5ConnectionTestResult(
            success=False,
            error_message="Invalid credentials"
        ))
        
        # Act
        result = await service.validate_account(
            account_id=sample_account.id,
            password="wrong_password",
            validated_by="test_user"
        )
        
        # Assert
        assert result.availability_status == AvailabilityStatus.INVALID_CREDENTIALS
        assert result.last_validation_status == ValidationStatus.FAILED


class TestMT5AccountServiceEnable:
    """Test MT5AccountService.enable_account"""
    
    @pytest.mark.asyncio
    async def test_enable_account_success(self, service, mock_repository, sample_account):
        """Test enabling account successfully"""
        # Arrange
        sample_account.validate_account(ValidationStatus.SUCCESS)
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.enable_account(
            account_id=sample_account.id,
            enabled_by="test_user"
        )
        
        # Assert
        assert result.is_enabled is True
        mock_repository.log_audit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enable_account_not_found(self, service, mock_repository):
        """Test enabling non-existent account raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            await service.enable_account(account_id=uuid4())
    
    @pytest.mark.asyncio
    async def test_enable_account_not_available(self, service, mock_repository, sample_account):
        """Test enabling account that hasn't been validated raises error"""
        # Arrange
        # Account is in UNKNOWN status (not validated yet)
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Account cannot be enabled"):
            await service.enable_account(account_id=sample_account.id)


class TestMT5AccountServiceDisable:
    """Test MT5AccountService.disable_account"""
    
    @pytest.mark.asyncio
    async def test_disable_account_success(self, service, mock_repository, sample_account):
        """Test disabling account successfully"""
        # Arrange
        sample_account.is_enabled = True
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.disable_account(
            account_id=sample_account.id,
            disabled_by="test_user"
        )
        
        # Assert
        assert result.is_enabled is False
    
    @pytest.mark.asyncio
    async def test_disable_account_not_found(self, service, mock_repository):
        """Test disabling non-existent account raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            await service.disable_account(account_id=uuid4())


class TestMT5AccountServiceArchive:
    """Test MT5AccountService.archive_account"""
    
    @pytest.mark.asyncio
    async def test_archive_account_success(self, service, mock_repository, sample_account):
        """Test archiving account successfully"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.archive_account(
            account_id=sample_account.id,
            archived_by="test_user"
        )
        
        # Assert
        assert result.lifecycle_status == LifecycleStatus.ARCHIVED
        assert result.is_enabled is False
        assert result.archived_at is not None
    
    @pytest.mark.asyncio
    async def test_archive_account_not_found(self, service, mock_repository):
        """Test archiving non-existent account raises error"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            await service.archive_account(account_id=uuid4())


class TestMT5AccountServiceDefault:
    """Test MT5AccountService.set_default_for_environment"""
    
    @pytest.mark.asyncio
    async def test_set_default_success(self, service, mock_repository, sample_account):
        """Test setting account as default for environment"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.get_by_environment = AsyncMock(return_value=[])
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        result = await service.set_default_for_environment(
            account_id=sample_account.id,
            set_by="test_user"
        )
        
        # Assert
        assert result.is_default_for_environment is True
    
    @pytest.mark.asyncio
    async def test_set_default_unsets_others(self, service, mock_repository, sample_account):
        """Test setting default unsets other defaults in same environment"""
        # Arrange
        other_account = MT5Account(
            id=uuid4(),
            account_name="Other Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="87654321",
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
            is_default_for_environment=True,
        )
        
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        mock_repository.get_by_environment = AsyncMock(return_value=[other_account])
        mock_repository.update = AsyncMock(return_value=sample_account)
        mock_repository.log_audit = AsyncMock()
        
        # Act
        await service.set_default_for_environment(
            account_id=sample_account.id,
            set_by="test_user"
        )
        
        # Assert
        # Other account should have been unset
        assert other_account.is_default_for_environment is False
        # New account should be set as default
        assert sample_account.is_default_for_environment is True
    
    @pytest.mark.asyncio
    async def test_set_default_inactive_account_fails(self, service, mock_repository, sample_account):
        """Test setting inactive account as default raises error"""
        # Arrange
        sample_account.deactivate()
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot set inactive or archived account as default"):
            await service.set_default_for_environment(account_id=sample_account.id)


class TestMT5AccountServiceQueries:
    """Test MT5AccountService query methods"""
    
    @pytest.mark.asyncio
    async def test_get_account(self, service, mock_repository, sample_account):
        """Test getting account by ID"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=sample_account)
        
        # Act
        result = await service.get_account(sample_account.id)
        
        # Assert
        assert result == sample_account
    
    @pytest.mark.asyncio
    async def test_get_account_not_found(self, service, mock_repository):
        """Test getting non-existent account returns None"""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.get_account(uuid4())
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_accounts(self, service, mock_repository):
        """Test getting all accounts"""
        # Arrange
        accounts = [MT5Account(
            account_name=f"Account {i}",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login=str(i),
            password_secret_ref="encrypted_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        ) for i in range(3)]
        
        mock_repository.get_all = AsyncMock(return_value=accounts)
        
        # Act
        result = await service.get_all_accounts()
        
        # Assert
        assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_get_operational_accounts(self, service, mock_repository):
        """Test getting operational accounts"""
        # Arrange
        operational_accounts = []
        mock_repository.get_operational_accounts = AsyncMock(return_value=operational_accounts)
        
        # Act
        result = await service.get_operational_accounts()
        
        # Assert
        assert result == operational_accounts
