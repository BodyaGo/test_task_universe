from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.reddit_client import RedditClient
from app.services.ai_analyzer import AIAnalyzer
from app.core.config import settings

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

# Global instances
_reddit_client = None
_ai_analyzer = None

class SentimentRequest(BaseModel):
    title: str
    
class BatchSentimentRequest(BaseModel):
    titles: List[str]

class RedditSearchRequest(BaseModel):
    keywords: List[str]
    subreddits: Optional[List[str]] = None
    limit: int = 50
    time_filter: str = "day"

async def get_reddit_client() -> RedditClient:
    """Get Reddit client instance"""
    global _reddit_client
    if _reddit_client is None:
        _reddit_client = RedditClient()
        await _reddit_client.initialize()
    return _reddit_client

async def get_ai_analyzer() -> AIAnalyzer:
    """Get AI analyzer instance"""
    global _ai_analyzer
    if _ai_analyzer is None:
        _ai_analyzer = AIAnalyzer()
        await _ai_analyzer.initialize()
    return _ai_analyzer

@router.post("/analyze-title")
async def analyze_title_sentiment(
    request: SentimentRequest,
    ai_analyzer: AIAnalyzer = Depends(get_ai_analyzer)
) -> Dict[str, Any]:
    """Analyze sentiment of a single title"""
    try:
        result = await ai_analyzer.analyze_title_sentiment(request.title)
        return {
            "success": True,
            "title": request.title,
            "sentiment_analysis": result
        }
    except Exception as e:
        logger.error(f"Error analyzing title sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-batch")
async def analyze_batch_sentiment(
    request: BatchSentimentRequest,
    ai_analyzer: AIAnalyzer = Depends(get_ai_analyzer)
) -> Dict[str, Any]:
    """Analyze sentiment of multiple titles"""
    try:
        results = []
        for title in request.titles:
            sentiment_result = await ai_analyzer.analyze_title_sentiment(title)
            results.append({
                "title": title,
                "sentiment_analysis": sentiment_result
            })
        
        # Calculate summary statistics
        positive_count = sum(1 for r in results if r["sentiment_analysis"]["is_positive"])
        negative_count = sum(1 for r in results if r["sentiment_analysis"]["is_negative"])
        neutral_count = len(results) - positive_count - negative_count
        
        return {
            "success": True,
            "total_analyzed": len(results),
            "summary": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "positive_percentage": round((positive_count / len(results)) * 100, 2) if results else 0,
                "negative_percentage": round((negative_count / len(results)) * 100, 2) if results else 0,
                "neutral_percentage": round((neutral_count / len(results)) * 100, 2) if results else 0
            },
            "results": results
        }
    except Exception as e:
        logger.error(f"Error analyzing batch sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-reddit-posts")
async def analyze_reddit_posts_sentiment(
    request: RedditSearchRequest,
    reddit_client: RedditClient = Depends(get_reddit_client),
    ai_analyzer: AIAnalyzer = Depends(get_ai_analyzer)
) -> Dict[str, Any]:
    """Search Reddit posts and analyze their sentiment"""
    try:
        # Search for posts
        posts = []
        async for post in reddit_client.search_posts_by_keywords(
            keywords=request.keywords,
            subreddits=request.subreddits,
            limit=request.limit,
            time_filter=request.time_filter
        ):
            posts.append(post)
        
        if not posts:
            return {
                "success": True,
                "message": "No posts found for the given keywords",
                "total_posts": 0,
                "results": []
            }
        
        # Analyze sentiment
        sentiment_results = await ai_analyzer.analyze_posts_sentiment_batch(posts)
        
        # Calculate summary statistics
        positive_count = sum(1 for r in sentiment_results if r["title_sentiment"]["is_positive"])
        negative_count = sum(1 for r in sentiment_results if r["title_sentiment"]["is_negative"])
        neutral_count = len(sentiment_results) - positive_count - negative_count
        
        return {
            "success": True,
            "search_params": {
                "keywords": request.keywords,
                "subreddits": request.subreddits,
                "limit": request.limit,
                "time_filter": request.time_filter
            },
            "total_posts": len(sentiment_results),
            "summary": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "positive_percentage": round((positive_count / len(sentiment_results)) * 100, 2) if sentiment_results else 0,
                "negative_percentage": round((negative_count / len(sentiment_results)) * 100, 2) if sentiment_results else 0,
                "neutral_percentage": round((neutral_count / len(sentiment_results)) * 100, 2) if sentiment_results else 0
            },
            "results": sentiment_results
        }
        
    except Exception as e:
        logger.error(f"Error analyzing Reddit posts sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo")
async def sentiment_demo(
    title: str = Query(..., description="Title to analyze"),
    ai_analyzer: AIAnalyzer = Depends(get_ai_analyzer)
) -> Dict[str, Any]:
    """Demo endpoint for quick sentiment analysis"""
    try:
        result = await ai_analyzer.analyze_title_sentiment(title)
        return {
            "success": True,
            "title": title,
            "sentiment": result["sentiment"],
            "is_positive": result["is_positive"],
            "is_negative": result["is_negative"],
            "confidence": result["confidence"],
            "explanation": result["explanation"]
        }
    except Exception as e:
        logger.error(f"Error in sentiment demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))