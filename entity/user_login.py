from .base import Base
from sqlalchemy import Column, Integer, String, DateTime

# class UserLogin(Base):
#     __tablename__ = "Users"
#
#     user_id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, unique=True,nullable=False)
#
#     def __repr__(self):
#         return f"<UserLogin({self.user_id=}, {self.email=})>"