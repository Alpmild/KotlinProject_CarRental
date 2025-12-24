from .base import Base

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from datetime import datetime

class RentalStatus:
    AWAITING = "AWAITING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Rental(Base):
    __tablename__ = "Rentals"

    rent_id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow) # Когда выдан
    end_date = Column(DateTime, nullable=False) # Когда должен быть возвращен
    actual_return_date = Column(DateTime, nullable=True) # Когда фактически вернули
    total_cost = Column(Numeric(precision=10, scale=2), nullable=True) # Итоговая стоимость аренды
    status = Column(String(20), default=RentalStatus.ACTIVE)
    notes = Column(String(1000), nullable=True) # Примечания
    created_at = Column(DateTime, default=datetime.now)

    # Связь "много к одному" с автомобилем
    car_id = Column(Integer, ForeignKey("Cars.car_id"))
    car = relationship("Car", back_populates="rentals", uselist=False)

    # Связь "много к одному" с клиентом
    client_id = Column(Integer, ForeignKey("Clients.client_id"))
    client = relationship("Client", back_populates="rentals", uselist=False)

    # Связь "много к одному" с сотрудником (опционально)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    user = relationship("User", back_populates="issued_rentals", uselist=False)

    def __repr__(self):
        return f"<Rental(rent_id={self.rent_id}, status='{self.status}', client_id={self.client_id}, car_id={self.car_id})>"