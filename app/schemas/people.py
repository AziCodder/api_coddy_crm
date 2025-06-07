from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date

from app.schemas.user import BaseSchema, UserInDB


# Схемы для студентов
class StudentBase(BaseSchema):
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class StudentCreate(StudentBase):
    user_id: int


class StudentUpdate(StudentBase):
    pass


class StudentInDB(StudentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class StudentWithUser(StudentInDB):
    user: UserInDB


# Схемы для преподавателей
class TeacherBase(BaseSchema):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = 0
    phone: Optional[str] = None


class TeacherCreate(TeacherBase):
    user_id: int


class TeacherUpdate(TeacherBase):
    pass


class TeacherInDB(TeacherBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TeacherWithUser(TeacherInDB):
    user: UserInDB


# Схемы для родителей
class ParentBase(BaseSchema):
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ParentCreate(ParentBase):
    user_id: int


class ParentUpdate(ParentBase):
    pass


class ParentInDB(ParentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ParentWithUser(ParentInDB):
    user: UserInDB


# Схемы для связи родителей и студентов
class StudentParentLink(BaseSchema):
    student_id: int
    parent_id: int


class StudentWithParents(StudentInDB):
    parents: List[ParentInDB] = []


class ParentWithStudents(ParentInDB):
    students: List[StudentInDB] = []

