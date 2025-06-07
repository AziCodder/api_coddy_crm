from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# Таблица связи учеников и родителей
student_parent = Table(
    "student_parent",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("parent_id", Integer, ForeignKey("parents.id"), primary_key=True),
)


# Модель ученика
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    birth_date = Column(Date)
    phone = Column(String(20))
    address = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    user = relationship("User", back_populates="student_profile")
    parents = relationship("Parent", secondary=student_parent, back_populates="students")
    groups = relationship("StudentGroup", back_populates="student")
    tasks = relationship("StudentTask", back_populates="student")

    def __repr__(self):
        return f"<Student {self.id}>"


# Модель преподавателя
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(100))
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    user = relationship("User", back_populates="teacher_profile")
    groups = relationship("Group", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher {self.id}>"


# Модель родителя
class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String(20))
    alt_phone = Column(String(20))
    address = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    user = relationship("User", back_populates="parent_profile")
    students = relationship("Student", secondary=student_parent, back_populates="parents")

    def __repr__(self):
        return f"<Parent {self.id}>"

