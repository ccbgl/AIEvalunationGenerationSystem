from sqlalchemy import select, insert
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import SystemConfig

DEFAULT_CONFIGS = [
    ("model_api_key", ""),
    ("model_name", ""),
    ("model_timeout", "15"),
    ("token_expire_hours", "24"),
    ("shop_cache_expire_minutes", "60"),
    ("daily_ai_limit_per_user", "20"),
]

async def ensure_default_configs():
    async with AsyncSessionLocal() as session:
        for key, val in DEFAULT_CONFIGS:
            q = select(SystemConfig).where(SystemConfig.config_key == key)
            res = await session.execute(q)
            obj = res.scalar_one_or_none()
            if not obj:
                cfg = SystemConfig(config_key=key, config_value=str(val), remark='auto init')
                session.add(cfg)
        await session.commit()
