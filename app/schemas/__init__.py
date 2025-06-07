from app.schemas.user import (
    BaseSchema, RoleBase, RoleCreate, RoleUpdate, RoleInDB,
    UserBase, UserCreate, UserUpdate, UserInDB,
    Token, TokenData, UserLogin
)
from app.schemas.people import (
    StudentBase, StudentCreate, StudentUpdate, StudentInDB, StudentWithUser,
    TeacherBase, TeacherCreate, TeacherUpdate, TeacherInDB, TeacherWithUser,
    ParentBase, ParentCreate, ParentUpdate, ParentInDB, ParentWithUser,
    StudentParentLink, StudentWithParents, ParentWithStudents
)
from app.schemas.education import (
    CourseBase, CourseCreate, CourseUpdate, CourseInDB,
    GroupBase, GroupCreate, GroupUpdate, GroupInDB, GroupWithDetails,
    StudentGroupLink, StudentGroupLinkUpdate, StudentGroupLinkInDB, GroupWithStudents
)
from app.schemas.activities import (
    ScheduleBase, ScheduleCreate, ScheduleUpdate, ScheduleInDB, ScheduleWithGroup,
    TaskBase, TaskCreate, TaskUpdate, TaskInDB, TaskWithCourse,
    StudentTaskBase, StudentTaskCreate, StudentTaskUpdate, StudentTaskInDB, StudentTaskWithDetails
)

# Для удобного импорта всех схем
__all__ = [
    "BaseSchema", "RoleBase", "RoleCreate", "RoleUpdate", "RoleInDB",
    "UserBase", "UserCreate", "UserUpdate", "UserInDB",
    "Token", "TokenData", "UserLogin",
    
    "StudentBase", "StudentCreate", "StudentUpdate", "StudentInDB", "StudentWithUser",
    "TeacherBase", "TeacherCreate", "TeacherUpdate", "TeacherInDB", "TeacherWithUser",
    "ParentBase", "ParentCreate", "ParentUpdate", "ParentInDB", "ParentWithUser",
    "StudentParentLink", "StudentWithParents", "ParentWithStudents",
    
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseInDB",
    "GroupBase", "GroupCreate", "GroupUpdate", "GroupInDB", "GroupWithDetails",
    "StudentGroupLink", "StudentGroupLinkUpdate", "StudentGroupLinkInDB", "GroupWithStudents",
    
    "ScheduleBase", "ScheduleCreate", "ScheduleUpdate", "ScheduleInDB", "ScheduleWithGroup",
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskInDB", "TaskWithCourse",
    "StudentTaskBase", "StudentTaskCreate", "StudentTaskUpdate", "StudentTaskInDB", "StudentTaskWithDetails"
]

