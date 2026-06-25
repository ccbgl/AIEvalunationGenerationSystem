from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import SysUser, Shop, UserEvaluation, SystemConfig
from backend.app.deps import get_current_user
from fastapi import Depends
from typing import List

router = APIRouter(prefix='/api/admin', tags=['admin'])

@router.get('/users')
async def list_users(q: str = None, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        query = select(SysUser)
        if q:
            query = query.where(SysUser.username.contains(q))
        res = await session.execute(query)
        users = res.scalars().all()
        return [{"id": u.id, "username": u.username, "role": u.role.name, "is_active": u.is_active} for u in users]

@router.get('/shops')
async def list_shops_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
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

@router.get('/evaluations')
async def list_evaluations(shop_id: int = None, level: str = None, target_platform: str = None, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        q = select(UserEvaluation)
        if shop_id:
            q = q.where(UserEvaluation.shop_id == shop_id)
        if level:
            q = q.where(UserEvaluation.level == level)
        if target_platform:
            q = q.where(UserEvaluation.target_platform == target_platform)
        q = q.order_by(UserEvaluation.create_time.desc())
        res = await session.execute(q)
        rows = res.scalars().all()
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'user_id': r.user_id,
                'shop_id': r.shop_id,
                'level': r.level.name if hasattr(r.level, 'name') else str(r.level),
                'tags': r.tags,
                'target_platform': r.target_platform,
                'content': r.content,
                'create_time': r.create_time.isoformat()
            })
        return out

@router.delete('/evaluations/{evaluation_id}')
async def delete_evaluation(evaluation_id: int, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        q = select(UserEvaluation).where(UserEvaluation.id==evaluation_id)
        res = await session.execute(q)
        ev = res.scalar_one_or_none()
        if not ev:
            raise HTTPException(status_code=404, detail='evaluation not found')
        shop_id = ev.shop_id
        await session.delete(ev)
        await session.commit()
    # recompute good rate and clear caches
    from backend.app.services.stats import recompute_good_rate
    import aioredis
    from backend.app.core.config import settings
    await recompute_good_rate(shop_id)
    r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    await r.delete('shop:list:active')
    await r.delete(f"shop:detail:{shop_id}")
    return {"ok": True}

@router.post('/users/{user_id}/toggle')
async def toggle_user_active(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        q = select(SysUser).where(SysUser.id==user_id)
        res = await session.execute(q)
        u = res.scalar_one_or_none()
        if not u:
            raise HTTPException(status_code=404, detail='user not found')
        u.is_active = 0 if u.is_active==1 else 1
        session.add(u)
        await session.commit()
        return {"ok": True, "is_active": u.is_active}

@router.post('/users/{user_id}/reset_password')
async def reset_user_password(user_id: int, new_password: str = None, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='admin only')
    async with AsyncSessionLocal() as session:
        q = select(SysUser).where(SysUser.id==user_id)
        res = await session.execute(q)
        u = res.scalar_one_or_none()
        if not u:
            raise HTTPException(status_code=404, detail='user not found')
        from backend.app.utils.security import get_password_hash
        pwd = new_password or '123456'
        u.password_hash = get_password_hash(pwd)
        session.add(u)
        await session.commit()
        return {"ok": True}
