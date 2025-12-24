from repository import CarRepository
from repository import CarSpecificationsRepository
from dto import CarCreateDTO, CarResponseDTO, CarWithSpecsResponseDTO, CarWithSpecsUpdateDTO, CarFilterDTO
from dto import CarSpecificationsResponseDTO
from entity import Car, CarSpecifications

from sqlalchemy.orm import Session
from typing import Dict, List


class CarService:
    def __init__(self, db_session: Session
                 ):
        self.db_session = db_session
        self.car_repo = CarRepository(db_session)
        self.specs_repo = CarSpecificationsRepository(db_session)

    def create_car(self, car_dto: CarCreateDTO) -> CarResponseDTO:
        """Создание автомобиля с DTO"""
        # Проверка уникальности VIN и номера
        if self.car_repo.vin_exists(car_dto.vin):
            raise ValueError(f"VIN {car_dto.vin} уже существует")
        if self.car_repo.license_plate_exists(car_dto.license_plate):
            raise ValueError(f"Номерной знак {car_dto.license_plate} уже существует")

        # Создаем автомобиль
        car_entity = Car(
            license_plate=car_dto.license_plate,
            vin=car_dto.vin,
            daily_rate=car_dto.daily_rate,
            status=car_dto.status
        )

        created_car = self.car_repo.create(car_entity)

        # Создаем характеристики, если они есть
        if car_dto.specifications is not None:
            specs_dto = car_dto.specifications
            specs_dto.car_id = created_car.car_id

            specs_entity = CarSpecifications(
                car_id=specs_dto.car_id,
                name=specs_dto.name,
                mileage=specs_dto.mileage,
                power=specs_dto.power,
                overclocking=specs_dto.overclocking,
                consump_in_city=specs_dto.consump_in_city,
                transmission=specs_dto.transmission.value,
                actuator=specs_dto.actuator.value,
                wheel=specs_dto.wheel.value,
                color=specs_dto.color,

            )
            self.specs_repo.create(specs_entity)

        # Используем model_validate вместо from_orm
        return CarResponseDTO.model_validate(created_car)

    def update_car(self, car_info_dto: CarWithSpecsUpdateDTO) -> CarWithSpecsResponseDTO:
        car = CarResponseDTO.model_validate(
            self.car_repo.update(car_info_dto.car)
        )
        if car_info_dto.specifications:
            specifications = CarSpecificationsResponseDTO.model_validate(
                self.specs_repo.update(car_info_dto.specifications)
            )
        else:
            specifications = None
        car_response_dto = CarWithSpecsResponseDTO(car=car, specifications=specifications)
        return car_response_dto

    def delete_car(self, car_id: int) -> bool:
        """Удаление автомобиля по ID"""
        return self.car_repo.delete(car_id)

    def get_cars_by_filter(
            self,
            cars_filter: CarFilterDTO) -> List[CarWithSpecsResponseDTO]:
        """Получение списка автомобилей с учетом заданного фильтра"""
        cars_entity_list = self.car_repo.find_by_filters(cars_filter)
        cars_with_specs = []

        for entity in cars_entity_list:
            car_dto = CarResponseDTO.model_validate(entity)
            if entity.car_specifications is not None:
                spec_dto = CarSpecificationsResponseDTO.model_validate(entity.car_specifications)
            else:
                spec_dto = None

            combined_dto = CarWithSpecsResponseDTO(car=car_dto, specifications=spec_dto).model_dump()
            cars_with_specs.append(combined_dto)

        return cars_with_specs

    def get_car_by_id(self, car_id: int) -> CarWithSpecsResponseDTO:
        car_entity = self.car_repo.get_by_id(car_id)
        if not car_entity:
            raise ValueError(f"Автомобиль с ID {car_id} не найден")

        car_dto = CarResponseDTO.model_validate(car_entity)
        specs_dto = None

        if car_entity.car_specifications is not None:
            specs_dto = CarSpecificationsResponseDTO.model_validate(car_entity.car_specifications)

        return CarWithSpecsResponseDTO(car=car_dto, specifications=specs_dto)

    def get_available_cars(self) -> List[CarWithSpecsResponseDTO]:
        """Получение списка доступных автомобилей"""
        filter_dict = {"status": "AVAILABLE"}
        return self.get_cars_by_filter(filter_dict)

    def get_cars_by_price_range(self, min_price: float, max_price: float) -> list[CarWithSpecsResponseDTO]:
        """Получение автомобилей в диапазоне цен"""
        filter_dict = {"min_rate": min_price, "max_rate": max_price}
        return self.get_cars_by_filter(filter_dict)

