from app.models.user import User, Role, RoleEnum, user_role
from app.models.people import Student, Teacher, Parent, student_parent
from app.models.education import Group, Course, StudentGroup
from app.models.activities import Schedule, Task, StudentTask, TaskStatusEnum

# Для удобного импорта всех моделей
__all__ = [
    "User", "Role", "RoleEnum", "user_role",
    "Student", "Teacher", "Parent", "student_parent",
    "Group", "Course", "StudentGroup",
    "Schedule", "Task", "StudentTask", "TaskStatusEnum"
]

