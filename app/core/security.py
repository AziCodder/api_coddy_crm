from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List, Union, Any
from jose import jwt

from app.core.config import settings

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешу
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], roles: List[str] = [], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT-токен доступа
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "roles": roles}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

