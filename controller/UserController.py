from service import get_user_service, get_current_user
from service import UserService
from dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO

from fastapi import APIRouter, Depends, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/{user_id:int}", response_model=UserResponseDTO)
def get_by_user_id(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.get("/{user_id:int}/exist")
def user_exist(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return service.exists(user_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.get("/count")
def users_count(service: UserService = Depends(get_user_service)):
    try:
        return dict(count=service.count_all())
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.post("/", response_model=UserResponseDTO, status_code=201)
def create_user(user_dto: UserCreateDTO, service: UserService = Depends(get_user_service)):
    try:
        return service.create_user(user_dto)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.put("/", response_model=UserResponseDTO)
def update_user(
        update_dto: UserUpdateDTO,
        service: UserService = Depends(get_user_service)
):
    try:
        return service.update_user(update_dto)
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{user_id:int}", status_code=200)
def delete_user(
        user_id: int,
        service: UserService = Depends(get_user_service)
):
    result = service.delete_user(user_id)
    if not result:
        raise HTTPException(404, f"Пользователь ID={user_id} не найден")
    return result
