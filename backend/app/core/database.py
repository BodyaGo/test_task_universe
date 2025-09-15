from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from loguru import logger
from typing import Optional

from app.core.config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def init_database():
    """Initialize database connection"""
    try:
        # Create MongoDB client
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Get database
        db.database = db.client[settings.mongodb_database]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Database connection closed")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db.database is None:
        await init_database()
    return db.database

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        database = await get_database()
        
        # Brand mentions collection indexes
        mentions_collection = database.brand_mentions
        await mentions_collection.create_index("reddit_post.id", unique=True)
        await mentions_collection.create_index("reddit_post.created_utc")
        await mentions_collection.create_index("threat_analysis.threat_level")
        await mentions_collection.create_index("sentiment_analysis.sentiment")
        await mentions_collection.create_index("reddit_post.subreddit")
        await mentions_collection.create_index("processed_at")
        await mentions_collection.create_index("is_reviewed")
        
        # Alert configs collection indexes
        alerts_collection = database.alert_configs
        await alerts_collection.create_index("name", unique=True)
        await alerts_collection.create_index("is_active")
        await alerts_collection.create_index("created_at")
        
        # User actions collection indexes
        actions_collection = database.user_actions
        await actions_collection.create_index("mention_id")
        await actions_collection.create_index("user_id")
        await actions_collection.create_index("timestamp")
        await actions_collection.create_index("action_type")
        
        # Monitoring stats collection indexes
        stats_collection = database.monitoring_stats
        await stats_collection.create_index("last_updated")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise

# Collection helpers
async def get_mentions_collection():
    """Get brand mentions collection"""
    database = await get_database()
    return database.brand_mentions

async def get_alerts_collection():
    """Get alert configs collection"""
    database = await get_database()
    return database.alert_configs

async def get_actions_collection():
    """Get user actions collection"""
    database = await get_database()
    return database.user_actions

async def get_stats_collection():
    """Get monitoring stats collection"""
    database = await get_database()
    return database.monitoring_stats