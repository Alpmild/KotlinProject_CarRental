from sqlalchemy.orm import Session
from typing import Optional
from entity import CarSpecifications  # Предполагается, что класс в models.py
from dto import CarSpecificationsUpdateDTO


class CarSpecificationsRepository:
    """Репозиторий для работы с характеристиками автомобилей"""

    def __init__(self, db: Session):
        self.db = db

    # CRUD операции

    def create(self, car_spec: CarSpecifications) -> CarSpecifications:
        """Создание новых характеристик автомобиля"""
        self.db.add(car_spec)
        self.db.commit()
        self.db.refresh(car_spec)
        return car_spec

    def get_by_car_id(self, car_id: int) -> Optional[CarSpecifications]:
        """Получение характеристик по ID автомобиля"""
        return self.db.query(CarSpecifications).filter(CarSpecifications.car_id == car_id).first()

    def update(self, update_data: Optional[CarSpecificationsUpdateDTO]) -> Optional[CarSpecifications]:
        """Обновление характеристик автомобиля"""
        car_spec = self.get_by_car_id(update_data.car_id)
        car_spec_info = update_data.model_dump(exclude_none=True)

        if car_spec:
            for key, value in car_spec_info.items():
                if hasattr(car_spec, key) and value is not None:
                    setattr(car_spec, key, value)
            self.db.commit()
            self.db.refresh(car_spec)
        return car_spec

    def delete(self, car_id: int) -> bool:
        """Удаление характеристик автомобиля"""
        car_spec = self.get_by_car_id(car_id)
        if car_spec:
            self.db.delete(car_spec)
            self.db.commit()
            return True
        return False

    def count_all(self) -> int:
        """Общее количество записей"""
        return self.db.query(CarSpecifications).count()