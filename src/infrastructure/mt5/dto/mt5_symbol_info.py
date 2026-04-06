"""
MT5 Symbol Info DTO for symbol discovery.
Infrastructure layer - data transfer object.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MT5SymbolInfo:
    """
    DTO representing a symbol discovered from MT5.
    
    Contains metadata about the symbol for classification.
    """
    symbol: str
    description: str
    path: str  # Symbol path/group in MT5
    digits: int
    trade_mode: int
    trade_contract_size: float
    currency_base: Optional[str] = None
    currency_profit: Optional[str] = None
    currency_margin: Optional[str] = None
    
    def __post_init__(self):
        """Validate and fix empty fields"""
        # If description is empty, use symbol as display name
        if not self.description or not self.description.strip():
            self.description = self.symbol
    
    @property
    def is_forex(self) -> bool:
        """Check if symbol is a forex pair"""
        return self.path.startswith("Forex\\") or (
            self.currency_base and len(self.currency_base) == 3 and
            self.currency_profit and len(self.currency_profit) == 3
        )
    
    @property
    def is_metal(self) -> bool:
        """Check if symbol is a metal (XAU, XAG, etc.)"""
        return self.symbol.startswith("XAU") or self.symbol.startswith("XAG") or \
               self.path.startswith("Metals\\")
    
    @property
    def is_energy(self) -> bool:
        """Check if symbol is energy (oil, gas, etc.)"""
        return self.symbol.startswith("USOIL") or self.symbol.startswith("NGAS") or \
               self.path.startswith("Energy\\")
    
    @property
    def is_crypto(self) -> bool:
        """Check if symbol is cryptocurrency"""
        return self.path.startswith("Crypto\\") or \
               "BTC" in self.symbol or "ETH" in self.symbol or \
               self.currency_base in ["BTC", "ETH"]
