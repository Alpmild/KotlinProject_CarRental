from ClientOverride import override_get_current_user
from main import app
from service import get_car_service, get_current_user
from dto import CarWithSpecsResponseDTO, CarResponseDTO, CarStatusEnum, TransmissionEnum, ActuatorEnum, WheelEnum, \
    CarSpecificationsResponseDTO

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone

# Создаем мок для сервиса
mock_car_service = MagicMock()
test_car_with_specs_response = CarWithSpecsResponseDTO(
    car=CarResponseDTO(
        car_id=1,
        license_plate='A111AA197',
        vin='W' * 17,
        daily_rate=300,
        status=CarStatusEnum.AVAILABLE,
        change_at=datetime.now(timezone.utc),
    ),
    specifications=CarSpecificationsResponseDTO(
        car_id=1,
        name='Nissan Silvia S15',
        mileage=3000,
        power=200,
        overclocking=3.1,
        consump_in_city=12.1,
        transmission=TransmissionEnum.MANUAL,
        actuator=ActuatorEnum.FRONT,
        wheel=WheelEnum.LEFT,
        color='белый'
    )
)

test_car_create = dict(
    license_plate='Р123РР197',
    vin='B' * 17,
    daily_rate=300,
    status=CarStatusEnum.AVAILABLE.value,
    specifications=None
)


@pytest.fixture
def client():
    # Устанавливаем переопределения зависимостей
    app.dependency_overrides[get_car_service] = lambda: mock_car_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# --- ТЕСТЫ ---

def test_get_car_by_id_success(client):
    # Настраиваем мок
    mock_car_service.get_car_by_id.return_value = test_car_with_specs_response.model_dump()
    car_id = test_car_with_specs_response.car.car_id

    response = client.get(f"/cars/{car_id}")

    assert response.status_code == 200
    assert response.json()['specifications']['name'] == test_car_with_specs_response.specifications.name
    mock_car_service.get_car_by_id.assert_called_once_with(1)


def test_get_car_by_id_not_found(client):
    # Имитируем ошибку из сервиса
    car_id = 999
    error_text = f"Автомобиль с ID {car_id} не найден"
    mock_car_service.get_car_by_id.side_effect = ValueError(error_text)

    response = client.get(f"/cars/{car_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == error_text


def test_create_car_success(client):
    car_id = 12
    mock_car_service.create_car.return_value = dict(
        car_id=car_id,
        license_plate=test_car_create['license_plate'],
        vin=test_car_create['vin'],
        daily_rate=test_car_create['daily_rate'],
        status=test_car_create['status'],
        change_at=datetime.now(timezone.utc)
    )

    response = client.post("/cars/", json=test_car_create)

    assert response.status_code == 201
    assert response.json()["car_id"] == car_id
    mock_car_service.create_car.assert_called_once()


def test_get_cars_by_price_range_invalid(client):
    # Проверка бизнес-логики контроллера: min > max
    response = client.get("/cars/price-range?min_price=5000&max_price=1000")

    assert response.status_code == 400
    assert response.json()["detail"] == "min_price > max_price"


def test_delete_car_success(client):
    mock_car_service.delete_car.return_value = True

    response = client.delete("/cars/1")

    assert response.status_code == 200
    assert response.json() is True


def test_delete_car_not_found(client):
    mock_car_service.delete_car.return_value = False

    response = client.delete("/cars/999")

    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_get_cars_by_filter(client):
    # Параметры фильтра передаются как Query-params благодаря Depends()
    mock_car_service.get_cars_by_filter.return_value = []

    response = client.get("/cars/filter?vin=WWWW&model=BMW")

    assert response.status_code == 200
    mock_car_service.get_cars_by_filter.assert_called_once()
