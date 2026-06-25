import httpx
from backend.app.core.config import settings
from backend.app.schemas.schemas import AIGenerateRequest

async def generate_evaluation(req: AIGenerateRequest) -> str:
    # assemble a lightweight prompt including optional shop info when available
    tags = ', '.join(getattr(req, 'tags', []) or [])
    shop_name = getattr(req, 'shop_name', '') or ''
    shop_desc = getattr(req, 'shop_description', '') or ''
    prompt = ''
    if req.target_platform.lower() == 'google':
        if shop_name:
            prompt = (f"You are a helpful local reviewer. Write an objective short English review for '{shop_name}' "
                      f"(shop id {req.shop_id}). Level: {req.level}. Tags: {tags}. Briefly mention: {shop_desc}. "
                      "Keep it natural and suitable for Google reviews.")
        else:
            prompt = (f"You are a helpful local reviewer. Write an objective short English review for the shop id {req.shop_id}. "
                      f"Level: {req.level}. Tags: {tags}. Keep it natural and suitable for Google reviews.")
    else:
        if shop_name:
            prompt = (f"你是一个热情的笔记作者。为店铺『{shop_name}』（id {req.shop_id}）写一段小红书风格的中文种草笔记，等级 {req.level}，标签：{tags}。"
                      f"可包含店铺信息：{shop_desc}。包含 Emoji，段落分行。")
        else:
            prompt = (f"你是一个热情的笔记作者。为店铺 {req.shop_id} 写一段小红书风格的中文种草笔记，等级 {req.level}，标签：{tags}。包含 Emoji，段落分行。")

    # placeholder: call a hypothetical third-party API via HTTP
    headers = {"Authorization": f"Bearer {settings.MODEL_API_KEY}"}
    payload = {"model": settings.MODEL_NAME or "gpt-like", "prompt": prompt, "max_tokens": 300}
    async with httpx.AsyncClient(timeout=settings.MODEL_TIMEOUT) as client:
        # In many real cases you'd call OpenAI/other SDKs. Here we simulate.
        try:
            resp = await client.post('https://api.example-model.com/v1/generate', json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('text', 'AI returned empty')
        except Exception:
            pass
    # fallback demo content
    if req.target_platform.lower() == 'google':
        return "Great place with friendly service. The drinks were delicious and value for money."
    return "超好喝的奶茶！环境干净，推荐大家来试试～ 😋\n口感很棒，服务也很热情。"
