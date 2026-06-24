from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import SysUser, Shop, UserEvaluation, SystemConfig
from backend.app.deps import get_current_user
from typing import List

router = APIRouter(prefix='/api/admin', tags=['admin'])

@router.get('/users')
async def list_users(q: str = None):
    async with AsyncSessionLocal() as session:
        query = select(SysUser)
        if q:
            query = query.where(SysUser.username.contains(q))
        res = await session.execute(query)
        users = res.scalars().all()
        return [{"id": u.id, "username": u.username, "role": u.role.name, "is_active": u.is_active} for u in users]

@router.get('/shops')
async def list_shops_admin():
    async with AsyncSessionLocal() as session:
        q = select(Shop)
        res = await session.execute(q)
        shops = res.scalars().all()
        return [{"id": s.id, "shop_name": s.shop_name, "is_active": s.is_active, "is_recommended": s.is_recommended} for s in shops]

@router.post('/config')
async def set_config(key: str, value: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        q = select(SystemConfig).where(SystemConfig.config_key==key)
        res = await session.execute(q)
        cfg = res.scalar_one_or_none()
        if not cfg:
            cfg = SystemConfig(config_key=key, config_value=value)
            session.add(cfg)
        else:
            cfg.config_value = value
            session.add(cfg)
        await session.commit()
        return {"ok": True}
