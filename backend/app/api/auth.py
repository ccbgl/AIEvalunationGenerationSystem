from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional
from backend.app.schemas.schemas import UserCreate, TokenResp, UserOut, RegisterResp, LogoutReq
from backend.app.crud.user import get_user_by_username, create_user
from backend.app.utils.security import verify_password, make_token
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.deps import extract_token

router = APIRouter(prefix='/api/auth', tags=['auth'])

@router.post('/register', response_model=RegisterResp)
async def register(payload: UserCreate):
    existing = await get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail='username exists')
    user = await create_user(payload.username, payload.password, role='user')
    # auto-login: generate token and store session in redis
    import aioredis
    redis = aioredis.from_url(settings.REDIS_URL)
    token = make_token()
    key = f"session:{token}"
    await redis.set(key, f"{user.id}|{user.username}|{user.role.name}", ex=settings.TOKEN_EXPIRE_HOURS*3600)
    return {"user": {"id": user.id, "username": user.username, "role": user.role.name}, "token": token, "expire_hours": settings.TOKEN_EXPIRE_HOURS}

@router.post('/login', response_model=TokenResp)
async def login(payload: UserCreate):
    user = await get_user_by_username(payload.username)
    if not user:
        raise HTTPException(status_code=400, detail='invalid credentials')
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail='invalid credentials')
    token = make_token()
    # store session in redis (simple example)
    import aioredis
    redis = aioredis.from_url(settings.REDIS_URL)
    key = f"session:{token}"
    await redis.set(key, f"{user.id}|{user.username}|{user.role.name}", ex=settings.TOKEN_EXPIRE_HOURS*3600)
    return {"token": token, "expire_hours": settings.TOKEN_EXPIRE_HOURS}

@router.post('/register_shop', response_model=RegisterResp)
async def register_shop(payload: UserCreate):
    existing = await get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail='username exists')
    # create user with shop role
    user = await create_user(payload.username, payload.password, role='shop')
    # auto-login: generate token and store session in redis
    import aioredis
    redis = aioredis.from_url(settings.REDIS_URL)
    token = make_token()
    key = f"session:{token}"
    await redis.set(key, f"{user.id}|{user.username}|{user.role.name}", ex=settings.TOKEN_EXPIRE_HOURS*3600)
    return {"user": {"id": user.id, "username": user.username, "role": user.role.name}, "token": token, "expire_hours": settings.TOKEN_EXPIRE_HOURS}

@router.post('/logout')
async def logout(payload: LogoutReq = Body(None), token: Optional[str] = Depends(extract_token)):
    import aioredis
    redis = aioredis.from_url(settings.REDIS_URL)
    # prefer explicit token in body, fallback to Authorization header
    t = None
    if payload is not None and getattr(payload, 'token', None):
        t = payload.token
    if not t:
        t = token
    if not t:
        raise HTTPException(status_code=400, detail='missing token')
    key = f"session:{t}"
    await redis.delete(key)
    return {"ok": True}
