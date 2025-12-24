from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from dto import (CarCreateDTO, CarSpecificationsCreateDTO,
                 UserCreateDTO, ClientCreateDTO, RentalCreateDTO,
                 CarStatusEnum, TransmissionEnum, ActuatorEnum,
                 WheelEnum, UserPositionEnum, RentalStatusEnum)
from service import CarService, ClientService, UserService, RentalService


class TestData:
    def __init__(self, session_db: Session):
        self.session = session_db
        self.car_service = CarService(session_db)
        self.client_service = ClientService(session_db)
        self.user_service = UserService(session_db)
        self.rental_service = RentalService(session_db)

    def load(self):

        cars = [
            CarCreateDTO(
                license_plate="А191АА21",
                vin='W' * 17,
                daily_rate=500,
                status=CarStatusEnum.AVAILABLE,
                specifications=CarSpecificationsCreateDTO(
                    car_id=1,
                    name='Nissan Silvia S15',
                    mileage=120_000,
                    power=250,
                    overclocking=4.2,
                    consump_in_city=9.2,
                    transmission=TransmissionEnum.MANUAL,
                    actuator=ActuatorEnum.FRONT,
                    wheel=WheelEnum.RIGHT, color='Белый'
                )
            ),
            CarCreateDTO(
                license_plate="О322ОО197",
                vin='W' * 8 + '1' * 9,
                daily_rate=700,
                status=CarStatusEnum.AVAILABLE,
                specifications=CarSpecificationsCreateDTO(
                    car_id=1,
                    name='Toyota Supra MK4',
                    mileage=10_000,
                    power=270,
                    overclocking=3.2,
                    consump_in_city=10.2,
                    transmission=TransmissionEnum.MANUAL,
                    actuator=ActuatorEnum.FRONT,
                    wheel=WheelEnum.RIGHT,
                    color='Черный'
                )
            )
        ]
        for car_dto in cars:
            self.car_service.create_car(car_dto)

        users = [
            UserCreateDTO(
                email='admin@yandex.ru',
                password='123',
                name='Петров Дмитрий',
                position=UserPositionEnum.ADMIN
            ),
            UserCreateDTO(
                email='agent@yandex.ru',
                password='secret',
                name='Какой-то Случайный человек',
                position=UserPositionEnum.AGENT
            )
        ]
        for user_dto in users:
            self.user_service.create_user(user_dto)

        clients = [
            ClientCreateDTO(
                name='Иванов ИВан Иванович',
                phone='89003123412',
                telegram_id='@ivan_tg',
                license_number='ГИБДД 1234'
            ),
            ClientCreateDTO(
                name='Бутусов Денис Николаевич',
                phone='89123221212',
                telegram_id='@the_best_butusov',
                license_number='ГИБДД 9000'
            )
        ]
        for client_dto in clients:
            self.client_service.create_client(client_dto)

        rentals = [
            RentalCreateDTO(
                car_id=26,      # Nissan Silvia S15
                client_id=6,    # Иванов Иван Иванович
                user_id=2,      # Петров Дмитрий, ADMIN
                start_date=datetime.now(timezone.utc) + timedelta(days=3),
                end_date=datetime.now(timezone.utc) + timedelta(days=5),
                status=RentalStatusEnum.AWAITING,
            ),
            RentalCreateDTO(
                car_id=27,      # Toyota Supra MK4
                client_id=7,    # Какой-то Случайный человек
                user_id=3,      # Бутусов Денис Николаевич
                start_date=datetime.now(timezone.utc) + timedelta(days=9),
                end_date=datetime.now(timezone.utc) + timedelta(days=11),
                status=RentalStatusEnum.AWAITING
            )
        ]
        for rental_dto in rentals:
            self.rental_service.create_rental(rental_dto)