from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.models.schemas import (
    BrandMention, APIResponse, ThreatLevel, SentimentType
)
from app.services.reddit_monitor import RedditMonitor

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

@router.get("/", response_model=APIResponse)
async def get_mentions(
    limit: int = Query(50, ge=1, le=200, description="Number of mentions to retrieve"),
    skip: int = Query(0, ge=0, description="Number of mentions to skip"),
    threat_level: Optional[ThreatLevel] = Query(None, description="Filter by threat level"),
    sentiment: Optional[SentimentType] = Query(None, description="Filter by sentiment"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get brand mentions with optional filtering"""
    try:
        mentions = await monitor.get_mentions(
            limit=limit,
            skip=skip,
            threat_level=threat_level,
            sentiment=sentiment,
            subreddit=subreddit,
            start_date=start_date,
            end_date=end_date
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(mentions)} mentions",
            data={
                "mentions": [mention.dict() for mention in mentions],
                "total": len(mentions),
                "limit": limit,
                "skip": skip
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting mentions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{mention_id}", response_model=APIResponse)
async def get_mention(
    mention_id: str,
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get a specific mention by ID"""
    try:
        mention = await monitor.get_mention_by_id(mention_id)
        
        if not mention:
            raise HTTPException(status_code=404, detail="Mention not found")
        
        return APIResponse(
            success=True,
            message="Mention retrieved successfully",
            data=mention.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mention {mention_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan", response_model=APIResponse)
async def trigger_manual_scan(
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Trigger a manual scan for new mentions"""
    try:
        mentions = await monitor.scan_for_mentions()
        
        return APIResponse(
            success=True,
            message=f"Manual scan completed. Found {len(mentions)} new mentions",
            data={
                "mentions_found": len(mentions),
                "mentions": [mention.dict() for mention in mentions]
            }
        )
        
    except Exception as e:
        logger.error(f"Error during manual scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan/{post_id}", response_model=APIResponse)
async def scan_specific_post(
    post_id: str,
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Scan a specific Reddit post by ID"""
    try:
        mention = await monitor.manual_scan_post(post_id)
        
        if not mention:
            raise HTTPException(status_code=404, detail="Post not found or could not be processed")
        
        return APIResponse(
            success=True,
            message=f"Post {post_id} scanned successfully",
            data=mention.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threats/high-priority", response_model=APIResponse)
async def get_high_priority_threats(
    limit: int = Query(20, ge=1, le=100),
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get high-priority threats (HIGH and CRITICAL threat levels)"""
    try:
        # Get high threats
        high_threats = await monitor.get_mentions(
            limit=limit,
            threat_level=ThreatLevel.HIGH
        )
        
        # Get critical threats
        critical_threats = await monitor.get_mentions(
            limit=limit,
            threat_level=ThreatLevel.CRITICAL
        )
        
        # Combine and sort by threat score
        all_threats = high_threats + critical_threats
        all_threats.sort(key=lambda x: x.threat_analysis.threat_score, reverse=True)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(all_threats)} high-priority threats",
            data={
                "threats": [mention.dict() for mention in all_threats[:limit]],
                "high_count": len(high_threats),
                "critical_count": len(critical_threats)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting high-priority threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/{sentiment_type}", response_model=APIResponse)
async def get_mentions_by_sentiment(
    sentiment_type: SentimentType,
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get mentions filtered by sentiment type"""
    try:
        mentions = await monitor.get_mentions(
            limit=limit,
            skip=skip,
            sentiment=sentiment_type
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(mentions)} {sentiment_type.value} mentions",
            data={
                "mentions": [mention.dict() for mention in mentions],
                "sentiment": sentiment_type.value,
                "total": len(mentions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting mentions by sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subreddit/{subreddit_name}", response_model=APIResponse)
async def get_mentions_by_subreddit(
    subreddit_name: str,
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get mentions from a specific subreddit"""
    try:
        mentions = await monitor.get_mentions(
            limit=limit,
            skip=skip,
            subreddit=subreddit_name
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(mentions)} mentions from r/{subreddit_name}",
            data={
                "mentions": [mention.dict() for mention in mentions],
                "subreddit": subreddit_name,
                "total": len(mentions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting mentions by subreddit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{mention_id}/review", response_model=APIResponse)
async def mark_mention_reviewed(
    mention_id: str,
    notes: Optional[str] = None,
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Mark a mention as reviewed with optional notes"""
    try:
        from app.core.database import get_mentions_collection
        from bson import ObjectId
        
        collection = await get_mentions_collection()
        
        update_data = {
            "is_reviewed": True,
            "reviewed_at": datetime.utcnow()
        }
        
        if notes:
            update_data["notes"] = notes
        
        result = await collection.update_one(
            {"_id": ObjectId(mention_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mention not found")
        
        return APIResponse(
            success=True,
            message="Mention marked as reviewed",
            data={"mention_id": mention_id, "notes": notes}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking mention as reviewed: {e}")
        raise HTTPException(status_code=500, detail=str(e))