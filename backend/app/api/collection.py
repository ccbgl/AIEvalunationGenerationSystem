from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_current_user
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import UserCollection, Shop
from sqlalchemy import select
from typing import List

router = APIRouter(prefix='/api/collection', tags=['collection'])

@router.post('/')
async def add_collection(shop_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        # check existing
        q = select(UserCollection).where(UserCollection.user_id==current_user['id'], UserCollection.shop_id==shop_id)
        res = await session.execute(q)
        if res.scalar_one_or_none():
            return {"ok": True}
        col = UserCollection(user_id=current_user['id'], shop_id=shop_id)
        session.add(col)
        await session.commit()
        return {"ok": True}

@router.delete('/')
async def remove_collection(shop_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserCollection).where(UserCollection.user_id==current_user['id'], UserCollection.shop_id==shop_id)
        res = await session.execute(q)
        col = res.scalar_one_or_none()
        if not col:
            return {"ok": True}
        await session.delete(col)
        await session.commit()
        return {"ok": True}

@router.get('/', response_model=List[dict])
async def list_collections(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserCollection).where(UserCollection.user_id==current_user['id']).order_by(UserCollection.create_time.desc())
        res = await session.execute(q)
        rows = res.scalars().all()
        out = []
        for r in rows:
            q2 = select(Shop).where(Shop.id==r.shop_id)
            r2 = await session.execute(q2)
            shop = r2.scalar_one_or_none()
            out.append({"shop_id": r.shop_id, "shop_name": shop.shop_name if shop else ''})
        return out
