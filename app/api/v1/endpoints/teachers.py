from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager
from app.models.user import User, RoleEnum
from app.schemas.people import TeacherCreate, TeacherUpdate, TeacherInDB, TeacherWithUser
from app.services import teacher as teacher_service

router = APIRouter()


@router.get("/", response_model=List[TeacherInDB])
def read_teachers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список преподавателей
    """
    teachers = teacher_service.get_multi(db, skip=skip, limit=limit)
    return teachers


@router.post("/", response_model=TeacherInDB, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_in: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать нового преподавателя
    """
    # Проверка, что пользователь существует
    if not teacher_service.user.exists(db, id=teacher_in.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Проверка, что профиль преподавателя для этого пользователя еще не существует
    existing_teacher = teacher_service.get_by_user_id(db, user_id=teacher_in.user_id)
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль преподавателя для этого пользователя уже существует",
        )
    
    # Создание преподавателя
    teacher = teacher_service.create(db, obj_in=teacher_in)
    return teacher


@router.get("/{teacher_id}", response_model=TeacherWithUser)
def read_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о преподавателе по ID
    """
    # Получаем преподавателя с данными пользователя
    teacher = teacher_service.get_with_user(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден",
        )
    
    # Проверка прав доступа: пользователь может видеть только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра информации о преподавателе",
        )
    
    return teacher


@router.put("/{teacher_id}", response_model=TeacherInDB)
def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить информацию о преподавателе
    """
    # Проверка, что преподаватель существует
    teacher = teacher_service.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден",
        )
    
    # Проверка прав доступа: пользователь может обновлять только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления информации о преподавателе",
        )
    
    # Обновление преподавателя
    teacher = teacher_service.update(db, db_obj=teacher, obj_in=teacher_in)
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить преподавателя (только для администраторов)
    """
    # Проверка, что преподаватель существует
    teacher = teacher_service.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден",
        )
    
    # Удаление преподавателя
    teacher_service.remove(db, id=teacher_id)
    return None

