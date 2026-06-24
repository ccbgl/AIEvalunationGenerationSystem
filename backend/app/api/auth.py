from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.schemas import UserCreate, TokenResp, UserOut
from backend.app.crud.user import get_user_by_username, create_user
from backend.app.utils.security import verify_password, make_token
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal

router = APIRouter(prefix='/api/auth', tags=['auth'])

@router.post('/register', response_model=UserOut)
async def register(payload: UserCreate):
    existing = await get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail='username exists')
    user = await create_user(payload.username, payload.password, role='user')
    return {"id": user.id, "username": user.username, "role": user.role.name}

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

@router.post('/logout')
async def logout(token: str):
    import aioredis
    redis = aioredis.from_url(settings.REDIS_URL)
    key = f"session:{token}"
    await redis.delete(key)
    return {"ok": True}
