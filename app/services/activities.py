from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from app.services.base import CRUDBase
from app.models.activities import Schedule, Task, StudentTask, TaskStatusEnum
from app.schemas.activities import (
    ScheduleCreate, ScheduleUpdate,
    TaskCreate, TaskUpdate,
    StudentTaskCreate, StudentTaskUpdate
)


class CRUDSchedule(CRUDBase[Schedule, ScheduleCreate, ScheduleUpdate]):
    """
    CRUD для расписания с дополнительными методами
    """
    
    def get_with_group(self, db: Session, *, id: int) -> Optional[Schedule]:
        """
        Получить расписание с группой
        """
        return db.query(Schedule).options(joinedload(Schedule.group)).filter(Schedule.id == id).first()
    
    def get_by_group(self, db: Session, *, group_id: int, skip: int = 0, limit: int = 100) -> List[Schedule]:
        """
        Получить расписание по группе
        """
        return db.query(Schedule).filter(Schedule.group_id == group_id).offset(skip).limit(limit).all()
    
    def get_by_day(self, db: Session, *, day_of_week: int, skip: int = 0, limit: int = 100) -> List[Schedule]:
        """
        Получить расписание по дню недели
        """
        return db.query(Schedule).filter(Schedule.day_of_week == day_of_week).offset(skip).limit(limit).all()
    
    def get_active_schedules(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Schedule]:
        """
        Получить активное расписание
        """
        return db.query(Schedule).filter(Schedule.is_active == True).offset(skip).limit(limit).all()


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """
    CRUD для задач с дополнительными методами
    """
    
    def get_with_course(self, db: Session, *, id: int) -> Optional[Task]:
        """
        Получить задачу с курсом
        """
        return db.query(Task).options(joinedload(Task.course)).filter(Task.id == id).first()
    
    def get_by_course(self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Получить задачи по курсу
        """
        return db.query(Task).filter(Task.course_id == course_id).offset(skip).limit(limit).all()
    
    def get_upcoming_tasks(self, db: Session, *, days: int = 7, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Получить предстоящие задачи
        """
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        return (
            db.query(Task)
            .filter(Task.due_date >= now, Task.due_date <= future)
            .order_by(Task.due_date)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDStudentTask(CRUDBase[StudentTask, StudentTaskCreate, StudentTaskUpdate]):
    """
    CRUD для задач студентов с дополнительными методами
    """
    
    def get_with_student(self, db: Session, *, id: int) -> Optional[StudentTask]:
        """
        Получить задачу студента с данными студента
        """
        return db.query(StudentTask).options(joinedload(StudentTask.student)).filter(StudentTask.id == id).first()
    
    def get_with_task(self, db: Session, *, id: int) -> Optional[StudentTask]:
        """
        Получить задачу студента с данными задачи
        """
        return db.query(StudentTask).options(joinedload(StudentTask.task)).filter(StudentTask.id == id).first()
    
    def get_with_all(self, db: Session, *, id: int) -> Optional[StudentTask]:
        """
        Получить задачу студента со всеми связанными данными
        """
        return (
            db.query(StudentTask)
            .options(
                joinedload(StudentTask.student),
                joinedload(StudentTask.task)
            )
            .filter(StudentTask.id == id)
            .first()
        )
    
    def get_by_student(
        self, db: Session, *, student_id: int, status: Optional[TaskStatusEnum] = None, 
        skip: int = 0, limit: int = 100
    ) -> List[StudentTask]:
        """
        Получить задачи по студенту
        """
        query = db.query(StudentTask).filter(StudentTask.student_id == student_id)
        
        if status:
            query = query.filter(StudentTask.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_task(
        self, db: Session, *, task_id: int, status: Optional[TaskStatusEnum] = None,
        skip: int = 0, limit: int = 100
    ) -> List[StudentTask]:
        """
        Получить задачи по задаче
        """
        query = db.query(StudentTask).filter(StudentTask.task_id == task_id)
        
        if status:
            query = query.filter(StudentTask.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def submit_solution(
        self, db: Session, *, id: int, solution: str
    ) -> Optional[StudentTask]:
        """
        Отправить решение задачи
        """
        student_task = self.get(db, id)
        if not student_task:
            return None
        
        student_task.solution = solution
        student_task.status = TaskStatusEnum.IN_PROGRESS
        student_task.submitted_at = datetime.utcnow()
        
        db.add(student_task)
        db.commit()
        db.refresh(student_task)
        return student_task
    
    def grade_task(
        self, db: Session, *, id: int, grade: int, feedback: Optional[str] = None
    ) -> Optional[StudentTask]:
        """
        Оценить задачу
        """
        student_task = self.get(db, id)
        if not student_task:
            return None
        
        student_task.grade = grade
        student_task.feedback = feedback
        student_task.status = TaskStatusEnum.COMPLETED
        student_task.graded_at = datetime.utcnow()
        
        db.add(student_task)
        db.commit()
        db.refresh(student_task)
        return student_task
    
    def update_status(
        self, db: Session, *, id: int, status: TaskStatusEnum
    ) -> Optional[StudentTask]:
        """
        Обновить статус задачи
        """
        student_task = self.get(db, id)
        if not student_task:
            return None
        
        student_task.status = status
        
        db.add(student_task)
        db.commit()
        db.refresh(student_task)
        return student_task


# Создаем экземпляры CRUD
schedule = CRUDSchedule(Schedule)
task = CRUDTask(Task)
student_task = CRUDStudentTask(StudentTask)

