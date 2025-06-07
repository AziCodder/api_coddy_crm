from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.services.base import CRUDBase
from app.models.education import Group, Course, StudentGroup
from app.models.people import Student
from app.schemas.education import (
    GroupCreate, GroupUpdate,
    CourseCreate, CourseUpdate,
    StudentGroupLink, StudentGroupLinkUpdate
)


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    """
    CRUD для курсов с дополнительными методами
    """
    
    def get_with_groups(self, db: Session, *, id: int) -> Optional[Course]:
        """
        Получить курс с группами
        """
        return db.query(Course).options(joinedload(Course.groups)).filter(Course.id == id).first()
    
    def get_active_courses(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Course]:
        """
        Получить активные курсы
        """
        return db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    """
    CRUD для групп с дополнительными методами
    """
    
    def get_with_course(self, db: Session, *, id: int) -> Optional[Group]:
        """
        Получить группу с курсом
        """
        return db.query(Group).options(joinedload(Group.course)).filter(Group.id == id).first()
    
    def get_with_teacher(self, db: Session, *, id: int) -> Optional[Group]:
        """
        Получить группу с преподавателем
        """
        return db.query(Group).options(joinedload(Group.teacher)).filter(Group.id == id).first()
    
    def get_with_students(self, db: Session, *, id: int) -> Optional[Group]:
        """
        Получить группу со студентами
        """
        group = (
            db.query(Group)
            .options(joinedload(Group.students).joinedload(StudentGroup.student))
            .filter(Group.id == id)
            .first()
        )

        if group:
            group.__dict__["students"] = [sg.student for sg in group.students]

        return group
    
    def get_with_all(self, db: Session, *, id: int) -> Optional[Group]:
        """
        Получить группу со всеми связанными данными
        """
        return (
            db.query(Group)
            .options(
                joinedload(Group.course),
                joinedload(Group.teacher),
                joinedload(Group.students)
            )
            .filter(Group.id == id)
            .first()
        )
    
    def get_by_course(self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
        """
        Получить группы по курсу
        """
        return db.query(Group).filter(Group.course_id == course_id).offset(skip).limit(limit).all()
    
    def get_by_teacher(self, db: Session, *, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
        """
        Получить группы по преподавателю
        """
        return db.query(Group).filter(Group.teacher_id == teacher_id).offset(skip).limit(limit).all()
    
    def get_active_groups(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Group]:
        """
        Получить активные группы
        """
        return db.query(Group).filter(Group.is_active == True).offset(skip).limit(limit).all()
    
    def get_with_details(self, db: Session, *, id: int) -> Optional[Dict[str, Any]]:
        """
        Получить группу с детальной информацией
        """
        group = self.get_with_all(db, id=id)
        if not group:
            return None
        
        # Подсчет количества студентов
        students_count = (
            db.query(func.count(StudentGroup.student_id))
            .filter(
                StudentGroup.group_id == id,
                StudentGroup.is_active == True
            )
            .scalar()
        )
        
        return {
            "group": group,
            "students_count": students_count
        }
    
    def add_student(
        self, db: Session, *, group_id: int, student_id: int, is_active: bool = True
    ) -> Optional[StudentGroup]:
        """
        Добавить студента в группу
        """
        group = self.get(db, group_id)
        student = db.query(Student).get(student_id)
        
        if not group or not student:
            return None
        
        # Проверяем, что связь еще не существует
        existing = (
            db.query(StudentGroup)
            .filter(
                StudentGroup.group_id == group_id,
                StudentGroup.student_id == student_id
            )
            .first()
        )
        
        if existing:
            # Обновляем статус, если связь уже существует
            existing.is_active = is_active
            db.commit()
            db.refresh(existing)
            return existing
        
        # Создаем новую связь
        student_group = StudentGroup(
            group_id=group_id,
            student_id=student_id,
            is_active=is_active
        )
        db.add(student_group)
        db.commit()
        db.refresh(student_group)
        return student_group
    
    def update_student_status(
        self, db: Session, *, group_id: int, student_id: int, is_active: bool
    ) -> Optional[StudentGroup]:
        """
        Обновить статус студента в группе
        """
        student_group = (
            db.query(StudentGroup)
            .filter(
                StudentGroup.group_id == group_id,
                StudentGroup.student_id == student_id
            )
            .first()
        )
        
        if not student_group:
            return None
        
        student_group.is_active = is_active
        db.commit()
        db.refresh(student_group)
        return student_group
    
    def remove_student(self, db: Session, *, group_id: int, student_id: int) -> bool:
        """
        Удалить студента из группы
        """
        student_group = (
            db.query(StudentGroup)
            .filter(
                StudentGroup.group_id == group_id,
                StudentGroup.student_id == student_id
            )
            .first()
        )
        
        if not student_group:
            return False
        
        db.delete(student_group)
        db.commit()
        return True
    
    def get_students_in_group(
        self, db: Session, *, group_id: int, active_only: bool = False, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """
        Получить студентов в группе
        """
        query = (
            db.query(Student)
            .join(StudentGroup)
            .filter(StudentGroup.group_id == group_id)
        )
        
        if active_only:
            query = query.filter(StudentGroup.is_active == True)
        
        return query.offset(skip).limit(limit).all()


# Создаем экземпляры CRUD
course = CRUDCourse(Course)
group = CRUDGroup(Group)

