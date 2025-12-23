import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from service import RentalService
from dto import (RentalCreateDTO, RentalUpdateDTO, RentalResponseDTO,
                 RentalWithRelationsDTO, RentalStatusEnum)
from entity import Rental


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def rental_service(mock_session):
    service = RentalService(mock_session)
    # Заменяем все репозитории и сервисы на моки
    service.rental_repo = MagicMock()
    service.car_repo = MagicMock()
    service.client_repo = MagicMock()
    service.user_repo = MagicMock()

    service.car_service = MagicMock()
    service.client_service = MagicMock()
    service.user_service = MagicMock()
    return service


def test_create_rental_success(rental_service):
    # Данные
    now = datetime.now(timezone.utc)
    start = now + timedelta(days=1)
    end = start + timedelta(days=2)
    dto = RentalCreateDTO(
        car_id=1, client_id=1, user_id=1,
        start_date=start, end_date=end, status=RentalStatusEnum.AWAITING
    )

    # Настройка моков (проверки существования)
    rental_service.client_repo.exists.return_value = True
    rental_service.car_repo.exists.return_value = True
    rental_service.user_repo.exists.return_value = True
    rental_service.rental_repo.is_car_available.return_value = True

    # Имитация создания
    mock_rental = Rental(
        rent_id=100, car_id=1, client_id=1, user_id=1,
        start_date=start, end_date=end, status=RentalStatusEnum.AWAITING,
        created_at=datetime.now(), notes=None
    )
    rental_service.rental_repo.create.return_value = mock_rental

    # Т.к. create_rental вызывает get_rent_by_id, мокаем его результат
    expected_result = MagicMock(spec=RentalWithRelationsDTO)
    with patch.object(RentalService, 'get_rent_by_id', return_value=expected_result):
        result = rental_service.create_rental(dto)

        assert result == expected_result
        rental_service.rental_repo.create.assert_called_once()


def test_extend_rental_valid(rental_service):
    rent_id = 1
    old_end = datetime(2025, 1, 1, tzinfo=timezone.utc)
    new_end = datetime(2025, 1, 10, tzinfo=timezone.utc)

    mock_rental = MagicMock(spec=Rental)
    mock_rental.end_date = old_end
    rental_service.rental_repo.get_by_rent_id.return_value = mock_rental

    with patch.object(RentalService, 'update_rental') as mock_update:
        rental_service.extend_rental(rent_id, new_end)
        mock_update.assert_called_once()
        # Проверяем, что в update передан DTO с новой датой
        args = mock_update.call_args[0][0]
        assert args.end_date == new_end


def test_complete_rental_calculation(rental_service):
    rent_id = 5
    actual_return = datetime(2025, 1, 1, 15, 0)  # 15:00

    # Мокаем аренду
    mock_rental = MagicMock()
    mock_rental.car_id = 10
    rental_service.rental_repo.get_by_rent_id.return_value = mock_rental
    rental_service.rental_repo.exist.return_value = True

    # Мокаем параметры машины для расчета цены
    # start_date 12:00, rate 1000. Разница 3 часа.
    rental_service.car_service.get_car_by_id.return_value = {
        'start_date': datetime(2025, 1, 1, 12, 0),
        'daily_rate': 1000
    }

    with patch.object(RentalService, 'get_rent_by_id'):
        rental_service.complete_rental(rent_id, actual_return)

        # 3 часа * 1000 = 3000
        rental_service.rental_repo.complete_rental.assert_called_once_with(
            rent_id, actual_return, 3000
        )


def test_cancel_rental_not_found(rental_service):
    rental_service.rental_repo.exist.return_value = False

    with pytest.raises(ValueError, match="не существует"):
        rental_service.cancel_rental(999)

