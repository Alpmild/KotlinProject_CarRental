from service import get_rental_service
from dto import RentalCreateDTO, RentalUpdateDTO, RentalStatusEnum
from config import SessionLocal

import pytest
from datetime import datetime, timedelta, timezone


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def rental_service(db_session):
    return get_rental_service(db_session)


def test_create_rental_success(rental_service):
    start = datetime.now(timezone.utc) + timedelta(days=10)
    end = start + timedelta(days=12)

    dto = RentalCreateDTO(
        car_id=26,
        client_id=6,
        user_id=2,
        start_date=start,
        end_date=end,
        notes="First rental"
    )

    result = rental_service.create_rental(dto)

    assert result.rental.car_id == dto.car_id
    assert result.rental.status == RentalStatusEnum.AWAITING
    rental_service.delete_rental(result.rental.rent_id)


def test_create_rental_car_not_available(rental_service):
    """
    В файле config/test_data.py мы уже ранее создавали аренду,
    которая будет пересекаться с той, которую мы хотим создать.
    """

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(days=3)

    dto = RentalCreateDTO(
        car_id=26,
        client_id=6,
        user_id=2,
        start_date=start,
        end_date=end
    )

    with pytest.raises(ValueError) as error:
        rental_service.create_rental(dto)


def test_create_rental_invalid_client(rental_service):
    dto = RentalCreateDTO(
        car_id=26,
        client_id=999,  # Несуществующий ID
        user_id=2,
        start_date=datetime.now(timezone.utc) + timedelta(days=2),
        end_date=datetime.now(timezone.utc) + timedelta(days=3)
    )
    with pytest.raises(ValueError, match="client_id=999 не существует"):
        rental_service.create_rental(dto)


def test_extend_rental(rental_service):
    start = datetime.now(timezone.utc) + timedelta(days=80)
    old_end = start + timedelta(days=90)
    new_end = (start + timedelta(days=100)).replace(microsecond=0)

    rental_dto = RentalCreateDTO(
        car_id=27,
        client_id=7,
        user_id=2,
        start_date=start,
        end_date=old_end
    )
    created = rental_service.create_rental(rental_dto)
    extended = rental_service.extend_rental(created.rental.rent_id, new_end)

    ext_date = extended.rental.end_date.replace(microsecond=0, tzinfo=timezone.utc)
    assert ext_date == new_end

    rental_service.delete_rental(created.rental.rent_id)


def test_get_rent_by_id_not_found(rental_service):
    with pytest.raises(ValueError, match="не существует"):
        rental_service.get_rent_by_id(888)

