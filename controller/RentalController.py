from datetime import datetime

from service import get_rental_service, get_current_user
from service import RentalService
from dto import RentalCreateDTO, RentalUpdateDTO, RentalWithRelationsDTO, RentalFilterDTO

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Annotated
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/rentals",
    tags=["Бронирования"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/filter", response_model=List[RentalWithRelationsDTO])
def get_rentals_by_filter(
        rentals_filter: Annotated[RentalFilterDTO, Query()],
        service: RentalService = Depends(get_rental_service)
):
    try:
        result = service.get_rentals_by_filter(rentals_filter)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return result


@router.post("/", response_model=RentalWithRelationsDTO, status_code=201)
def create_rental(
        rental_dto: RentalCreateDTO,
        service: RentalService = Depends(get_rental_service)
):
    try:
        return service.create_rental(rental_dto)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.put("/", response_model=RentalWithRelationsDTO)
def update_rental(
        update_dto: RentalUpdateDTO,
        service: RentalService = Depends(get_rental_service)
):
    try:
        return service.update_rental(update_dto)
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.put("/extend/{rent_id:int}", response_model=RentalWithRelationsDTO)
def extend_rental(
        rent_id: int,
        new_end_date: datetime,
        service: RentalService = Depends(get_rental_service)
):
    try:
        return service.extend_rental(rent_id, new_end_date)
    except ValueError as e:
        return RentalWithRelationsDTO()
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.put("/complete/{rent_id:int}", response_model=RentalWithRelationsDTO)
def complete_rental(
        rent_id: int,
        actual_return_date: datetime,
        service: RentalService = Depends(get_rental_service)
):
    try:
        return service.complete_rental(rent_id, actual_return_date)
    except ValueError as e:
        return RentalWithRelationsDTO()
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.put("/cancel/{rent_id:int}", response_model=RentalWithRelationsDTO)
def cancel_rental(
        rent_id: int,
        service: RentalService = Depends(get_rental_service)
):
    try:
        return service.cancel_rental(rent_id)
    except ValueError as e:
        return RentalWithRelationsDTO()
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{rent_id:int}", status_code=200)
def delete_client(
        rent_id: int,
        service: RentalService = Depends(get_rental_service)
):
    result = service.delete_rental(rent_id)
    if not result:
        raise HTTPException(404, f"{rent_id=} не найден")
    return result
