from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Brand Monitor"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", env="ALLOWED_HOSTS")
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        return self.allowed_hosts.split(",")
    
    # Reddit API settings
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "BrandMonitor/1.0")
    reddit_username: str = os.getenv("REDDIT_USERNAME", "")
    reddit_password: str = os.getenv("REDDIT_PASSWORD", "")
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # MongoDB settings
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "brand_monitor")
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Monitoring settings
    brand_keywords: str = Field(default="your_brand,your_product", env="BRAND_KEYWORDS")
    monitor_subreddits: str = Field(default="all,technology,business", env="MONITOR_SUBREDDITS")
    
    @property
    def brand_keywords_list(self) -> List[str]:
        return self.brand_keywords.split(",")
    
    @property
    def monitor_subreddits_list(self) -> List[str]:
        return self.monitor_subreddits.split(",")
    monitor_interval: int = int(os.getenv("MONITOR_INTERVAL", "300"))
    threat_threshold: float = float(os.getenv("THREAT_THRESHOLD", "0.7"))
    
    # AI settings
    sentiment_model: str = os.getenv("SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")
    threat_detection_model: str = os.getenv("THREAT_DETECTION_MODEL", "gpt-3.5-turbo")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.3"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()