from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager
from app.models.user import User
from app.schemas.education import CourseCreate, CourseUpdate, CourseInDB, GroupInDB
from app.services import course as course_service

router = APIRouter()


@router.get("/", response_model=List[CourseInDB])
def read_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список курсов
    """
    if active_only:
        courses = course_service.get_active_courses(db, skip=skip, limit=limit)
    else:
        courses = course_service.get_multi(db, skip=skip, limit=limit)
    
    return courses


@router.post("/", response_model=CourseInDB, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать новый курс
    """
    # Создание курса
    course = course_service.create(db, obj_in=course_in)
    return course


@router.get("/{course_id}", response_model=CourseInDB)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о курсе по ID
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    return course


@router.put("/{course_id}", response_model=CourseInDB)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Обновить информацию о курсе
    """
    # Проверка, что курс существует
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Обновление курса
    course = course_service.update(db, db_obj=course, obj_in=course_in)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Удалить курс (только для администраторов)
    """
    # Проверка, что курс существует
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Удаление курса
    course_service.remove(db, id=course_id)
    return None


@router.get("/{course_id}/groups", response_model=List[GroupInDB])
def read_course_groups(
    course_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список групп по курсу
    """
    # Проверка, что курс существует
    if not course_service.exists(db, id=course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Получаем группы по курсу
    groups = course_service.group.get_by_course(db, course_id=course_id, skip=skip, limit=limit)
    
    return groups

