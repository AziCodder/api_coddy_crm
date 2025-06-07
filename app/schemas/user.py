from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

from app.models.user import RoleEnum


# Базовая схема для всех моделей
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True


# Схемы для ролей
class RoleBase(BaseSchema):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    name: Optional[str] = None


class RoleInDB(RoleBase):
    id: int


# Схемы для пользователей
class UserBase(BaseSchema):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    roles: List[RoleEnum] = [RoleEnum.STUDENT]


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    roles: Optional[List[RoleEnum]] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[RoleInDB] = []


# Схемы для токена
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    username: Optional[str] = None
    user_id: Optional[int] = None
    roles: List[str] = []


# Схема для входа
class UserLogin(BaseSchema):
    username: str
    password: str

