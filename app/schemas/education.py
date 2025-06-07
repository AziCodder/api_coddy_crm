from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.user import BaseSchema
from app.schemas.people import StudentInDB, TeacherInDB


# Схемы для курсов
class CourseBase(BaseSchema):
    title: str
    description: Optional[str] = None
    duration_weeks: Optional[int] = None
    level: Optional[str] = None
    price: Optional[int] = None
    is_active: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_weeks: Optional[int] = None
    level: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None


class CourseInDB(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Схемы для групп
class GroupBase(BaseSchema):
    name: str
    course_id: int
    teacher_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_students: Optional[int] = 15
    description: Optional[str] = None
    is_active: bool = True


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseSchema):
    name: Optional[str] = None
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_students: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class GroupInDB(GroupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class GroupWithDetails(GroupInDB):
    course: CourseInDB
    teacher: Optional[TeacherInDB] = None
    students_count: int = 0


# Схемы для связи студентов и групп
class StudentGroupLink(BaseSchema):
    student_id: int
    group_id: int
    is_active: bool = True


class StudentGroupLinkUpdate(BaseSchema):
    is_active: Optional[bool] = None


class StudentGroupLinkInDB(StudentGroupLink):
    joined_at: datetime


class GroupWithStudents(GroupInDB):
    students: List[StudentInDB] = []

