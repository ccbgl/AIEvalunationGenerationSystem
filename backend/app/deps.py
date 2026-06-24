from fastapi import Depends, Header, Query, HTTPException
from typing import Optional
import aioredis
from backend.app.core.config import settings

async def get_redis():
    return aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)

async def extract_token(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> Optional[str]:
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
    return token

async def get_current_user(token: Optional[str] = Depends(extract_token)):
    if not token:
        raise HTTPException(status_code=401, detail='Missing token')
    redis = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    key = f"session:{token}"
    data = await redis.get(key)
    if not data:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    # stored format: "{user.id}|{username}|{role}"
    parts = data.split('|')
    return {"id": int(parts[0]), "username": parts[1], "role": parts[2]}
