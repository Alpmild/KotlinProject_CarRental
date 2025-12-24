from config import SessionLocal
from dto import UserCreateDTO, UserPositionEnum, UserUpdateDTO
from main import app  # Импорт вашего FastAPI приложения
from service import get_user_service, get_current_user, UserService
from ClientOverride import override_get_current_user

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone

test_user_create = UserCreateDTO(
    email="agent@test.com",
    password="secret_password",
    name="Алексей",
    position="AGENT"
)


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def client(db_session):
    # Устанавливаем переопределения зависимостей
    real_service = UserService(db_session)
    app.dependency_overrides[get_user_service] = lambda: real_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_create_user_success(client):
    response = client.post("/users/", json=test_user_create.model_dump(mode='json'))
    assert response.status_code == 201
    client.delete(f"/users/{response.json()['user_id']}")


def test_create_user_duplicate_email(client):
    user_data = test_user_create.model_dump(mode='json')
    res1 = client.post("/users/", json=user_data)
    response = client.post("/users/", json=user_data)

    assert response.status_code == 400
    assert "уже используется" in response.json()["detail"]
    client.delete(f"/users/{res1.json()['user_id']}")


def test_get_user_by_id(client):
    # Создаем
    create_resp = client.post("/users/", json={
        "email": "find@test.com", "password": "123", "name": "FindMe", "position": UserPositionEnum.AGENT.value
    })
    user_id = create_resp.json()["user_id"]

    # Получаем
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "find@test.com"
    client.delete(f"/users/{user_id}")


def test_user_exists_endpoint(client):
    create_resp = client.post("/users/", json={
        "email": "exists@test.com", "password": "123", "name": "Ex", "position": "Ex"
    })
    user_id = create_resp.json()["user_id"]

    response = client.get(f"/users/{user_id}/exist")
    assert response.status_code == 200
    assert response.json() is True


def test_users_count(client):
    # В базе уже есть 2 пользователя
    res1 = client.post("/users/", json={"email": "u1@tc.com", "password": "eqw1",
                                        "name": "Иван", "position": UserPositionEnum.AGENT.value})
    res2 = client.post("/users/", json={"email": "u2@tc.com", "password": "1qwe",
                                        "name": "Алексей", "position": UserPositionEnum.AGENT.value})

    response = client.get("/users/count")
    assert response.status_code == 200
    assert response.json()["count"] == 4

    client.delete(f"/users/{res1.json()['user_id']}")
    client.delete(f"/users/{res2.json()['user_id']}")


def test_update_user(client):
    # Создаем
    create_resp = client.post("/users/", json={
        "email": "old@tdsa.com", "password": "123", "name": "Old", "position": UserPositionEnum.AGENT.value
    })
    user_id = create_resp.json()["user_id"]

    # Обновляем
    update_data = UserUpdateDTO(
        user_id=user_id,
        email="new@test.com",
    )
    response = client.put("/users/", json=update_data.model_dump(mode='json'))

    assert response.status_code == 200
    assert response.json()["email"] == "new@test.com"
    client.delete(f"/users/{user_id}")


def test_delete_user_success(client):
    create_resp = client.post("/users/", json={
        "email": "del@t.com", "password": "123", "name": "Del", "position": UserPositionEnum.AGENT.value
    })
    user_id = create_resp.json()["user_id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200

    # Проверка удаления
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404
