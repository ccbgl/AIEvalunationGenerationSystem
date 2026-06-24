from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.app.deps import get_current_user
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import UserEvaluation, EvaluationLike, EvaluationReply, Shop
from sqlalchemy import select, func
from backend.app.services.ai_service import generate_evaluation
from backend.app.services.stats import recompute_good_rate
import asyncio
import aioredis
from backend.app.core.config import settings
from datetime import datetime
import math

router = APIRouter(prefix='/api/evaluations', tags=['evaluations'])

class EvalCreate(BaseModel):
    shop_id: int
    level: str
    tags: list
    target_platform: str
    content: str = ''
    is_ai: bool = False

@router.post('/generate')
async def generate(payload: EvalCreate, token: str = ''):
    # token param optional as user may pass token in query or header; simplified
    # check daily limits
    # here payload must include shop_id etc.
    # simulate current_user retrieval via token
    from backend.app.deps import extract_token, get_current_user
    raise HTTPException(status_code=501, detail='use POST /api/evaluations/generate_authenticated with auth token')

@router.post('/generate_authenticated')
async def generate_authenticated(payload: EvalCreate, current_user: dict = Depends(get_current_user)):
    # rate limit
    today = datetime.utcnow().strftime('%Y-%m-%d')
    limit_key = f"limit:ai:{current_user['id']}:{today}"
    r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    count = await r.get(limit_key) or '0'
    count = int(count)
    if count >= settings.DAILY_AI_LIMIT_PER_USER:
        raise HTTPException(status_code=429, detail='daily ai limit reached')
    # call ai
    gen_req = type('X', (), {})()
    gen_req.shop_id = payload.shop_id
    gen_req.level = payload.level
    gen_req.tags = payload.tags
    gen_req.target_platform = payload.target_platform
    content = await generate_evaluation(gen_req)
    await r.set(limit_key, str(count+1), ex=24*3600)
    return {"content": content}

@router.post('/')
async def submit_eval(payload: EvalCreate, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        ev = UserEvaluation(user_id=current_user['id'], shop_id=payload.shop_id, level=payload.level, tags=','.join(payload.tags), target_platform=payload.target_platform, content=payload.content or '', is_ai_generated=1 if payload.is_ai else 0)
        session.add(ev)
        await session.commit()
        await session.refresh(ev)
        # async recompute
        asyncio.create_task(recompute_good_rate(payload.shop_id))
        # clear caches
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        await r.delete(f"shop:detail:{payload.shop_id}")
        return {"id": ev.id}

@router.post('/{evaluation_id}/like')
async def like_evaluation(evaluation_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        # check existing
        q = select(EvaluationLike).where(EvaluationLike.evaluation_id==evaluation_id, EvaluationLike.user_id==current_user['id'])
        res = await session.execute(q)
        existing = res.scalar_one_or_none()
        if existing:
            # unlike
            await session.delete(existing)
            # decrement count
            q2 = select(UserEvaluation).where(UserEvaluation.id==evaluation_id)
            res2 = await session.execute(q2)
            ev = res2.scalar_one_or_none()
            if ev and ev.like_count>0:
                ev.like_count -=1
                session.add(ev)
            await session.commit()
            return {"liked": False}
        else:
            like = EvaluationLike(evaluation_id=evaluation_id, user_id=current_user['id'])
            session.add(like)
            q2 = select(UserEvaluation).where(UserEvaluation.id==evaluation_id)
            res2 = await session.execute(q2)
            ev = res2.scalar_one_or_none()
            if ev:
                ev.like_count +=1
                session.add(ev)
            await session.commit()
            return {"liked": True}

@router.post('/{evaluation_id}/reply')
async def reply_evaluation(evaluation_id: int, content: str, parent_reply_id: int = None, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        reply = EvaluationReply(evaluation_id=evaluation_id, reply_user_id=current_user['id'], reply_role=current_user['role'], content=content, parent_reply_id=parent_reply_id)
        session.add(reply)
        # update reply_count
        q = select(UserEvaluation).where(UserEvaluation.id==evaluation_id)
        res = await session.execute(q)
        ev = res.scalar_one_or_none()
        if ev:
            ev.reply_count +=1
            session.add(ev)
        await session.commit()
        return {"id": reply.id}

@router.get('/user', response_model=list)
async def list_my_evaluations(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserEvaluation).where(UserEvaluation.user_id == current_user['id']).order_by(UserEvaluation.create_time.desc())
        res = await session.execute(q)
        rows = res.scalars().all()
        out = []
        for r in rows:
            out.append({
                "id": r.id,
                "shop_id": r.shop_id,
                "level": r.level.name if hasattr(r.level, 'name') else str(r.level),
                "tags": r.tags,
                "target_platform": r.target_platform,
                "content": r.content,
                "is_ai_generated": bool(r.is_ai_generated),
                "like_count": r.like_count,
                "reply_count": r.reply_count,
                "create_time": r.create_time.isoformat()
            })
        return out

@router.get('/user_paginated')
async def list_my_evaluations_paginated(page: int = 1, page_size: int = 10, current_user: dict = Depends(get_current_user)):
    """Return paginated list of current user's evaluations."""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    async with AsyncSessionLocal() as session:
        total_q = select(func.count()).select_from(UserEvaluation).where(UserEvaluation.user_id == current_user['id'])
        total = (await session.execute(total_q)).scalar() or 0
        # calculate total_pages using math.ceil, ensure at least 1
        total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
        q = select(UserEvaluation).where(UserEvaluation.user_id == current_user['id']).order_by(UserEvaluation.create_time.desc()).offset((page-1)*page_size).limit(page_size)
        res = await session.execute(q)
        rows = res.scalars().all()
        items = []
        for r in rows:
            items.append({
                "id": r.id,
                "shop_id": r.shop_id,
                "level": r.level.name if hasattr(r.level, 'name') else str(r.level),
                "tags": r.tags,
                "target_platform": r.target_platform,
                "content": r.content,
                "is_ai_generated": bool(r.is_ai_generated),
                "like_count": r.like_count,
                "reply_count": r.reply_count,
                "create_time": r.create_time.isoformat()
            })
        return {"total": total, "total_pages": total_pages, "page": page, "page_size": page_size, "items": items}
