"""
MT5 Gateway implementation for connection testing and symbol discovery.
Infrastructure layer - implements IMT5Gateway interface.
"""

import logging
import os
from typing import List, Optional
from src.domain.interfaces.i_mt5_gateway import IMT5Gateway, MT5ConnectionTestResult
from src.infrastructure.mt5.dto.mt5_symbol_info import MT5SymbolInfo

logger = logging.getLogger(__name__)


class MT5Gateway(IMT5Gateway):
    """
    Implementation of MT5 Gateway using MetaTrader5 Python package.
    
    Handles connection testing, metadata retrieval, and symbol discovery from MT5 terminal.
    """
    
    def __init__(self):
        """Initialize gateway"""
        self._initialized = False
    
    def _ensure_initialized(self) -> bool:
        """
        Ensure MT5 is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        import MetaTrader5 as mt5
        
        if not self._initialized:
            if not mt5.initialize():
                logger.error("Failed to initialize MT5")
                return False
            self._initialized = True
        
        return True
    
    def _shutdown(self):
        """Shutdown MT5 connection"""
        import MetaTrader5 as mt5
        
        if self._initialized:
            mt5.shutdown()
            self._initialized = False
    
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
        import MetaTrader5 as mt5
        
        logger.info(f"Testing MT5 connection: login={login}, server={server}")
        
        # Verify terminal exists
        if not await self.verify_terminal_path(terminal_path):
            return MT5ConnectionTestResult(
                success=False,
                error_message=f"Terminal not found at path: {terminal_path}"
            )
        
        # Set terminal path
        if not mt5.initialize(path=terminal_path):
            error_msg = f"Failed to initialize MT5 at {terminal_path}. Error: {mt5.last_error()}"
            logger.error(error_msg)
            return MT5ConnectionTestResult(
                success=False,
                error_message=error_msg
            )
        
        try:
            # Try to login with credentials
            login_result = mt5.login(login=login, password=password, server=server)
            
            if not login_result:
                error_msg = f"Login failed. Error: {mt5.last_error()}"
                logger.warning(error_msg)
                return MT5ConnectionTestResult(
                    success=False,
                    error_message=error_msg
                )
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                error_msg = "Failed to retrieve account info"
                logger.error(error_msg)
                return MT5ConnectionTestResult(
                    success=False,
                    error_message=error_msg
                )
            
            # Build result with metadata (no sensitive data)
            result = MT5ConnectionTestResult(
                success=True,
                account_info={
                    "login": account_info.login,
                    "trade_mode": account_info.trade_mode,
                    "balance": account_info.balance,
                    "currency": account_info.currency,
                    "server": account_info.server,
                    "company": account_info.company,
                    "name": account_info.name,
                },
                broker_name=account_info.company,
                server_name=account_info.server,
                account_type="DEMO" if account_info.trade_mode == 0 else "LIVE",
                currency=account_info.currency,
                balance=account_info.balance,
            )
            
            logger.info(f"MT5 connection test successful: {account_info.login}@{account_info.server}")
            return result
            
        except Exception as e:
            error_msg = f"Connection test failed with exception: {e}"
            logger.error(error_msg)
            return MT5ConnectionTestResult(
                success=False,
                error_message=error_msg
            )
        finally:
            # Shutdown MT5 connection
            mt5.shutdown()
    
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
        import MetaTrader5 as mt5
        
        try:
            account_info = mt5.account_info()
            if account_info and str(account_info.login) == str(login):
                return {
                    "login": account_info.login,
                    "trade_mode": account_info.trade_mode,
                    "balance": account_info.balance,
                    "currency": account_info.currency,
                    "server": account_info.server,
                    "company": account_info.company,
                    "name": account_info.name,
                }
            return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def get_available_servers(self) -> list[str]:
        """
        Get list of available MT5 servers.
        
        Note: MT5 doesn't provide a direct API for this.
        Returns common servers or configured servers.
        
        Returns:
            List of server names
        """
        import MetaTrader5 as mt5
        
        try:
            # This is a simplified implementation
            # In reality, you might need to read from config or registry
            if mt5.initialize():
                account_info = mt5.account_info()
                if account_info:
                    return [account_info.server]
                mt5.shutdown()
        except Exception as e:
            logger.error(f"Error getting servers: {e}")
        
        # Return empty list if cannot determine
        return []
    
    async def verify_terminal_path(self, terminal_path: str) -> bool:
        """
        Verify that MT5 terminal exists at the given path.
        
        Args:
            terminal_path: Path to MT5 terminal executable
            
        Returns:
            True if terminal exists at path, False otherwise
        """
        # Check if file exists
        if not terminal_path:
            return False
        
        # For Windows, check if .exe exists
        if not os.path.exists(terminal_path):
            logger.warning(f"Terminal path does not exist: {terminal_path}")
            return False
        
        # Additional check: verify it's an executable
        if not terminal_path.endswith('.exe'):
            logger.warning(f"Terminal path is not an executable: {terminal_path}")
            return False
        
        return True
    
    async def get_available_symbols(self) -> List[MT5SymbolInfo]:
        """
        Get all available symbols from MT5.
        
        Returns:
            List of MT5SymbolInfo with symbol metadata
        """
        import MetaTrader5 as mt5
        
        logger.info("Retrieving available symbols from MT5")
        
        # Ensure MT5 is initialized
        if not self._ensure_initialized():
            logger.error("MT5 not initialized, cannot retrieve symbols")
            return []
        
        try:
            # Get all symbols
            symbols = mt5.symbols_get()
            
            if not symbols:
                logger.warning("No symbols returned from MT5")
                return []
            
            # Convert to DTOs
            symbol_infos = []
            for symbol in symbols:
                symbol_info = MT5SymbolInfo(
                    symbol=symbol.name,
                    description=symbol.description,
                    path=symbol.path if hasattr(symbol, 'path') else "",
                    digits=symbol.digits,
                    trade_mode=symbol.trade_mode,
                    trade_contract_size=symbol.trade_contract_size,
                    currency_base=symbol.currency_base,
                    currency_profit=symbol.currency_profit,
                    currency_margin=symbol.currency_margin,
                )
                symbol_infos.append(symbol_info)
            
            logger.info(f"Retrieved {len(symbol_infos)} symbols from MT5")
            return symbol_infos
            
        except Exception as e:
            error_msg = f"Failed to retrieve symbols: {e}"
            logger.error(error_msg)
            return []
    
    async def get_symbol_info(self, symbol: str) -> Optional[MT5SymbolInfo]:
        """
        Get detailed information about a specific symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            MT5SymbolInfo if found, None otherwise
        """
        import MetaTrader5 as mt5
        
        # Ensure MT5 is initialized
        if not self._ensure_initialized():
            logger.error("MT5 not initialized, cannot retrieve symbol info")
            return None
        
        try:
            # Get symbol info
            symbol_obj = mt5.symbol_info(symbol)
            
            if not symbol_obj:
                logger.warning(f"Symbol not found: {symbol}")
                return None
            
            # Convert to DTO
            return MT5SymbolInfo(
                symbol=symbol_obj.name,
                description=symbol_obj.description,
                path=symbol_obj.path if hasattr(symbol_obj, 'path') else "",
                digits=symbol_obj.digits,
                trade_mode=symbol_obj.trade_mode,
                trade_contract_size=symbol_obj.trade_contract_size,
                currency_base=symbol_obj.currency_base,
                currency_profit=symbol_obj.currency_profit,
                currency_margin=symbol_obj.currency_margin,
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve symbol info for {symbol}: {e}"
            logger.error(error_msg)
            return None

