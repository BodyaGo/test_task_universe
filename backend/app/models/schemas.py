from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PostType(str, Enum):
    POST = "post"
    COMMENT = "comment"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class RedditPost(BaseModel):
    id: str = Field(..., description="Reddit post/comment ID")
    title: Optional[str] = Field(None, description="Post title")
    content: str = Field(..., description="Post/comment content")
    author: str = Field(..., description="Author username")
    subreddit: str = Field(..., description="Subreddit name")
    url: str = Field(..., description="Reddit URL")
    score: int = Field(0, description="Reddit score (upvotes - downvotes)")
    num_comments: int = Field(0, description="Number of comments")
    created_utc: datetime = Field(..., description="Creation timestamp")
    post_type: PostType = Field(..., description="Type of post")
    permalink: str = Field(..., description="Permanent link to post")

class SentimentAnalysis(BaseModel):
    sentiment: SentimentType = Field(..., description="Overall sentiment")
    confidence: float = Field(..., description="Confidence score (0-1)")
    positive_score: float = Field(0.0, description="Positive sentiment score")
    negative_score: float = Field(0.0, description="Negative sentiment score")
    neutral_score: float = Field(0.0, description="Neutral sentiment score")

class ThreatAnalysis(BaseModel):
    threat_level: ThreatLevel = Field(..., description="Threat level")
    threat_score: float = Field(..., description="Threat score (0-1)")
    threat_categories: List[str] = Field(default_factory=list, description="Categories of threats")
    keywords_matched: List[str] = Field(default_factory=list, description="Brand keywords found")
    context_analysis: str = Field("", description="AI analysis of context")
    potential_impact: str = Field("", description="Potential impact assessment")

class ResponseRecommendation(BaseModel):
    action_type: str = Field(..., description="Type of recommended action")
    priority: int = Field(..., description="Priority level (1-5)")
    message_template: str = Field("", description="Suggested response template")
    escalation_needed: bool = Field(False, description="Whether escalation is needed")
    reasoning: str = Field("", description="Reasoning for recommendation")

class BrandMention(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    reddit_post: RedditPost = Field(..., description="Reddit post data")
    sentiment_analysis: SentimentAnalysis = Field(..., description="Sentiment analysis")
    threat_analysis: ThreatAnalysis = Field(..., description="Threat analysis")
    response_recommendation: Optional[ResponseRecommendation] = Field(None, description="Response recommendation")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    is_reviewed: bool = Field(False, description="Whether manually reviewed")
    notes: str = Field("", description="Manual notes")
    tags: List[str] = Field(default_factory=list, description="Custom tags")
    # Apple-specific categorization
    apple_product_category: Optional[str] = Field(None, description="Primary Apple product category")
    apple_product_categories: List[str] = Field(default_factory=list, description="All Apple product categories mentioned")
    apple_topics: List[str] = Field(default_factory=list, description="Apple-specific topics discussed")
    apple_primary_topic: Optional[str] = Field(None, description="Primary Apple topic")
    is_apple_related: bool = Field(False, description="Whether post is Apple-related")

class MonitoringStats(BaseModel):
    total_mentions: int = Field(0, description="Total mentions found")
    threat_distribution: Dict[ThreatLevel, int] = Field(default_factory=dict, description="Threat level distribution")
    sentiment_distribution: Dict[SentimentType, int] = Field(default_factory=dict, description="Sentiment distribution")
    top_subreddits: List[Dict[str, Any]] = Field(default_factory=list, description="Top subreddits by mentions")
    trending_keywords: List[str] = Field(default_factory=list, description="Trending keywords")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class AlertConfig(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    name: str = Field(..., description="Alert configuration name")
    keywords: List[str] = Field(..., description="Keywords to monitor")
    subreddits: List[str] = Field(..., description="Subreddits to monitor")
    threat_threshold: float = Field(0.7, description="Minimum threat score to trigger alert")
    sentiment_filter: Optional[SentimentType] = Field(None, description="Filter by sentiment")
    is_active: bool = Field(True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class UserAction(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    mention_id: str = Field(..., description="Related mention ID")
    action_type: str = Field(..., description="Type of action taken")
    description: str = Field(..., description="Action description")
    user_id: str = Field(..., description="User who performed action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether request was successful")
    message: str = Field("", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")