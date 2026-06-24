from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import SysUser, SystemConfig
from backend.app.utils.security import get_password_hash

async def get_user_by_username(username: str):
    async with AsyncSessionLocal() as session:
        q = select(SysUser).where(SysUser.username == username)
        res = await session.execute(q)
        return res.scalar_one_or_none()

async def create_user(username: str, password: str, role: str = 'user'):
    user = SysUser(username=username, password_hash=get_password_hash(password), role=role)
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
