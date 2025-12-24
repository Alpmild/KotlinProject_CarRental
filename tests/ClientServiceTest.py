from service import get_client_service
from config import SessionLocal
from dto import ClientCreateDTO, ClientUpdateDTO, ClientFilterDTO

import pytest


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def client_service(db_session):
    return get_client_service(db_session)


def test_create_client_success(client_service):
    dto = ClientCreateDTO(
        name="Димон Димонович",
        phone="89991234567",
        telegram_id="@test_tg",
        license_number="ГИБДД 1298"
    )
    result = client_service.create_client(dto)

    assert result.client_id is not None
    assert result.name == "Димон Димонович"
    assert result.phone == "89991234567"
    client_service.delete_client(result.client_id)


def test_create_client_duplicate_phone_raises_error(client_service):
    dto = ClientCreateDTO(
        name="Клон",
        phone="89003123412",  # Номер уже есть в базе
        telegram_id="@clone1",
        license_number="ГИБДД 0000"
    )

    # Повторная попытка с тем же номером
    with pytest.raises(ValueError, match=f'Номер {dto.phone} уже есть в базе.'):
        client_service.create_client(dto)


def test_get_client_by_id_success(client_service):
    dto = ClientCreateDTO(name="Петр", phone="89003309191", telegram_id="@petr", license_number="ГИБДД 7312")
    created = client_service.create_client(dto)

    found = client_service.get_client_by_id(created.client_id)
    assert found.name == "Петр"
    assert found.client_id == created.client_id
    client_service.delete_client(created.client_id)


def test_get_client_by_id_not_found(client_service):
    with pytest.raises(ValueError, match="Клиент с ID 999 не найден"):
        client_service.get_client_by_id(999)


def test_update_client(client_service):
    initial = client_service.create_client(
        ClientCreateDTO(name="Старое Имя", phone="89004401111", telegram_id="@old", license_number="8800")
    )
    updated = client_service.update_client(
        ClientUpdateDTO(
            client_id=initial.client_id,
            name="Новое Имя",  # Оставляем тот же или меняем
            telegram_id="@new_tg",
        )
    )

    assert initial.client_id == updated.client_id
    assert updated.name == "Новое Имя"
    assert updated.telegram_id == "@new_tg"
    client_service.delete_client(initial.client_id)


def test_delete_client(client_service):
    # Создаем
    client = client_service.create_client(
        ClientCreateDTO(name="Удаляемый", phone="89998887766", telegram_id="@del", license_number="9999")
    )

    # Удаляем
    delete_res = client_service.delete_client(client.client_id)
    assert delete_res is True

    # Проверяем, что больше не находится
    with pytest.raises(ValueError):
        client_service.get_client_by_id(client.client_id)


def test_get_clients_by_filter(client_service):
    res = [
        client_service.create_client(
            ClientCreateDTO(name="Алексей", phone="89998881122", telegram_id="@1", license_number="1111")),
        client_service.create_client(
            ClientCreateDTO(name="Александр", phone="89998881123", telegram_id="@2", license_number="2111")),
        client_service.create_client(
            ClientCreateDTO(name="Борис", phone="89998881124", telegram_id="@3", license_number="3111"))
    ]

    filter_dto = ClientFilterDTO(name="Алекс")
    results = client_service.get_clients_by_filter(filter_dto)

    assert len(results) == 2
    for r in res:
        client_service.delete_client(r.client_id)


def test_get_by_name(client_service):
    name = 'Бутусов Денис Николаевич'
    results = client_service.get_by_name(name)
    assert len(results) == 1
    assert results[0].name == name

