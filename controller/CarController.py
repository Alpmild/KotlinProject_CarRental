from service import get_car_service, get_current_user
from service import CarService
from dto import (CarCreateDTO, CarWithSpecsUpdateDTO, CarWithSpecsResponseDTO,
                 CarFilterDTO, CarResponseDTO)


from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/cars",
    tags=["Автомобили"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/filter", response_model=List[CarWithSpecsResponseDTO])
def get_cars_by_filter(
        car_filter: CarFilterDTO = Depends(),
        service: CarService = Depends(get_car_service)
):
    try:

        result = service.get_cars_by_filter(cars_filter=car_filter)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return result

@router.get("/available", response_model=List[CarWithSpecsResponseDTO])
def get_available_cars(service: CarService = Depends(get_car_service)):
    return service.get_available_cars()

@router.get("/price-range", response_model=List[CarWithSpecsResponseDTO])
def get_cars_by_price(
    min_price: int = Query(..., gt=0),
    max_price: int = Query(..., gt=0),
    service: CarService = Depends(get_car_service)
):
    if min_price > max_price:
        raise HTTPException(400, "min_price > max_price")
    return service.get_cars_by_price_range(min_price, max_price)

@router.get("/{car_id:int}", response_model=CarWithSpecsResponseDTO)
def get_car_by_id(car_id: int, service: CarService = Depends(get_car_service)):
    try:
        return service.get_car_by_id(car_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/", response_model=CarResponseDTO, status_code=201)
def create_car(car_dto: CarCreateDTO, service: CarService = Depends(get_car_service)):
    try:
        return service.create_car(car_dto)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.put("/", response_model=CarWithSpecsResponseDTO)
def update_car(
        update_dto: CarWithSpecsUpdateDTO,
        service: CarService = Depends(get_car_service)
):
    try:
        return service.update_car(update_dto)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router.delete("/{car_id:int}", status_code=200)
def delete_car(
    car_id: int,
    service: CarService = Depends(get_car_service)
):
    result = service.delete_car(car_id)
    if not result:
        raise HTTPException(404, f"Автомобиль ID={car_id} не найден")
    return result

