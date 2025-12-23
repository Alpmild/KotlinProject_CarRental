from pprint import pprint
from typing import Optional

from ClientOverride import override_get_current_user
from dto import RentalWithRelationsDTO, RentalStatusEnum
from main import app
from service import get_rental_service, get_current_user

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

# Мок сервиса
mock_rental_service = MagicMock()

@pytest.fixture
def client():
    app.dependency_overrides[get_rental_service] = lambda: mock_rental_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    mock_rental_service.reset_mock()

# Вспомогательная функция для создания мок-ответа RentalWithRelationsDTO
def get_mock_rental_relation(
        rent_id: int,
):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "rental": {
            "rent_id": rent_id, "car_id": 1, "client_id": 1, "user_id": 1,
            "start_date": now, "end_date": now, "status": RentalStatusEnum.ACTIVE,
            "actual_return_date": now, "total_cost": 1000, "notes": None,
            "created_at": now
        },
        "car": None,
        "client": None,
        "user": None
    }


def test_create_rental_success(client):
    rent_id = 10
    now = datetime.now(timezone.utc)

    rental_data = {
        "car_id": 1,
        "client_id": 1,
        "user_id": 1,
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=2)).isoformat(),
        "status": RentalStatusEnum.AWAITING.value,
        "actual_return_date": now.isoformat(), "total_cost": None, "notes": None
    }

    mock_rental_service.create_rental.return_value = get_mock_rental_relation(rent_id=rent_id)

    response = client.post("/rentals/", json=rental_data)
    assert response.status_code == 201
    assert response.json()["rental"]["rent_id"] == rent_id
    mock_rental_service.create_rental.assert_called_once()


def test_extend_rental_success(client):
    rent_id = 5
    new_date = "2025-12-31T23:59:59Z"
    mock_rental_service.extend_rental.return_value = get_mock_rental_relation(rent_id)

    # Передача даты через Query-параметр (как ожидает FastAPI для datetime в GET/PUT)
    response = client.put(f"/rentals/extend/{rent_id}?new_end_date={new_date}")

    assert response.status_code == 200
    assert response.json()["rental"]["rent_id"] == rent_id
    mock_rental_service.extend_rental.assert_called_once()


def test_complete_rental_success(client):
    rent_id = 1
    return_date = datetime.now().isoformat()
    mock_rental_service.complete_rental.return_value = get_mock_rental_relation(rent_id)

    response = client.put(f"/rentals/complete/{rent_id}?actual_return_date={return_date}")

    assert response.status_code == 200
    mock_rental_service.complete_rental.assert_called_once()


def test_cancel_rental_success(client):
    rent_id = 1
    mock_rental_service.cancel_rental.return_value = get_mock_rental_relation(rent_id)

    response = client.put(f"/rentals/cancel/{rent_id}")

    assert response.status_code == 200
    mock_rental_service.cancel_rental.assert_called_once_with(rent_id)


def test_get_rentals_by_filter(client):
    rent_id = 1
    mock_rental_service.get_rentals_by_filter.return_value = [get_mock_rental_relation(rent_id)]

    # Фильтры передаются в URL
    response = client.get("/rentals/filter?car_id=1&status=ACTIVE")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_rental_service.get_rentals_by_filter.assert_called_once()


def test_delete_rental_not_found(client):
    mock_rental_service.delete_rental.return_value = False

    response = client.delete("/rentals/999")

    assert response.status_code == 404
    assert "999" in response.json()["detail"]
