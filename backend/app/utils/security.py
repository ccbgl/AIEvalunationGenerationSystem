import hashlib
import uuid
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def make_token() -> str:
    u = uuid.uuid4().hex
    h = hashlib.sha256(u.encode()).hexdigest()
    return h
