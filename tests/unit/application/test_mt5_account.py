"""
Unit tests for MT5 Account domain entities.
Tests business logic, state transitions, and validation.
"""

import pytest
from datetime import datetime
from uuid import UUID

from src.domain.entities.mt5_account import (
    MT5Account,
    EnvironmentType,
    AvailabilityStatus,
    LifecycleStatus,
    ValidationStatus,
)


class TestMT5AccountCreation:
    """Test MT5Account entity creation and validation"""
    
    def test_create_account_with_valid_data(self):
        """Test creating account with valid data"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        assert account.account_name == "Test Demo Account"
        assert account.broker_name == "MetaQuotes"
        assert account.environment_type == EnvironmentType.DEMO
        assert account.is_enabled is False
        assert account.availability_status == AvailabilityStatus.UNKNOWN
        assert account.lifecycle_status == LifecycleStatus.ACTIVE
        assert account.is_default_for_environment is False
        assert isinstance(account.id, UUID)
        assert isinstance(account.created_at, datetime)
    
    def test_create_account_empty_name_fails(self):
        """Test that empty account name raises error"""
        with pytest.raises(ValueError, match="Account name cannot be empty"):
            MT5Account(
                account_name="",
                broker_name="MetaQuotes",
                server_name="MetaQuotes-Demo",
                login="12345678",
                password_secret_ref="encrypted_password_ref",
                terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
                environment_type=EnvironmentType.DEMO,
            )
    
    def test_create_account_empty_login_fails(self):
        """Test that empty login raises error"""
        with pytest.raises(ValueError, match="Login cannot be empty"):
            MT5Account(
                account_name="Test Demo Account",
                broker_name="MetaQuotes",
                server_name="MetaQuotes-Demo",
                login="",
                password_secret_ref="encrypted_password_ref",
                terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
                environment_type=EnvironmentType.DEMO,
            )
    
    def test_create_account_empty_server_fails(self):
        """Test that empty server name raises error"""
        with pytest.raises(ValueError, match="Server name cannot be empty"):
            MT5Account(
                account_name="Test Demo Account",
                broker_name="MetaQuotes",
                server_name="",
                login="12345678",
                password_secret_ref="encrypted_password_ref",
                terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
                environment_type=EnvironmentType.DEMO,
            )
    
    def test_create_account_empty_terminal_path_fails(self):
        """Test that empty terminal path raises error"""
        with pytest.raises(ValueError, match="Terminal path cannot be empty"):
            MT5Account(
                account_name="Test Demo Account",
                broker_name="MetaQuotes",
                server_name="MetaQuotes-Demo",
                login="12345678",
                password_secret_ref="encrypted_password_ref",
                terminal_path="",
                environment_type=EnvironmentType.DEMO,
            )


class TestMT5AccountValidation:
    """Test MT5Account validation state transitions"""
    
    def test_validate_account_success(self):
        """Test successful validation updates status correctly"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        
        assert account.availability_status == AvailabilityStatus.AVAILABLE
        assert account.last_validation_status == ValidationStatus.SUCCESS
        assert account.last_validation_at is not None
    
    def test_validate_account_failure(self):
        """Test failed validation updates status correctly"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.FAILED)
        
        assert account.availability_status == AvailabilityStatus.UNAVAILABLE
        assert account.last_validation_status == ValidationStatus.FAILED


class TestMT5AccountEnablement:
    """Test MT5Account enable/disable functionality"""
    
    def test_enable_account_success(self):
        """Test enabling account when available"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        # First validate to make it available
        account.validate_account(ValidationStatus.SUCCESS)
        
        # Then enable
        result = account.enable()
        
        assert result is True
        assert account.is_enabled is True
        assert account.is_operational() is True
    
    def test_enable_account_not_available_fails(self):
        """Test enabling account when not available fails"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        # Try to enable without validation
        result = account.enable()
        
        assert result is False
        assert account.is_enabled is False
    
    def test_enable_archived_account_fails(self):
        """Test enabling archived account fails"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        # Archive the account
        account.archive()
        
        # Try to enable
        result = account.enable()
        
        assert result is False
        assert account.is_enabled is False
    
    def test_disable_account(self):
        """Test disabling account"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        account.enable()
        
        # Disable
        account.disable()
        
        assert account.is_enabled is False
        assert account.availability_status == AvailabilityStatus.AVAILABLE


class TestMT5AccountArchival:
    """Test MT5Account archival functionality"""
    
    def test_archive_account(self):
        """Test archiving account"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        account.enable()
        
        # Archive
        account.archive()
        
        assert account.lifecycle_status == LifecycleStatus.ARCHIVED
        assert account.is_enabled is False
        assert account.archived_at is not None
        assert account.is_operational() is False
    
    def test_activate_archived_account_fails(self):
        """Test activating archived account fails"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.archive()
        
        with pytest.raises(ValueError, match="Cannot activate an archived account"):
            account.activate()
    
    def test_activate_inactive_account(self):
        """Test activating inactive account"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.deactivate()
        account.activate()
        
        assert account.lifecycle_status == LifecycleStatus.ACTIVE


class TestMT5AccountDefaultEnvironment:
    """Test MT5Account default for environment functionality"""
    
    def test_set_default_for_environment(self):
        """Test setting account as default for environment"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.set_default_for_environment()
        
        assert account.is_default_for_environment is True
    
    def test_unset_default_for_environment(self):
        """Test unsetting account as default for environment"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.set_default_for_environment()
        account.unset_default_for_environment()
        
        assert account.is_default_for_environment is False


class TestMT5AccountOperational:
    """Test MT5Account operational status checks"""
    
    def test_is_operational_true(self):
        """Test account is operational when all conditions met"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        account.enable()
        
        assert account.is_operational() is True
    
    def test_is_operational_false_when_not_enabled(self):
        """Test account is not operational when not enabled"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        # Don't enable
        
        assert account.is_operational() is False
    
    def test_is_operational_false_when_archived(self):
        """Test account is not operational when archived"""
        account = MT5Account(
            account_name="Test Demo Account",
            broker_name="MetaQuotes",
            server_name="MetaQuotes-Demo",
            login="12345678",
            password_secret_ref="encrypted_password_ref",
            terminal_path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            environment_type=EnvironmentType.DEMO,
        )
        
        account.validate_account(ValidationStatus.SUCCESS)
        account.enable()
        account.archive()
        
        assert account.is_operational() is False
