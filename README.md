# API-сервер для CRM-системы школы программирования

Полноценный API-сервер для управления школой программирования, включающий функционал для работы с пользователями, учениками, преподавателями, группами, курсами, расписанием и задачами.

## Технологический стек

- **FastAPI** - современный веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Alembic** - инструмент для миграций базы данных
- **Pydantic** - библиотека для валидации данных
- **python-jose** - библиотека для работы с JWT
- **passlib[bcrypt]** - библиотека для хеширования паролей
- **uvicorn** - ASGI-сервер для запуска приложения

## Структура проекта

```
school_crm_api/
├── alembic/                  # Директория для миграций Alembic
│   ├── versions/             # Файлы миграций
│   ├── env.py                # Настройки окружения Alembic
│   └── script.py.mako        # Шаблон для файлов миграций
├── app/                      # Основной код приложения
│   ├── api/                  # API-эндпоинты
│   │   └── v1/               # Версия API v1
│   │       ├── dependencies/ # Зависимости для API (авторизация и т.д.)
│   │       └── endpoints/    # Эндпоинты API
│   ├── core/                 # Ядро приложения
│   │   ├── config.py         # Конфигурация приложения
│   │   └── security.py       # Функции безопасности (JWT, хеширование)
│   ├── db/                   # Настройки базы данных
│   │   └── session.py        # Сессия SQLAlchemy
│   ├── models/               # Модели SQLAlchemy
│   ├── schemas/              # Схемы Pydantic
│   ├── services/             # Сервисы для работы с данными
│   └── utils/                # Вспомогательные утилиты
├── tests/                    # Тесты
├── .env                      # Переменные окружения
├── .env.example              # Пример файла с переменными окружения
├── alembic.ini               # Конфигурация Alembic
├── main.py                   # Точка входа в приложение
├── requirements.txt          # Зависимости проекта
└── seed_db.py                # Скрипт для заполнения базы данных начальными данными
```

## Установка и запуск

### Предварительные требования

- Python 3.8+
- PostgreSQL

