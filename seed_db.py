import sys
import os
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.user import User, Role, RoleEnum
from app.models.people import Student, Teacher, Parent
from app.models.education import Course, Group, StudentGroup
from app.models.activities import Task, Schedule, StudentTask, TaskStatusEnum
from app.core.security import get_password_hash

# Создаем подключение к базе данных
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Создаем роли
    roles = {
        RoleEnum.ADMIN: Role(name=RoleEnum.ADMIN.value, description="Администратор системы"),
        RoleEnum.MANAGER: Role(name=RoleEnum.MANAGER.value, description="Менеджер школы"),
        RoleEnum.TEACHER: Role(name=RoleEnum.TEACHER.value, description="Преподаватель"),
        RoleEnum.STUDENT: Role(name=RoleEnum.STUDENT.value, description="Ученик"),
        RoleEnum.PARENT: Role(name=RoleEnum.PARENT.value, description="Родитель ученика")
    }
    
    for role in roles.values():
        db.add(role)
    
    db.commit()
    print("Роли созданы")
    
    # Создаем пользователей
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        first_name="Админ",
        last_name="Админов",
        is_active=True
    )
    admin.roles.append(roles[RoleEnum.ADMIN])
    
    manager = User(
        email="manager@example.com",
        username="manager",
        hashed_password=get_password_hash("manager123"),
        first_name="Менеджер",
        last_name="Менеджеров",
        is_active=True
    )
    manager.roles.append(roles[RoleEnum.MANAGER])
    
    teacher1 = User(
        email="teacher1@example.com",
        username="teacher1",
        hashed_password=get_password_hash("teacher123"),
        first_name="Иван",
        last_name="Петров",
        is_active=True
    )
    teacher1.roles.append(roles[RoleEnum.TEACHER])
    
    teacher2 = User(
        email="teacher2@example.com",
        username="teacher2",
        hashed_password=get_password_hash("teacher123"),
        first_name="Мария",
        last_name="Иванова",
        is_active=True
    )
    teacher2.roles.append(roles[RoleEnum.TEACHER])
    
    student1 = User(
        email="student1@example.com",
        username="student1",
        hashed_password=get_password_hash("student123"),
        first_name="Алексей",
        last_name="Смирнов",
        is_active=True
    )
    student1.roles.append(roles[RoleEnum.STUDENT])
    
    student2 = User(
        email="student2@example.com",
        username="student2",
        hashed_password=get_password_hash("student123"),
        first_name="Екатерина",
        last_name="Соколова",
        is_active=True
    )
    student2.roles.append(roles[RoleEnum.STUDENT])
    
    parent1 = User(
        email="parent1@example.com",
        username="parent1",
        hashed_password=get_password_hash("parent123"),
        first_name="Сергей",
        last_name="Смирнов",
        is_active=True
    )
    parent1.roles.append(roles[RoleEnum.PARENT])
    
    parent2 = User(
        email="parent2@example.com",
        username="parent2",
        hashed_password=get_password_hash("parent123"),
        first_name="Ольга",
        last_name="Соколова",
        is_active=True
    )
    parent2.roles.append(roles[RoleEnum.PARENT])
    
    users = [admin, manager, teacher1, teacher2, student1, student2, parent1, parent2]
    for user in users:
        db.add(user)
    
    db.commit()
    print("Пользователи созданы")
    
    # Создаем профили преподавателей
    teacher1_profile = Teacher(
        user_id=teacher1.id,
        specialization="Python, JavaScript",
        bio="Опытный преподаватель программирования",
        experience_years=5,
        phone="+7 (900) 123-45-67"
    )
    
    teacher2_profile = Teacher(
        user_id=teacher2.id,
        specialization="Java, C++",
        bio="Преподаватель с опытом работы в IT-компаниях",
        experience_years=3,
        phone="+7 (900) 765-43-21"
    )
    
    db.add(teacher1_profile)
    db.add(teacher2_profile)
    
    # Создаем профили студентов
    student1_profile = Student(
        user_id=student1.id,
        birth_date=date(2005, 5, 15),
        phone="+7 (900) 111-22-33",
        address="г. Москва, ул. Примерная, д. 1"
    )
    
    student2_profile = Student(
        user_id=student2.id,
        birth_date=date(2006, 8, 20),
        phone="+7 (900) 444-55-66",
        address="г. Москва, ул. Тестовая, д. 2"
    )
    
    db.add(student1_profile)
    db.add(student2_profile)
    
    # Создаем профили родителей
    parent1_profile = Parent(
        user_id=parent1.id,
        phone="+7 (900) 777-88-99",
        alt_phone="+7 (900) 777-88-00",
        address="г. Москва, ул. Примерная, д. 1"
    )
    
    parent2_profile = Parent(
        user_id=parent2.id,
        phone="+7 (900) 333-22-11",
        alt_phone="+7 (900) 333-22-00",
        address="г. Москва, ул. Тестовая, д. 2"
    )
    
    db.add(parent1_profile)
    db.add(parent2_profile)
    
    db.commit()
    print("Профили созданы")
    
    # Связываем родителей и студентов
    parent1_profile.students.append(student1_profile)
    parent2_profile.students.append(student2_profile)
    
    db.commit()
    print("Связи родителей и студентов созданы")
    
    # Создаем курсы
    python_course = Course(
        title="Python для начинающих",
        description="Базовый курс программирования на Python",
        duration_weeks=8,
        level="beginner",
        price=15000,
        is_active=True
    )
    
    java_course = Course(
        title="Java разработка",
        description="Курс по разработке приложений на Java",
        duration_weeks=12,
        level="intermediate",
        price=20000,
        is_active=True
    )
    
    web_course = Course(
        title="Веб-разработка",
        description="Курс по разработке веб-приложений",
        duration_weeks=10,
        level="beginner",
        price=18000,
        is_active=True
    )
    
    db.add(python_course)
    db.add(java_course)
    db.add(web_course)
    
    db.commit()
    print("Курсы созданы")
    
    # Создаем группы
    python_group = Group(
        name="Python-1",
        course_id=python_course.id,
        teacher_id=teacher1_profile.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(weeks=8),
        max_students=10,
        description="Группа по изучению Python",
        is_active=True
    )
    
    java_group = Group(
        name="Java-1",
        course_id=java_course.id,
        teacher_id=teacher2_profile.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(weeks=12),
        max_students=8,
        description="Группа по изучению Java",
        is_active=True
    )
    
    db.add(python_group)
    db.add(java_group)
    
    db.commit()
    print("Группы созданы")
    
    # Добавляем студентов в группы
    student_group1 = StudentGroup(
        student_id=student1_profile.id,
        group_id=python_group.id,
        is_active=True
    )
    
    student_group2 = StudentGroup(
        student_id=student2_profile.id,
        group_id=java_group.id,
        is_active=True
    )
    
    db.add(student_group1)
    db.add(student_group2)
    
    db.commit()
    print("Студенты добавлены в группы")
    
    # Создаем расписание
    schedule1 = Schedule(
        group_id=python_group.id,
        day_of_week=1,  # Понедельник
        start_time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
        end_time=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0),
        room="Кабинет 101",
        is_active=True
    )
    
    schedule2 = Schedule(
        group_id=python_group.id,
        day_of_week=3,  # Среда
        start_time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
        end_time=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0),
        room="Кабинет 101",
        is_active=True
    )
    
    schedule3 = Schedule(
        group_id=java_group.id,
        day_of_week=2,  # Вторник
        start_time=datetime.now().replace(hour=19, minute=0, second=0, microsecond=0),
        end_time=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0),
        room="Кабинет 102",
        is_active=True
    )
    
    schedule4 = Schedule(
        group_id=java_group.id,
        day_of_week=4,  # Четверг
        start_time=datetime.now().replace(hour=19, minute=0, second=0, microsecond=0),
        end_time=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0),
        room="Кабинет 102",
        is_active=True
    )
    
    db.add(schedule1)
    db.add(schedule2)
    db.add(schedule3)
    db.add(schedule4)
    
    db.commit()
    print("Расписание создано")
    
    # Создаем задачи
    task1 = Task(
        title="Введение в Python",
        description="Задача на изучение основ Python",
        course_id=python_course.id,
        due_date=datetime.now() + timedelta(days=7)
    )
    
    task2 = Task(
        title="Работа с функциями",
        description="Задача на изучение функций в Python",
        course_id=python_course.id,
        due_date=datetime.now() + timedelta(days=14)
    )
    
    task3 = Task(
        title="Введение в Java",
        description="Задача на изучение основ Java",
        course_id=java_course.id,
        due_date=datetime.now() + timedelta(days=7)
    )
    
    db.add(task1)
    db.add(task2)
    db.add(task3)
    
    db.commit()
    print("Задачи созданы")
    
    # Создаем задачи для студентов
    student_task1 = StudentTask(
        student_id=student1_profile.id,
        task_id=task1.id,
        status=TaskStatusEnum.PENDING
    )
    
    student_task2 = StudentTask(
        student_id=student1_profile.id,
        task_id=task2.id,
        status=TaskStatusEnum.PENDING
    )
    
    student_task3 = StudentTask(
        student_id=student2_profile.id,
        task_id=task3.id,
        status=TaskStatusEnum.PENDING
    )
    
    db.add(student_task1)
    db.add(student_task2)
    db.add(student_task3)
    
    db.commit()
    print("Задачи для студентов созданы")
    
    print("База данных успешно заполнена начальными данными")

except Exception as e:
    db.rollback()
    print(f"Ошибка при заполнении базы данных: {e}")

finally:
    db.close()

