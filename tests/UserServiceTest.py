from service import get_user_service
from config import SessionLocal
from dto import UserCreateDTO, UserUpdateDTO, UserPositionEnum

import pytest


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def user_service(db_session):
    return get_user_service(db_session)


def test_create_user_success(user_service):
    dto = UserCreateDTO(
        email="test@example.com",
        password="securepassword123",
        name="  Иван Иванов ",
        position="Manager"
    )
    result = user_service.create_user(dto)

    assert result.email == "test@example.com"
    assert result.name == "Иван Иванов"
    assert "password" not in result
    user_service.delete_user(result.user_id)


def test_create_user_duplicate_email_raises_error(user_service):
    email = "duplicate@test.com"
    dto = UserCreateDTO(
        email="duplicate@test.com",
        password="password",
        name="User1",
        position="agent"
    )
    res = user_service.create_user(dto)

    with pytest.raises(ValueError, match=f"Email {email} уже используется"):
        user_service.create_user(dto)
    user_service.delete_user(res.user_id)


def test_get_user_by_id_success(user_service):
    # Создаем пользователя
    dto = UserCreateDTO(email="find@me.com", password="123", name="Find", position="AGENT")
    created = user_service.create_user(dto)
    user_id = created.user_id

    # Получаем
    user = user_service.get_user_by_id(user_id)
    assert user.email == "find@me.com"
    assert user.user_id == user_id
    user_service.delete_user(user_id)


def test_get_user_by_id_not_found(user_service):
    with pytest.raises(ValueError, match="Сотрудник с ID 999 не найден"):
        user_service.get_user_by_id(999)


def test_update_user(user_service):
    # Создаем
    created = user_service.create_user(
        UserCreateDTO(email="old@test.com", password="123", name="Old", position="MANAGER")
    )
    user_id = created.user_id

    update_dto = UserUpdateDTO(
        user_id=user_id,
        email="new@test.com",
        name="New Name",
    )
    updated = user_service.update_user(update_dto)

    assert updated.name == "New Name"
    user_service.delete_user(user_id)


def test_delete_user(user_service):
    created = user_service.create_user(
        UserCreateDTO(email="del@test.com", password="khfhdghg", name="Del", position="AGENT")
    )
    user_id = created.user_id

    res = user_service.delete_user(user_id)
    assert res is True
    assert user_service.exists(user_id) is False


def test_count_all(user_service):
    res = []
    for i in range(3):
        res.append(user_service.create_user(
            UserCreateDTO(email=f"user{i}@test.com", password="1fsdf", name="Npjosdf", position=UserPositionEnum.AGENT)
        ))

    assert user_service.count_all() == 5
    for i in res:
        user_service.delete_user(i.user_id)
