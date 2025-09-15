from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.models.schemas import APIResponse, AlertConfig, SentimentType
from app.core.database import get_alerts_collection
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
async def get_alert_configs():
    """Get all alert configurations"""
    try:
        collection = await get_alerts_collection()
        
        alerts = []
        async for doc in collection.find():
            try:
                alert = AlertConfig(**doc)
                alerts.append(alert.dict())
            except Exception as e:
                logger.warning(f"Error converting alert document: {e}")
                continue
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(alerts)} alert configurations",
            data={"alerts": alerts}
        )
        
    except Exception as e:
        logger.error(f"Error getting alert configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=APIResponse)
async def create_alert_config(
    name: str,
    keywords: List[str],
    subreddits: List[str],
    threat_threshold: float = 0.7,
    sentiment_filter: Optional[SentimentType] = None
):
    """Create a new alert configuration"""
    try:
        collection = await get_alerts_collection()
        
        # Check if alert with same name exists
        existing = await collection.find_one({"name": name})
        if existing:
            raise HTTPException(status_code=400, detail="Alert configuration with this name already exists")
        
        # Create new alert config
        alert_config = AlertConfig(
            name=name,
            keywords=keywords,
            subreddits=subreddits,
            threat_threshold=threat_threshold,
            sentiment_filter=sentiment_filter,
            is_active=True
        )
        
        # Insert into database
        result = await collection.insert_one(alert_config.dict())
        
        return APIResponse(
            success=True,
            message="Alert configuration created successfully",
            data={
                "alert_id": str(result.inserted_id),
                "alert": alert_config.dict()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alert_id}", response_model=APIResponse)
async def get_alert_config(alert_id: str):
    """Get a specific alert configuration"""
    try:
        from bson import ObjectId
        collection = await get_alerts_collection()
        
        doc = await collection.find_one({"_id": ObjectId(alert_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Alert configuration not found")
        
        alert = AlertConfig(**doc)
        
        return APIResponse(
            success=True,
            message="Alert configuration retrieved",
            data=alert.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{alert_id}", response_model=APIResponse)
async def update_alert_config(
    alert_id: str,
    name: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    subreddits: Optional[List[str]] = None,
    threat_threshold: Optional[float] = None,
    sentiment_filter: Optional[SentimentType] = None,
    is_active: Optional[bool] = None
):
    """Update an alert configuration"""
    try:
        from bson import ObjectId
        collection = await get_alerts_collection()
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            # Check if another alert with same name exists
            existing = await collection.find_one({
                "name": name,
                "_id": {"$ne": ObjectId(alert_id)}
            })
            if existing:
                raise HTTPException(status_code=400, detail="Alert configuration with this name already exists")
            update_data["name"] = name
        
        if keywords is not None:
            update_data["keywords"] = keywords
        
        if subreddits is not None:
            update_data["subreddits"] = subreddits
        
        if threat_threshold is not None:
            update_data["threat_threshold"] = threat_threshold
        
        if sentiment_filter is not None:
            update_data["sentiment_filter"] = sentiment_filter
        
        if is_active is not None:
            update_data["is_active"] = is_active
        
        # Update in database
        result = await collection.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert configuration not found")
        
        # Get updated document
        updated_doc = await collection.find_one({"_id": ObjectId(alert_id)})
        alert = AlertConfig(**updated_doc)
        
        return APIResponse(
            success=True,
            message="Alert configuration updated successfully",
            data=alert.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{alert_id}", response_model=APIResponse)
async def delete_alert_config(alert_id: str):
    """Delete an alert configuration"""
    try:
        from bson import ObjectId
        collection = await get_alerts_collection()
        
        result = await collection.delete_one({"_id": ObjectId(alert_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alert configuration not found")
        
        return APIResponse(
            success=True,
            message="Alert configuration deleted successfully",
            data={"alert_id": alert_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/toggle", response_model=APIResponse)
async def toggle_alert_config(alert_id: str):
    """Toggle alert configuration active status"""
    try:
        from bson import ObjectId
        collection = await get_alerts_collection()
        
        # Get current status
        doc = await collection.find_one({"_id": ObjectId(alert_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Alert configuration not found")
        
        # Toggle status
        new_status = not doc.get("is_active", True)
        
        result = await collection.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "is_active": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return APIResponse(
            success=True,
            message=f"Alert configuration {'activated' if new_status else 'deactivated'}",
            data={
                "alert_id": alert_id,
                "is_active": new_status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/{alert_id}", response_model=APIResponse)
async def test_alert_config(
    alert_id: str,
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Test an alert configuration by running a search"""
    try:
        from bson import ObjectId
        collection = await get_alerts_collection()
        
        # Get alert config
        doc = await collection.find_one({"_id": ObjectId(alert_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Alert configuration not found")
        
        alert = AlertConfig(**doc)
        
        # Run a test search
        test_mentions = []
        async for reddit_post in monitor.reddit_client.search_posts_by_keywords(
            keywords=alert.keywords,
            subreddits=alert.subreddits,
            limit=10,
            time_filter="day"
        ):
            # Analyze the post
            mention = await monitor.analyze_post(reddit_post)
            
            # Check if it meets alert criteria
            meets_criteria = True
            
            if mention.threat_analysis.threat_score < alert.threat_threshold:
                meets_criteria = False
            
            if alert.sentiment_filter and mention.sentiment_analysis.sentiment != alert.sentiment_filter:
                meets_criteria = False
            
            test_mentions.append({
                "mention": mention.dict(),
                "meets_criteria": meets_criteria
            })
        
        matching_mentions = [m for m in test_mentions if m["meets_criteria"]]
        
        return APIResponse(
            success=True,
            message=f"Alert test completed. Found {len(matching_mentions)} matching mentions out of {len(test_mentions)} total",
            data={
                "alert": alert.dict(),
                "test_results": {
                    "total_mentions": len(test_mentions),
                    "matching_mentions": len(matching_mentions),
                    "mentions": test_mentions
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing alert config: {e}")
        raise HTTPException(status_code=500, detail=str(e))