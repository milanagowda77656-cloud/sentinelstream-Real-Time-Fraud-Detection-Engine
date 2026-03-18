import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# --- Test Database Setup (SQLite in-memory, no Postgres needed for tests) ---
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


# --- Helper ---
def create_user_and_login(username="testuser", password="testpass"):
    client.post("/users/", json={"username": username, "password": password})
    response = client.post("/token", data={"username": username, "password": password})
    return response.json()["access_token"]


# --- Tests ---

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Fraud Detection API is running!"}


def test_create_user():
    response = client.post("/users/", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 201
    assert response.json()["username"] == "alice"


def test_create_duplicate_user():
    client.post("/users/", json={"username": "alice", "password": "secret123"})
    response = client.post("/users/", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 400


def test_login_success():
    client.post("/users/", json={"username": "bob", "password": "mypassword"})
    response = client.post("/token", data={"username": "bob", "password": "mypassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    client.post("/users/", json={"username": "bob", "password": "mypassword"})
    response = client.post("/token", data={"username": "bob", "password": "wrongpass"})
    assert response.status_code == 401


def test_submit_transaction_authenticated():
    token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": 1,
        "amount": 150.0,
        "location": "NY",
        "device_id": "device_abc"
    }
    response = client.post("/transaction/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "fraud_score" in data
    assert data["status"] in ["approved", "review", "rejected"]


def test_submit_transaction_unauthenticated():
    payload = {
        "user_id": 1,
        "amount": 150.0,
        "location": "NY",
        "device_id": "device_abc"
    }
    response = client.post("/transaction/", json=payload)
    assert response.status_code == 401


def test_high_amount_flagged():
    token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": 1,
        "amount": 9999.0,        # High amount → rule engine flags
        "location": "International",  # Suspicious location
        "device_id": "BLACKLISTED_DEVICE_123"  # Blacklisted device
    }
    response = client.post("/transaction/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] in ["review", "rejected"]
    assert data["fraud_score"] > 0.3


def test_get_transactions_authenticated():
    token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/transactions/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transactions_unauthenticated():
    response = client.get("/transactions/")
    assert response.status_code == 401


def test_get_transaction_by_id():
    token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": 1,
        "amount": 50.0,
        "location": "TX",
        "device_id": "device_xyz"
    }
    create_resp = client.post("/transaction/", json=payload, headers=headers)
    txn_id = create_resp.json()["id"]

    response = client.get(f"/transactions/{txn_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == txn_id


def test_get_transaction_not_found():
    token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/transactions/99999", headers=headers)
    assert response.status_code == 404
