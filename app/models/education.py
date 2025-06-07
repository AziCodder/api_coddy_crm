from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# Таблица связи студентов и групп
class StudentGroup(Base):
    __tablename__ = "student_group"
    
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Отношения
    student = relationship("Student", back_populates="groups")
    group = relationship("Group", back_populates="students")


# Модель группы
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    max_students = Column(Integer, default=15)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    course = relationship("Course", back_populates="groups")
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("StudentGroup", back_populates="group")
    schedules = relationship("Schedule", back_populates="group")

    def __repr__(self):
        return f"<Group {self.name}>"


# Модель курса
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    duration_weeks = Column(Integer)
    level = Column(String(50))  # beginner, intermediate, advanced
    price = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    groups = relationship("Group", back_populates="course")
    tasks = relationship("Task", back_populates="course")

    def __repr__(self):
        return f"<Course {self.title}>"

