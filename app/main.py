import os
import sys

# Add the project root directory to sys.path to allow imports from 'services' and 'worker'
# Assumes main.py is in 'app/' directory within the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth
from .database import SessionLocal, engine, get_db

from services import decision_engine
from worker import celery_worker

# Create database tables
# In a production environment, use Alembic for migrations
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fraud Detection System API",
    description="A FastAPI application for fraud detection with rule-based and ML-based engines, JWT authentication, and async logging.",
    version="1.0.0"
)

# Root endpoint for health check
@app.get("/", summary="Health Check")
def read_root():
    return {"message": "Fraud Detection API is running!"}

# Endpoint for user authentication and JWT token generation
@app.post("/token", response_model=schemas.Token, summary="Authenticate User and Get JWT Token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to create a user (for initial setup/testing, should be secured in production)
@app.post("/users/", response_model=schemas.TokenData, status_code=status.HTTP_201_CREATED, summary="Create a New User (for testing/admin)")
def create_new_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    crud.create_user(db=db, user=user)
    return {"username": user.username} # Returns username as a simple acknowledgment

# Endpoint to process new transactions
@app.post("/transaction/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Process New Transaction for Fraud Detection")
def process_transaction(
    transaction: schemas.TransactionCreate,
    current_user: str = Depends(auth.get_current_user), # Requires JWT authentication
    db: Session = Depends(get_db)
):
    # Pass transaction data to the decision engine
    decision_results = decision_engine.make_fraud_decision(transaction.dict())

    # Create transaction in DB with initial fraud score and status
    db_transaction = crud.create_transaction(db=db, transaction=transaction)

    # Update transaction in DB with decision engine results
    updated_transaction = crud.update_transaction_status(
        db=db,
        transaction_id=db_transaction.id,
        status=decision_results['status'],
        fraud_score=decision_results['final_fraud_score']
    )

    # Asynchronously log the processing details using Celery
    # In a real app, you might want to pass more context or use a dedicated logging schema
    celery_worker.log_suspicious_transaction.delay(
        transaction_id=updated_transaction.id,
        details={
            "user_id": updated_transaction.user_id,
            "amount": updated_transaction.amount,
            "location": updated_transaction.location,
            "device_id": updated_transaction.device_id,
            "rule_score": decision_results['rule_score'],
            "ml_score": decision_results['ml_score'],
            "final_fraud_score": decision_results['final_fraud_score'],
            "status_decision": decision_results['status']
        }
    )

    return updated_transaction

# Endpoint to retrieve all transactions (protected route)
@app.get("/transactions/", response_model=List[schemas.TransactionResponse], summary="Get All Transactions (requires authentication)")
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(auth.get_current_user), # Requires JWT authentication
    db: Session = Depends(get_db)
):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions

# Endpoint to retrieve a single transaction by ID (protected route)
@app.get("/transactions/{transaction_id}", response_model=schemas.TransactionResponse, summary="Get Transaction by ID (requires authentication)")
def read_transaction(
    transaction_id: int,
    current_user: str = Depends(auth.get_current_user), # Requires JWT authentication
    db: Session = Depends(get_db)
):
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return db_transaction

print('app/main.py updated successfully to integrate refactored decision_engine and celery_worker.')