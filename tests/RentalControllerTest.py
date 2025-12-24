from ClientOverride import override_get_current_user
from config import SessionLocal
from dto import RentalWithRelationsDTO, RentalStatusEnum, RentalCreateDTO
from main import app
from service import get_rental_service, get_current_user, RentalService

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

start = (datetime.now(timezone.utc) + timedelta(days=120)).replace(microsecond=0)
test_rental_create = RentalCreateDTO(
    car_id=26,
    client_id=6,
    user_id=2,
    start_date = start,
    end_date = start + timedelta(days=10),
    status=RentalStatusEnum.AWAITING
)

@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def client(db_session):
    real_service = RentalService(db_session)
    app.dependency_overrides[get_rental_service] = lambda: real_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_create_rental_success(client):
    # Дата старта + 1 час (чтобы пройти валидацию FutureDate)
    response = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))
    assert response.status_code == 201
    client.delete(f"/rentals/{response.json()['rental']['rent_id']}")


def test_create_rental_conflict(client):
    # Создаем первую аренду на те же даты
    res1 = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))
    # Вторая попытка на то же авто
    response = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))

    assert response.status_code == 400
    assert "не доступен" in response.json()["detail"]
    client.delete(f"/rentals/{res1.json()['rental']['rent_id']}")


def test_extend_rental(client):
    # 1. Создаем
    resp = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))
    rent_id = resp.json()["rental"]["rent_id"]

    # 2. Продлеваем
    new_end = (test_rental_create.end_date + timedelta(days=5))
    response = client.put(f"/rentals/extend/{rent_id}", params={"new_end_date": new_end.isoformat()})

    assert response.status_code == 200
    client.delete(f"/rentals/{rent_id}")


def test_cancel_rental(client):
    # Создаем
    resp = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))
    rent_id = resp.json()["rental"]["rent_id"]

    response = client.put(f"/rentals/cancel/{rent_id}")
    assert response.status_code == 200
    assert response.json()["rental"]["status"] == "CANCELLED"


def test_delete_rental_success(client):
    # Создаем
    resp = client.post("/rentals/", json=test_rental_create.model_dump(mode="json"))
    rent_id = resp.json()["rental"]["rent_id"]

    # Удаляем
    del_resp = client.delete(f"/rentals/{rent_id}")
    assert del_resp.status_code == 200


    check_resp = client.put(f"/rentals/cancel/{rent_id}")
    assert check_resp.json()['rental'] is None

