"""
Asset Classifier Service - Classifies assets by type based on MT5 metadata.
Application layer - strategy pattern for asset classification.
"""

import logging
from typing import Dict, Type

from src.domain.entities.asset import AssetType
from src.infrastructure.mt5.dto.mt5_symbol_info import MT5SymbolInfo

logger = logging.getLogger(__name__)


class IAssetClassifier:
    """Interface for asset classification strategies"""
    
    def classify(self, symbol_info: MT5SymbolInfo) -> AssetType:
        """
        Classify an asset based on symbol information.
        
        Args:
            symbol_info: MT5 symbol metadata
            
        Returns:
            AssetType classification
        """
        ...


class PathBasedClassifier(IAssetClassifier):
    """Classifies assets based on MT5 symbol path"""
    
    def classify(self, symbol_info: MT5SymbolInfo) -> AssetType:
        """Classify by path"""
        path = symbol_info.path.lower()
        symbol = symbol_info.symbol.upper()
        
        # Check path first
        if "forex" in path:
            # Determine major vs minor
            if symbol_info.is_forex:
                majors = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
                if symbol in majors:
                    return AssetType.FOREX_MAJOR
                return AssetType.FOREX_MINOR
        
        if "metal" in path or symbol_info.is_metal:
            return AssetType.METAL
        
        if "energy" in path or symbol_info.is_energy:
            return AssetType.ENERGY
        
        if "crypto" in path or symbol_info.is_crypto:
            return AssetType.CRYPTO
        
        if "index" in path or "indices" in path:
            return AssetType.INDEX
        
        if "stock" in path or "shares" in path:
            return AssetType.STOCK
        
        return AssetType.UNKNOWN


class SymbolBasedClassifier(IAssetClassifier):
    """Classifies assets based on symbol name patterns"""
    
    # Major forex pairs
    MAJOR_PAIRS = {
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "USDCAD", "NZDUSD"
    }
    
    # Metal symbols
    METAL_PREFIXES = {"XAU", "XAG", "XPT", "XPD"}
    
    # Energy symbols
    ENERGY_SYMBOLS = {"USOIL", "UKOIL", "NGAS", "BRENT", "WTI"}
    
    def classify(self, symbol_info: MT5SymbolInfo) -> AssetType:
        """Classify by symbol name"""
        symbol = symbol_info.symbol.upper()
        
        # Check for metals
        for prefix in self.METAL_PREFIXES:
            if symbol.startswith(prefix):
                return AssetType.METAL
        
        # Check for energy
        if symbol in self.ENERGY_SYMBOLS:
            return AssetType.ENERGY
        
        # Check for major forex
        if symbol in self.MAJOR_PAIRS:
            return AssetType.FOREX_MAJOR
        
        # Check for forex (currency pairs)
        if len(symbol) >= 6 and symbol_info.is_forex:
            return AssetType.FOREX_MINOR
        
        # Check for crypto
        if "BTC" in symbol or "ETH" in symbol:
            return AssetType.CRYPTO
        
        return AssetType.UNKNOWN


class CompositeAssetClassifier:
    """
    Composite classifier that tries multiple strategies.
    Uses Chain of Responsibility pattern.
    """
    
    def __init__(self):
        self._classifiers: list[IAssetClassifier] = [
            PathBasedClassifier(),
            SymbolBasedClassifier(),
        ]
    
    def classify(self, symbol_info: MT5SymbolInfo) -> AssetType:
        """
        Classify asset using multiple strategies.
        
        Tries each classifier in order until one returns a non-UNKNOWN type.
        
        Args:
            symbol_info: MT5 symbol metadata
            
        Returns:
            AssetType classification
        """
        for classifier in self._classifiers:
            asset_type = classifier.classify(symbol_info)
            if asset_type != AssetType.UNKNOWN:
                return asset_type
        
        # Default to UNKNOWN if no classifier could determine type
        logger.warning(f"Could not classify asset: {symbol_info.symbol}")
        return AssetType.UNKNOWN
