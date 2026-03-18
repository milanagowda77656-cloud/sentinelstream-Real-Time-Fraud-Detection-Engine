
import os
import joblib # For saving/loading scikit-learn models
import pandas as pd
from datetime import datetime

MODEL_PATH = './ml/fraud_model.pkl'

def _get_encoded_location(location_str: str) -> int:
    """Dummy encoding for location string."""
    # In a real system, this would use a fitted encoder from training
    return hash(location_str) % 100 if isinstance(location_str, str) else 0

def _get_encoded_device_id(device_id_str: str) -> int:
    """Dummy encoding for device ID string."""
    # In a real system, this would use a fitted encoder from training
    return hash(device_id_str) % 1000 if isinstance(device_id_str, str) else 0

def load_model():
    """
    Loads the pre-trained machine learning model.
    """
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print(f"ML Model loaded successfully from {MODEL_PATH}.")
            return model
        except Exception as e:
            print(f"Error loading ML model from {MODEL_PATH}: {e}")
            return None
    else:
        print(f"ML Model file not found at {MODEL_PATH}. Please train the model first.")
        return None

# Load ML model once when the application starts
_ml_model = load_model()

def predict_fraud(transaction_data: dict) -> float:
    """
    Uses the loaded ML model to predict a fraud score for a given transaction.
    The `transaction_data` is preprocessed into features that the model expects.
    Returns a fraud score between 0.0 and 1.0.
    """
    if _ml_model is None:
        print("No ML model loaded, returning default fraud score of 0.0.")
        return 0.0

    try:
        # Preprocess transaction data to match training features
        amount = transaction_data.get('amount', 0.0)
        location_encoded = _get_encoded_location(transaction_data.get('location', 'unknown'))
        device_id_encoded = _get_encoded_device_id(transaction_data.get('device_id', 'unknown'))

        # Extract transaction hour from timestamp
        timestamp_str = transaction_data.get('timestamp')
        if isinstance(timestamp_str, datetime):
            transaction_hour = timestamp_str.hour
        else:
            # Fallback if timestamp is not datetime object (e.g., string from request body)
            try:
                transaction_hour = datetime.fromisoformat(timestamp_str).hour
            except (ValueError, TypeError): # Handle cases where timestamp might be missing or malformed
                transaction_hour = datetime.utcnow().hour # Default to current hour

        features = pd.DataFrame([[amount, location_encoded, device_id_encoded, transaction_hour]],
                                columns=['amount', 'location_encoded', 'device_id_encoded', 'transaction_hour'])

        # Get anomaly score from IsolationForest model
        # IsolationForest decision_function: lower score indicates higher anomaly
        anomaly_score = _ml_model.decision_function(features)[0]

        # Normalize the anomaly score to a fraud probability (0 to 1)
        # This is a heuristic; a more robust normalization might involve fitting a scaler
        # or using expected score range from training.
        # Let's assume scores roughly range from -0.5 to 0.5 for demonstration
        # and map lower scores to higher fraud risk.
        # If score is -0.5 (very anomalous), fraud_score ~ 1.0
        # If score is 0.5 (very normal), fraud_score ~ 0.0
        normalized_fraud_score = (0.5 - anomaly_score) / 1.0 # Adjust denominator based on expected score range
        final_fraud_score = max(0.0, min(1.0, normalized_fraud_score))

        print(f"ML prediction: Anomaly Score={anomaly_score:.4f}, Fraud Score={final_fraud_score:.4f}")
        return final_fraud_score

    except Exception as e:
        print(f"Error during ML fraud prediction: {e}. Returning default fraud score.")
        return 0.0

print('services/ml_engine.py created successfully.')
