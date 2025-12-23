from entity import Client
from repository import ClientRepository
from dto import ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO, ClientFilterDTO

from sqlalchemy.orm import Session
from typing import Dict, Any, List


class ClientService:
    def __init__(self, db_session: Session):
        self.db_session: Session = db_session
        self.client_repo: ClientRepository = ClientRepository(db_session)

    def create_client(self, client_dto: ClientCreateDTO) -> ClientResponseDTO:
        """Создание клиента с DTO"""
        # Проверка уникальности VIN и номера
        if self.client_repo.phone_exists(client_dto.phone):
            raise ValueError(f'Номер {client_dto.phone} уже есть в базе.')
        if client_dto.telegram_id and self.client_repo.telegram_exists(client_dto.telegram_id):
            raise ValueError(f'Телеграм ID {client_dto.telegram_id} уже есть в базе.')

        client_entity = Client(
            name=client_dto.name,
            phone=client_dto.phone,
            telegram_id=client_dto.telegram_id,
            license_number=client_dto.license_number,
        )

        created_client = self.client_repo.create(client_entity)
        return ClientResponseDTO.model_validate(created_client)

    def update_client(self, car_info_dto: ClientUpdateDTO) -> ClientResponseDTO:
        client_response_dto = ClientResponseDTO.model_validate(self.client_repo.update(car_info_dto))
        return client_response_dto

    def delete_client(self, client_id: int) -> bool:
        """Удаление автомобиля по ID"""
        return self.client_repo.delete(client_id)

    def get_clients_by_filter(self, clients_filter_dto: ClientFilterDTO) -> List[ClientResponseDTO]:
        """Получение списка клиентов с учетом заданного фильтра"""
        clients_entity_list = self.client_repo.find_by_filters(clients_filter_dto)
        clients_dto_seq = list(map(
            lambda x: ClientResponseDTO.model_validate(x), clients_entity_list
        ))
        return clients_dto_seq

    def get_client_by_id(self, client_id: int) -> ClientResponseDTO:
        """Получение автомобиля с характеристиками по ID"""
        client_entity = self.client_repo.get_by_id(client_id)
        if not client_entity:
            raise ValueError(f"Клиент с ID {client_id} не найден")
        return ClientResponseDTO.model_validate(client_entity)

    def get_by_name(self, name: str) -> List[ClientResponseDTO]:
        return list(map(
            lambda x: ClientResponseDTO.model_validate(x), self.client_repo.get_by_name(name)
        ))