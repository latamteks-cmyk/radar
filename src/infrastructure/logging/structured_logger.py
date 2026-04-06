"""
Structured logging configuration with correlation_id support.
All logs are JSON-formatted for easy parsing and analysis.
"""

import logging
import sys
from typing import Any, Dict, Optional
import structlog
from structlog.types import Processor


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Standard logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if not is_dev_mode() else structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured structlog BoundLogger instance
    """
    return structlog.get_logger(name)


def is_dev_mode() -> bool:
    """Check if running in development mode"""
    from src.infrastructure.config.settings import settings
    return settings.APP_ENV == "development"


def add_correlation_id(correlation_id: str) -> None:
    """
    Add correlation_id to the current context.
    This will be included in all subsequent log messages.
    
    Args:
        correlation_id: UUID v4 correlation identifier
    """
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def add_context(**kwargs: Any) -> None:
    """
    Add arbitrary context to the current logging context.
    
    Args:
        **kwargs: Key-value pairs to add to context
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables"""
    structlog.contextvars.clear_contextvars()


# Convenience function for backward compatibility
def setup_basic_logging():
    """Setup basic logging without structlog (fallback)"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
