from .CarSpecificationsDTO import (CarSpecificationsCreateDTO, CarSpecificationsResponseDTO,
                                   TransmissionEnum, CarSpecificationsUpdateDTO)

import re
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Final
from datetime import datetime
from enum import Enum

_LICENSE_PLATE_PATTERN: Final[str] = r"^[АВЕКМНОРСТУХ]?\d{3}[АВЕКМНОРСТУХ]{2}\d{0,3}$"

_VIN_LENGTH: Final[int] = 17
_VIN_ALLOWED_CHARS: Final[frozenset[str]] = frozenset("0123456789ABCDEFGHJKLMNPRSTUVWXYZ")
_VIN_PATTERN: Final[re.Pattern] = re.compile(r"^[0-9A-HJ-NPR-Z]{17}$", re.ASCII)

# ============== CAR DTOs ==============

class CarStatusEnum(str, Enum):
    """Статусы автомобилей"""
    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    RENTED = "RENTED"
    MAINTENANCE = "MAINTENANCE"


class ValidatedBaseModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_validator('vin', check_fields=False)
    @classmethod
    def validate_vin(cls, v: str):
        vin_clean = v.strip().upper()
        if len(vin_clean) != _VIN_LENGTH:
            raise ValueError(f"VIN должен содержать ровно {_VIN_LENGTH} символов, получено: {len(vin_clean)}")

        invalid_chars = set(vin_clean) - _VIN_ALLOWED_CHARS
        if invalid_chars:
            raise ValueError(f"VIN содержит недопустимые символы: {sorted(invalid_chars)}")
        return vin_clean

    @field_validator('license_plate', check_fields=False)
    @classmethod
    def validate_license_plate(cls, v: str):
        v = v.upper()
        res = re.match(_LICENSE_PLATE_PATTERN, v).group(0)
        if v != res:
            raise ValueError(f'Номерной знак не соответствует формату: {v=}')
        return v

class CarCreateDTO(ValidatedBaseModel):
    """DTO для создания автомобиля"""
    license_plate: str = Field(..., min_length=8, max_length=9, pattern=_LICENSE_PLATE_PATTERN)
    vin: str = Field(..., min_length=17, max_length=17)
    daily_rate: int = Field(..., gt=0)
    status: str = Field(default=CarStatusEnum.AVAILABLE)
    specifications: Optional[CarSpecificationsCreateDTO] = None

    model_config = ConfigDict(from_attributes=True)



class CarUpdateDTO(ValidatedBaseModel):
    """DTO для обновления автомобиля"""
    car_id: int = Field(..., gt=0)
    license_plate: Optional[str] = Field(None, min_length=1, max_length=9, pattern=_LICENSE_PLATE_PATTERN)
    daily_rate: Optional[int] = Field(None, gt=0)
    status: Optional[CarStatusEnum] = None

    model_config = ConfigDict(from_attributes=True)


class CarResponseDTO(BaseModel):
    """DTO для ответа с данными автомобиля"""
    car_id: int
    license_plate: str
    vin: str
    daily_rate: int
    status: str
    change_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CarWithSpecsResponseDTO(BaseModel):
    """DTO с автомобилем и его характеристиками"""
    car: CarResponseDTO
    specifications: Optional[CarSpecificationsResponseDTO]

    model_config = ConfigDict(from_attributes=True)

class CarWithSpecsUpdateDTO(BaseModel):
    """DTO с автомобилем и его характеристиками"""
    car: Optional[CarUpdateDTO] = None
    specifications: Optional[CarSpecificationsUpdateDTO] = None

    model_config = ConfigDict(from_attributes=True)


class CarFilterDTO(BaseModel):
    """DTO для поиска автомобилей"""
    license_plate: Optional[str] = None
    vin: Optional[str] = None
    status: Optional[str] = None
    min_rate: Optional[int] = None
    max_rate: Optional[int] = None

    model: Optional[str] = None
    transmission: Optional[str] = None
    actuator: Optional[str] = None
    color: Optional[str] = None
    min_power: Optional[int] = None
    max_power: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
