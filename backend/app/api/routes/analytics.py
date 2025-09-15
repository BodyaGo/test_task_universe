from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.schemas import APIResponse, ThreatLevel, SentimentType
from app.core.database import get_mentions_collection
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

@router.get("/overview", response_model=APIResponse)
async def get_analytics_overview(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    monitor: RedditMonitor = Depends(get_reddit_monitor)
):
    """Get analytics overview for the specified time period"""
    try:
        collection = await get_mentions_collection()
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total mentions
        total_mentions = await collection.count_documents({
            "processed_at": {"$gte": start_date, "$lte": end_date}
        })
        
        # Threat level distribution
        threat_pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": "$threat_analysis.threat_level",
                "count": {"$sum": 1}
            }}
        ]
        
        threat_distribution = {}
        async for doc in collection.aggregate(threat_pipeline):
            threat_distribution[doc["_id"]] = doc["count"]
        
        # Sentiment distribution
        sentiment_pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": "$sentiment_analysis.sentiment",
                "count": {"$sum": 1}
            }}
        ]
        
        sentiment_distribution = {}
        async for doc in collection.aggregate(sentiment_pipeline):
            sentiment_distribution[doc["_id"]] = doc["count"]
        
        # Daily trends
        daily_pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$processed_at"},
                    "month": {"$month": "$processed_at"},
                    "day": {"$dayOfMonth": "$processed_at"}
                },
                "count": {"$sum": 1},
                "avg_threat_score": {"$avg": "$threat_analysis.threat_score"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]
        
        daily_trends = []
        async for doc in collection.aggregate(daily_pipeline):
            date_str = f"{doc['_id']['year']}-{doc['_id']['month']:02d}-{doc['_id']['day']:02d}"
            daily_trends.append({
                "date": date_str,
                "mentions": doc["count"],
                "avg_threat_score": round(doc["avg_threat_score"] or 0, 3)
            })
        
        # Top subreddits
        subreddit_pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": "$reddit_post.subreddit",
                "count": {"$sum": 1},
                "avg_threat_score": {"$avg": "$threat_analysis.threat_score"},
                "avg_sentiment_score": {"$avg": "$sentiment_analysis.confidence"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_subreddits = []
        async for doc in collection.aggregate(subreddit_pipeline):
            top_subreddits.append({
                "subreddit": doc["_id"],
                "mentions": doc["count"],
                "avg_threat_score": round(doc["avg_threat_score"] or 0, 3),
                "avg_sentiment_score": round(doc["avg_sentiment_score"] or 0, 3)
            })
        
        overview_data = {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_mentions": total_mentions,
                "threat_distribution": threat_distribution,
                "sentiment_distribution": sentiment_distribution
            },
            "trends": {
                "daily": daily_trends
            },
            "top_subreddits": top_subreddits
        }
        
        return APIResponse(
            success=True,
            message=f"Analytics overview for {days} days retrieved",
            data=overview_data
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-trends", response_model=APIResponse)
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=90),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly)$")
):
    """Get sentiment trends over time"""
    try:
        collection = await get_mentions_collection()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build aggregation pipeline based on granularity
        if granularity == "hourly":
            group_id = {
                "year": {"$year": "$processed_at"},
                "month": {"$month": "$processed_at"},
                "day": {"$dayOfMonth": "$processed_at"},
                "hour": {"$hour": "$processed_at"}
            }
        elif granularity == "weekly":
            group_id = {
                "year": {"$year": "$processed_at"},
                "week": {"$week": "$processed_at"}
            }
        else:  # daily
            group_id = {
                "year": {"$year": "$processed_at"},
                "month": {"$month": "$processed_at"},
                "day": {"$dayOfMonth": "$processed_at"}
            }
        
        pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {
                    "period": group_id,
                    "sentiment": "$sentiment_analysis.sentiment"
                },
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$sentiment_analysis.confidence"}
            }},
            {"$sort": {"_id.period": 1}}
        ]
        
        # Process results
        trends_data = {}
        async for doc in collection.aggregate(pipeline):
            period = doc["_id"]["period"]
            sentiment = doc["_id"]["sentiment"]
            
            # Create period key
            if granularity == "hourly":
                period_key = f"{period['year']}-{period['month']:02d}-{period['day']:02d} {period['hour']:02d}:00"
            elif granularity == "weekly":
                period_key = f"{period['year']}-W{period['week']:02d}"
            else:
                period_key = f"{period['year']}-{period['month']:02d}-{period['day']:02d}"
            
            if period_key not in trends_data:
                trends_data[period_key] = {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0
                }
            
            trends_data[period_key][sentiment] = doc["count"]
            trends_data[period_key]["total"] += doc["count"]
        
        # Convert to list format
        trends_list = []
        for period, data in sorted(trends_data.items()):
            trends_list.append({
                "period": period,
                "positive": data["positive"],
                "negative": data["negative"],
                "neutral": data["neutral"],
                "total": data["total"],
                "positive_pct": round((data["positive"] / data["total"]) * 100, 1) if data["total"] > 0 else 0,
                "negative_pct": round((data["negative"] / data["total"]) * 100, 1) if data["total"] > 0 else 0,
                "neutral_pct": round((data["neutral"] / data["total"]) * 100, 1) if data["total"] > 0 else 0
            })
        
        return APIResponse(
            success=True,
            message=f"Sentiment trends for {days} days retrieved",
            data={
                "granularity": granularity,
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "trends": trends_list
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threat-analysis", response_model=APIResponse)
async def get_threat_analysis(
    days: int = Query(7, ge=1, le=90),
    min_threat_score: float = Query(0.0, ge=0.0, le=1.0)
):
    """Get detailed threat analysis"""
    try:
        collection = await get_mentions_collection()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Threat categories analysis
        categories_pipeline = [
            {"$match": {
                "processed_at": {"$gte": start_date, "$lte": end_date},
                "threat_analysis.threat_score": {"$gte": min_threat_score}
            }},
            {"$unwind": "$threat_analysis.threat_categories"},
            {"$group": {
                "_id": "$threat_analysis.threat_categories",
                "count": {"$sum": 1},
                "avg_threat_score": {"$avg": "$threat_analysis.threat_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        threat_categories = []
        async for doc in collection.aggregate(categories_pipeline):
            threat_categories.append({
                "category": doc["_id"],
                "count": doc["count"],
                "avg_threat_score": round(doc["avg_threat_score"], 3)
            })
        
        # Keywords analysis
        keywords_pipeline = [
            {"$match": {
                "processed_at": {"$gte": start_date, "$lte": end_date},
                "threat_analysis.threat_score": {"$gte": min_threat_score}
            }},
            {"$unwind": "$threat_analysis.keywords_matched"},
            {"$group": {
                "_id": "$threat_analysis.keywords_matched",
                "count": {"$sum": 1},
                "avg_threat_score": {"$avg": "$threat_analysis.threat_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        threat_keywords = []
        async for doc in collection.aggregate(keywords_pipeline):
            threat_keywords.append({
                "keyword": doc["_id"],
                "count": doc["count"],
                "avg_threat_score": round(doc["avg_threat_score"], 3)
            })
        
        # Threat score distribution
        score_ranges = [
            {"min": 0.0, "max": 0.2, "label": "Very Low"},
            {"min": 0.2, "max": 0.4, "label": "Low"},
            {"min": 0.4, "max": 0.6, "label": "Medium"},
            {"min": 0.6, "max": 0.8, "label": "High"},
            {"min": 0.8, "max": 1.0, "label": "Critical"}
        ]
        
        score_distribution = []
        for range_info in score_ranges:
            count = await collection.count_documents({
                "processed_at": {"$gte": start_date, "$lte": end_date},
                "threat_analysis.threat_score": {
                    "$gte": range_info["min"],
                    "$lt": range_info["max"] if range_info["max"] < 1.0 else 1.1
                }
            })
            
            score_distribution.append({
                "range": f"{range_info['min']}-{range_info['max']}",
                "label": range_info["label"],
                "count": count
            })
        
        return APIResponse(
            success=True,
            message=f"Threat analysis for {days} days retrieved",
            data={
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "filters": {
                    "min_threat_score": min_threat_score
                },
                "threat_categories": threat_categories,
                "threat_keywords": threat_keywords,
                "score_distribution": score_distribution
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting threat analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subreddit-analysis", response_model=APIResponse)
async def get_subreddit_analysis(
    days: int = Query(30, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100)
):
    """Get detailed subreddit analysis"""
    try:
        collection = await get_mentions_collection()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        pipeline = [
            {"$match": {"processed_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": "$reddit_post.subreddit",
                "total_mentions": {"$sum": 1},
                "avg_threat_score": {"$avg": "$threat_analysis.threat_score"},
                "avg_sentiment_confidence": {"$avg": "$sentiment_analysis.confidence"},
                "avg_reddit_score": {"$avg": "$reddit_post.score"},
                "total_comments": {"$sum": "$reddit_post.num_comments"},
                "positive_mentions": {
                    "$sum": {
                        "$cond": [{"$eq": ["$sentiment_analysis.sentiment", "positive"]}, 1, 0]
                    }
                },
                "negative_mentions": {
                    "$sum": {
                        "$cond": [{"$eq": ["$sentiment_analysis.sentiment", "negative"]}, 1, 0]
                    }
                },
                "high_threat_mentions": {
                    "$sum": {
                        "$cond": [{"$gte": ["$threat_analysis.threat_score", 0.6]}, 1, 0]
                    }
                }
            }},
            {"$sort": {"total_mentions": -1}},
            {"$limit": limit}
        ]
        
        subreddit_analysis = []
        async for doc in collection.aggregate(pipeline):
            total = doc["total_mentions"]
            subreddit_analysis.append({
                "subreddit": doc["_id"],
                "total_mentions": total,
                "avg_threat_score": round(doc["avg_threat_score"] or 0, 3),
                "avg_sentiment_confidence": round(doc["avg_sentiment_confidence"] or 0, 3),
                "avg_reddit_score": round(doc["avg_reddit_score"] or 0, 1),
                "total_comments": doc["total_comments"],
                "positive_mentions": doc["positive_mentions"],
                "negative_mentions": doc["negative_mentions"],
                "neutral_mentions": total - doc["positive_mentions"] - doc["negative_mentions"],
                "high_threat_mentions": doc["high_threat_mentions"],
                "positive_percentage": round((doc["positive_mentions"] / total) * 100, 1) if total > 0 else 0,
                "negative_percentage": round((doc["negative_mentions"] / total) * 100, 1) if total > 0 else 0,
                "threat_percentage": round((doc["high_threat_mentions"] / total) * 100, 1) if total > 0 else 0
            })
        
        return APIResponse(
            success=True,
            message=f"Subreddit analysis for {days} days retrieved",
            data={
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "subreddits": subreddit_analysis
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting subreddit analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export", response_model=APIResponse)
async def export_analytics_data(
    days: int = Query(30, ge=1, le=365),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export analytics data"""
    try:
        collection = await get_mentions_collection()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all mentions in the period
        mentions_data = []
        async for doc in collection.find({
            "processed_at": {"$gte": start_date, "$lte": end_date}
        }).sort("processed_at", -1):
            mention_export = {
                "id": str(doc.get("_id", "")),
                "reddit_id": doc.get("reddit_post", {}).get("id", ""),
                "title": doc.get("reddit_post", {}).get("title", ""),
                "subreddit": doc.get("reddit_post", {}).get("subreddit", ""),
                "author": doc.get("reddit_post", {}).get("author", ""),
                "score": doc.get("reddit_post", {}).get("score", 0),
                "num_comments": doc.get("reddit_post", {}).get("num_comments", 0),
                "created_utc": doc.get("reddit_post", {}).get("created_utc", ""),
                "processed_at": doc.get("processed_at", ""),
                "sentiment": doc.get("sentiment_analysis", {}).get("sentiment", ""),
                "sentiment_confidence": doc.get("sentiment_analysis", {}).get("confidence", 0),
                "threat_level": doc.get("threat_analysis", {}).get("threat_level", ""),
                "threat_score": doc.get("threat_analysis", {}).get("threat_score", 0),
                "threat_categories": ", ".join(doc.get("threat_analysis", {}).get("threat_categories", [])),
                "keywords_matched": ", ".join(doc.get("threat_analysis", {}).get("keywords_matched", [])),
                "url": doc.get("reddit_post", {}).get("permalink", "")
            }
            mentions_data.append(mention_export)
        
        if format == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            if mentions_data:
                writer = csv.DictWriter(output, fieldnames=mentions_data[0].keys())
                writer.writeheader()
                writer.writerows(mentions_data)
            
            csv_data = output.getvalue()
            output.close()
            
            return APIResponse(
                success=True,
                message=f"Exported {len(mentions_data)} mentions as CSV",
                data={
                    "format": "csv",
                    "content": csv_data,
                    "filename": f"brand_mentions_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                }
            )
        else:
            return APIResponse(
                success=True,
                message=f"Exported {len(mentions_data)} mentions as JSON",
                data={
                    "format": "json",
                    "mentions": mentions_data,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": days
                    }
                }
            )
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail=str(e))