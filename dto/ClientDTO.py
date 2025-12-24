from typing import Optional
from datetime import datetime

from pydantic import BaseModel, field_validator, Field, ConfigDict
import re

PHONE_PATTERN = r'^8\d{10}$'
TELEGRAM_PATTERN = '^@[a-zA-Z0-9]{5}$'
LICENSE_PATTERN = r'^ГИБДД \d{4}$'

class ValidatedBaseModel(BaseModel):
    """Базовый класс с общими валидаторами"""
    model_config = ConfigDict(extra='forbid')

    @field_validator('phone', check_fields=False)
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v is None:  # Для опциональных полей
            return None

        if not re.match(PHONE_PATTERN, v):
            raise ValueError("Phone must be in E.164 format 8dddddddddd")

        return v

    @field_validator('telegram_id', check_fields=False)
    @classmethod
    def validate_telegram_id(cls, v: Optional[str]):
        if v is None:
            return None

        v = v.strip().lstrip('@')
        if not v:
            raise ValueError("telegram_id не должно быть пустой строкой.")
        return '@' + v

    @classmethod
    def normalized_phone(cls, v) -> str:
        """Возвращает нормализованный номер"""
        if v.startswith('8') and len(v) == 11:
            return '+7' + v[1:]
        elif not v.startswith('+'):
            return '+' + v
        return v


# ============== CLIENT DTOs ==============

class ClientCreateDTO(ValidatedBaseModel):
    """DTO для создания клиента"""
    name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    telegram_id: Optional[str] = Field(None, max_length=30)
    license_number: str = Field(..., min_length=4, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class ClientUpdateDTO(BaseModel):
    """DTO для обновления клиента"""
    client_id: int = Field(..., gt=0)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    telegram_id: Optional[str] = Field(None, max_length=30)
    license_number: Optional[str] = Field(None, min_length=4, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class ClientResponseDTO(BaseModel):
    """DTO для ответа с данными клиента"""
    client_id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    license_number: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClientFilterDTO(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    license_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)