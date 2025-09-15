import praw
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone
from loguru import logger
import re

from app.core.config import settings
from app.models.schemas import RedditPost, PostType

class RedditClient:
    """Reddit API client for fetching posts and comments"""
    
    def __init__(self):
        self.reddit = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize Reddit client"""
        try:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
            
            # Test connection with read-only access
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.reddit.subreddit('test').hot(limit=1).__next__()
            )
            
            self.is_initialized = True
            logger.info("Reddit client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            raise
    
    def _extract_keywords_from_text(self, text: str, keywords: List[str]) -> List[str]:
        """Extract matching keywords from text"""
        if not text:
            return []
            
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower and keyword_lower in text_lower:
                found_keywords.append(keyword)
                
        return found_keywords
    
    def _convert_submission_to_post(self, submission) -> RedditPost:
        """Convert Reddit submission to RedditPost model"""
        return RedditPost(
            id=submission.id,
            title=submission.title,
            content=submission.selftext or "",
            author=str(submission.author) if submission.author else "[deleted]",
            subreddit=str(submission.subreddit),
            url=submission.url,
            score=submission.score,
            num_comments=submission.num_comments,
            created_utc=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            post_type=PostType.POST,
            permalink=f"https://reddit.com{submission.permalink}"
        )
    
    def _convert_comment_to_post(self, comment, submission_title: str = "") -> RedditPost:
        """Convert Reddit comment to RedditPost model"""
        return RedditPost(
            id=comment.id,
            title=submission_title,
            content=comment.body or "",
            author=str(comment.author) if comment.author else "[deleted]",
            subreddit=str(comment.subreddit),
            url=f"https://reddit.com{comment.permalink}",
            score=comment.score,
            num_comments=0,
            created_utc=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
            post_type=PostType.COMMENT,
            permalink=f"https://reddit.com{comment.permalink}"
        )
    
    async def search_posts_by_keywords(
        self, 
        keywords: List[str], 
        subreddits: List[str] = None,
        limit: int = 100,
        time_filter: str = "day"
    ) -> AsyncGenerator[RedditPost, None]:
        """Search for posts containing brand keywords"""
        if not self.is_initialized:
            raise RuntimeError("Reddit client not initialized")
        
        try:
            # Prepare search query
            search_query = " OR ".join([f'"{keyword}"' for keyword in keywords])
            
            # Determine subreddits to search
            if not subreddits or "all" in subreddits:
                subreddit_obj = self.reddit.subreddit("all")
            else:
                subreddit_names = "+".join(subreddits)
                subreddit_obj = self.reddit.subreddit(subreddit_names)
            
            logger.info(f"Searching Reddit for: {search_query} in {subreddit_obj.display_name}")
            
            # Search submissions
            submissions = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(subreddit_obj.search(
                    search_query,
                    sort="new",
                    time_filter=time_filter,
                    limit=limit
                ))
            )
            
            for submission in submissions:
                try:
                    # Check if keywords are actually in the content
                    title_keywords = self._extract_keywords_from_text(submission.title, keywords)
                    content_keywords = self._extract_keywords_from_text(submission.selftext, keywords)
                    
                    if title_keywords or content_keywords:
                        reddit_post = self._convert_submission_to_post(submission)
                        yield reddit_post
                        
                        # Also check comments for keywords
                        await asyncio.sleep(0.1)  # Rate limiting
                        async for comment_post in self._search_comments_in_submission(submission, keywords):
                            yield comment_post
                            
                except Exception as e:
                    logger.warning(f"Error processing submission {submission.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching Reddit posts: {e}")
            raise
    
    async def _search_comments_in_submission(
        self, 
        submission, 
        keywords: List[str],
        max_comments: int = 50
    ) -> AsyncGenerator[RedditPost, None]:
        """Search for comments containing keywords in a submission"""
        try:
            # Expand all comments
            await asyncio.get_event_loop().run_in_executor(
                None, submission.comments.replace_more, 0
            )
            
            comment_count = 0
            for comment in submission.comments.list():
                if comment_count >= max_comments:
                    break
                    
                try:
                    if hasattr(comment, 'body') and comment.body:
                        comment_keywords = self._extract_keywords_from_text(comment.body, keywords)
                        
                        if comment_keywords:
                            reddit_post = self._convert_comment_to_post(comment, submission.title)
                            yield reddit_post
                            comment_count += 1
                            
                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error searching comments in submission: {e}")
    
    async def get_hot_posts(
        self, 
        subreddits: List[str] = None,
        limit: int = 50
    ) -> AsyncGenerator[RedditPost, None]:
        """Get hot posts from specified subreddits"""
        if not self.is_initialized:
            raise RuntimeError("Reddit client not initialized")
        
        try:
            # Determine subreddits
            if not subreddits or "all" in subreddits:
                subreddit_obj = self.reddit.subreddit("all")
            else:
                subreddit_names = "+".join(subreddits)
                subreddit_obj = self.reddit.subreddit(subreddit_names)
            
            # Get hot submissions
            submissions = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(subreddit_obj.hot(limit=limit))
            )
            
            for submission in submissions:
                try:
                    reddit_post = self._convert_submission_to_post(submission)
                    yield reddit_post
                except Exception as e:
                    logger.warning(f"Error processing hot post {submission.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting hot posts: {e}")
            raise
    
    async def get_post_by_id(self, post_id: str) -> Optional[RedditPost]:
        """Get a specific post by ID"""
        if not self.is_initialized:
            raise RuntimeError("Reddit client not initialized")
        
        try:
            submission = await asyncio.get_event_loop().run_in_executor(
                None, self.reddit.submission, post_id
            )
            
            return self._convert_submission_to_post(submission)
            
        except Exception as e:
            logger.error(f"Error getting post {post_id}: {e}")
            return None
    
    async def monitor_subreddit_stream(
        self, 
        subreddit_name: str,
        keywords: List[str]
    ) -> AsyncGenerator[RedditPost, None]:
        """Monitor a subreddit stream for new posts with keywords"""
        if not self.is_initialized:
            raise RuntimeError("Reddit client not initialized")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Stream new submissions
            for submission in subreddit.stream.submissions(skip_existing=True):
                try:
                    # Check for keywords
                    title_keywords = self._extract_keywords_from_text(submission.title, keywords)
                    content_keywords = self._extract_keywords_from_text(submission.selftext, keywords)
                    
                    if title_keywords or content_keywords:
                        reddit_post = self._convert_submission_to_post(submission)
                        yield reddit_post
                        
                except Exception as e:
                    logger.warning(f"Error processing streamed submission: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error monitoring subreddit stream: {e}")
            raise