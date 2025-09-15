from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from loguru import logger

from app.models.schemas import APIResponse, MonitoringStats
from app.services.reddit_monitor import RedditMonitor
from app.services.scheduler import get_scheduler

router = APIRouter()

# Global variable to store reddit monitor instance
_reddit_monitor = None

async def get_reddit_monitor() -> RedditMonitor:
    """Dependency to get Reddit monitor instance"""
    global _reddit_monitor
    if not _reddit_monitor:
        _reddit_monitor = RedditMonitor()
        await _reddit_monitor.initialize()
    if not _reddit_monitor.is_initialized:
        raise HTTPException(status_code=503, detail="Reddit monitor not available")
    return _reddit_monitor

@router.get("/status", response_model=APIResponse)
async def get_monitoring_status(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get current monitoring status"""
    try:
        scheduler = get_scheduler()
        
        status_data = {
            "monitor_initialized": monitor.is_initialized,
            "scheduler_running": scheduler.is_running if scheduler else False,
            "reddit_client_status": "connected" if monitor.reddit_client.is_initialized else "disconnected",
            "ai_analyzer_status": "ready" if monitor.ai_analyzer.is_initialized else "not_ready"
        }
        
        return APIResponse(
            success=True,
            message="Monitoring status retrieved",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=APIResponse)
async def get_monitoring_stats(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get monitoring statistics"""
    try:
        stats = await monitor.get_monitoring_stats()
        
        if not stats:
            # Return empty stats if none exist
            stats = MonitoringStats(
                total_mentions=0,
                threat_distribution={},
                sentiment_distribution={},
                top_subreddits=[],
                trending_keywords=[]
            )
        
        return APIResponse(
            success=True,
            message="Monitoring statistics retrieved",
            data=stats.dict()
        )
        
    except Exception as e:
        logger.error(f"Error getting monitoring stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start", response_model=APIResponse)
async def start_monitoring(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Start the monitoring process"""
    try:
        scheduler = get_scheduler()
        
        if not scheduler:
            raise HTTPException(status_code=503, detail="Scheduler not available")
        
        if scheduler.is_running:
            return APIResponse(
                success=True,
                message="Monitoring is already running",
                data={"status": "already_running"}
            )
        
        await scheduler.start()
        
        return APIResponse(
            success=True,
            message="Monitoring started successfully",
            data={"status": "started"}
        )
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=APIResponse)
async def stop_monitoring():
    """Stop the monitoring process"""
    try:
        scheduler = get_scheduler()
        
        if not scheduler:
            return APIResponse(
                success=True,
                message="Monitoring is not running",
                data={"status": "not_running"}
            )
        
        if not scheduler.is_running:
            return APIResponse(
                success=True,
                message="Monitoring is already stopped",
                data={"status": "already_stopped"}
            )
        
        await scheduler.stop()
        
        return APIResponse(
            success=True,
            message="Monitoring stopped successfully",
            data={"status": "stopped"}
        )
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart", response_model=APIResponse)
async def restart_monitoring(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Restart the monitoring process"""
    try:
        scheduler = get_scheduler()
        
        if not scheduler:
            raise HTTPException(status_code=503, detail="Scheduler not available")
        
        # Stop if running
        if scheduler.is_running:
            await scheduler.stop()
        
        # Start again
        await scheduler.start()
        
        return APIResponse(
            success=True,
            message="Monitoring restarted successfully",
            data={"status": "restarted"}
        )
        
    except Exception as e:
        logger.error(f"Error restarting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-stats", response_model=APIResponse)
async def update_monitoring_stats(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Manually trigger stats update"""
    try:
        await monitor.update_monitoring_stats()
        
        return APIResponse(
            success=True,
            message="Monitoring statistics updated successfully",
            data={"status": "updated"}
        )
        
    except Exception as e:
        logger.error(f"Error updating monitoring stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=APIResponse)
async def monitoring_health_check(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Detailed health check for monitoring components"""
    try:
        health_data = {
            "overall_status": "healthy",
            "components": {
                "reddit_monitor": {
                    "status": "healthy" if monitor.is_initialized else "unhealthy",
                    "initialized": monitor.is_initialized
                },
                "reddit_client": {
                    "status": "healthy" if monitor.reddit_client.is_initialized else "unhealthy",
                    "initialized": monitor.reddit_client.is_initialized
                },
                "ai_analyzer": {
                    "status": "healthy" if monitor.ai_analyzer.is_initialized else "unhealthy",
                    "initialized": monitor.ai_analyzer.is_initialized
                }
            }
        }
        
        # Check scheduler
        scheduler = get_scheduler()
        health_data["components"]["scheduler"] = {
            "status": "healthy" if scheduler and scheduler.is_running else "unhealthy",
            "running": scheduler.is_running if scheduler else False
        }
        
        # Check database connectivity
        try:
            from app.core.database import get_database
            db = await get_database()
            await db.command("ping")
            health_data["components"]["database"] = {
                "status": "healthy",
                "connected": True
            }
        except Exception as db_error:
            health_data["components"]["database"] = {
                "status": "unhealthy",
                "connected": False,
                "error": str(db_error)
            }
            health_data["overall_status"] = "degraded"
        
        # Determine overall status
        unhealthy_components = [
            name for name, component in health_data["components"].items()
            if component["status"] == "unhealthy"
        ]
        
        if unhealthy_components:
            health_data["overall_status"] = "unhealthy"
            health_data["unhealthy_components"] = unhealthy_components
        
        return APIResponse(
            success=True,
            message=f"Health check completed - Status: {health_data['overall_status']}",
            data=health_data
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_model=APIResponse)
async def get_monitoring_config():
    """Get current monitoring configuration"""
    try:
        from app.core.config import settings
        
        config_data = {
            "brand_keywords": settings.brand_keywords,
            "monitor_subreddits": settings.monitor_subreddits,
            "monitor_interval": settings.monitor_interval,
            "threat_threshold": settings.threat_threshold,
            "sentiment_model": settings.sentiment_model,
            "threat_detection_model": settings.threat_detection_model
        }
        
        return APIResponse(
            success=True,
            message="Monitoring configuration retrieved",
            data=config_data
        )
        
    except Exception as e:
        logger.error(f"Error getting monitoring config: {e}")
        raise HTTPException(status_code=500, detail=str(e))