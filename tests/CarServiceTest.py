from service import get_car_service
from dto import (CarCreateDTO, CarSpecificationsCreateDTO, CarFilterDTO,
                 CarWithSpecsUpdateDTO, TransmissionEnum, ActuatorEnum,
                 WheelEnum, CarStatusEnum, CarUpdateDTO)
from config import SessionLocal

import pytest


@pytest.fixture(scope="function")
def db_session():
    return SessionLocal()


@pytest.fixture
def car_service(db_session):
    return get_car_service(db_session)


def test_create_car_success(car_service):
    # Подготовка данных
    specs_dto = CarSpecificationsCreateDTO(
        car_id=1,
        name="Tesla Model 3",
        mileage=100,
        power=450,
        overclocking=3.3,
        consump_in_city=20,
        transmission=TransmissionEnum.AUTOMATIC,
        actuator=ActuatorEnum.ALL,
        wheel=WheelEnum.LEFT,
        color="White"
    )
    car_dto = CarCreateDTO(
        license_plate="А523АА21",
        vin="1234567890ABCDEFG",
        daily_rate=5000,
        status=CarStatusEnum.AVAILABLE,
        specifications=specs_dto
    )

    # Действие
    result = car_service.create_car(car_dto)

    # Проверки
    assert result.license_plate == "А523АА21"
    assert result.vin == "1234567890ABCDEFG"

    # Проверка в базе через сервис
    db_car = car_service.get_car_by_id(result.car_id)
    assert db_car.car.vin == "1234567890ABCDEFG"
    assert db_car.specifications.name == "Tesla Model 3"


def test_create_car_duplicate_vin_raises_error(car_service):
    car_dto = CarCreateDTO(
        license_plate="А111АА77",
        vin="WWWWWWWWWWWWWWWWW",  # Данный vin уже есть в базе
        daily_rate=1000,
        status=CarStatusEnum.AVAILABLE,
        specifications=None
    )

    with pytest.raises(ValueError, match=f"VIN {car_dto.vin} уже существует"):
        car_service.create_car(car_dto)


def test_get_car_by_id_not_found(car_service):
    car_id = 9999
    with pytest.raises(ValueError, match=f"Автомобиль с ID {car_id} не найден"):
        car_service.get_car_by_id(car_id)


def test_delete_car(car_service):
    # Сначала создаем
    car_dto = CarCreateDTO(
        license_plate="О000ОО197",
        vin="XEATC02DFWGBK4LTX",
        daily_rate=2000,
        status=CarStatusEnum.AVAILABLE,
        specifications=None
    )
    created = car_service.create_car(car_dto)

    delete_result = car_service.delete_car(created.car_id)
    assert delete_result is True

    with pytest.raises(ValueError):
        car_service.get_car_by_id(created.car_id)


def test_get_cars_by_filter(car_service):
    # Создаем машину с ценой 3000
    car1_id = car_service.create_car(CarCreateDTO(
        license_plate="С333СС77", vin="V" * 17, daily_rate=3000,
        status=CarStatusEnum.AVAILABLE, specifications=None
    )).car_id
    # Создаем машину с ценой 7000
    car2_id = car_service.create_car(CarCreateDTO(
        license_plate="О444ОО77", vin="A" * 17, daily_rate=7000,
        status=CarStatusEnum.AVAILABLE, specifications=None
    )).car_id

    results = car_service.get_cars_by_filter(CarFilterDTO(
        min_rate=2999, max_rate=3001
    ))

    assert len(results) == 1
    assert results[0]['car']['daily_rate'] == 3000

    car_service.delete_car(car1_id)
    car_service.delete_car(car2_id)


def test_update_car(car_service):
    car_dto = car_service.create_car(CarCreateDTO(
        license_plate="Е555ЕЕ77",
        vin="P" * 17,
        daily_rate=1000,
        status=CarStatusEnum.AVAILABLE,
        specifications=None
    ))
    assert car_dto.license_plate == "Е555ЕЕ77"

    update_dto = car_service.update_car(CarWithSpecsUpdateDTO(
        car=CarUpdateDTO(
            car_id=car_dto.car_id,
            license_plate="А555АА77"
        )
    ))
    assert update_dto.car.car_id == car_dto.car_id and update_dto.car.license_plate == "А555АА77"
    car_service.delete_car(car_dto.car_id)
