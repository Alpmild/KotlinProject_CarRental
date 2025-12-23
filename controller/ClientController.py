from service import get_client_service, get_current_user
from service import ClientService
from dto import ClientResponseDTO, ClientCreateDTO, ClientUpdateDTO, ClientFilterDTO

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/clients",
    tags=["Клиенты"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/{client_id:int}", response_model=ClientResponseDTO)
def get_client_by_id(client_id: int, service: ClientService = Depends(get_client_service)):
    try:
        return service.get_client_by_id(client_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.get("/name", response_model=List[ClientResponseDTO])
def get_by_name(name: str, service: ClientService = Depends(get_client_service)):
    return service.get_by_name(name)


@router.get("/filter", response_model=List[ClientResponseDTO])
def get_client_by_filter(
        client_filter: ClientFilterDTO = Depends(),
        service: ClientService = Depends(get_client_service)
):
    try:
        result = service.get_clients_by_filter(clients_filter_dto=client_filter)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return result


@router.post("/", response_model=ClientResponseDTO, status_code=201)
def create_client(
        client_dto: ClientCreateDTO,
        service: ClientService = Depends(get_client_service)
):
    try:
        return service.create_client(client_dto)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.put("/", response_model=ClientResponseDTO)
def update_client(
        update_dto: ClientUpdateDTO,
        service: ClientService = Depends(get_client_service)
):
    try:
        return service.update_client(update_dto)
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{client_id:int}", status_code=200)
def delete_client(
        client_id: int,
        service: ClientService = Depends(get_client_service)
):
    result = service.delete_client(client_id)
    if not result:
        raise HTTPException(404, f"{client_id=} не найден")
    return result
