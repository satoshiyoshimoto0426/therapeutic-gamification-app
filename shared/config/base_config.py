"""
Base configuration for all microservices
Handles environment variables, database connections, and common settings
"""

import os
from typing import Optional
from pydantic import BaseSettings
from google.cloud import firestore
import redis
from functools import lru_cache

class BaseConfig(BaseSettings):
    """Base configuration class for all services"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Google Cloud
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "therapeutic-gamification")
    firestore_database: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # AI Services
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # External APIs
    line_channel_secret: Optional[str] = os.getenv("LINE_CHANNEL_SECRET")
    line_channel_access_token: Optional[str] = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Performance
    max_concurrent_ai_requests: int = int(os.getenv("MAX_CONCURRENT_AI_REQUESTS", "200"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # RPG System Configuration
    gacha_rates: dict = {
        "common": 0.60,
        "uncommon": 0.25,
        "rare": 0.10,
        "epic": 0.04,
        "legendary": 0.01
    }
    gacha_costs: dict = {
        "single": 100,
        "ten_pull": 900,
        "premium": 300
    }
    coin_rates: dict = {
        "task_completion": {"routine": 10, "one_shot": 15, "skill_up": 20, "social": 25},
        "demon_defeat": {"common": 50, "rare": 100, "epic": 200, "legendary": 500},
        "daily_bonus": 30,
        "reflection_bonus": 25
    }
    
    # Growth Note Configuration
    reflection_time: str = "22:00"
    reflection_xp_reward: int = 25
    reminder_threshold_days: int = 2
    
    # ADHD Support Configuration
    default_task_limit: int = 16
    pomodoro_default_duration: int = 25
    break_reminder_interval: int = 60  # minutes
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_config() -> BaseConfig:
    """Get cached configuration instance"""
    return BaseConfig()

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self._firestore_client = None
        self._redis_client = None
    
    @property
    def firestore(self) -> firestore.Client:
        """Get Firestore client with lazy initialization"""
        if self._firestore_client is None:
            self._firestore_client = firestore.Client(
                project=self.config.project_id,
                database=self.config.firestore_database
            )
        return self._firestore_client
    
    @property
    def redis(self) -> redis.Redis:
        """Get Redis client with lazy initialization"""
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                decode_responses=True
            )
        return self._redis_client
    
    def get_collection(self, collection_name: str):
        """Get Firestore collection reference"""
        return self.firestore.collection(collection_name)
    
    def cache_get(self, key: str):
        """Get value from Redis cache"""
        try:
            return self.redis.get(key)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def cache_set(self, key: str, value: str, ttl: int = 3600):
        """Set value in Redis cache with TTL"""
        try:
            return self.redis.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager(get_config())

def get_firestore_client() -> firestore.Client:
    """Get Firestore client instance"""
    return db_manager.firestore