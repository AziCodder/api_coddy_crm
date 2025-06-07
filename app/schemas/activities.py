from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time

from app.schemas.user import BaseSchema
from app.schemas.people import StudentInDB
from app.schemas.education import GroupInDB, CourseInDB
from app.models.activities import TaskStatusEnum


# Схемы для расписания
class ScheduleBase(BaseSchema):
    group_id: int
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: datetime
    end_time: datetime
    room: Optional[str] = None
    is_active: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseSchema):
    group_id: Optional[int] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    room: Optional[str] = None
    is_active: Optional[bool] = None


class ScheduleInDB(ScheduleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ScheduleWithGroup(ScheduleInDB):
    group: GroupInDB


# Схемы для задач
class TaskBase(BaseSchema):
    title: str
    description: Optional[str] = None
    course_id: int
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskWithCourse(TaskInDB):
    course: CourseInDB


# Схемы для задач студентов
class StudentTaskBase(BaseSchema):
    student_id: int
    task_id: int
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    solution: Optional[str] = None
    grade: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None


class StudentTaskCreate(StudentTaskBase):
    pass


class StudentTaskUpdate(BaseSchema):
    status: Optional[TaskStatusEnum] = None
    solution: Optional[str] = None
    grade: Optional[int] = Field(None, ge=0, le=100)
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None


class StudentTaskInDB(StudentTaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class StudentTaskWithDetails(StudentTaskInDB):
    student: StudentInDB
    task: TaskInDB

