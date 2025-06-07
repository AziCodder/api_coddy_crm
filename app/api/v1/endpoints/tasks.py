from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.dependencies.auth import get_current_active_user, check_admin, check_manager, check_teacher
from app.models.user import User, RoleEnum
from app.models.activities import TaskStatusEnum
from app.schemas.activities import (
    TaskCreate, TaskUpdate, TaskInDB, TaskWithCourse,
    StudentTaskCreate, StudentTaskUpdate, StudentTaskInDB, StudentTaskWithDetails
)
from app.services import task as task_service
from app.services import student_task as student_task_service
from app.services import course as course_service
from app.services import student as student_service

router = APIRouter()


@router.get("/", response_model=List[TaskInDB])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    upcoming_days: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить список задач с возможностью фильтрации
    """
    if course_id:
        tasks = task_service.get_by_course(db, course_id=course_id, skip=skip, limit=limit)
    elif upcoming_days:
        tasks = task_service.get_upcoming_tasks(db, days=upcoming_days, skip=skip, limit=limit)
    else:
        tasks = task_service.get_multi(db, skip=skip, limit=limit)
    
    return tasks


@router.post("/", response_model=TaskInDB, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Создать новую задачу
    """
    # Проверка, что курс существует
    if not course_service.exists(db, id=task_in.course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Создание задачи
    task = task_service.create(db, obj_in=task_in)
    return task


@router.get("/{task_id}", response_model=TaskWithCourse)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о задаче по ID
    """
    task = task_service.get_with_course(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    return task


@router.put("/{task_id}", response_model=TaskInDB)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Обновить информацию о задаче
    """
    # Проверка, что задача существует
    task = task_service.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Проверка, что курс существует, если указан
    if task_in.course_id is not None and not course_service.exists(db, id=task_in.course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )
    
    # Обновление задачи
    task = task_service.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager)
):
    """
    Удалить задачу
    """
    # Проверка, что задача существует
    task = task_service.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Удаление задачи
    task_service.remove(db, id=task_id)
    return None


@router.get("/{task_id}/student-tasks", response_model=List[StudentTaskInDB])
def read_task_student_tasks(
    task_id: int,
    db: Session = Depends(get_db),
    status: Optional[TaskStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_teacher)
):
    """
    Получить список задач студентов по задаче
    """
    # Проверка, что задача существует
    if not task_service.exists(db, id=task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Получаем задачи студентов по задаче
    student_tasks = student_task_service.get_by_task(
        db, task_id=task_id, status=status, skip=skip, limit=limit
    )
    
    return student_tasks


@router.post("/student-tasks", response_model=StudentTaskInDB, status_code=status.HTTP_201_CREATED)
def create_student_task(
    student_task_in: StudentTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Создать новую задачу для студента
    """
    # Проверка, что студент существует
    if not student_service.exists(db, id=student_task_in.student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден",
        )
    
    # Проверка, что задача существует
    if not task_service.exists(db, id=student_task_in.task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Создание задачи для студента
    student_task = student_task_service.create(db, obj_in=student_task_in)
    return student_task


@router.get("/student-tasks/{student_task_id}", response_model=StudentTaskWithDetails)
def read_student_task(
    student_task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о задаче студента по ID
    """
    student_task = student_task_service.get_with_all(db, id=student_task_id)
    if not student_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача студента не найдена",
        )
    
    # Проверка прав доступа: студент может видеть только свои задачи,
    # если он не администратор, менеджер или преподаватель
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.TEACHER.value] for role in current_user.roles)
    is_student = any(role.name == RoleEnum.STUDENT.value for role in current_user.roles)
    
    if not is_staff:
        if is_student:
            # Получаем профиль студента
            student_profile = student_service.get_by_user_id(db, user_id=current_user.id)
            if not student_profile or student_profile.id != student_task.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для просмотра информации о задаче студента",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра информации о задаче студента",
            )
    
    return student_task


@router.put("/student-tasks/{student_task_id}", response_model=StudentTaskInDB)
def update_student_task(
    student_task_id: int,
    student_task_in: StudentTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить информацию о задаче студента
    """
    # Проверка, что задача студента существует
    student_task = student_task_service.get(db, id=student_task_id)
    if not student_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача студента не найдена",
        )
    
    # Проверка прав доступа: студент может обновлять только свои задачи,
    # если он не администратор, менеджер или преподаватель
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.TEACHER.value] for role in current_user.roles)
    is_student = any(role.name == RoleEnum.STUDENT.value for role in current_user.roles)
    
    if not is_staff:
        if is_student:
            # Получаем профиль студента
            student_profile = student_service.get_by_user_id(db, user_id=current_user.id)
            if not student_profile or student_profile.id != student_task.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для обновления информации о задаче студента",
                )
            
            # Студент может обновлять только решение и статус
            if student_task_in.grade is not None or student_task_in.feedback is not None or student_task_in.graded_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Студент может обновлять только решение и статус задачи",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для обновления информации о задаче студента",
            )
    
    # Обновление задачи студента
    student_task = student_task_service.update(db, db_obj=student_task, obj_in=student_task_in)
    return student_task


@router.post("/student-tasks/{student_task_id}/submit", response_model=StudentTaskInDB)
def submit_student_task(
    student_task_id: int,
    solution: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Отправить решение задачи
    """
    # Проверка, что задача студента существует
    student_task = student_task_service.get(db, id=student_task_id)
    if not student_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача студента не найдена",
        )
    
    # Проверка прав доступа: студент может отправлять решение только для своих задач
    is_staff = any(role.name in [RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.TEACHER.value] for role in current_user.roles)
    is_student = any(role.name == RoleEnum.STUDENT.value for role in current_user.roles)
    
    if not is_staff:
        if is_student:
            # Получаем профиль студента
            student_profile = student_service.get_by_user_id(db, user_id=current_user.id)
            if not student_profile or student_profile.id != student_task.student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для отправки решения задачи",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для отправки решения задачи",
            )
    
    # Отправка решения задачи
    student_task = student_task_service.submit_solution(db, id=student_task_id, solution=solution)
    return student_task


@router.post("/student-tasks/{student_task_id}/grade", response_model=StudentTaskInDB)
def grade_student_task(
    student_task_id: int,
    grade: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Оценить задачу студента
    """
    # Проверка, что задача студента существует
    student_task = student_task_service.get(db, id=student_task_id)
    if not student_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача студента не найдена",
        )
    
    # Проверка корректности оценки
    if grade < 0 or grade > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Оценка должна быть от 0 до 100",
        )
    
    # Оценка задачи студента
    student_task = student_task_service.grade_task(db, id=student_task_id, grade=grade, feedback=feedback)
    return student_task


@router.delete("/student-tasks/{student_task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_task(
    student_task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher)
):
    """
    Удалить задачу студента
    """
    # Проверка, что задача студента существует
    student_task = student_task_service.get(db, id=student_task_id)
    if not student_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача студента не найдена",
        )
    
    # Удаление задачи студента
    student_task_service.remove(db, id=student_task_id)
    return None

