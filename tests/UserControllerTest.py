from main import app  # Импорт вашего FastAPI приложения
from service import get_user_service, get_current_user
from ClientOverride import override_get_current_user

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone

mock_user_service = MagicMock()


@pytest.fixture
def client():
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    mock_user_service.reset_mock()


def test_get_user_by_id_success(client):
    user_id = 1
    email = "test@test.com"
    mock_user_service.get_user_by_id.return_value = dict(
        user_id=user_id,
        email=email,
        name="Иван",
        position="MANAGER",
        created_at=datetime.now(timezone.utc)
    )

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == email
    mock_user_service.get_user_by_id.assert_called_once_with(1)


def test_get_user_by_id_not_found(client):
    user_id = 99
    error_text = f"Сотрудник с ID {user_id} не найден"
    mock_user_service.get_user_by_id.side_effect = ValueError(error_text)

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == error_text


def test_user_exist(client):
    mock_user_service.exists.return_value = True

    response = client.get("/users/1/exist")

    assert response.status_code == 200
    assert response.json() is True
    mock_user_service.exists.assert_called_once_with(1)


def test_users_count(client):
    count = 10
    mock_user_service.count_all.return_value = count

    response = client.get("/users/count")

    assert response.status_code == 200
    assert response.json() == dict(count=count)


def test_create_user_success(client):
    user_data = {
        "email": "new@test.com",
        "password": "strongpassword",
        "name": "Петр",
        "position": "AGENT"
    }

    mock_user_service.create_user.return_value = {
        "user_id": 2,
        "email": "new@test.com",
        "name": "Петр",
        "position": "AGENT",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    assert response.json()["user_id"] == 2
    mock_user_service.create_user.assert_called_once()


def test_create_user_email_taken(client):
    email = "taken@test.com"
    error_text = f"Email {email} уже используется"
    mock_user_service.create_user.side_effect = ValueError(error_text)

    user_data = {
        "email": email,
        "password": "123",
        "name": "Имя",
        "position": "AGENT"
    }
    response = client.post("/users/", json=user_data)

    assert response.status_code == 400
    assert error_text in response.json()["detail"]


def test_update_user_success(client):
    update_data = {"user_id": 1, "name": "Новое Имя"}
    mock_user_service.update_user.return_value = {
        "user_id": 1,
        "email": "test@test.com",
        "name": "Новое Имя",
        "position": "MANAGER",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    response = client.put("/users/", json=update_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Новое Имя"


def test_delete_user_success(client):
    mock_user_service.delete_user.return_value = True

    response = client.delete("/users/1")

    assert response.status_code == 200
    assert response.json() is True

