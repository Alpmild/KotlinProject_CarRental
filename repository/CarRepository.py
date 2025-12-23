from dto.CarDTO import CarFilterDTO
from entity import Car, CarStatus, CarSpecifications
from dto import CarUpdateDTO, CarFilterDTO

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, asc
from typing import Optional, List, Dict
from datetime import datetime


class CarRepository:
    """Репозиторий для работы с автомобилями"""

    def __init__(self, session: Session):
        self.session_db = session

    def create(self, car: Car) -> Car:
        """Создание нового автомобиля"""
        self.session_db.add(car)
        self.session_db.commit()
        self.session_db.refresh(car)
        return car

    def update(self, update_data: Optional[CarUpdateDTO]) -> Optional[Car]:
        """Обновление информации об автомобиле"""
        car = self.get_by_id(update_data.car_id)
        car_info = update_data.model_dump(exclude_none=True)

        if car:
            for key, value in car_info.items():
                if hasattr(car, key) and value is not None:
                    setattr(car, key, value)
            car.created_at = datetime.now()  # Обновляем время изменения
            self.session_db.commit()
            self.session_db.refresh(car)
        return car

    def delete(self, car_id: int) -> bool:
        """Удаление автомобиля"""
        car = self.get_by_id(car_id)
        if car:
            self.session_db.delete(car)
            self.session_db.commit()
            return True
        return False

    def get_by_id(self, car_id: int) -> Optional[Car]:
        """Получение автомобиля по ID"""
        return self.session_db.query(Car).filter(Car.car_id == car_id).first()


    def find_by_filters(self, car_filter_dto: CarFilterDTO) -> List[type[Car]]:
        """Поиск по нескольким фильтрам"""

        query = self.session_db.query(Car)
        filters = []

        if car_filter_dto.license_plate:
            filters.append(Car.license_plate.olike(f'%{car_filter_dto.license_plate}%'))
        if car_filter_dto.vin:
            filters.append(Car.vin.ilike(f'%{car_filter_dto.vin}%'))
        if car_filter_dto.status:
            filters.append(Car.status.ilike(car_filter_dto.status))
        if car_filter_dto.min_rate is not None:
            filters.append(Car.daily_rate >= car_filter_dto.min_rate)
        if car_filter_dto.max_rate is not None:
            filters.append(Car.daily_rate <= car_filter_dto.max_rate)

        if car_filter_dto.model:
            filters.append(
                Car.car_specifications.has(CarSpecifications.name.ilike(f'%{car_filter_dto.model}%'))
            )
        if car_filter_dto.transmission:
            filters.append(
                Car.car_specifications.has(CarSpecifications.transmission.ilike(car_filter_dto.transmission))
            )
        if car_filter_dto.actuator:
            filters.append(
                Car.car_specifications.has(CarSpecifications.actuator.ilike(car_filter_dto.actuator))
            )
        if car_filter_dto.color:
            filters.append(
                Car.car_specifications.has(CarSpecifications.color.ilike(f'%{car_filter_dto.color}%'))
            )
        if car_filter_dto.min_power is not None and car_filter_dto.min_power >= 0:
            filters.append(
                Car.car_specifications.has(CarSpecifications.power >= car_filter_dto.min_power)
            )
        if car_filter_dto.max_power is not None and car_filter_dto.max_power > 0:
            filters.append(
                Car.car_specifications.has(CarSpecifications.power <= car_filter_dto.max_power)
            )

        if filters:
            query = query.filter(and_(*filters))

        return query.all()

    # ==================== СТАТИСТИКА И АНАЛИТИКА ====================

    def get_status_distribution(self) -> Dict[str, int]:
        """Распределение автомобилей по статусам"""
        results = self.session_db.query(
            Car.status,
            func.count(Car.car_id)
        ).group_by(Car.status).all()

        return {status: count for status, count in results}

    def get_most_expensive_cars(self, limit: int = 10) -> list[type[Car]]:
        """Самые дорогие автомобили для аренды"""
        return self.session_db.query(Car).order_by(desc(Car.daily_rate)).limit(limit).all()

    def get_cheapest_cars(self, limit: int = 10) -> List[Car]:
        """Самые дешевые автомобили для аренды"""
        return self.session_db.query(Car).filter(
            Car.status == CarStatus.AVAILABLE
        ).order_by(asc(Car.daily_rate)).limit(limit).all()

    # ==================== БИЗНЕС-ЛОГИКА ====================

    def change_status(self, car_id: int, new_status: str) -> Optional[Car]:
        """Изменение статуса автомобиля"""
        valid_statuses = [CarStatus.AVAILABLE, CarStatus.RENTED,
                          CarStatus.MAINTENANCE, CarStatus.NOT_AVAILABLE]

        if new_status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые значения: {valid_statuses}")

        car = self.get_by_id(car_id)
        if car:
            car.status = new_status
            self.session_db.commit()
            self.session_db.refresh(car)
        return car

    def mark_as_rented(self, car_id: int) -> Optional[Car]:
        """Пометить автомобиль как арендованный"""
        return self.change_status(car_id, CarStatus.RENTED)

    def mark_as_available(self, car_id: int) -> Optional[Car]:
        """Пометить автомобиль как доступный"""
        return self.change_status(car_id, CarStatus.AVAILABLE)

    def mark_as_maintenance(self, car_id: int) -> Optional[Car]:
        """Пометить автомобиль как находящийся на обслуживании"""
        return self.change_status(car_id, CarStatus.MAINTENANCE)

    def update_daily_rate(self, car_id: int, new_rate: int) -> Optional[Car]:
        """Обновление стоимости аренды"""
        if new_rate <= 0:
            raise ValueError("Стоимость аренды должна быть положительной")
        return self.update(car_id, {'daily_rate': new_rate})

    def is_car_available(self, car_id: int) -> bool:
        """Проверка доступности автомобиля для аренды"""
        car = self.get_by_id(car_id)
        return car is not None and car.status == CarStatus.AVAILABLE

    # ==================== СВЯЗАННЫЕ ДАННЫЕ ====================

    def get_car_with_specifications(self, car_id: int) -> Optional[Car]:
        """Получение автомобиля с его характеристиками"""
        return self.session_db.query(Car) \
            .options(joinedload(Car.car_specifications)) \
            .filter(Car.car_id == car_id) \
            .first()

    # ==================== ПРОВЕРКИ И ВАЛИДАЦИЯ ====================

    def license_plate_exists(self, license_plate: str, exclude_id: Optional[int] = None) -> bool:
        """Проверка существования номера (для уникальности)"""
        query = self.session_db.query(Car).filter(Car.license_plate == license_plate)

        if exclude_id:
            query = query.filter(Car.car_id != exclude_id)

        return query.first() is not None

    def vin_exists(self, vin: str, exclude_id: Optional[int] = None) -> bool:
        """Проверка существования VIN (для уникальности)"""
        query = self.session_db.query(Car).filter(Car.vin == vin)

        if exclude_id:
            query = query.filter(Car.car_id != exclude_id)

        return query.first() is not None

    def exists(self, car_id: int) -> bool:
        query = self.session_db.query(Car).filter(Car.car_id == car_id)
        return query.first() is not None

    def count_all(self) -> int:
        """Общее количество автомобилей"""
        return self.session_db.query(Car).count()

    def count_by_status(self, status: str) -> int:
        """Количество автомобилей по статусу"""
        return self.session_db.query(Car) \
            .filter(Car.status == status) \
            .count()
