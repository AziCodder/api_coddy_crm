from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager, check_teacher
from app.models.user import User, RoleEnum
from app.schemas.education import (
    GroupCreate, GroupUpdate, GroupInDB, GroupWithDetails,
    StudentGroupLink, StudentGroupLinkUpdate, GroupWithStudents
)
from app.schemas.people import StudentInDB
from app.services import group as group_service
from app.services import student as student_service
from app.services import teacher as teacher_service

router = APIRouter()


@router.get("/", response_model=List[GroupInDB])
def read_groups(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список групп с возможностью фильтрации
    """
    if course_id:
        groups = group_service.get_by_course(db, course_id=course_id, skip=skip, limit=limit)
    elif teacher_id:
        groups = group_service.get_by_teacher(db, teacher_id=teacher_id, skip=skip, limit=limit)
    elif active_only:
        groups = group_service.get_active_groups(db, skip=skip, limit=limit)
    else:
        groups = group_service.get_multi(db, skip=skip, limit=limit)
    
    return groups


@router.post("/", response_model=GroupInDB, status_code=status.HTTP_201_CREATED)
def create_group(
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать новую группу
    """
    # Проверка, что курс существует
    if not group_service.course.exists(db, id=group_in.course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Проверка, что преподаватель существует, если указан
    if group_in.teacher_id and not teacher_service.exists(db, id=group_in.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден",
        )
    
    # Создание группы
    group = group_service.create(db, obj_in=group_in)
    return group


@router.get("/{group_id}", response_model=GroupWithDetails)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о группе по ID
    """
    # Получаем группу с детальной информацией
    group_details = group_service.get_with_details(db, id=group_id)
    if not group_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    return group_details


@router.put("/{group_id}", response_model=GroupInDB)
def update_group(
    group_id: int,
    group_in: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Обновить информацию о группе
    """
    # Проверка, что группа существует
    group = group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка, что курс существует, если указан
    if group_in.course_id is not None and not group_service.course.exists(db, id=group_in.course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Проверка, что преподаватель существует, если указан
    if group_in.teacher_id is not None and group_in.teacher_id != 0 and not teacher_service.exists(db, id=group_in.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден",
        )
    
    # Обновление группы
    group = group_service.update(db, db_obj=group, obj_in=group_in)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить группу (только для администраторов)
    """
    # Проверка, что группа существует
    group = group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Удаление группы
    group_service.remove(db, id=group_id)
    return None


@router.get("/{group_id}/students", response_model=List[StudentInDB])
def read_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список студентов в группе
    """
    # Проверка, что группа существует
    if not group_service.exists(db, id=group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Получаем студентов в группе
    students = group_service.get_students_in_group(
        db, group_id=group_id, active_only=active_only, skip=skip, limit=limit
    )
    
    return students


@router.post("/{group_id}/students", response_model=GroupWithStudents, status_code=status.HTTP_201_CREATED)
def add_student_to_group(
    group_id: int,
    link: StudentGroupLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Добавить студента в группу
    """
    # Проверка, что группа существует
    group = group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка, что студент существует
    student = student_service.get(db, id=link.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Добавление студента в группу
    student_group = group_service.add_student(
        db, group_id=group_id, student_id=link.student_id, is_active=link.is_active
    )
    if not student_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить студента в группу",
        )
    
    # Получаем обновленные данные
    group = group_service.get_with_students(db, id=group_id)
    return group


@router.put("/{group_id}/students/{student_id}", response_model=GroupWithStudents)
def update_student_in_group(
    group_id: int,
    student_id: int,
    link_update: StudentGroupLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Обновить статус студента в группе
    """
    # Проверка, что группа существует
    group = group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Обновление статуса студента в группе
    student_group = group_service.update_student_status(
        db, group_id=group_id, student_id=student_id, is_active=link_update.is_active
    )
    if not student_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось обновить статус студента в группе",
        )
    
    # Получаем обновленные данные
    group = group_service.get_with_students(db, id=group_id)
    return group


@router.delete("/{group_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student_from_group(
    group_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Удалить студента из группы
    """
    # Проверка, что группа существует
    group = group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка, что студент существует
    student = student_service.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Удаление студента из группы
    success = group_service.remove_student(db, group_id=group_id, student_id=student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить студента из группы",
        )
    
    return None

