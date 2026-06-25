from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.models import ShopProduct, Shop
from backend.app.deps import get_current_user
from typing import List

router = APIRouter(prefix='/api/products', tags=['products'])

@router.post('/', response_model=dict)
async def create_product(shop_id: int, product_name: str, price: float, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(Shop).where(Shop.id==shop_id)
        res = await session.execute(q)
        shop = res.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail='shop not found')
        if current_user['role']!='admin' and shop.owner_id!=current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        prod = ShopProduct(shop_id=shop_id, product_name=product_name, price=price)
        session.add(prod)
        await session.commit()
        await session.refresh(prod)
        # clear shop detail cache
        import aioredis
        from backend.app.core.config import settings
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete(f"shop:detail:{shop_id}")
        return {"id": prod.id, "product_name": prod.product_name, "price": float(prod.price)}

@router.get('/{shop_id}', response_model=List[dict])
async def list_products(shop_id: int):
    async with AsyncSessionLocal() as session:
        q = select(ShopProduct).where(ShopProduct.shop_id==shop_id, ShopProduct.is_active==1).order_by(ShopProduct.sort.desc())
        res = await session.execute(q)
        prods = res.scalars().all()
        return [{"id": p.id, "product_name": p.product_name, "price": float(p.price), "product_image": p.product_image or '', "description": p.description or ''} for p in prods]

@router.put('/{product_id}', response_model=dict)
async def update_product(product_id: int, product_name: str = None, price: float = None, description: str = None, sort: int = None, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(ShopProduct).where(ShopProduct.id==product_id)
        res = await session.execute(q)
        p = res.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=404, detail='product not found')
        # check ownership
        q2 = select(Shop).where(Shop.id==p.shop_id)
        r2 = await session.execute(q2)
        shop = r2.scalar_one_or_none()
        if current_user.get('role')!='admin' and shop and shop.owner_id!=current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        if product_name is not None:
            p.product_name = product_name
        if price is not None:
            p.price = price
        if description is not None:
            p.description = description
        if sort is not None:
            p.sort = sort
        session.add(p)
        await session.commit()
        await session.refresh(p)
        # clear cache
        import aioredis
        from backend.app.core.config import settings
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete(f"shop:detail:{p.shop_id}")
        return {"id": p.id, "product_name": p.product_name, "price": float(p.price)}

@router.delete('/{product_id}')
async def delete_product(product_id: int, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        q = select(ShopProduct).where(ShopProduct.id==product_id)
        res = await session.execute(q)
        p = res.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=404, detail='product not found')
        q2 = select(Shop).where(Shop.id==p.shop_id)
        r2 = await session.execute(q2)
        shop = r2.scalar_one_or_none()
        if current_user.get('role')!='admin' and shop and shop.owner_id!=current_user['id']:
            raise HTTPException(status_code=403, detail='not owner')
        # soft delete: mark is_active=0
        p.is_active = 0
        session.add(p)
        await session.commit()
        import aioredis
        from backend.app.core.config import settings
        r = aioredis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
        await r.delete(f"shop:detail:{p.shop_id}")
        return {"ok": True}