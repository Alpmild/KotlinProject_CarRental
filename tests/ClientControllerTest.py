from main import app
from ClientOverride import override_get_current_user
from config import SessionLocal
from service import get_current_user, get_client_service, ClientService
from dto import ClientCreateDTO, ClientUpdateDTO

import pytest
from fastapi.testclient import TestClient

test_client_create = ClientCreateDTO(
    name="Иван Иванов",
    phone="89990001122",
    telegram_id="@vanya",
    license_number="ГИБДД 9999"
)


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def client(db_session):
    # Устанавливаем переопределения зависимостей
    real_service = ClientService(db_session)
    app.dependency_overrides[get_client_service] = lambda: real_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_create_client_success(client):
    response = client.post("/clients/", json=test_client_create.model_dump(mode='json'))
    assert response.status_code == 201
    client.delete(f"/clients/{response.json()['client_id']}")


def test_create_client_duplicate_phone_error(client):
    res1 = client.post("/clients/", json=test_client_create.model_dump(mode='json'))

    response = client.post("/clients/", json=test_client_create.model_dump(mode='json'))
    assert response.status_code == 400
    assert "уже есть в базе" in response.json()["detail"]
    client.delete(f"/clients/{res1.json()['client_id']}")


def test_get_client_by_id_success(client):
    create_resp = client.post("/clients/", json=test_client_create.model_dump(mode='json'))
    client_id = create_resp.json()["client_id"]

    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    client.delete(f"/clients/{response.json()['client_id']}")



def test_get_client_not_found(client):
    response = client.get("/clients/9999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_update_client_success(client):
    # Создаем
    create_resp = client.post("/clients/", json=test_client_create.model_dump(mode='json'))
    client_id = create_resp.json()["client_id"]

    # Обновляем
    update_dto = ClientUpdateDTO(
        client_id=client_id,
        name="Новый",
        telegram_id="@new_tg"
    )
    response = client.put("/clients/", json=update_dto.model_dump(mode='json'))

    assert response.status_code == 200
    assert response.json()["name"] == "Новый"
    assert response.json()["telegram_id"] == "@new_tg"
    client.delete(f"/clients/{client_id}")


def test_delete_client_success(client):
    # Создаем
    create_resp = client.post("/clients/", json=test_client_create.model_dump(mode='json'))
    client_id = create_resp.json()["client_id"]

    del_response = client.delete(f"/clients/{client_id}")
    assert del_response.status_code == 200

    check_response = client.get(f"/clients/{client_id}")
    assert check_response.status_code == 404
