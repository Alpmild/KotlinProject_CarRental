from entity import User
from dto import UserUpdateDTO
from utils import hash_password

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

class UserRepository:
    """Репозиторий для работы с сотрудниками"""

    def __init__(self, session: Session):
        self.session_db = session

    def create(self, user: User) -> User:
        self.session_db.add(user)
        self.session_db.commit()
        self.session_db.refresh(user)
        return user

    def update(self, update_data: Optional[UserUpdateDTO]) -> Optional[User]:
        user = self.get_by_user_id(update_data.user_id)
        user_info = update_data.model_dump()

        if user:
            if user_info.get('password', None) is not None:
                user_info['password'] =  hash_password(user_info['password'])

            for key, value in user_info.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            user.created_at = datetime.now()  # Обновляем время изменения
            self.session_db.commit()
            self.session_db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_user_id(user_id)
        if user:
            self.session_db.delete(user)
            self.session_db.commit()
            return True
        return False

    def get_by_user_id(self, user_id: int) -> Optional[User]:
        return self.session_db.query(User).filter(User.user_id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session_db.query(User).filter(User.email == email).first()

    def get_password_by_email(self, email: str) -> Optional[bytes]:
        return self.session_db.query(User.password).filter(User.email == email).scalar()

    def email_exists(self, email: str) -> bool:
        query = self.session_db.query(User).filter(User.email == email)
        return query.first() is not None

    def exists(self, user_id: int) -> bool:
        query = self.session_db.query(User).filter(User.user_id == user_id)
        return query.first() is not None

    def count_all(self) -> int:
        return self.session_db.query(User).count()
