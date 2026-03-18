import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Define model path
MODEL_PATH = './ml/fraud_model.pkl'

def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    data = {
        'amount': np.random.normal(loc=100, scale=50, size=n_samples),
        'location_encoded': np.random.randint(0, 5, size=n_samples), # 0-4 for different locations
        'device_id_encoded': np.random.randint(0, 10, size=n_samples), # 0-9 for different devices
        'transaction_hour': np.random.randint(0, 24, size=n_samples)
    }
    df = pd.DataFrame(data)

    # Introduce some anomalies (fraudulent transactions)
    # High amount, unusual location, unusual device_id
    n_anomalies = int(n_samples * 0.05)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)

    df.loc[anomaly_indices, 'amount'] = np.random.normal(loc=1000, scale=200, size=n_anomalies) # High amounts
    df.loc[anomaly_indices, 'location_encoded'] = np.random.randint(5, 10, size=n_anomalies) # Unusual locations
    df.loc[anomaly_indices, 'device_id_encoded'] = np.random.randint(10, 15, size=n_anomalies) # Unusual devices

    # Mark anomalies for demonstration purposes, IsolationForest is unsupervised
    df['is_fraud'] = 0
    df.loc[anomaly_indices, 'is_fraud'] = 1

    return df

def train_and_save_model():
    print("Generating synthetic data...")
    df = generate_synthetic_data(n_samples=2000)
    X = df[['amount', 'location_encoded', 'device_id_encoded', 'transaction_hour']]

    print("Training Isolation Forest model...")
    # Isolation Forest is good for anomaly detection
    model = IsolationForest(random_state=42, contamination=0.05) # contamination set to expected proportion of anomalies
    model.fit(X)

    print(f"Saving model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved successfully.")

    # Optional: Evaluate the model (for supervised metrics if 'is_fraud' was known)
    # predictions = model.predict(X)
    # df['anomaly_score'] = model.decision_function(X)
    # df['is_anomaly'] = (predictions == -1).astype(int)
    # if 'is_fraud' in df.columns:
    #    print("\nClassification Report (Anomaly vs. Fraud Labels):\n")
    #    print(classification_report(df['is_fraud'], df['is_anomaly']))

if __name__ == '__main__':
    train_and_save_model()
