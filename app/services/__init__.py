from app.services.user import user, role
from app.services.people import student, teacher, parent
from app.services.education import course, group
from app.services.activities import schedule, task, student_task

# Для удобного импорта всех сервисов
__all__ = [
    "user", "role",
    "student", "teacher", "parent",
    "course", "group",
    "schedule", "task", "student_task"
]

