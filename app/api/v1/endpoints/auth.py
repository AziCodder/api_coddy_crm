from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.api.v1.dependencies.auth import authenticate_user, get_current_active_user
from app.models.user import User, Role, RoleEnum
from app.schemas.user import UserCreate, UserInDB, Token

router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    """
    # Проверка, что пользователь с таким email или username не существует
    user_by_email = db.query(User).filter(User.email == user_in.email).first()
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    
    user_by_username = db.query(User).filter(User.username == user_in.username).first()
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует",
        )
    
    # Создание пользователя
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user_in.is_active,
    )
    
    # Добавление ролей
    for role_enum in user_in.roles:
        role = db.query(Role).filter(Role.name == role_enum.value).first()
        if not role:
            # Если роль не существует, создаем ее
            role = Role(name=role_enum.value, description=f"Роль {role_enum.value}")
            db.add(role)
            db.flush()
        user.roles.append(role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Получение токена доступа OAuth2
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание токена доступа
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    roles = [role.name for role in user.roles]
    access_token = create_access_token(
        subject=user.username, roles=roles, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserInDB)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Получение информации о текущем пользователе
    """
    return current_user

