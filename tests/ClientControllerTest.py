from main import app
from service import get_client_service, get_current_user
from ClientOverride import override_get_current_user

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone

mock_client_service = MagicMock()


@pytest.fixture
def client():
    # Устанавливаем переопределения
    app.dependency_overrides[get_client_service] = lambda: mock_client_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    # Сбрасываем переопределения после каждого теста
    app.dependency_overrides.clear()


def test_get_client_by_id_success(client):
    # Настраиваем мок
    client_id = 1
    name = "Иван Иванов"
    mock_client_service.get_client_by_id.return_value = dict(
        client_id=client_id,
        name=name,
        phone="89991234567",
        telegram_id="@ivan",
        license_number="ГИБДД 1234",
        change_at=datetime.now(timezone.utc)
    )

    response = client.get(f"/clients/{client_id}")

    assert response.status_code == 200
    assert response.json()["name"] == name
    mock_client_service.get_client_by_id.assert_called_once_with(1)


def test_get_client_by_id_not_found(client):
    # Имитируем ошибку в сервисе
    client_id = 999
    error_text = f"Клиент с ID {client_id} не найден"
    mock_client_service.get_client_by_id.side_effect = ValueError(error_text)

    response = client.get("/clients/999")

    assert response.status_code == 404
    assert response.json()["detail"] == error_text


def test_create_client_success(client):
    client_id = 10
    client_data = {
        "name": "Петр Петров",
        "phone": "89001112233",
        "telegram_id": "@petr",
        "license_number": "ГИБДД 5566"
    }

    # Настраиваем возврат мока (объект или словарь)
    mock_client_service.create_client.return_value = dict(
        client_id=client_id,
        **client_data,
        created_at=datetime.now(timezone.utc)
    )

    response = client.post("/clients/", json=client_data)

    assert response.status_code == 201
    assert response.json()["client_id"] == client_id
    mock_client_service.create_client.assert_called_once()


def test_create_client_duplicate_error(client):
    # Если телефон уже существует, сервис кидает ValueError
    phone = "89001112233"
    error_text = f'Номер {phone} уже есть в базе.'
    mock_client_service.create_client.side_effect = ValueError(error_text)

    client_data = {
        "name": "Дубликат",
        "phone": phone,
        "telegram_id": "@tg",
        "license_number": "ГИБДД 1111"
    }

    response = client.post("/clients/", json=client_data)

    assert response.status_code == 400
    assert error_text in response.json()["detail"]


def test_get_client_by_filter(client):
    mock_client_service.get_clients_by_filter.return_value = []

    # Параметры фильтра передаются как Query-params благодаря Depends() в контроллере
    response = client.get("/clients/filter?name=Иван&phone=8999")

    assert response.status_code == 200
    mock_client_service.get_clients_by_filter.assert_called_once()


def test_delete_client_success(client):
    mock_client_service.delete_client.return_value = True

    response = client.delete("/clients/1")

    assert response.status_code == 200
    assert response.json() is True


def test_delete_client_not_found(client):
    client_id = "999"
    mock_client_service.delete_client.return_value = False

    response = client.delete(f"/clients/{client_id}")

    assert response.status_code == 404
    assert client_id in response.json()["detail"]
