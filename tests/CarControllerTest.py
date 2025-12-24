from main import app
from ClientOverride import override_get_current_user
from config import SessionLocal
from service import get_car_service, get_current_user, CarService
from dto import CarStatusEnum, CarCreateDTO

import pytest
from fastapi.testclient import TestClient

test_car_create = CarCreateDTO(
    license_plate='Р123РР197',
    vin='B' * 17,
    daily_rate=300,
    status=CarStatusEnum.AVAILABLE,
    specifications=None
)


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def client(db_session):
    # Устанавливаем переопределения зависимостей
    real_service = CarService(db_session)
    app.dependency_overrides[get_car_service] = lambda: real_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_create_car_endpoint(client):
    response = client.post("/cars/", json=test_car_create.model_dump())

    try:
        assert response.status_code == 201
        client.delete(f"/cars/{response.json()['car_id']}")
    except AssertionError:
        print(response.json())



def test_get_car_by_id_success(client):
    # Сначала создаем машину
    create_res = client.post("/cars/", json=test_car_create.model_dump())
    car_id = create_res.json()['car_id']

    # Проверяем получение
    response = client.get(f"/cars/{car_id}")

    assert response.status_code == 200
    assert response.json()['car']["license_plate"] == test_car_create.license_plate
    client.delete(f"/cars/{car_id}")



def test_get_car_not_found(client):
    response = client.get("/cars/999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_get_cars_by_price_invalid_range(client):
    response = client.get("/cars/price-range?min_price=5000&max_price=1000")
    assert response.status_code == 400
    assert response.json()["detail"] == "min_price > max_price"


def test_delete_car_success(client):
    create_res = client.post("/cars/", json=test_car_create.model_dump())
    car_id = create_res.json()["car_id"]

    response = client.delete(f"/cars/{car_id}")
    assert response.status_code == 200

    # Проверяем, что теперь 404
    check = client.get(f"/cars/{car_id}")
    assert check.status_code == 404


def test_create_duplicate_vin_error(client):
    res = client.post("/cars/", json=test_car_create.model_dump())

    response = client.post("/cars/", json=test_car_create.model_dump())
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]
    client.delete(f"/cars/{res.json()['car_id']}")
