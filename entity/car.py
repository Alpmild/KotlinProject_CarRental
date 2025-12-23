from .base import Base

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class CarStatus:
    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    RENTED = "RENTED"
    MAINTENANCE = "MAINTENANCE" # На обслуживании

class Car(Base):
    __tablename__ = "Cars"

    car_id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), nullable=False, unique=True, index=True) # Номерной знак
    vin = Column(String(17), nullable=False, unique=True, index=True) # VIN
    daily_rate = Column(Integer, nullable=False) # Стоимость аренды
    status = Column(String(20), default=CarStatus.AVAILABLE) # Статус автомобиля
    change_at = Column(DateTime, default=datetime.now)

    car_specifications = relationship(
        "CarSpecifications", back_populates="car",
        cascade="all, delete-orphan", uselist=False
    )
    rentals = relationship("Rental", back_populates="car")

    def __repr__(self):
        return f"<Car(id={self.car_id}, name='{self.car_specifications.name}, plate='{self.license_plate}')>"