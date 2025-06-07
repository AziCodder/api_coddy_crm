from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager, check_teacher
from app.models.user import User
from app.schemas.activities import ScheduleCreate, ScheduleUpdate, ScheduleInDB, ScheduleWithGroup
from app.services import schedule as schedule_service
from app.services import group as group_service

router = APIRouter()


@router.get("/", response_model=List[ScheduleInDB])
def read_schedules(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    group_id: Optional[int] = None,
    day_of_week: Optional[int] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список расписаний с возможностью фильтрации
    """
    if group_id:
        schedules = schedule_service.get_by_group(db, group_id=group_id, skip=skip, limit=limit)
    elif day_of_week is not None:
        schedules = schedule_service.get_by_day(db, day_of_week=day_of_week, skip=skip, limit=limit)
    elif active_only:
        schedules = schedule_service.get_active_schedules(db, skip=skip, limit=limit)
    else:
        schedules = schedule_service.get_multi(db, skip=skip, limit=limit)
    
    return schedules


@router.post("/", response_model=ScheduleInDB, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_in: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Создать новое расписание
    """
    # Проверка, что группа существует
    if not group_service.exists(db, id=schedule_in.group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка корректности времени
    if schedule_in.start_time >= schedule_in.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала должно быть раньше времени окончания",
        )
    
    # Создание расписания
    schedule = schedule_service.create(db, obj_in=schedule_in)
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleWithGroup)
def read_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о расписании по ID
    """
    schedule = schedule_service.get_with_group(db, id=schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено",
        )
    
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleInDB)
def update_schedule(
    schedule_id: int,
    schedule_in: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Обновить информацию о расписании
    """
    # Проверка, что расписание существует
    schedule = schedule_service.get(db, id=schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено",
        )
    
    # Проверка, что группа существует, если указана
    if schedule_in.group_id is not None and not group_service.exists(db, id=schedule_in.group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )
    
    # Проверка корректности времени, если указано
    if schedule_in.start_time is not None and schedule_in.end_time is not None:
        if schedule_in.start_time >= schedule_in.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время начала должно быть раньше времени окончания",
            )
    elif schedule_in.start_time is not None and schedule_in.start_time >= schedule.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала должно быть раньше времени окончания",
        )
    elif schedule_in.end_time is not None and schedule.start_time >= schedule_in.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала должно быть раньше времени окончания",
        )
    
    # Обновление расписания
    schedule = schedule_service.update(db, db_obj=schedule, obj_in=schedule_in)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Удалить расписание
    """
    # Проверка, что расписание существует
    schedule = schedule_service.get(db, id=schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено",
        )
    
    # Удаление расписания
    schedule_service.remove(db, id=schedule_id)
    return None

