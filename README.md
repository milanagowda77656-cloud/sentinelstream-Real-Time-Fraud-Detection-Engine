# SentinelStream 🛡️
### Real-Time Fraud Detection Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io)

A high-throughput, production-grade fraud detection system capable of processing transactions in real-time under 200ms. Built for neo-banks and fintech platforms using a hybrid rule-based + machine learning approach.

---

## 🏗️ Architecture

```
Client Request
      │
      ▼
┌─────────────┐
│   FastAPI   │  ← JWT Auth + Pydantic Validation
│  (API Layer)│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│      Decision Engine        │
│  ┌──────────┐ ┌──────────┐  │
│  │  Rule    │ │    ML    │  │
│  │ Engine   │ │ Engine   │  │
│  │ (Rules)  │ │(Isolation│  │
│  │          │ │ Forest)  │  │
│  └────┬─────┘ └────┬─────┘  │
│       └─────┬──────┘        │
│        Final Score          │
│    (approved/review/        │
│       rejected)             │
└────────────┬────────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌─────────┐    ┌────────────┐
│Postgres │    │   Celery   │
│(Ledger) │    │  + Redis   │
│         │    │(Async Logs)│
└─────────┘    └────────────┘
```

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | PostgreSQL 15 + SQLAlchemy |
| Caching & Queue | Redis 7 |
| Async Workers | Celery |
| ML Model | Scikit-Learn (Isolation Forest) |
| Authentication | JWT (python-jose) |
| Containerization | Docker + Docker Compose |
| Testing | PyTest |

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sentinelstream-Real-Time-Fraud-Detection-Engine.git
cd sentinelstream-Real-Time-Fraud-Detection-Engine
```

### 2. Create the `.env` file
```bash
cat > .env << 'EOF'
DB_USER=user
DB_PASSWORD=password
DB_NAME=fraud_detection_db
DB_HOST=db
DB_PORT=5432
SECRET_KEY=change-this-to-a-random-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_BROKER_URL=redis://redis:6379/0
REDIS_BACKEND_URL=redis://redis:6379/0
EOF
```

### 3. Start all services
```bash
docker compose up --build -d
```

### 4. Open Swagger UI
```
http://localhost:8000/docs
```

That's it. All 4 services (API, PostgreSQL, Redis, Celery) start automatically. ✅

---

## 📁 Project Structure

```
sentinelstream/
├── app/
│   ├── main.py             # FastAPI app + all API endpoints
│   ├── auth.py             # JWT authentication
│   ├── crud.py             # Database operations
│   ├── database.py         # SQLAlchemy engine + session
│   ├── models.py           # ORM models (User, Transaction)
│   └── schemas.py          # Pydantic request/response schemas
├── services/
│   ├── rule_engine.py      # Rule-based fraud scoring
│   ├── ml_engine.py        # Isolation Forest ML scoring
│   └── decision_engine.py  # Combines scores → final decision
├── worker/
│   └── celery_worker.py    # Async task: log suspicious transactions
├── ml/
│   ├── train_model.py      # Model training script
│   └── fraud_model.pkl     # Pre-trained Isolation Forest model
├── tests/
│   └── test_api.py         # PyTest test suite (11 tests)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env                    # (not committed to git)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | ❌ | Health check |
| POST | `/users/` | ❌ | Create a user |
| POST | `/token` | ❌ | Login → get JWT token |
| POST | `/transaction/` | ✅ | Submit transaction for fraud detection |
| GET | `/transactions/` | ✅ | Get all transactions |
| GET | `/transactions/{id}` | ✅ | Get transaction by ID |

---

## 🧪 Testing the API

### Step 1 — Create a user
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "lohith", "password": "test123"}'
```

### Step 2 — Login and get token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=lohith&password=test123"
```
Copy the `access_token` from the response.

### Step 3 — Submit a transaction
```bash
curl -X POST "http://localhost:8000/transaction/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "amount": 9999.0,
    "location": "International",
    "device_id": "BLACKLISTED_DEVICE_123"
  }'
```

**Example Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 9999.0,
  "location": "International",
  "device_id": "BLACKLISTED_DEVICE_123",
  "fraud_score": 0.82,
  "status": "rejected",
  "timestamp": "2026-03-18T10:00:00.000Z"
}
```

---

## 🤖 How Fraud Detection Works

### Rule Engine
Evaluates hard rules and adds to fraud score:
- Amount > $1,000 → +0.3
- Location is `Unknown` or `International` → +0.2
- Blacklisted device ID → +0.3
- Rapid repeat transactions → +0.4

### ML Engine (Isolation Forest)
- Trained on 2,000 synthetic transactions
- Detects anomalies based on amount, location, device, and time patterns
- Returns anomaly score normalized to 0.0–1.0

### Decision Engine
```
final_score = (0.5 × rule_score) + (0.5 × ml_score)

final_score < 0.4  → approved
final_score < 0.7  → review
final_score ≥ 0.7  → rejected
```

---

## 🧪 Run Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest tests/test_api.py -v
```

Expected: **11 tests passing** covering auth, transactions, fraud scoring, and edge cases.

---

## ⚙️ Performance

| Metric | Target | Status |
|---|---|---|
| Throughput | 100+ req/sec | ✅ |
| Latency | < 200ms | ✅ |
| Test Coverage | > 80% | ✅ |

---

## 🔒 Security

- JWT tokens with configurable expiry
- Bcrypt password hashing
- Pydantic input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- Redis-based rate limiting ready

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
