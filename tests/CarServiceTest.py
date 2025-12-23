from service import CarService
from dto import CarCreateDTO, CarResponseDTO, CarFilterDTO
from entity import Car, CarSpecifications

import pytest
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def car_service(mock_db):
    # При создании сервиса подменяем репозитории внутри через моки
    service = CarService(db_session=mock_db)
    service.car_repo = MagicMock()
    service.specs_repo = MagicMock()
    return service


def test_create_car_success(car_service):
    """Проверка успешного создания автомобиля"""
    # Данные для теста
    car_dto = CarCreateDTO(
        license_plate="А111АА123",
        vin="B" * 17,
        daily_rate=5000,
        status="AVAILABLE",
        specifications=None
    )

    mock_car_entity = Car(
        car_id=1,
        license_plate=car_dto.license_plate,
        vin=car_dto.vin,
        daily_rate=car_dto.daily_rate,
        status=car_dto.status,
        change_at=datetime.now()
    )

    car_service.car_repo.vin_exists.return_value = False
    car_service.car_repo.license_plate_exists.return_value = False

    car_service.car_repo.create.return_value = mock_car_entity

    result = car_service.create_car(car_dto)

    assert result.car_id == 1
    assert result.change_at is not None


def test_create_car_duplicate_vin(car_service):
    """Проверка ошибки при дублировании VIN"""
    vin = "WWWWWW1111111111W"
    car_dto = CarCreateDTO(
        license_plate="А413ВА12",
        vin=vin,
        daily_rate=5000,
        status="AVAILABLE"
    )

    # Имитируем, что VIN уже есть в базе
    car_service.car_repo.vin_exists.return_value = True

    # Проверяем, что вызывается ValueError
    with pytest.raises(ValueError) as excinfo:
        car_service.create_car(car_dto)

    assert f"VIN {vin} уже существует" in str(excinfo.value)
    # Убеждаемся, что метод create даже не вызывался
    car_service.car_repo.create.assert_not_called()


def test_get_car_by_id_not_found(car_service):
    """Проверка ошибки, если машина не найдена"""
    car_id = 999
    car_service.car_repo.get_by_id.return_value = None

    with pytest.raises(ValueError) as excinfo:
        car_service.get_car_by_id(car_id)

    assert f"Автомобиль с ID {car_id} не найден" in str(excinfo.value)


def test_get_cars_by_filter(car_service):
    """Проверка фильтрации машин"""

    # 1. Создаем реальный объект характеристик
    # Заполняем ВСЕ поля, которые Pydantic ожидает в CarSpecificationsResponseDTO
    mock_specs = CarSpecifications(
        car_id=101,
        name="Tesla Model 3",
        mileage=100,
        power=450,
        overclocking=3.3,
        consump_in_city=0.0,
        transmission="AUTOMATIC",  # Передаем строку или .value от Enum
        actuator="AWD",
        wheel="LEFT",
        color="Black"
    )

    # 2. Создаем реальный объект машины
    mock_car = Car(
        car_id=101,
        license_plate="Р213ОА197",
        vin="TESTVIN1234567890",
        daily_rate=3000.0,
        status="AVAILABLE",
        change_at=datetime.now(),
        car_specifications=mock_specs  # Привязываем характеристики
    )

    # 3. Настраиваем мок репозитория
    car_service.car_repo.find_by_filters.return_value = [mock_car]

    filter_dto = CarFilterDTO(status="AVAILABLE")

    # 4. Вызов метода
    result = car_service.get_cars_by_filter(filter_dto)

    # 5. Проверки
    assert len(result) == 1
    # Если метод возвращает список DTO
    assert result[0]['car']['license_plate'] == "Р213ОА197"
    assert result[0]['specifications']['name'] == "Tesla Model 3"
