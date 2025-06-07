from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload

from app.services.base import CRUDBase
from app.models.people import Student, Teacher, Parent, student_parent
from app.schemas.people import (
    StudentCreate, StudentUpdate,
    TeacherCreate, TeacherUpdate,
    ParentCreate, ParentUpdate
)


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    """
    CRUD для студентов с дополнительными методами
    """
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Student]:
        """
        Получить студента по ID пользователя
        """
        return db.query(Student).filter(Student.user_id == user_id).first()
    
    def get_with_user(self, db: Session, *, id: int) -> Optional[Student]:
        """
        Получить студента с данными пользователя
        """
        return db.query(Student).options(joinedload(Student.user)).filter(Student.id == id).first()
    
    def get_with_parents(self, db: Session, *, id: int) -> Optional[Student]:
        """
        Получить студента с родителями
        """
        return db.query(Student).options(joinedload(Student.parents)).filter(Student.id == id).first()
    
    def get_with_groups(self, db: Session, *, id: int) -> Optional[Student]:
        """
        Получить студента с группами
        """
        return db.query(Student).options(joinedload(Student.groups)).filter(Student.id == id).first()
    
    def get_with_all(self, db: Session, *, id: int) -> Optional[Student]:
        """
        Получить студента со всеми связанными данными
        """
        return (
            db.query(Student)
            .options(
                joinedload(Student.user),
                joinedload(Student.parents),
                joinedload(Student.groups)
            )
            .filter(Student.id == id)
            .first()
        )
    
    def add_parent(self, db: Session, *, student_id: int, parent_id: int) -> bool:
        """
        Добавить родителя студенту
        """
        student = self.get(db, student_id)
        parent = db.query(Parent).get(parent_id)
        
        if not student or not parent:
            return False
        
        # Проверяем, что связь еще не существует
        existing = (
            db.query(student_parent)
            .filter(
                student_parent.c.student_id == student_id,
                student_parent.c.parent_id == parent_id
            )
            .first()
        )
        
        if existing:
            return True
        
        # Добавляем связь
        student.parents.append(parent)
        db.commit()
        return True
    
    def remove_parent(self, db: Session, *, student_id: int, parent_id: int) -> bool:
        """
        Удалить родителя у студента
        """
        student = self.get(db, student_id)
        parent = db.query(Parent).get(parent_id)
        
        if not student or not parent:
            return False
        
        # Проверяем, что связь существует
        if parent not in student.parents:
            return False
        
        # Удаляем связь
        student.parents.remove(parent)
        db.commit()
        return True


class CRUDTeacher(CRUDBase[Teacher, TeacherCreate, TeacherUpdate]):
    """
    CRUD для преподавателей с дополнительными методами
    """
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Teacher]:
        """
        Получить преподавателя по ID пользователя
        """
        return db.query(Teacher).filter(Teacher.user_id == user_id).first()
    
    def get_with_user(self, db: Session, *, id: int) -> Optional[Teacher]:
        """
        Получить преподавателя с данными пользователя
        """
        return db.query(Teacher).options(joinedload(Teacher.user)).filter(Teacher.id == id).first()
    
    def get_with_groups(self, db: Session, *, id: int) -> Optional[Teacher]:
        """
        Получить преподавателя с группами
        """
        return db.query(Teacher).options(joinedload(Teacher.groups)).filter(Teacher.id == id).first()
    
    def get_with_all(self, db: Session, *, id: int) -> Optional[Teacher]:
        """
        Получить преподавателя со всеми связанными данными
        """
        return (
            db.query(Teacher)
            .options(
                joinedload(Teacher.user),
                joinedload(Teacher.groups)
            )
            .filter(Teacher.id == id)
            .first()
        )


class CRUDParent(CRUDBase[Parent, ParentCreate, ParentUpdate]):
    """
    CRUD для родителей с дополнительными методами
    """
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Parent]:
        """
        Получить родителя по ID пользователя
        """
        return db.query(Parent).filter(Parent.user_id == user_id).first()
    
    def get_with_user(self, db: Session, *, id: int) -> Optional[Parent]:
        """
        Получить родителя с данными пользователя
        """
        return db.query(Parent).options(joinedload(Parent.user)).filter(Parent.id == id).first()
    
    def get_with_students(self, db: Session, *, id: int) -> Optional[Parent]:
        """
        Получить родителя со студентами
        """
        return db.query(Parent).options(joinedload(Parent.students)).filter(Parent.id == id).first()
    
    def get_with_all(self, db: Session, *, id: int) -> Optional[Parent]:
        """
        Получить родителя со всеми связанными данными
        """
        return (
            db.query(Parent)
            .options(
                joinedload(Parent.user),
                joinedload(Parent.students)
            )
            .filter(Parent.id == id)
            .first()
        )
    
    def add_student(self, db: Session, *, parent_id: int, student_id: int) -> bool:
        """
        Добавить студента родителю
        """
        parent = self.get(db, parent_id)
        student = db.query(Student).get(student_id)
        
        if not parent or not student:
            return False
        
        # Проверяем, что связь еще не существует
        existing = (
            db.query(student_parent)
            .filter(
                student_parent.c.parent_id == parent_id,
                student_parent.c.student_id == student_id
            )
            .first()
        )
        
        if existing:
            return True
        
        # Добавляем связь
        parent.students.append(student)
        db.commit()
        return True
    
    def remove_student(self, db: Session, *, parent_id: int, student_id: int) -> bool:
        """
        Удалить студента у родителя
        """
        parent = self.get(db, parent_id)
        student = db.query(Student).get(student_id)
        
        if not parent or not student:
            return False
        
        # Проверяем, что связь существует
        if student not in parent.students:
            return False
        
        # Удаляем связь
        parent.students.remove(student)
        db.commit()
        return True


# Создаем экземпляры CRUD
student = CRUDStudent(Student)
teacher = CRUDTeacher(Teacher)
parent = CRUDParent(Parent)

