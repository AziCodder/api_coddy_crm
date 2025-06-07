from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager, check_teacher
from app.models.user import User, RoleEnum
from app.schemas.people import (
    StudentCreate, StudentUpdate, StudentInDB, StudentWithUser,
    StudentParentLink, StudentWithParents
)
from app.services import student as student_service
from app.services import parent as parent_service

router = APIRouter()


@router.get("/", response_model=List[StudentInDB])
def read_students(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_teacher)
):
    """
    Получить список студентов
    """
    students = student_service.get_multi(db, skip=skip, limit=limit)
    return students


@router.post("/", response_model=StudentInDB, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать нового студента
    """
    # Проверка, что пользователь существует
    if not student_service.user.exists(db, id=student_in.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Проверка, что профиль студента для этого пользователя еще не существует
    existing_student = student_service.get_by_user_id(db, user_id=student_in.user_id)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль студента для этого пользователя уже существует",
        )
    
    # Создание студента
    student = student_service.create(db, obj_in=student_in)
    return student


@router.get("/{student_id}", response_model=StudentWithUser)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о студенте по ID
    """
    # Проверка прав доступа
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.TEACHER.value] for role in current_user.roles)
    is_parent = any(role.name == RoleEnum.PARENT.value for role in current_user.roles)
    
    # Получаем студента с данными пользователя
    student = student_service.get_with_user(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка прав доступа: пользователь может видеть только свою информацию,
    # если он не администратор, менеджер, преподаватель или родитель этого студента
    if not is_staff:
        if current_user.id == student.user_id:
            # Студент смотрит свой профиль
            return student
        elif is_parent:
            # Проверяем, является ли текущий пользователь родителем этого студента
            parent_profile = parent_service.get_by_user_id(db, user_id=current_user.id)
            if not parent_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для просмотра информации о студенте",
                )
            
            # Проверяем, есть ли студент в списке детей родителя
            parent_with_students = parent_service.get_with_students(db, id=parent_profile.id)
            if not any(s.id == student_id for s in parent_with_students.students):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для просмотра информации о студенте",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра информации о студенте",
            )
    
    return student


@router.put("/{student_id}", response_model=StudentInDB)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить информацию о студенте
    """
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка прав доступа
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value] for role in current_user.roles)
    
    if not is_staff and current_user.id != student.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления информации о студенте",
        )
    
    # Обновление студента
    student = student_service.update(db, db_obj=student, obj_in=student_in)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить студента (только для администраторов)
    """
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Удаление студента
    student_service.remove(db, id=student_id)
    return None


@router.get("/{student_id}/parents", response_model=StudentWithParents)
def read_student_parents(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список родителей студента
    """
    # Проверка, что студент существует
    student = student_service.get_with_parents(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка прав доступа
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.TEACHER.value] for role in current_user.roles)
    
    if not is_staff and current_user.id != student.user_id:
        # Проверяем, является ли текущий пользователь родителем этого студента
        is_parent = any(role.name == RoleEnum.PARENT.value for role in current_user.roles)
        if is_parent:
            parent_profile = parent_service.get_by_user_id(db, user_id=current_user.id)
            if not parent_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для просмотра информации о родителях студента",
                )
            
            # Проверяем, есть ли студент в списке детей родителя
            parent_with_students = parent_service.get_with_students(db, id=parent_profile.id)
            if not any(s.id == student_id for s in parent_with_students.students):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для просмотра информации о родителях студента",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра информации о родителях студента",
            )
    
    return student


@router.post("/{student_id}/parents", response_model=StudentWithParents, status_code=status.HTTP_201_CREATED)
def add_parent_to_student(
    student_id: int,
    link: StudentParentLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Добавить родителя студенту
    """
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=link.parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Добавление родителя студенту
    success = student_service.add_parent(db, student_id=student_id, parent_id=link.parent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить родителя студенту",
        )
    
    # Получаем обновленные данные
    student = student_service.get_with_parents(db, id=student_id)
    return student


@router.delete("/{student_id}/parents/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_parent_from_student(
    student_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Удалить родителя у студента
    """
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка, что родитель существует
    parent = parent_service.get(db, id=parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родитель не найден",
        )
    
    # Удаление родителя у студента
    success = student_service.remove_parent(db, student_id=student_id, parent_id=parent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить родителя у студента",
        )
    
    return None

