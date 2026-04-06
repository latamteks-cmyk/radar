"""
Radar Trading Intelligence Platform
Main entry point for the FastAPI application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import settings
from src.infrastructure.logging.structured_logger import setup_logging

# Setup structured logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Radar Trading Intelligence Platform")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Trading Mode: {settings.TRADING_MODE}")
    
    # TODO: Initialize database connection
    # TODO: Initialize MT5 adapter
    # TODO: Load configuration
    # TODO: Start scheduler
    
    yield
    
    # Shutdown
    logger.info("Shutting down Radar Trading Intelligence Platform")
    # TODO: Cleanup resources
    # TODO: Close database connections
    # TODO: Disconnect MT5


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Radar Trading Intelligence Platform - Sistema modular de análisis, priorización, control de riesgo y ejecución asistida/automatizada",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    from src.presentation.api.routes import mt5_accounts
    from src.presentation.api.routes import assets
    app.include_router(mt5_accounts.router)
    app.include_router(assets.router)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "ok",
            "environment": settings.APP_ENV,
            "trading_mode": settings.TRADING_MODE,
        }
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Radar Trading Intelligence Platform",
            "version": "0.1.0",
            "docs": "/docs",
        }
    
    return app


# Create app instance
app = create_app()


def main():
    """CLI entry point"""
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
