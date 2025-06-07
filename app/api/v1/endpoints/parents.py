from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager
from app.models.user import User, RoleEnum
from app.schemas.people import (
    ParentCreate, ParentUpdate, ParentInDB, ParentWithUser,
    StudentParentLink, ParentWithStudents
)
from app.services import parent as parent_service
from app.services import student as student_service

router = APIRouter()


@router.get("/", response_model=List[ParentInDB])
def read_parents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_manager)
):
    """
    Получить список родителей
    """
    parents = parent_service.get_multi(db, skip=skip, limit=limit)
    return parents


@router.post("/", response_model=ParentInDB, status_code=status.HTTP_201_CREATED)
def create_parent(
    parent_in: ParentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать нового родителя
    """
    # Проверка, что пользователь существует
    if not parent_service.user.exists(db, id=parent_in.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Проверка, что профиль родителя для этого пользователя еще не существует
    existing_parent = parent_service.get_by_user_id(db, user_id=parent_in.user_id)
    if existing_parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль родителя для этого пользователя уже существует",
        )
    
    # Создание родителя
    parent = parent_service.create(db, obj_in=parent_in)
    return parent


@router.get("/{parent_id}", response_model=ParentWithUser)
def read_parent(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о родителе по ID
    """
    # Получаем родителя с данными пользователя
    parent = parent_service.get_with_user(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Проверка прав доступа: пользователь может видеть только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != parent.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра информации о родителе",
        )
    
    return parent


@router.put("/{parent_id}", response_model=ParentInDB)
def update_parent(
    parent_id: int,
    parent_in: ParentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить информацию о родителе
    """
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Проверка прав доступа: пользователь может обновлять только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != parent.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления информации о родителе",
        )
    
    # Обновление родителя
    parent = parent_service.update(db, db_obj=parent, obj_in=parent_in)
    return parent


@router.delete("/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parent(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить родителя (только для администраторов)
    """
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Удаление родителя
    parent_service.remove(db, id=parent_id)
    return None


@router.get("/{parent_id}/students", response_model=ParentWithStudents)
def read_parent_students(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список студентов родителя
    """
    # Проверка, что родитель существует
    parent = parent_service.get_with_students(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Проверка прав доступа: пользователь может видеть только свою информацию,
    # если он не администратор или менеджер
    is_admin_or_manager = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    if not is_admin_or_manager and current_user.id != parent.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра информации о студентах родителя",
        )
    
    return parent


@router.post("/{parent_id}/students", response_model=ParentWithStudents, status_code=status.HTTP_201_CREATED)
def add_student_to_parent(
    parent_id: int,
    link: StudentParentLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Добавить студента родителю
    """
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Проверка, что студент существует
    student = student_service.get(db, id=link.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Добавление студента родителю
    success = parent_service.add_student(db, parent_id=parent_id, student_id=link.student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить студента родителю",
        )
    
    # Получаем обновленные данные
    parent = parent_service.get_with_students(db, id=parent_id)
    return parent


@router.delete("/{parent_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student_from_parent(
    parent_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Удалить студента у родителя
    """
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Удаление студента у родителя
    success = parent_service.remove_student(db, parent_id=parent_id, student_id=student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить студента у родителя",
        )
    
    return None

