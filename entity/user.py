from .base import Base

from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    name = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Связь "один ко многим" с арендами (кто выдал/оформил)
    issued_rentals = relationship("Rental", back_populates="user")

    def __repr__(self):
        return f"<User(employee_id={self.user_id}, name='{self.name}', position='{self.position}')>"