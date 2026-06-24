from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import Shop
from backend.app.schemas.schemas import ShopOut, ShopBase
from backend.app.deps import extract_token
import aioredis
from backend.app.core.config import settings
from backend.app.models.models import UserBrowseHistory

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
async def get_shop(shop_id: int, token: Optional[str] = Depends(extract_token)):
    redis = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    key = f"shop:detail:{shop_id}"
    cached = await redis.get(key)
    if cached:
        import json
        # try to record history asynchronously
        if token:
            data = await redis.get(f"session:{token}")
            if data:
                try:
                    user_id = int(data.split('|')[0])
                    async with AsyncSessionLocal() as session:
                        bh = UserBrowseHistory(user_id=user_id, shop_id=shop_id)
                        session.add(bh)
                        await session.commit()
                except Exception:
                    pass
        return json.loads(cached)
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id==shop_id, Shop.is_active==1)
        res = await session.execute(q)
        s = res.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail='shop not found')
        out = {"id": s.id, "shop_name": s.shop_name, "address": s.address, "avg_cost": float(s.avg_cost), "description": s.description or '', "cover_image": s.cover_image, "good_rate": float(s.good_rate)}
        await redis.set(key, __import__('json').dumps(out), ex=settings.SHOP_CACHE_EXPIRE_MINUTES*60)
        # record browse history if token present
        if token:
            data = await redis.get(f"session:{token}")
            if data:
                try:
                    user_id = int(data.split('|')[0])
                    bh = UserBrowseHistory(user_id=user_id, shop_id=shop_id)
                    session.add(bh)
                    await session.commit()
                except Exception:
                    pass
        return out

@router.post('/', response_model=ShopOut)
async def create_shop(payload: ShopBase, current_user: dict = None):
    # kept simple: current_user handling delegated to auth middleware if added
    if current_user and current_user.get('role') not in ('shop', 'admin'):
        raise HTTPException(status_code=403, detail='Only shop users can create shops')
    async with AsyncSessionLocal() as session:
        shop = Shop(owner_id=(current_user['id'] if current_user else 0), shop_name=payload.shop_name, cover_image='', address=payload.address, avg_cost=payload.avg_cost, description=payload.description)
        session.add(shop)
        await session.commit()
        await session.refresh(shop)
        # clear shop list cache
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        return {"id": shop.id, "shop_name": shop.shop_name, "address": shop.address, "avg_cost": float(shop.avg_cost), "description": shop.description or '', "cover_image": shop.cover_image, "good_rate": float(shop.good_rate)}
