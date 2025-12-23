from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator, Field, ConfigDict
from enum import Enum

from dto import ClientResponseDTO, UserResponseDTO, CarWithSpecsResponseDTO


class RentalStatusEnum(str, Enum):
    """Статусы аренды"""
    AWAITING = "AWAITING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class RentalCreateDTO(BaseModel):
    """DTO для создания аренды"""
    car_id: int = Field(..., gt=0)
    client_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    start_date: datetime = Field(gt=datetime.now(), default=datetime.now())
    end_date: datetime = Field(...)
    status: RentalStatusEnum = Field(RentalStatusEnum.AWAITING)
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('Дата возврата должна быть в будущем')
        return v


class RentalUpdateDTO(BaseModel):
    """DTO для обновления аренды"""
    rent_id: int = Field(..., gt=0)
    end_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    total_cost: Optional[int] = None
    status: Optional[RentalStatusEnum] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('actual_return_date')
    @classmethod
    def validate_actual_return_date(cls, v):
        if v and v > datetime.now(timezone.utc):
            raise ValueError('Фактическая дата возврата не может быть в будущем')
        return v


class RentalResponseDTO(BaseModel):
    """DTO для ответа с данными аренды"""
    rent_id: int
    start_date: datetime
    end_date: datetime
    actual_return_date: Optional[datetime]
    total_cost: Optional[int]
    status: str
    notes: Optional[str]
    car_id: int
    client_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RentalWithRelationsDTO(BaseModel):
    """DTO с арендой и связанными данными"""
    rental: Optional[RentalResponseDTO] = None
    car: Optional[CarWithSpecsResponseDTO] = None
    client: Optional[ClientResponseDTO] = None
    user: Optional[UserResponseDTO] = None

    model_config = ConfigDict(from_attributes=True)

class RentalFilterDTO(BaseModel):
    client_id: Optional[int] = None
    car_id: Optional[int] = None
    user_id: Optional[int] = None
    time_range: Optional[List[datetime]] = None
    status: Optional[RentalStatusEnum] = None

    model_config = ConfigDict(from_attributes=True)
