from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.app.deps import get_current_user
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import UserBrowseHistory, Shop
from sqlalchemy import select

router = APIRouter(prefix='/api/history', tags=['history'])

@router.get('/', response_model=List[dict])
async def list_history(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserBrowseHistory).where(UserBrowseHistory.user_id==current_user['id']).order_by(UserBrowseHistory.browse_time.desc())
        res = await session.execute(q)
        rows = res.scalars().all()
        out = []
        for r in rows:
            # fetch shop basic info
            q2 = select(Shop).where(Shop.id==r.shop_id)
            r2 = await session.execute(q2)
            shop = r2.scalar_one_or_none()
            out.append({"id": r.id, "shop_id": r.shop_id, "shop_name": shop.shop_name if shop else '', "browse_time": r.browse_time.isoformat()})
        return out

@router.delete('/{history_id}')
async def delete_history(history_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserBrowseHistory).where(UserBrowseHistory.id==history_id, UserBrowseHistory.user_id==current_user['id'])
        res = await session.execute(q)
        h = res.scalar_one_or_none()
        if not h:
            raise HTTPException(status_code=404, detail='not found')
        await session.delete(h)
        await session.commit()
        return {"ok": True}

@router.delete('/')
async def clear_history(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(UserBrowseHistory).where(UserBrowseHistory.user_id==current_user['id'])
        res = await session.execute(q)
        rows = res.scalars().all()
        for r in rows:
            await session.delete(r)
        await session.commit()
    return {"ok": True}
