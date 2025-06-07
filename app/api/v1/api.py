from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    students,
    teachers,
    groups,
    courses,
    schedules,
    tasks,
    parents
)

api_router = APIRouter()

# Подключение всех роутеров
api_router.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])
api_router.include_router(users.router, prefix="/users", tags=["Пользователи"])
api_router.include_router(students.router, prefix="/students", tags=["Ученики"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["Преподаватели"])
api_router.include_router(groups.router, prefix="/groups", tags=["Группы"])
api_router.include_router(courses.router, prefix="/courses", tags=["Курсы"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["Расписание"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Задачи"])
api_router.include_router(parents.router, prefix="/parents", tags=["Родители"])

