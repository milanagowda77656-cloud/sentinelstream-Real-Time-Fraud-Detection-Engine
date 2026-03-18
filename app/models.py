from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Optional: If User has transactions
    # transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    location = Column(String(255), nullable=False)
    device_id = Column(String(255), nullable=False)
    fraud_score = Column(Float, default=0.0)
    status = Column(String(50), default='pending', nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to User model
    # user = relationship("User", back_populates="transactions")

print('app/models.py updated successfully with User model.')
