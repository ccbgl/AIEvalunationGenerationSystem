from fastapi import APIRouter, Depends, HTTPException
from backend.app.schemas.schemas import AIGenerateRequest, AIGenerateResp
from backend.app.services.ai_service import generate_evaluation
from backend.app.core.config import settings
from backend.app.deps import get_current_user
from fastapi import Depends

router = APIRouter(prefix='/api/ai', tags=['ai'])

@router.post('/generate', response_model=AIGenerateResp)
async def ai_generate(payload: AIGenerateRequest, current_user: dict = Depends(get_current_user)):
    # require authenticated user
    if not settings.MODEL_API_KEY:
        raise HTTPException(status_code=400, detail='model_api_key not configured')
    content = await generate_evaluation(payload)
    return {"content": content}
