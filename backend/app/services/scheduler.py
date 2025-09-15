import asyncio
from typing import Optional
from loguru import logger
from datetime import datetime, timedelta

from app.services.reddit_monitor import RedditMonitor
from app.core.config import settings

class MonitoringScheduler:
    """Scheduler for Reddit monitoring tasks"""
    
    def __init__(self, reddit_monitor: RedditMonitor):
        self.reddit_monitor = reddit_monitor
        self.is_running = False
        self.main_task: Optional[asyncio.Task] = None
        self.stats_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the monitoring scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        
        # Start main monitoring task
        self.main_task = asyncio.create_task(self._main_monitoring_loop())
        
        # Start stats update task
        self.stats_task = asyncio.create_task(self._stats_update_loop())
        
        logger.info("Monitoring scheduler started")
    
    async def stop(self):
        """Stop the monitoring scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel tasks
        if self.main_task:
            self.main_task.cancel()
            try:
                await self.main_task
            except asyncio.CancelledError:
                pass
        
        if self.stats_task:
            self.stats_task.cancel()
            try:
                await self.stats_task
            except asyncio.CancelledError:
                pass
        
        # Stop Reddit monitor
        await self.reddit_monitor.stop_monitoring()
        
        logger.info("Monitoring scheduler stopped")
    
    async def _main_monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting main monitoring loop")
        
        while self.is_running:
            try:
                # Perform monitoring scan
                mentions = await self.reddit_monitor.scan_for_mentions()
                
                if mentions:
                    logger.info(f"Processed {len(mentions)} new mentions")
                    
                    # Check for high-priority threats
                    await self._check_high_priority_threats(mentions)
                
                # Wait for next scan
                await asyncio.sleep(settings.monitor_interval)
                
            except asyncio.CancelledError:
                logger.info("Main monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in main monitoring loop: {e}")
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def _stats_update_loop(self):
        """Statistics update loop"""
        logger.info("Starting stats update loop")
        
        while self.is_running:
            try:
                # Update monitoring statistics every 5 minutes
                await self.reddit_monitor.update_monitoring_stats()
                
                # Wait 5 minutes
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("Stats update loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in stats update loop: {e}")
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def _check_high_priority_threats(self, mentions):
        """Check for high-priority threats and handle them"""
        try:
            from app.models.schemas import ThreatLevel
            
            high_priority_mentions = [
                mention for mention in mentions
                if mention.threat_analysis.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            ]
            
            if high_priority_mentions:
                logger.warning(f"Found {len(high_priority_mentions)} high-priority threats")
                
                for mention in high_priority_mentions:
                    await self._handle_high_priority_threat(mention)
                    
        except Exception as e:
            logger.error(f"Error checking high-priority threats: {e}")
    
    async def _handle_high_priority_threat(self, mention):
        """Handle a high-priority threat"""
        try:
            logger.warning(
                f"High-priority threat detected: {mention.reddit_post.id} "
                f"(Level: {mention.threat_analysis.threat_level.value}, "
                f"Score: {mention.threat_analysis.threat_score:.2f})"
            )
            
            # Here you could implement:
            # - Send notifications (email, Slack, etc.)
            # - Create alerts in external systems
            # - Trigger automated responses
            # - Escalate to human reviewers
            
            # For now, just log the details
            logger.info(
                f"Threat details - Subreddit: {mention.reddit_post.subreddit}, "
                f"Keywords: {mention.threat_analysis.keywords_matched}, "
                f"Categories: {mention.threat_analysis.threat_categories}"
            )
            
        except Exception as e:
            logger.error(f"Error handling high-priority threat: {e}")

# Global scheduler instance
_scheduler: Optional[MonitoringScheduler] = None

async def start_monitoring_scheduler(reddit_monitor: RedditMonitor):
    """Start the global monitoring scheduler"""
    global _scheduler
    
    if _scheduler:
        logger.warning("Scheduler already exists")
        return
    
    _scheduler = MonitoringScheduler(reddit_monitor)
    await _scheduler.start()

async def stop_monitoring_scheduler():
    """Stop the global monitoring scheduler"""
    global _scheduler
    
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None

def get_scheduler() -> Optional[MonitoringScheduler]:
    """Get the global scheduler instance"""
    return _scheduler