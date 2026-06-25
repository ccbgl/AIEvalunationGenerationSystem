from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import UserEvaluation, Shop, EvaluationLevel
from sqlalchemy import select, func
import aioredis
from backend.app.core.config import settings

async def recompute_good_rate(shop_id: int):
    async with AsyncSessionLocal() as session:
        q_total = select(func.count()).select_from(UserEvaluation).where(UserEvaluation.shop_id == shop_id)
        q_reco = select(func.count()).select_from(UserEvaluation).where(UserEvaluation.shop_id == shop_id).where(UserEvaluation.level == EvaluationLevel.recommend)
        total = (await session.execute(q_total)).scalar() or 0
        reco = (await session.execute(q_reco)).scalar() or 0
        rate = 0.0
        if total > 0:
            rate = round((reco / total) * 100, 2)
        # update shop
        q = select(Shop).where(Shop.id == shop_id)
        res = await session.execute(q)
        shop = res.scalar_one_or_none()
        if shop:
            shop.good_rate = rate
            session.add(shop)
            await session.commit()
    # clear related caches in redis (best-effort)
    try:
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete('shop:list:active')
        await r.delete(f"shop:detail:{shop_id}")
    except Exception:
        pass

