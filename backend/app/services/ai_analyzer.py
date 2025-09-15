from openai import AsyncOpenAI
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Any, Optional
from loguru import logger
import re
import asyncio
from textblob import TextBlob

from app.core.config import settings
from app.models.schemas import (
    SentimentAnalysis, ThreatAnalysis, ResponseRecommendation,
    SentimentType, ThreatLevel, RedditPost
)

class AIAnalyzer:
    """AI service for sentiment analysis and threat detection"""
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.openai_client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize AI models and clients"""
        try:
            # Initialize OpenAI client
            if settings.openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            
            # Initialize sentiment analysis pipeline
            await self._initialize_sentiment_model()
            
            self.is_initialized = True
            logger.info("AI Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Analyzer: {e}")
            raise
    
    async def _initialize_sentiment_model(self):
        """Initialize sentiment analysis model"""
        try:
            # Load pre-trained sentiment model
            model_name = settings.sentiment_model
            
            # Run in executor to avoid blocking
            self.sentiment_pipeline = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
            )
            
            logger.info(f"Sentiment model loaded: {model_name}")
            
        except Exception as e:
            logger.warning(f"Failed to load sentiment model, using fallback: {e}")
            # Fallback to TextBlob
            self.sentiment_pipeline = None
    
    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment of text"""
        if not text or not text.strip():
            return SentimentAnalysis(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0
            )
        
        try:
            if self.sentiment_pipeline:
                # Use transformer model
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self._analyze_with_transformer, text
                )
                return result
            else:
                # Fallback to TextBlob
                return await self._analyze_with_textblob(text)
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment on error
            return SentimentAnalysis(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0
            )
    
    def _analyze_with_transformer(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment using transformer model"""
        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        result = self.sentiment_pipeline(text)
        
        # Parse result
        label = result[0]['label'].lower()
        confidence = result[0]['score']
        
        # Map labels to our sentiment types
        if 'positive' in label or label == 'label_2':
            sentiment = SentimentType.POSITIVE
            positive_score = confidence
            negative_score = 0.0
            neutral_score = 1.0 - confidence
        elif 'negative' in label or label == 'label_0':
            sentiment = SentimentType.NEGATIVE
            positive_score = 0.0
            negative_score = confidence
            neutral_score = 1.0 - confidence
        else:
            sentiment = SentimentType.NEUTRAL
            positive_score = 0.0
            negative_score = 0.0
            neutral_score = confidence
        
        return SentimentAnalysis(
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score
        )
    
    async def _analyze_with_textblob(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment using TextBlob (fallback)"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        # Convert polarity to our format
        if polarity > 0.1:
            sentiment = SentimentType.POSITIVE
            positive_score = (polarity + 1) / 2
            negative_score = 0.0
            neutral_score = 1.0 - positive_score
            confidence = abs(polarity)
        elif polarity < -0.1:
            sentiment = SentimentType.NEGATIVE
            positive_score = 0.0
            negative_score = (abs(polarity) + 1) / 2
            neutral_score = 1.0 - negative_score
            confidence = abs(polarity)
        else:
            sentiment = SentimentType.NEUTRAL
            positive_score = 0.0
            negative_score = 0.0
            neutral_score = 1.0
            confidence = 1.0 - abs(polarity)
        
        return SentimentAnalysis(
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score
        )
    
    async def analyze_threat(self, reddit_post: RedditPost, keywords: List[str]) -> ThreatAnalysis:
        """Analyze potential threats in a Reddit post"""
        try:
            # Combine title and content for analysis
            full_text = f"{reddit_post.title or ''} {reddit_post.content or ''}".strip()
            
            # Find matched keywords
            matched_keywords = self._find_matched_keywords(full_text, keywords)
            
            # Calculate base threat score
            threat_score = await self._calculate_threat_score(reddit_post, full_text, matched_keywords)
            
            # Determine threat level
            threat_level = self._determine_threat_level(threat_score)
            
            # Identify threat categories
            threat_categories = await self._identify_threat_categories(full_text)
            
            # Generate context analysis
            context_analysis = await self._analyze_context(reddit_post, full_text)
            
            # Assess potential impact
            potential_impact = await self._assess_potential_impact(reddit_post, threat_score)
            
            return ThreatAnalysis(
                threat_level=threat_level,
                threat_score=threat_score,
                threat_categories=threat_categories,
                keywords_matched=matched_keywords,
                context_analysis=context_analysis,
                potential_impact=potential_impact
            )
            
        except Exception as e:
            logger.error(f"Error analyzing threat: {e}")
            # Return low threat on error
            return ThreatAnalysis(
                threat_level=ThreatLevel.LOW,
                threat_score=0.1,
                threat_categories=[],
                keywords_matched=[],
                context_analysis="Error occurred during analysis",
                potential_impact="Unable to assess impact"
            )
    
    def _find_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find keywords that match in the text"""
        text_lower = text.lower()
        matched = []
        
        for keyword in keywords:
            if keyword.lower().strip() in text_lower:
                matched.append(keyword)
        
        return matched
    
    async def _calculate_threat_score(self, reddit_post: RedditPost, text: str, matched_keywords: List[str]) -> float:
        """Calculate threat score based on various factors"""
        score = 0.0
        
        # Keyword matching factor (0.0 - 0.3)
        keyword_factor = min(len(matched_keywords) * 0.1, 0.3)
        score += keyword_factor
        
        # Negative sentiment factor (0.0 - 0.4)
        sentiment = await self.analyze_sentiment(text)
        if sentiment.sentiment == SentimentType.NEGATIVE:
            sentiment_factor = sentiment.confidence * 0.4
            score += sentiment_factor
        
        # Engagement factor (0.0 - 0.2)
        if reddit_post.score < -5:  # Heavily downvoted
            score += 0.1
        elif reddit_post.num_comments > 50:  # High engagement
            score += 0.1
        
        # Content analysis factor (0.0 - 0.3)
        threat_words = [
            'scam', 'fraud', 'terrible', 'awful', 'worst', 'hate', 'boycott',
            'lawsuit', 'legal action', 'complaint', 'refund', 'broken', 'defective',
            'dangerous', 'unsafe', 'toxic', 'avoid', 'warning', 'alert'
        ]
        
        text_lower = text.lower()
        threat_word_count = sum(1 for word in threat_words if word in text_lower)
        content_factor = min(threat_word_count * 0.05, 0.3)
        score += content_factor
        
        return min(score, 1.0)
    
    def _determine_threat_level(self, threat_score: float) -> ThreatLevel:
        """Determine threat level based on score"""
        if threat_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            return ThreatLevel.HIGH
        elif threat_score >= 0.3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _identify_threat_categories(self, text: str) -> List[str]:
        """Identify categories of threats"""
        categories = []
        text_lower = text.lower()
        
        # Define threat category keywords
        category_keywords = {
            'Product Quality': ['defective', 'broken', 'poor quality', 'faulty', 'malfunctioning'],
            'Customer Service': ['rude', 'unhelpful', 'poor service', 'bad support', 'ignored'],
            'Pricing': ['overpriced', 'expensive', 'rip off', 'scam', 'money grab'],
            'Security': ['data breach', 'privacy', 'security', 'hack', 'leak'],
            'Legal': ['lawsuit', 'legal action', 'sue', 'court', 'lawyer'],
            'Reputation': ['boycott', 'avoid', 'warning', 'alert', 'reputation'],
            'Competition': ['competitor', 'alternative', 'better option', 'switch to']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    async def _analyze_context(self, reddit_post: RedditPost, text: str) -> str:
        """Analyze context using AI"""
        if not self.openai_client or not settings.openai_api_key:
            return "Context analysis unavailable (OpenAI not configured)"
        
        try:
            prompt = f"""
            Analyze the following Reddit post for brand-related threats or concerns:
            
            Subreddit: {reddit_post.subreddit}
            Title: {reddit_post.title}
            Content: {reddit_post.content}
            Score: {reddit_post.score}
            Comments: {reddit_post.num_comments}
            
            Provide a brief analysis of:
            1. The main concern or issue raised
            2. The tone and sentiment
            3. Potential impact on brand reputation
            4. Context and background
            
            Keep the analysis concise (max 200 words).
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.ChatCompletion.create(
                    model=settings.threat_detection_model,
                    messages=[
                        {"role": "system", "content": "You are a brand monitoring expert analyzing social media content for potential threats."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in context analysis: {e}")
            return f"Context analysis failed: {str(e)}"
    
    async def _assess_potential_impact(self, reddit_post: RedditPost, threat_score: float) -> str:
        """Assess potential impact of the threat"""
        impact_factors = []
        
        # Subreddit reach
        high_reach_subreddits = ['all', 'popular', 'technology', 'business', 'news']
        if reddit_post.subreddit.lower() in high_reach_subreddits:
            impact_factors.append("High visibility subreddit")
        
        # Engagement level
        if reddit_post.score > 100:
            impact_factors.append("High upvote count")
        elif reddit_post.score < -10:
            impact_factors.append("Negative community response")
        
        if reddit_post.num_comments > 50:
            impact_factors.append("High engagement (many comments)")
        
        # Threat score impact
        if threat_score > 0.7:
            impact_factors.append("Severe threat detected")
        elif threat_score > 0.4:
            impact_factors.append("Moderate threat level")
        
        if not impact_factors:
            return "Low potential impact - limited reach and engagement"
        
        return "Potential impact: " + ", ".join(impact_factors)
    
    async def analyze_title_sentiment(self, title: str) -> Dict[str, Any]:
        """Analyze sentiment of Reddit post title using OpenAI"""
        if not title or not title.strip():
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "explanation": "Empty title",
                "is_positive": False,
                "is_negative": False
            }
        
        try:
            if self.openai_client and settings.openai_api_key:
                try:
                    # Use OpenAI for more accurate sentiment analysis
                    prompt = f"""
Проаналізуй настрій наступного заголовка поста з Reddit та визнач чи він позитивний, негативний або нейтральний.

Заголовок: "{title}"

Відповідь у форматі JSON:
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "explanation": "коротке пояснення чому такий настрій",
    "is_positive": true/false,
    "is_negative": true/false
}}

