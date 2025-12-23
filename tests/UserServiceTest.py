from service import UserService
from dto import UserCreateDTO, UserResponseDTO, UserUpdateDTO
from entity import User

import pytest
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def user_service(mock_repo):
    # Создаем сервис, подменяя репозиторий на мок
    session = MagicMock()
    service = UserService(session)
    service.user_repo = mock_repo
    return service


def test_create_user_success(user_service, mock_repo):
    # Данные
    user_dto = UserCreateDTO(
        email="test@example.com",
        password="secure_password",
        name="  Иван Иванов  ",  # Проверим strip()
        position="AGENT"
    )

    # Настройка мока: email свободен
    mock_repo.email_exists.return_value = False

    # Имитируем возврат созданного пользователя из БД
    mock_created_user = User(
        user_id=1,
        email=user_dto.email,
        password=bytes("Заглушка", "utf-8"),
        name="Иван Иванов",
        position=user_dto.position,
        created_at=datetime.now()
    )
    mock_repo.create.return_value = mock_created_user

    # Вызов метода
    result = user_service.create_user(user_dto)

    # Проверки
    assert result["email"] == mock_created_user.email
    assert result["name"] == mock_created_user.name.strip()  # Проверка, что strip() сработал
    mock_repo.email_exists.assert_called_once_with(user_dto.email)
    mock_repo.create.assert_called_once()


def test_create_user_email_exists(user_service, mock_repo):
    email = "exists@example.com"
    user_dto = UserCreateDTO(
        email=email,
        password="123",
        name="Имя",
        position="Должность"
    )

    # Настройка мока: email занят
    mock_repo.email_exists.return_value = True

    # Проверка исключения
    with pytest.raises(ValueError, match=f"Email {email} уже используется"):
        user_service.create_user(user_dto)


def test_get_user_by_id_success(user_service, mock_repo):
    # Настройка мока
    user_id = 10
    mock_user = User(
        user_id=user_id,
        email="user@test.com",
        name="Тест",
        position="AGENT",
        password=bytes("Заглушка", "utf-8"),
        created_at=datetime.now()
    )
    mock_repo.get_by_user_id.return_value = UserResponseDTO.model_validate(mock_user)

    result = user_service.get_user_by_id(user_id)

    assert isinstance(result, UserResponseDTO)
    assert result.user_id == user_id
    mock_repo.get_by_user_id.assert_called_with(user_id)


def test_get_user_by_id_not_found(user_service, mock_repo):
    # Репозиторий возвращает None
    user_id = 999
    mock_repo.get_by_user_id.return_value = None

    with pytest.raises(ValueError, match=f"Сотрудник с ID {user_id} не найден"):
        user_service.get_user_by_id(999)


def test_update_user(user_service, mock_repo):
    new_name = "Новое Имя"
    update_dto = UserUpdateDTO(user_id=1, name=new_name)

    # Мокаем возвращаемый объект после обновления
    updated_entity = User(
        user_id=1,
        email="test@test.com",
        password=bytes(1),
        name=new_name,
        position="ADMIN",
        created_at=datetime.now()
    )
    mock_repo.update.return_value = updated_entity

    result = user_service.update_user(update_dto)

    assert result.name == new_name
    mock_repo.update.assert_called_once_with(update_dto)


def test_delete_user(user_service, mock_repo):
    mock_repo.delete.return_value = True

    result = user_service.delete_user(1)

    assert result is True
    mock_repo.delete.assert_called_once_with(1)


def test_count_all(user_service, mock_repo):
    mock_repo.count_all.return_value = 42

    assert user_service.count_all() == 42
    mock_repo.count_all.assert_called_once()
