from . import CarService, UserService, ClientService, RentalService, UserDetailsService
from database import get_db

import datetime
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "super-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_car_service(db: Session = Depends(get_db)) -> CarService:
    return CarService(db_session=db)


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    return ClientService(db_session=db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db_session=db)

def get_auth_service(db: Session = Depends(get_db)) -> UserDetailsService:
    return UserDetailsService(db_session=db)


def get_rental_service(db: Session = Depends(get_db)) -> RentalService:
    return RentalService(db_session=db)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: UserDetailsService = Depends(get_auth_service)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Токен пустой")
        res = auth_service.get_user_login_response(int(user_id))
        return res

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))