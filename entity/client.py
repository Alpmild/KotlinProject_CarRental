from .base import Base

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Client(Base):
    __tablename__ = "Clients"

    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(11), nullable=False, unique=True, index=True)
    telegram_id = Column(String(30), unique=True, index=True)
    license_number = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)

    # Связь "один ко многим" с арендами
    rentals = relationship("Rental", back_populates="client")

    def __repr__(self):
        return f"<Client({self.client_id=}, {self.name=}, {self.phone=})>"