from service import ClientService
from dto import ClientCreateDTO, ClientResponseDTO, ClientFilterDTO
from entity import Client

import pytest
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def client_service():
    # Создаем мок сессии, сам репозиторий подменим внутри
    mock_db = MagicMock()
    service = ClientService(db_session=mock_db)
    service.client_repo = MagicMock()
    return service


def test_create_client_success(client_service):
    """Тест успешного создания клиента"""
    client_dto = ClientCreateDTO(
        name="Иван Иванов",
        phone="89991234567",
        telegram_id="@ivan_tg",
        license_number="ГИБДД 4123"
    )

    # Настраиваем моки репозитория
    client_service.client_repo.phone_exists.return_value = False
    client_service.client_repo.telegram_exists.return_value = False

    # Имитируем возврат из БД (с ID и датой)
    mock_created_client = Client(
        client_id=1,
        name=client_dto.name,
        phone=client_dto.phone,
        telegram_id=client_dto.telegram_id,
        license_number=client_dto.license_number,
        created_at=datetime.now()  # Важно для валидации в DTO
    )
    client_service.client_repo.create.return_value = mock_created_client

    result = client_service.create_client(client_dto)

    assert isinstance(result, ClientResponseDTO)
    assert result.client_id == 1
    assert result.phone == "89991234567"
    client_service.client_repo.create.assert_called_once()


def test_create_client_duplicate_phone(client_service):
    """Тест ошибки при дубликате телефона"""

    phone = "89003309191"
    client_dto = ClientCreateDTO(name="Тест", phone=phone, license_number="ГИБДД 9999", telegram_id="@uniqtg")
    client_service.client_repo.phone_exists.return_value = True

    with pytest.raises(ValueError) as exc:
        client_service.create_client(client_dto)

    assert f"Номер {phone} уже есть в базе" in str(exc.value)


def test_get_client_by_id_success(client_service):
    """Тест получения клиента по ID"""
    mock_client = Client(
        client_id=5,
        name="Петр",
        phone="555",
        change_at=datetime.now()
    )
    client_service.client_repo.get_by_id.return_value = mock_client

    result = client_service.get_client_by_id(5)

    assert result.name == "Петр"
    assert result.client_id == 5


def test_get_client_by_id_not_found(client_service):
    """Тест ошибки, если клиент не найден"""
    client_service.client_repo.get_by_id.return_value = None
    client_id = 99

    with pytest.raises(ValueError) as exc:
        client_service.get_client_by_id(client_id)

    assert f"Клиент с ID {client_id} не найден" in str(exc.value)


def test_get_clients_by_filter(client_service):
    """Тест фильтрации клиентов"""
    mock_client = Client(
        client_id=10,
        name="Мария",
        phone="89238713221",
        telegram_id="@maria_tg",
        license_number="ГИБДД 1337",
        created_at=datetime.now()
    )
    client_service.client_repo.find_by_filters.return_value = [mock_client]

    filter_dto = ClientFilterDTO(name="ари", phone="7132")
    result = client_service.get_clients_by_filter(filter_dto)

    assert len(result) == 1
    assert isinstance(result[0], ClientResponseDTO)
    assert result[0].name == mock_client.name
