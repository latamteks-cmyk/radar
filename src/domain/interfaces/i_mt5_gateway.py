"""
MT5 Gateway interface for connection testing and metadata retrieval.
Part of the domain layer - defines contract for infrastructure implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from src.infrastructure.mt5.dto.mt5_symbol_info import MT5SymbolInfo


@dataclass
class MT5ConnectionTestResult:
    """Result of MT5 connection test"""
    success: bool
    account_info: Optional[dict] = None  # Account metadata (no credentials)
    error_message: Optional[str] = None
    broker_name: Optional[str] = None
    server_name: Optional[str] = None
    account_type: Optional[str] = None  # Demo, Live, etc.
    currency: Optional[str] = None
    balance: Optional[float] = None


class IMT5Gateway(ABC):
    """
    Gateway interface for MT5 operations.
    
    Defines the contract for connecting to MetaTrader 5 terminal,
    testing connections, retrieving account metadata, and discovering symbols.
    Infrastructure layer (MT5 Adapter) will implement this interface.
    """
    
    @abstractmethod
    async def test_connection(
        self,
        login: str,
        password: str,
        server: str,
        terminal_path: str
    ) -> MT5ConnectionTestResult:
        """
        Test connection to MT5 terminal with given credentials.
        
        Args:
            login: MT5 account login
            password: MT5 account password
            server: MT5 server name
            terminal_path: Path to MT5 terminal executable
            
        Returns:
            MT5ConnectionTestResult with success status and metadata
        """
        ...
    
    @abstractmethod
    async def get_account_info(
        self,
        login: str
    ) -> Optional[dict]:
        """
        Get account information from already-connected terminal.
        
        Args:
            login: MT5 account login
            
        Returns:
            Dictionary with account metadata or None if not found
        """
        ...
    
    @abstractmethod
    async def get_available_servers(self) -> list[str]:
        """
        Get list of available MT5 servers.
        
        Returns:
            List of server names configured in MT5
        """
        ...
    
    @abstractmethod
    async def verify_terminal_path(self, terminal_path: str) -> bool:
        """
        Verify that MT5 terminal exists at the given path.
        
        Args:
            terminal_path: Path to MT5 terminal executable
            
        Returns:
            True if terminal exists at path, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_available_symbols(self) -> List[MT5SymbolInfo]:
        """
        Get all available symbols from MT5.
        
        Returns:
            List of MT5SymbolInfo with symbol metadata
        """
        ...
    
    @abstractmethod
    async def get_symbol_info(self, symbol: str) -> Optional[MT5SymbolInfo]:
        """
        Get detailed information about a specific symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            MT5SymbolInfo if found, None otherwise
        """
        ...

