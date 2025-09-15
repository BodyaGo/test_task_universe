import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.services.reddit_client import RedditClient
from app.services.ai_analyzer import AIAnalyzer
from app.core.database import get_mentions_collection, get_stats_collection
from app.core.config import settings
from app.models.schemas import (
    BrandMention, RedditPost, MonitoringStats, ThreatLevel, SentimentType
)

class RedditMonitor:
    """Main Reddit monitoring service"""
    
    def __init__(self):
        self.reddit_client = RedditClient()
        self.ai_analyzer = AIAnalyzer()
        self.is_initialized = False
        self.is_monitoring = False
        self.monitoring_task = None
        
    async def initialize(self):
        """Initialize all components"""
        try:
            # Initialize Reddit client
            await self.reddit_client.initialize()
            
            # Initialize AI analyzer
            await self.ai_analyzer.initialize()
            
            self.is_initialized = True
            logger.info("Reddit Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit Monitor: {e}")
            raise
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.is_initialized:
            raise RuntimeError("Reddit Monitor not initialized")
        
        if self.is_monitoring:
            logger.warning("Monitoring already in progress")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Reddit monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Reddit monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        while self.is_monitoring:
            try:
                # Perform monitoring scan
                await self.scan_for_mentions()
                
                # Update monitoring statistics
                await self.update_monitoring_stats()
                
                # Wait for next scan
                await asyncio.sleep(settings.monitor_interval)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def scan_for_mentions(self) -> List[BrandMention]:
        """Scan Reddit for brand mentions"""
        try:
            logger.info("Scanning for brand mentions...")
            mentions = []
            
            # Search for posts containing brand keywords
            async for reddit_post in self.reddit_client.search_posts_by_keywords(
                keywords=settings.brand_keywords,
                subreddits=settings.monitor_subreddits,
                limit=100,
                time_filter="day"
            ):
                try:
                    # Check if we already processed this post
                    if await self._is_post_already_processed(reddit_post.id):
                        continue
                    
                    # Analyze the post
                    mention = await self.analyze_post(reddit_post)
                    
                    # Save to database
                    await self.save_mention(mention)
                    
                    mentions.append(mention)
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing post {reddit_post.id}: {e}")
                    continue
            
            logger.info(f"Found {len(mentions)} new mentions")
            return mentions
            
        except Exception as e:
            logger.error(f"Error scanning for mentions: {e}")
            return []
    
    async def analyze_post(self, reddit_post: RedditPost) -> BrandMention:
        """Analyze a Reddit post for sentiment and threats"""
        try:
            # Combine title and content for analysis
            full_text = f"{reddit_post.title or ''} {reddit_post.content or ''}".strip()
            
            # Perform sentiment analysis
            sentiment_analysis = await self.ai_analyzer.analyze_sentiment(full_text)
            
            # Perform threat analysis
            threat_analysis = await self.ai_analyzer.analyze_threat(
                reddit_post, settings.brand_keywords
            )
            
            # Generate response recommendation
            response_recommendation = None
            if threat_analysis.threat_score >= settings.threat_threshold:
                response_recommendation = await self.ai_analyzer.generate_response_recommendation(
                    reddit_post, threat_analysis
                )
            
            # Create brand mention
            mention = BrandMention(
                reddit_post=reddit_post,
                sentiment_analysis=sentiment_analysis,
                threat_analysis=threat_analysis,
                response_recommendation=response_recommendation,
                processed_at=datetime.utcnow()
            )
            
            logger.info(
                f"Analyzed post {reddit_post.id}: "
                f"sentiment={sentiment_analysis.sentiment.value}, "
                f"threat={threat_analysis.threat_level.value}"
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing post {reddit_post.id}: {e}")
            raise
    
    async def _is_post_already_processed(self, post_id: str) -> bool:
        """Check if a post has already been processed"""
        try:
            collection = await get_mentions_collection()
            existing = await collection.find_one({"reddit_post.id": post_id})
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking if post exists: {e}")
            return False
    
    async def save_mention(self, mention: BrandMention) -> str:
        """Save brand mention to database"""
        try:
            collection = await get_mentions_collection()
            
            # Convert to dict for MongoDB
            mention_dict = mention.dict()
            
            # Insert into database
            result = await collection.insert_one(mention_dict)
            
            logger.info(f"Saved mention {mention.reddit_post.id} to database")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving mention: {e}")
            raise
    
    async def get_mentions(
        self,
        limit: int = 50,
        skip: int = 0,
        threat_level: Optional[ThreatLevel] = None,
        sentiment: Optional[SentimentType] = None,
        subreddit: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BrandMention]:
        """Get brand mentions with filtering"""
        try:
            collection = await get_mentions_collection()
            
            # Build query
            query = {}
            
            if threat_level:
                query["threat_analysis.threat_level"] = threat_level.value
            
            if sentiment:
                query["sentiment_analysis.sentiment"] = sentiment.value
            
            if subreddit:
                query["reddit_post.subreddit"] = subreddit
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["processed_at"] = date_query
            
            # Execute query
            cursor = collection.find(query).sort("processed_at", -1).skip(skip).limit(limit)
            
            mentions = []
            async for doc in cursor:
                try:
                    # Convert MongoDB document to BrandMention
                    mention = BrandMention(**doc)
                    mentions.append(mention)
                except Exception as e:
                    logger.warning(f"Error converting document to BrandMention: {e}")
                    continue
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            return []
    
    async def get_mention_by_id(self, mention_id: str) -> Optional[BrandMention]:
        """Get a specific mention by ID"""
        try:
            from bson import ObjectId
            collection = await get_mentions_collection()
            
            doc = await collection.find_one({"_id": ObjectId(mention_id)})
            
            if doc:
                return BrandMention(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting mention by ID: {e}")
            return None
    
    async def update_monitoring_stats(self):
        """Update monitoring statistics"""
        try:
            collection = await get_mentions_collection()
            stats_collection = await get_stats_collection()
            
            # Calculate stats for the last 24 hours
            since = datetime.utcnow() - timedelta(days=1)
            
            # Total mentions
            total_mentions = await collection.count_documents({
                "processed_at": {"$gte": since}
            })
            
            # Threat distribution
            threat_pipeline = [
                {"$match": {"processed_at": {"$gte": since}}},
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
                {"$match": {"processed_at": {"$gte": since}}},
                {"$group": {
                    "_id": "$sentiment_analysis.sentiment",
                    "count": {"$sum": 1}
                }}
            ]
            
            sentiment_distribution = {}
            async for doc in collection.aggregate(sentiment_pipeline):
                sentiment_distribution[doc["_id"]] = doc["count"]
            
            # Top subreddits
            subreddit_pipeline = [
                {"$match": {"processed_at": {"$gte": since}}},
                {"$group": {
                    "_id": "$reddit_post.subreddit",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            top_subreddits = []
            async for doc in collection.aggregate(subreddit_pipeline):
                top_subreddits.append({
                    "subreddit": doc["_id"],
                    "count": doc["count"]
                })
            
            # Create stats object
            stats = MonitoringStats(
                total_mentions=total_mentions,
                threat_distribution=threat_distribution,
                sentiment_distribution=sentiment_distribution,
                top_subreddits=top_subreddits,
                trending_keywords=settings.brand_keywords_list,  # Simplified for now
                last_updated=datetime.utcnow()
            )
            
            # Save to database
            await stats_collection.replace_one(
                {},  # Replace the single stats document
                stats.dict(),
                upsert=True
            )
            
            logger.info("Monitoring stats updated")
            
        except Exception as e:
            logger.error(f"Error updating monitoring stats: {e}")
    
    async def get_monitoring_stats(self) -> Optional[MonitoringStats]:
        """Get current monitoring statistics"""
        try:
            stats_collection = await get_stats_collection()
            doc = await stats_collection.find_one()
            
            if doc:
                return MonitoringStats(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting monitoring stats: {e}")
            return None
    
    async def manual_scan_post(self, post_id: str) -> Optional[BrandMention]:
        """Manually scan a specific Reddit post"""
        try:
            # Get post from Reddit
            reddit_post = await self.reddit_client.get_post_by_id(post_id)
            
            if not reddit_post:
                logger.warning(f"Post {post_id} not found")
                return None
            
            # Analyze the post
            mention = await self.analyze_post(reddit_post)
            
            # Save to database
            await self.save_mention(mention)
            
            logger.info(f"Manually scanned and saved post {post_id}")
            return mention
            
        except Exception as e:
            logger.error(f"Error manually scanning post {post_id}: {e}")
            return None