from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, between

from dto import RentalUpdateDTO, RentalStatusEnum, RentalFilterDTO
from entity import Rental
from entity import RentalStatus


class RentalRepository:
    """Репозиторий для работы с арендами автомобилей"""

    def __init__(self, session: Session):
        self.session_db = session

    def create(self, rental: Rental) -> Rental:
        """Сохранить аренду (создать или обновить)"""
        self.session_db.add(rental)
        self.session_db.commit()
        self.session_db.refresh(rental)
        return rental

    def update(self, update_data: Optional[RentalUpdateDTO]) -> Optional[Rental]:
        """Обновление информации о клиенте"""
        rental = self.get_by_rent_id(update_data.rent_id)
        rental_info = update_data.model_dump()

        if rental:
            for key, value in rental_info.items():
                if hasattr(rental, key) and value is not None:
                    setattr(rental, key, value)
            rental.created_at = datetime.now()  # Обновляем время изменения
            self.session_db.commit()
            self.session_db.refresh(rental)
        return rental

    def extend_rental(self, rental_id: int, new_end_date: datetime) -> Optional[Rental]:
        """Продлить аренду"""
        rental = self.get_by_rent_id(rental_id)

        if rental and rental.status == RentalStatus.ACTIVE:
            rental = self.update(
                RentalUpdateDTO(rent_id=rental_id, end_date=new_end_date)
            )
        return rental

    def complete_rental(
            self, rental_id: int, actual_return_date: datetime, total_cost: int
    ) -> Optional[Rental]:
        """Завершить аренду (автомобиль возвращен)"""

        rental = self.get_by_rent_id(rental_id)
        if rental and rental.status == RentalStatus.ACTIVE:
            rental = self.update(
                RentalUpdateDTO(
                    rent_id=rental_id, actual_return_date=actual_return_date,
                    total_cost=total_cost, status=RentalStatusEnum.COMPLETED
                )
            )
        return rental

    def cancel_rental(self, rental_id: int) -> Optional[Rental]:
        """Отменить аренду"""

        rental = self.get_by_rent_id(rental_id)
        if rental and rental.status == RentalStatus.AWAITING:
            rental = self.update(
                RentalUpdateDTO(rent_id=rental_id, status=RentalStatusEnum.CANCELLED)
            )
        return rental

    def delete(self, rental_id: int) -> bool:
        """Удаление клиента"""
        car = self.get_by_rent_id(rental_id)
        if car:
            self.session_db.delete(car)
            self.session_db.commit()
            return True
        return False

    def find_by_filters(self, rental_filter_dto: RentalFilterDTO) -> List[type[Rental]]:
        query = self.session_db.query(Rental)
        filters = []

        if rental_filter_dto.client_id:
            filters.append(Rental.client_id == rental_filter_dto.client_id)
        if rental_filter_dto.car_id:
            filters.append(Rental.car_id == rental_filter_dto.car_id)
        if rental_filter_dto.user_id:
            filters.append(Rental.user_id == rental_filter_dto.user_id)
        if rental_filter_dto.time_range:
            if len(rental_filter_dto.time_range) != 2:
                raise ValueError("time_range должен иметь длину 2.")
            filters.append(or_(
                Rental.start_date.between(*rental_filter_dto.time_range),
                Rental.end_date.between(*rental_filter_dto.time_range)
            ))
        if rental_filter_dto.status:
            filters.append(Rental.status == rental_filter_dto.status)

        if filters:
            query = query.filter(*filters)
        return query.all()

    def get_by_rent_id(self, rent_id: int) -> Optional[Rental]:
        return self.session_db.query(Rental).filter(Rental.rent_id == rent_id).first()

    def is_car_available(self, car_id: int, start_date: datetime, end_date: datetime) -> bool:
        """Проверить, доступен ли автомобиль для аренды в указанный период"""

        res = self.session_db.query(Rental).filter(
            and_(
                Rental.car_id == car_id,
                Rental.status != RentalStatus.CANCELLED,
                or_(
                    and_(start_date <= Rental.start_date, Rental.start_date <= end_date),
                    and_(start_date <= Rental.end_date, Rental.end_date <= end_date)
                )
            )
        ).first()

        return res is None

    def exist(self, rent_id: int):
        res = self.session_db.query(Rental).filter(Rental.rent_id == rent_id).first()
        return res is not None
