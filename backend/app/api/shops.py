from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import Shop
from backend.app.schemas.schemas import ShopOut, ShopBase
from backend.app.deps import extract_token, get_current_user
import aioredis
from backend.app.core.config import settings
from backend.app.models.models import UserBrowseHistory

router = APIRouter(prefix='/api/shops', tags=['shops'])

@router.get('/')
async def list_shops(q: Optional[str] = None, sort: Optional[str] = None, page: int = 1, page_size: int = 10):
    """List active shops with pagination.
    Query params:
      - q: optional search keyword for shop_name
      - sort: one of 'recommended' (default), 'good_rate', 'avg_cost', 'name'
      - page, page_size: pagination
    Returns: { total, page, page_size, items: [...] }
    """
    # normalize pagination
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10

    redis = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    cache_key = f"shop:list:active:{sort or 'recommended'}:{q or ''}:p{page}:s{page_size}"
    cached = await redis.get(cache_key)
    if cached:
        import json
        return json.loads(cached)

    async with AsyncSessionLocal() as session:
        # base filters
        base_q = select(Shop).where(Shop.is_active == 1)
        if q:
            base_q = base_q.where(Shop.shop_name.contains(q))
        # count total
        from sqlalchemy import select, func
        total_q = select(func.count()).select_from(Shop).where(Shop.is_active == 1)
        if q:
            total_q = total_q.where(Shop.shop_name.contains(q))
        total = (await session.execute(total_q)).scalar() or 0

        # apply sorting
        if sort == 'good_rate':
            base_q = base_q.order_by(Shop.good_rate.desc())
        elif sort == 'avg_cost':
            base_q = base_q.order_by(Shop.avg_cost.desc())
        elif sort == 'name':
            base_q = base_q.order_by(Shop.shop_name.asc())
        else:
            base_q = base_q.order_by(Shop.is_recommended.desc(), Shop.good_rate.desc())

        # pagination
        offset = (page - 1) * page_size
        q_page = base_q.offset(offset).limit(page_size)
        res = await session.execute(q_page)
        shops = res.scalars().all()

        items = []
        for s in shops:
            items.append({
                "id": s.id,
                "shop_name": s.shop_name,
                "address": s.address,
                "avg_cost": float(s.avg_cost),
                "description": s.description or '',
                "cover_image": s.cover_image,
                "good_rate": float(s.good_rate)
            })

        result = {"total": total, "page": page, "page_size": page_size, "items": items}
        try:
            await redis.set(cache_key, __import__('json').dumps(result), ex=settings.SHOP_CACHE_EXPIRE_MINUTES*60)
        except Exception:
            pass
        return result

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
async def create_shop(payload: ShopBase, current_user: dict = Depends(get_current_user)):
    # only shop or admin users can create a shop
    if current_user.get('role') not in ('shop', 'admin'):
        raise HTTPException(status_code=403, detail='Only shop users can create shops')
    async with AsyncSessionLocal() as session:
        # enforce one shop per shop-user
        q = select(Shop).where(Shop.owner_id == current_user['id'])
        res = await session.execute(q)
        existing = res.scalar_one_or_none()
        if existing and current_user.get('role') != 'admin':
            raise HTTPException(status_code=400, detail='shop already exists for this user')
        shop = Shop(owner_id=current_user['id'], shop_name=payload.shop_name, cover_image='', address=payload.address, avg_cost=payload.avg_cost, description=payload.description)
        session.add(shop)
        await session.commit()
        await session.refresh(shop)
        # clear shop list cache
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        return {"id": shop.id, "shop_name": shop.shop_name, "address": shop.address, "avg_cost": float(shop.avg_cost), "description": shop.description or '', "cover_image": shop.cover_image, "good_rate": float(shop.good_rate)}


@router.get('/me', response_model=ShopOut)
async def get_my_shop(current_user: dict = Depends(get_current_user)):
    # return the shop owned by current user
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.owner_id == current_user['id'])
        res = await session.execute(q)
        s = res.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail='shop not found')
        return {"id": s.id, "shop_name": s.shop_name, "address": s.address, "avg_cost": float(s.avg_cost), "description": s.description or '', "cover_image": s.cover_image, "good_rate": float(s.good_rate)}


@router.put('/{shop_id}', response_model=ShopOut)
async def update_shop(shop_id: int, payload: ShopBase, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id == shop_id)
        res = await session.execute(q)
        s = res.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail='shop not found')
        if current_user.get('role') != 'admin' and s.owner_id != current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        s.shop_name = payload.shop_name
        s.address = payload.address
        s.avg_cost = payload.avg_cost
        s.description = payload.description
        session.add(s)
        await session.commit()
        await session.refresh(s)
        # clear caches
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        await r.delete(f"shop:detail:{shop_id}")
        return {"id": s.id, "shop_name": s.shop_name, "address": s.address, "avg_cost": float(s.avg_cost), "description": s.description or '', "cover_image": s.cover_image, "good_rate": float(s.good_rate)}


@router.post('/{shop_id}/toggle')
async def toggle_shop_active(shop_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id == shop_id)
        res = await session.execute(q)
        s = res.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail='shop not found')
        if current_user.get('role') != 'admin' and s.owner_id != current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        s.is_active = 0 if s.is_active==1 else 1
        session.add(s)
        await session.commit()
        # clear caches
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        await r.delete(f"shop:detail:{shop_id}")
        return {"ok": True, "is_active": s.is_active}
