from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.core.config import settings
from app.api import router as api_router
from app.core.database import init_database, close_database
from app.services.reddit_monitor import RedditMonitor
from app.services.scheduler import start_monitoring_scheduler, stop_monitoring_scheduler

# Global variables
reddit_monitor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global reddit_monitor
    
    # Startup
    logger.info("Starting Brand Monitor application...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize Reddit monitor
        reddit_monitor = RedditMonitor()
        await reddit_monitor.initialize()
        logger.info("Reddit monitor initialized successfully")
        
        # Start monitoring scheduler
        await start_monitoring_scheduler(reddit_monitor)
        logger.info("Monitoring scheduler started successfully")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Brand Monitor application...")
    
    try:
        # Stop monitoring scheduler
        await stop_monitoring_scheduler()
        logger.info("Monitoring scheduler stopped")
        
        # Close database connections
        await close_database()
        logger.info("Database connections closed")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time brand monitoring agent for Reddit",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.core.database import get_database
        db = await get_database()
        await db.command("ping")
        
        # Check Reddit monitor status
        monitor_status = "active" if reddit_monitor and reddit_monitor.is_initialized else "inactive"
        
        return {
            "status": "healthy",
            "database": "connected",
            "reddit_monitor": monitor_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )