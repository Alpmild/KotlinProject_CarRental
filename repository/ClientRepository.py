from entity import Client, Rental
from dto import ClientUpdateDTO, ClientFilterDTO

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_


class ClientRepository:
    def __init__(self, session: Session):
        self.session_db = session

    def create(self, client: Client) -> Client:
        """Сохранить аренду (создать или обновить)"""
        self.session_db.add(client)
        self.session_db.commit()
        self.session_db.refresh(client)
        return client

    def update(self, update_data: Optional[ClientUpdateDTO]) -> Optional[Client]:
        """Обновление информации о клиенте"""
        client = self.get_by_id(update_data.client_id)
        client_info = update_data.model_dump()

        if client:
            for key, value in client_info.items():
                if hasattr(client, key) and value is not None:
                    setattr(client, key, value)
            client.created_at = datetime.now()  # Обновляем время изменения
            self.session_db.commit()
            self.session_db.refresh(client)
        return client

    def delete(self, client_id: int) -> bool:
        """Удаление клиента"""
        car = self.get_by_id(client_id)
        if car:
            self.session_db.delete(car)
            self.session_db.commit()
            return True
        return False

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.session_db.query(Client).filter(Client.client_id == client_id).first()

    def get_by_name(self, name: str) -> List[type[Client]]:
        return self.session_db.query(Client).filter(Client.name.ilike(f'%{name}%')).all()

    def get_rentals_by_client_id_and_period(
            self, client_id: int, start: datetime, end: datetime) -> List[type[Client]]:

        res = self.session_db.query(Client).filter(
            and_(Rental.client_id == client_id, Rental.start_date >= start, Rental.start_date <= end)
        ).order_by(Rental.start_date)
        return res.all()

    def get_all_rentals_in_period(self, start: datetime, end: datetime) -> List[type[Client]]:
        res = self.session_db.query(Client).filter(
            and_(Rental.start_date >= start, Rental.start_date <= end)
        ).order_by(Rental.start_date)
        return res.all()

    def phone_exists(self, phone: str) -> bool:
        query = self.session_db.query(Client).filter(Client.phone == phone)
        return query.first() is not None

    def telegram_exists(self, telegram_id: str) -> bool:
        query = self.session_db.query(Client).filter(Client.telegram_id == telegram_id)
        return query.first() is not None

    def exists(self, client_id: int) -> bool:
        query = self.session_db.query(Client).filter(Client.client_id == client_id)
        return query.first() is not None


    def find_by_filters(self, client_filter_dto: ClientFilterDTO) -> List[type[Client]]:
        query = self.session_db.query(Client)
        filters = []
        if client_filter_dto.name:
            filters.append(Client.name.ilike(f'%{client_filter_dto.name}%'))
        if client_filter_dto.phone:
            filters.append(Client.phone.ilike(f'%{client_filter_dto.phone}%'))
        if client_filter_dto.telegram_id:
            filters.append(Client.telegram_id.ilike(f'%{client_filter_dto.telegram_id}%'))
        if client_filter_dto.license_number:
            filters.append(Client.license_number.ilike(f'%{client_filter_dto.license_number}%'))

        if filters:
            query = query.filter(and_(*filters))
        return query.all()


