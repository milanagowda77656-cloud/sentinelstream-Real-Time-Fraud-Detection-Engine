
from celery import Celery
import json
import os

# Configure Celery using environment variables
REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')
REDIS_BACKEND_URL = os.getenv('REDIS_BACKEND_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'fraud_detection_worker',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL
)

# Optional: Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def log_suspicious_transaction(transaction_id: int, details: dict):
    """Asynchronously logs suspicious transaction details."""
    # In a real application, this would write to a log file, a database, or a monitoring system
    log_entry = {
        "timestamp": str(os.getenv('CURRENT_TIMESTAMP', 'N/A')),
        "transaction_id": transaction_id,
        "log_details": details,
        "message": "Suspicious transaction logged for review."
    }
    print(f"[CELERY WORKER LOG] Suspicious transaction {transaction_id}: {json.dumps(log_entry)}")
    return log_entry

print('worker/celery_worker.py created successfully.')
