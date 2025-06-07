from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


# Перечисление для статуса задачи
class TaskStatusEnum(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


# Модель расписания
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6, где 0 - понедельник
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    room = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    group = relationship("Group", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule {self.id} for Group {self.group_id}>"


# Модель задачи
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    course = relationship("Course", back_populates="tasks")
    student_tasks = relationship("StudentTask", back_populates="task")

    def __repr__(self):
        return f"<Task {self.title}>"


# Модель задачи для студента
class StudentTask(Base):
    __tablename__ = "student_tasks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    solution = Column(Text)
    grade = Column(Integer)
    feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True))
    graded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    student = relationship("Student", back_populates="tasks")
    task = relationship("Task", back_populates="student_tasks")

    def __repr__(self):
        return f"<StudentTask {self.id}>"

