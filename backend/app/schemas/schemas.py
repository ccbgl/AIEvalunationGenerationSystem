from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class RoleEnum(str, Enum):
    user = 'user'
    shop = 'shop'
    admin = 'admin'

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: RoleEnum

class TokenResp(BaseModel):
    token: str
    expire_hours: int

class ShopBase(BaseModel):
    shop_name: str
    address: str
    avg_cost: float
    description: Optional[str] = ''

class ShopOut(ShopBase):
    id: int
    cover_image: str
    good_rate: float

class AIGenerateRequest(BaseModel):
    shop_id: int
    level: str
    tags: List[str]
    target_platform: str

class AIGenerateResp(BaseModel):
    content: str

