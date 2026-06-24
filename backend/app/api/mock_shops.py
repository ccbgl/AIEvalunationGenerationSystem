# Minimal endpoints for demo

from fastapi import APIRouter

router = APIRouter()

@router.get('/api/shops')
async def list_shops():
    # demo static response; real implementation should query DB
    return [
        {"id": 1, "shop_name": "Sunny Tea House", "good_rate": 95.0, "cover_image": "/static/img/cover.jpg"}
    ]
