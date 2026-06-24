from fastapi import APIRouter, Depends
from backend.app.deps import get_current_user

router = APIRouter(prefix='/api/auth', tags=['auth'])

@router.get('/me')
async def me(current_user: dict = Depends(get_current_user)):
    return {"id": current_user['id'], "username": current_user['username'], "role": current_user['role']}
