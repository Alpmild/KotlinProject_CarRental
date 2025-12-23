from .base import Base

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship



class CarSpecifications(Base):
    __tablename__ = 'CarSpecifications'

    # Первичный ключ - car_id, который также является внешним ключом
    car_id = Column(
        Integer, ForeignKey('Cars.car_id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True, nullable=False
    )

    name = Column(String(255), nullable=False)
    mileage = Column(Integer, nullable=False)  # Пробег
    power = Column(Integer, nullable=False)  # Мощность
    overclocking = Column(DECIMAL(5, 2), nullable=False)  # Разгон до 100 км/ч
    consump_in_city = Column(DECIMAL(5, 2), nullable=False)  # Расход в городе
    transmission = Column(String(50), nullable=False)  # Коробка передач
    actuator = Column(String(50), nullable=False)  # Привод
    wheel = Column(String(50), nullable=False)  # Руль
    color = Column(String(50), nullable=False)  # Цвет

    # Связь один-к-одному с таблицей Cars
    car = relationship("Car", back_populates="car_specifications", uselist=False)

    def __repr__(self):
        return f"<CarSpecifications(car_id={self.car_id}, name='{self.name}')>"