Врахуй контекст, сарказм, іронію та емоційне забарвлення слів."""
                    
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Ти експерт з аналізу настроїв тексту. Відповідай тільки у форматі JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.3
                    )
                    
                    import json
                    result = json.loads(response.choices[0].message.content.strip())
                    return result
                    
                except Exception as openai_error:
                    logger.warning(f"OpenAI API error, falling back to basic analysis: {openai_error}")
                    # Fall through to basic analysis
            
            # Fallback to basic sentiment analysis
            sentiment_result = await self.analyze_sentiment(title)
            return {
                "sentiment": sentiment_result.sentiment.value,
                "confidence": sentiment_result.confidence,
                "explanation": f"Basic analysis: {sentiment_result.sentiment.value}",
                "is_positive": sentiment_result.sentiment == SentimentType.POSITIVE,
                "is_negative": sentiment_result.sentiment == SentimentType.NEGATIVE
            }
                
        except Exception as e:
            logger.error(f"Error analyzing title sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "explanation": f"Analysis error: {str(e)}",
                "is_positive": False,
                "is_negative": False
            }
    
    async def analyze_posts_sentiment_batch(self, posts: List[RedditPost]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple posts"""
        results = []
        
        for post in posts:
            title_sentiment = await self.analyze_title_sentiment(post.title)
            content_sentiment = await self.analyze_sentiment(post.content) if post.content else None
            
            result = {
                "post_id": post.id,
                "title": post.title,
                "title_sentiment": title_sentiment,
                "content_sentiment": {
                    "sentiment": content_sentiment.sentiment.value if content_sentiment else "neutral",
                    "confidence": content_sentiment.confidence if content_sentiment else 0.0
                } if content_sentiment else None,
                "overall_sentiment": title_sentiment["sentiment"],  # Title has more weight
                "subreddit": post.subreddit,
                "score": post.score,
                "created_utc": post.created_utc.isoformat()
            }
            
            results.append(result)
            
        return results

    async def generate_response_recommendation(self, reddit_post: RedditPost, threat_analysis: ThreatAnalysis) -> ResponseRecommendation:
        """Generate response recommendations"""
        try:
            # Determine action type based on threat level
            if threat_analysis.threat_level == ThreatLevel.CRITICAL:
                action_type = "Immediate Response Required"
                priority = 5
                escalation_needed = True
            elif threat_analysis.threat_level == ThreatLevel.HIGH:
                action_type = "Urgent Response"
                priority = 4
                escalation_needed = True
            elif threat_analysis.threat_level == ThreatLevel.MEDIUM:
                action_type = "Standard Response"
                priority = 3
                escalation_needed = False
            else:
                action_type = "Monitor"
                priority = 1
                escalation_needed = False
            
            # Generate message template
            message_template = await self._generate_message_template(reddit_post, threat_analysis)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(threat_analysis)
            
            return ResponseRecommendation(
                action_type=action_type,
                priority=priority,
                message_template=message_template,
                escalation_needed=escalation_needed,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error generating response recommendation: {e}")
            return ResponseRecommendation(
                action_type="Review Required",
                priority=2,
                message_template="Please review this mention manually.",
                escalation_needed=False,
                reasoning="Error occurred during recommendation generation"
            )
    
    async def _generate_message_template(self, reddit_post: RedditPost, threat_analysis: ThreatAnalysis) -> str:
        """Generate response message template"""
        if threat_analysis.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            return """
            Thank you for bringing this to our attention. We take all feedback seriously and would like to address your concerns directly. 
            Please send us a private message with more details so we can investigate and resolve this issue promptly.
            """
        elif threat_analysis.threat_level == ThreatLevel.MEDIUM:
            return """
            We appreciate your feedback and would like to learn more about your experience. 
            Please feel free to reach out to our customer support team so we can assist you better.
            """
        else:
            return "Monitor for further developments. Consider engaging if conversation grows."
    
    def _generate_reasoning(self, threat_analysis: ThreatAnalysis) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        reasons.append(f"Threat level: {threat_analysis.threat_level.value}")
        reasons.append(f"Threat score: {threat_analysis.threat_score:.2f}")
        
        if threat_analysis.keywords_matched:
            reasons.append(f"Brand keywords detected: {', '.join(threat_analysis.keywords_matched)}")
        
        if threat_analysis.threat_categories:
            reasons.append(f"Threat categories: {', '.join(threat_analysis.threat_categories)}")
        
        return "; ".join(reasons)