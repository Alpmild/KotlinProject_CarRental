from utils import hash_password
from repository import UserRepository
from dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from entity import User

from sqlalchemy.orm import Session
from typing import Dict


class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)

    def create_user(self, user_dto: UserCreateDTO) -> Dict:
        email = str(user_dto.email)
        if self.user_repo.email_exists(email):
            raise ValueError(f"Email {email} уже используется")

        user_entity = User(
            email=user_dto.email,
            password=hash_password(user_dto.password),
            name=user_dto.name.strip(),
            position=user_dto.position
        )

        created_user = self.user_repo.create(user_entity)
        return UserResponseDTO.model_validate(created_user).model_dump()

    def update_user(self, user_info_dto: UserUpdateDTO) -> UserResponseDTO:
        client_response_dto = UserResponseDTO.model_validate(self.user_repo.update(user_info_dto))
        return client_response_dto

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete(user_id)

    def get_user_by_id(self, user_id: int) -> UserResponseDTO:
        user_entity = self.user_repo.get_by_user_id(user_id)
        if not user_entity:
            raise ValueError(f"Сотрудник с ID {user_id} не найден")
        return UserResponseDTO.model_validate(user_entity)

    def exists(self, user_id: int) -> bool:
        return self.user_repo.exists(user_id)

    def count_all(self) -> int:
        """Общее количество автомобилей"""
        return self.user_repo.count_all()
