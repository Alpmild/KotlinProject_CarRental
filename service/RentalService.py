from repository import RentalRepository, CarRepository, ClientRepository, UserRepository
from dto import (RentalUpdateDTO, RentalCreateDTO, RentalResponseDTO,
                 RentalStatusEnum, RentalWithRelationsDTO, RentalFilterDTO)
from entity import Rental, RentalStatus
from service import CarService, ClientService, UserService

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Optional, List
from math import ceil


class RentalService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.rental_repo = RentalRepository(db_session)

        self.car_repo = CarRepository(db_session)
        self.car_service = CarService(db_session)

        self.client_repo = ClientRepository(db_session)
        self.client_service = ClientService(db_session)

        self.user_repo = UserRepository(db_session)
        self.user_service = UserService(db_session)

    def create_rental(self, rental_dto: RentalCreateDTO) -> Optional[RentalWithRelationsDTO]:
        client_id = rental_dto.client_id
        car_id = rental_dto.car_id
        user_id = rental_dto.user_id

        if not self.client_repo.exists(client_id):
            raise ValueError(f'{client_id=} не существует')
        if not self.car_repo.exists(car_id):
            raise ValueError(f'{car_id=} не существует')
        if not self.user_repo.exists(user_id):
            raise ValueError(f'{user_id=} не существует')

        if not self.rental_repo.is_car_available(
                car_id, rental_dto.start_date, rental_dto.end_date):
            raise ValueError(
                f'Автомобиль {car_id} не доступен в данный промежуток времени:'
                f' {(rental_dto.start_date, rental_dto.end_date)=}'
            )

        rental_dto.start_date = rental_dto.start_date.replace(tzinfo=timezone.utc)
        if rental_dto.start_date > datetime.now(timezone.utc):
            status = RentalStatusEnum.AWAITING
        else:
            status = RentalStatus.ACTIVE

        rental_entity = Rental(
            car_id=car_id,
            client_id=client_id,
            user_id=user_id,
            start_date=rental_dto.start_date,
            end_date=rental_dto.end_date,
            status=status,
            notes=rental_dto.notes,
        )

        res = self.rental_repo.create(rental_entity)
        return self.get_rent_by_id(res.rent_id)

    def update_rental(self, rental_info_dto: RentalUpdateDTO) -> RentalWithRelationsDTO:
        self.rental_repo.update(rental_info_dto)
        return self.get_rent_by_id(rental_info_dto.rent_id)

    def extend_rental(self, rent_id: int, new_end_date: datetime) -> Optional[RentalWithRelationsDTO]:
        rental = self.rental_repo.get_by_rent_id(rent_id)
        if rental is None:
            raise ValueError(f'{rent_id=} не существует')

        end_date = rental.end_date.replace(tzinfo=timezone.utc)
        new_end_date = new_end_date.replace(tzinfo=timezone.utc)

        if end_date > new_end_date:
            return self.get_rent_by_id(rent_id)
        return self.update_rental(
            RentalUpdateDTO(rent_id=rent_id, end_date=new_end_date)
        )

    def complete_rental(self, rent_id: int, actual_return_date: datetime) -> Optional[RentalWithRelationsDTO]:
        if not self.rental_repo.exist(rent_id):
            raise ValueError(f'{rent_id=} не существует')

        car_id = self.rental_repo.get_by_rent_id(rent_id).car_id
        car_json = self.car_service.get_car_by_id(car_id)

        start_date, cost = car_json['start_date'], car_json['daily_rate']
        total_cost = int(cost * ceil((actual_return_date - start_date).total_seconds() / 3600))

        self.rental_repo.complete_rental(rent_id, actual_return_date, total_cost)
        return self.get_rent_by_id(rent_id)

    def cancel_rental(self, rent_id: int) -> RentalWithRelationsDTO:
        if not self.rental_repo.exist(rent_id):
            raise ValueError(f'{rent_id=} не существует')

        self.rental_repo.cancel_rental(rent_id)
        return self.get_rent_by_id(rent_id)

    def delete_rental(self, rental_id: int) -> bool:
        return self.rental_repo.delete(rental_id)

    def get_rent_by_id(self, rent_id: int) -> Optional[RentalWithRelationsDTO]:
        res = self.rental_repo.get_by_rent_id(rent_id)
        if res is None:
            raise ValueError(f'{rent_id=} не существует')

        rental_dto = RentalResponseDTO.model_validate(self.rental_repo.get_by_rent_id(rent_id))
        car_dto = self.car_service.get_car_by_id(rental_dto.car_id)
        client_dto = self.client_service.get_client_by_id(rental_dto.client_id)
        user_dto = self.user_service.get_user_by_id(rental_dto.user_id)

        return RentalWithRelationsDTO(rental=rental_dto, car=car_dto, client=client_dto, user=user_dto)

    def get_rentals_by_filter(self, rentals_filter: RentalFilterDTO) -> List[RentalWithRelationsDTO]:

        rentals = self.rental_repo.find_by_filters(rentals_filter)
        rentals_with_relations = []

        for rental in rentals:
            car_id, client_id, user_id = rental.car_id, rental.client_id, rental.user_id

            rental = RentalResponseDTO.model_validate(rental).model_dump()
            car_with_specs_dto = self.car_service.get_car_by_id(car_id)
            client_dto = self.client_service.get_client_by_id(client_id)
            user_dto = self.user_service.get_user_by_id(user_id)

            rentals_with_relations.append(
                RentalWithRelationsDTO(rental=rental, car=car_with_specs_dto, client=client_dto, user=user_dto)
            )
        return rentals_with_relations

    def is_car_available(self, car_id: int, start_date: datetime, end_date: datetime) -> bool:
        return self.rental_repo.is_car_available(car_id, start_date, end_date)
