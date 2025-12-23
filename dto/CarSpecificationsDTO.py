from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

class TransmissionEnum(str, Enum):
    """Типы коробок передач"""
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"
    ROBOT = "ROBOT"
    CVT = "CVT"


class ActuatorEnum(str, Enum):
    """Типы привода"""
    FRONT = "FRONT"
    REAR = "REAR"
    ALL = "ALL"


class WheelEnum(str, Enum):
    """Расположение руля"""
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class CarSpecificationsCreateDTO(BaseModel):
    """DTO для создания характеристик автомобиля"""
    car_id: int = Field(..., gt=0, description="ID автомобиля")
    name: str = Field(..., min_length=1, max_length=255)
    mileage: int = Field(..., ge=0)
    power: int = Field(..., gt=0, ge=50, le=2000)
    overclocking: float = Field(..., gt=0)
    consump_in_city: float = Field(..., gt=0)
    transmission: TransmissionEnum = Field(default=TransmissionEnum.AUTOMATIC)
    actuator: ActuatorEnum = Field(default=ActuatorEnum.FRONT)
    wheel: WheelEnum = Field(default=WheelEnum.LEFT)
    color: str = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class CarSpecificationsUpdateDTO(BaseModel):
    """DTO для обновления характеристик"""
    car_id: int = Field(..., gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    mileage: Optional[int] = Field(None, ge=0)
    power: Optional[int] = Field(None, gt=0, ge=50, le=2000)
    overclocking: Optional[float] = Field(None, gt=0, le=30.0)
    consump_in_city: Optional[float] = Field(None, gt=0, le=30.0)
    transmission: Optional[TransmissionEnum] = None
    actuator: Optional[ActuatorEnum] = None
    wheel: Optional[WheelEnum] = None

    model_config = ConfigDict(from_attributes=True)


class CarSpecificationsResponseDTO(BaseModel):
    """DTO для ответа с характеристиками"""
    car_id: int
    name: str
    mileage: int
    power: int
    overclocking: float
    consump_in_city: float
    transmission: str
    actuator: str
    wheel: str
    color: str

    model_config = ConfigDict(from_attributes=True)
