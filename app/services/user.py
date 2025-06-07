from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session

from app.services.base import CRUDBase
from app.models.user import User, Role, RoleEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD для пользователей с дополнительными методами
    """
    
    def create_with_roles(
        self, db: Session, *, obj_in: UserCreate
    ) -> User:
        """
        Создать пользователя с ролями
        """
        # Создаем пользователя
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active,
        )
        
        # Добавляем роли
        for role_enum in obj_in.roles:
            role = db.query(Role).filter(Role.name == role_enum.value).first()
            if not role:
                # Если роль не существует, создаем ее
                role = Role(name=role_enum.value, description=f"Роль {role_enum.value}")
                db.add(role)
                db.flush()
            db_obj.roles.append(role)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_password(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Обновить пользователя с паролем
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Хешируем пароль, если он предоставлен
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
        
        # Обновляем роли, если они предоставлены
        if "roles" in update_data and update_data["roles"]:
            # Очищаем текущие роли
            db_obj.roles = []
            
            # Добавляем новые роли
            for role_enum in update_data["roles"]:
                role = db.query(Role).filter(Role.name == role_enum.value).first()
                if not role:
                    # Если роль не существует, создаем ее
                    role = Role(name=role_enum.value, description=f"Роль {role_enum.value}")
                    db.add(role)
                    db.flush()
                db_obj.roles.append(role)
            
            del update_data["roles"]
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Получить пользователя по username
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_users_by_role(
        self, db: Session, *, role: RoleEnum, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Получить пользователей по роли
        """
        return (
            db.query(User)
            .join(User.roles)
            .filter(Role.name == role.value)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDRole(CRUDBase[Role, UserCreate, UserUpdate]):
    """
    CRUD для ролей с дополнительными методами
    """
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        """
        Получить роль по имени
        """
        return db.query(Role).filter(Role.name == name).first()
    
    def get_or_create(self, db: Session, *, name: str, description: Optional[str] = None) -> Role:
        """
        Получить роль по имени или создать, если не существует
        """
        role = self.get_by_name(db, name=name)
        if not role:
            role = Role(name=name, description=description or f"Роль {name}")
            db.add(role)
            db.commit()
            db.refresh(role)
        return role


# Создаем экземпляры CRUD
user = CRUDUser(User)
role = CRUDRole(Role)

