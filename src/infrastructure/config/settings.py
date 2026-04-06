"""
Application settings and configuration management.
Loads configuration from environment variables and .env files.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "radar-trading-platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "change-this-secret-key"
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "radar_trading"
    DB_USER: str = "radar_user"
    DB_PASSWORD: str = Field(..., description="Database password")
    
    # Redis (optional cache)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # MT5 Connection
    MT5_PATH: str = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    MT5_LOGIN: str = ""
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""
    MT5_TIMEOUT: int = 30000
    
    # LLM API
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4"
    LLM_TIMEOUT: int = 60
    LLM_MAX_TOKENS: int = 2000
    
    # ML Models
    ML_MODEL_PATH: str = "./models"
    ML_MODEL_VERSION: str = "1.0.0"
    
    # Trading Mode
    TRADING_MODE: str = "paper"  # monitor_only | paper | live
    
    # Risk Settings
    MAX_DAILY_LOSS: float = 1000.0
    MAX_POSITION_SIZE: float = 0.02  # 2% of account
    MAX_OPEN_POSITIONS: int = 3
    
    @property
    def database_url(self) -> str:
        """Construct database URL from settings"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        """Construct async database URL from settings"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from settings"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