### Шаги по установке

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd school_crm_api
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example` и настройте подключение к базе данных:

```bash
cp .env.example .env
# Отредактируйте .env файл, указав настройки вашей базы данных
```

5. Создайте базу данных в PostgreSQL:

```bash
createdb school_crm
```

6. Примените миграции:

```bash
alembic upgrade head
```

7. (Опционально) Заполните базу данных тестовыми данными:

```bash
python seed_db.py
```

8. Запустите сервер:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

После запуска API будет доступен по адресу: http://localhost:8000

## Документация API

Swagger UI доступен по адресу: http://localhost:8000/docs
ReDoc доступен по адресу: http://localhost:8000/redoc

## Роли пользователей

В системе предусмотрены следующие роли:

- **admin** - Администратор системы с полным доступом
- **manager** - Менеджер школы с доступом к управлению пользователями, группами и курсами
- **teacher** - Преподаватель с доступом к своим группам, расписанию и задачам
- **student** - Ученик с доступом к своему профилю, группам и задачам
- **parent** - Родитель с доступом к профилям своих детей

## Основные функции API

### Аутентификация и авторизация

- Регистрация пользователей: `POST /api/v1/auth/register`
- Вход в систему (получение JWT-токена): `POST /api/v1/auth/login`
- Получение информации о текущем пользователе: `GET /api/v1/auth/me`

### Пользователи

- Получение списка пользователей: `GET /api/v1/users/`
- Создание пользователя: `POST /api/v1/users/`
- Получение информации о пользователе: `GET /api/v1/users/{user_id}`
- Обновление пользователя: `PUT /api/v1/users/{user_id}`
- Удаление пользователя: `DELETE /api/v1/users/{user_id}`

### Ученики

- Получение списка учеников: `GET /api/v1/students/`
- Создание ученика: `POST /api/v1/students/`
- Получение информации об ученике: `GET /api/v1/students/{student_id}`
- Обновление ученика: `PUT /api/v1/students/{student_id}`
- Удаление ученика: `DELETE /api/v1/students/{student_id}`
- Получение родителей ученика: `GET /api/v1/students/{student_id}/parents`
- Добавление родителя ученику: `POST /api/v1/students/{student_id}/parents`
- Удаление родителя у ученика: `DELETE /api/v1/students/{student_id}/parents/{parent_id}`

### Преподаватели

- Получение списка преподавателей: `GET /api/v1/teachers/`
- Создание преподавателя: `POST /api/v1/teachers/`
- Получение информации о преподавателе: `GET /api/v1/teachers/{teacher_id}`
- Обновление преподавателя: `PUT /api/v1/teachers/{teacher_id}`
- Удаление преподавателя: `DELETE /api/v1/teachers/{teacher_id}`

### Родители

- Получение списка родителей: `GET /api/v1/parents/`
- Создание родителя: `POST /api/v1/parents/`
- Получение информации о родителе: `GET /api/v1/parents/{parent_id}`
- Обновление родителя: `PUT /api/v1/parents/{parent_id}`
- Удаление родителя: `DELETE /api/v1/parents/{parent_id}`
- Получение учеников родителя: `GET /api/v1/parents/{parent_id}/students`
- Добавление ученика родителю: `POST /api/v1/parents/{parent_id}/students`
- Удаление ученика у родителя: `DELETE /api/v1/parents/{parent_id}/students/{student_id}`

### Группы

- Получение списка групп: `GET /api/v1/groups/`
- Создание группы: `POST /api/v1/groups/`
- Получение информации о группе: `GET /api/v1/groups/{group_id}`
- Обновление группы: `PUT /api/v1/groups/{group_id}`
- Удаление группы: `DELETE /api/v1/groups/{group_id}`
- Получение учеников в группе: `GET /api/v1/groups/{group_id}/students`
- Добавление ученика в группу: `POST /api/v1/groups/{group_id}/students`
- Обновление статуса ученика в группе: `PUT /api/v1/groups/{group_id}/students/{student_id}`
- Удаление ученика из группы: `DELETE /api/v1/groups/{group_id}/students/{student_id}`

### Курсы

- Получение списка курсов: `GET /api/v1/courses/`
- Создание курса: `POST /api/v1/courses/`
- Получение информации о курсе: `GET /api/v1/courses/{course_id}`
- Обновление курса: `PUT /api/v1/courses/{course_id}`
- Удаление курса: `DELETE /api/v1/courses/{course_id}`
- Получение групп по курсу: `GET /api/v1/courses/{course_id}/groups`

### Расписание

- Получение списка расписаний: `GET /api/v1/schedules/`
- Создание расписания: `POST /api/v1/schedules/`
- Получение информации о расписании: `GET /api/v1/schedules/{schedule_id}`
- Обновление расписания: `PUT /api/v1/schedules/{schedule_id}`
- Удаление расписания: `DELETE /api/v1/schedules/{schedule_id}`

### Задачи

- Получение списка задач: `GET /api/v1/tasks/`
- Создание задачи: `POST /api/v1/tasks/`
- Получение информации о задаче: `GET /api/v1/tasks/{task_id}`
- Обновление задачи: `PUT /api/v1/tasks/{task_id}`
- Удаление задачи: `DELETE /api/v1/tasks/{task_id}`
- Получение задач студентов по задаче: `GET /api/v1/tasks/{task_id}/student-tasks`
- Создание задачи для студента: `POST /api/v1/tasks/student-tasks`
- Получение информации о задаче студента: `GET /api/v1/tasks/student-tasks/{student_task_id}`
- Обновление задачи студента: `PUT /api/v1/tasks/student-tasks/{student_task_id}`
- Отправка решения задачи: `POST /api/v1/tasks/student-tasks/{student_task_id}/submit`
- Оценка задачи студента: `POST /api/v1/tasks/student-tasks/{student_task_id}/grade`
- Удаление задачи студента: `DELETE /api/v1/tasks/student-tasks/{student_task_id}`

## Тестовые данные

После запуска скрипта `seed_db.py` в базе данных будут созданы следующие тестовые пользователи:

| Логин    | Пароль     | Роль      | Email               |
|----------|------------|-----------|---------------------|
| admin    | admin123   | admin     | admin@example.com   |
| manager  | manager123 | manager   | manager@example.com |
| teacher1 | teacher123 | teacher   | teacher1@example.com|
| teacher2 | teacher123 | teacher   | teacher2@example.com|
| student1 | student123 | student   | student1@example.com|
| student2 | student123 | student   | student2@example.com|
| parent1  | parent123  | parent    | parent1@example.com |
| parent2  | parent123  | parent    | parent2@example.com |

## Разработка

### Создание новых миграций

Для создания новой миграции после изменения моделей используйте команду:

```bash
alembic revision --autogenerate -m "описание миграции"
```

### Применение миграций

Для применения всех миграций используйте команду:

```bash
alembic upgrade head
```

Для отката последней миграции:

```bash
alembic downgrade -1
```

## Лицензия

[MIT](LICENSE)

