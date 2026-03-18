from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash # Import for user creation

# User operations
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserLogin):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Transaction operations
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def update_transaction_status(db: Session, transaction_id: int, status: str, fraud_score: float = None):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db_transaction.status = status
        if fraud_score is not None:
            db_transaction.fraud_score = fraud_score
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

print('app/crud.py created successfully.')
