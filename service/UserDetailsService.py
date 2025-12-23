from repository import UserRepository
from dto import UserLoginDTO, UserLoginResponseDTO
from utils import verify_password

from sqlalchemy.orm import Session

class UserDetailsService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)

    def check_authorization(self, email: str, password: str) -> bool:
        if not self.user_repo.email_exists(email):
            return False

        hashed_password = self.user_repo.get_password_by_email(email)
        return verify_password(hashed_password, password)

    def get_user_login_response(self, user_id: int) -> UserLoginResponseDTO:
        res = self.user_repo.get_by_user_id(user_id)
        if res is None:
            ValueError(f"{user_id=} не существует.")
        return UserLoginResponseDTO.model_validate(res)


    def get_user_by_email(self, email: str):
        res = self.user_repo.get_by_email(email)
        if res is None:
            ValueError(f"{email=} не существует.")
        return UserLoginResponseDTO.model_validate(res)

