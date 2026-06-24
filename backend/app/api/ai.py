from fastapi import APIRouter, Depends, HTTPException
from backend.app.schemas.schemas import AIGenerateRequest, AIGenerateResp
from backend.app.services.ai_service import generate_evaluation
from backend.app.core.config import settings

router = APIRouter(prefix='/api/ai', tags=['ai'])

@router.post('/generate', response_model=AIGenerateResp)
async def ai_generate(payload: AIGenerateRequest, token: str):
    # token required; token validation skipped for brevity
    if not settings.MODEL_API_KEY:
        raise HTTPException(status_code=400, detail='model_api_key not configured')
    content = await generate_evaluation(payload)
    return {"content": content}
