import asyncio
from backend.app.db.session import engine, Base
from backend.app.models.models import *
from backend.app.crud.user import get_user_by_username, create_user
from backend.app.crud.config import ensure_default_configs
from backend.app.utils.security import get_password_hash

async def init_models_and_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # ensure default configs and admin user
    await ensure_default_configs()

    # create admin if not exists
    admin = await get_user_by_username('admin')
    if not admin:
        await create_user('admin', '123456', role='admin')

if __name__ == '__main__':
    asyncio.run(init_models_and_data())
