from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password
from app.models.user import User, Role, RoleEnum
from app.schemas.user import TokenData

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по имени пользователя и паролю
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Получает текущего пользователя по токену
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Проверяет, что текущий пользователь активен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Неактивный пользователь"
        )
    return current_user


def check_user_role(required_roles: List[RoleEnum]):
    """
    Проверяет, что у пользователя есть необходимые роли
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_roles = [role.name for role in current_user.roles]
        for role in required_roles:
            if role.value in user_roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Недостаточно прав. Требуются роли: {', '.join([r.value for r in required_roles])}",
        )
    return role_checker


# Предопределенные проверки ролей
check_admin = check_user_role([RoleEnum.ADMIN])
check_manager = check_user_role([RoleEnum.ADMIN, RoleEnum.MANAGER])
check_teacher = check_user_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TEACHER])
check_student = check_user_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TEACHER, RoleEnum.STUDENT])
check_parent = check_user_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.PARENT])

