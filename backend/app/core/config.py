from __future__ import annotations

import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MYSQL_URL: str = os.getenv("MYSQL_URL", "mysql+aiomysql://root:root@127.0.0.1:3306/tea_shop")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "")
    MODEL_TIMEOUT: int = int(os.getenv("MODEL_TIMEOUT", "15"))
    TOKEN_EXPIRE_HOURS: int = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
    SHOP_CACHE_EXPIRE_MINUTES: int = int(os.getenv("SHOP_CACHE_EXPIRE_MINUTES", "60"))
    DAILY_AI_LIMIT_PER_USER: int = int(os.getenv("DAILY_AI_LIMIT_PER_USER", "20"))

settings = Settings()
