from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import Shop
from backend.app.schemas.schemas import ShopOut, ShopBase
from backend.app.deps import get_current_user
import aioredis
from backend.app.core.config import settings

router = APIRouter(prefix='/api/shops', tags=['shops'])

@router.get('/', response_model=List[ShopOut])
async def list_shops():
    redis = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    cached = await redis.get('shop:list:active')
    if cached:
        import json
        return json.loads(cached)
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.is_active==1).order_by(Shop.is_recommended.desc(), Shop.good_rate.desc())
        res = await session.execute(q)
        shops = res.scalars().all()
        out = []
        for s in shops:
            out.append({
                "id": s.id,
                "shop_name": s.shop_name,
                "address": s.address,
                "avg_cost": float(s.avg_cost),
                "description": s.description or '',
                "cover_image": s.cover_image,
                "good_rate": float(s.good_rate)
            })
        await redis.set('shop:list:active', __import__('json').dumps(out), ex=settings.SHOP_CACHE_EXPIRE_MINUTES*60)
        return out

@router.get('/{shop_id}', response_model=ShopOut)
async def get_shop(shop_id: int):
    redis = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    key = f"shop:detail:{shop_id}"
    cached = await redis.get(key)
    if cached:
        import json
        return json.loads(cached)
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id==shop_id, Shop.is_active==1)
        res = await session.execute(q)
        s = res.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail='shop not found')
        out = {"id": s.id, "shop_name": s.shop_name, "address": s.address, "avg_cost": float(s.avg_cost), "description": s.description or '', "cover_image": s.cover_image, "good_rate": float(s.good_rate)}
        await redis.set(key, __import__('json').dumps(out), ex=settings.SHOP_CACHE_EXPIRE_MINUTES*60)
        return out

@router.post('/', response_model=ShopOut)
async def create_shop(payload: ShopBase, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'shop' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Only shop users can create shops')
    async with AsyncSessionLocal() as session:
        shop = Shop(owner_id=current_user['id'], shop_name=payload.shop_name, cover_image='', address=payload.address, avg_cost=payload.avg_cost, description=payload.description)
        session.add(shop)
        await session.commit()
        await session.refresh(shop)
        # clear shop list cache
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        return {"id": shop.id, "shop_name": shop.shop_name, "address": shop.address, "avg_cost": float(shop.avg_cost), "description": shop.description or '', "cover_image": shop.cover_image, "good_rate": float(shop.good_rate)}

@router.put('/{shop_id}', response_model=ShopOut)
async def update_shop(shop_id: int, payload: ShopBase, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id==shop_id)
        res = await session.execute(q)
        shop = res.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail='shop not found')
        if current_user['role']!='admin' and shop.owner_id!=current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        shop.shop_name = payload.shop_name
        shop.address = payload.address
        shop.avg_cost = payload.avg_cost
        shop.description = payload.description
        session.add(shop)
        await session.commit()
        # clear caches
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        await r.delete(f"shop:detail:{shop_id}")
        return {"id": shop.id, "shop_name": shop.shop_name, "address": shop.address, "avg_cost": float(shop.avg_cost), "description": shop.description or '', "cover_image": shop.cover_image, "good_rate": float(shop.good_rate)}
