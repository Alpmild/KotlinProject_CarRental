from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import re

_EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
_MIN_PASSWORD_LENGTH = 3


class UserPositionEnum(str, Enum):
    """Должности сотрудников"""
    MANAGER = "MANAGER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"


class ValidatedBaseModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_validator('email', check_fields=False)
    @classmethod
    def validate_email(cls, v: str):
        if not re.match(_EMAIL_PATTERN, v):
            raise ValueError('Неверный формат email. Пример: user@example.com')
        return v


class UserCreateDTO(ValidatedBaseModel):
    """DTO для создания сотрудника"""
    email: EmailStr = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    position: str = Field(default=UserPositionEnum.AGENT)

    model_config = ConfigDict(from_attributes=True)


class UserUpdateDTO(ValidatedBaseModel):
    """DTO для обновления сотрудника"""
    user_id: int = Field(..., gt=0)
    email: Optional[str] = Field(None, min_length=4, max_length=50)
    password: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    position: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponseDTO(BaseModel):
    """DTO для ответа с данными сотрудника"""
    user_id: int
    email: str
    name: str
    position: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
