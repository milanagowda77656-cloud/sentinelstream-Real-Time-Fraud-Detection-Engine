from celery import Celery
import json
import os

# Configure Celery using environment variables
REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')
REDIS_BACKEND_URL = os.getenv('REDIS_BACKEND_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'fraud_detection_tasks',
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
def log_transaction_processing(transaction_id: int, details: dict):
    """Asynchronously logs transaction processing details."""
    # In a real application, this would write to a log file, a database, or a monitoring system
    log_entry = {
        "timestamp": str(os.getenv('CURRENT_TIMESTAMP', 'N/A')),
        "transaction_id": transaction_id,
        "log_details": details
    }
    print(f"[CELERY LOG] Transaction {transaction_id} processed: {json.dumps(log_entry)}")
    return log_entry

print('app/tasks.py created successfully.')
