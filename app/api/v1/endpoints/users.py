from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.services import user as user_service

router = APIRouter()


@router.get("/", response_model=List[UserInDB])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    role: Optional[RoleEnum] = None,
    current_user: User = Depends(check_manager)
):
    """
    Получить список пользователей с возможностью фильтрации по роли
    """
    if role:
        users = user_service.get_users_by_role(db, role=role, skip=skip, limit=limit)
    else:
        users = user_service.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Создать нового пользователя (только для администраторов)
    """
    # Проверка, что пользователь с таким email или username не существует
    user_by_email = user_service.get_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    
    user_by_username = user_service.get_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует",
        )
    
    # Создание пользователя
    user = user_service.create_with_roles(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserInDB)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о пользователе по ID
    """
    # Проверка прав доступа: пользователь может видеть только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра информации о другом пользователе",
        )
    
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return user


@router.put("/{user_id}", response_model=UserInDB)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить информацию о пользователе
    """
    # Проверка прав доступа: пользователь может обновлять только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления информации о другом пользователе",
        )
    
    # Проверка, что пользователь существует
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Проверка, что обычный пользователь не меняет роли
    if not is_admin_or_manager and user_in.roles is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения ролей",
        )
    
    # Обновление пользователя
    user = user_service.update_with_password(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить пользователя (только для администраторов)
    """
    # Проверка, что пользователь существует
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Проверка, что администратор не удаляет сам себя
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя",
        )
    
    # Удаление пользователя
    user_service.remove(db, id=user_id)
    return None

