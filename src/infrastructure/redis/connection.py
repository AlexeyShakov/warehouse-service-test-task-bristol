import redis.asyncio as redis
from src.config import get_project_settings

SETTINGS = get_project_settings()

REDIS_CLIENT = redis.Redis(
    host=SETTINGS.redis_host, port=SETTINGS.redis_port, decode_responses=True
)
