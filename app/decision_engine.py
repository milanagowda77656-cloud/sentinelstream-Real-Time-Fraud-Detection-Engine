
# decision_engine.py

from app.rules import evaluate_transaction_rules
from app.ml_engine import predict_fraud, load_model

# Load ML model once when the application starts
ml_model = load_model()

def make_fraud_decision(transaction_data: dict) -> dict:
    """
    Combines fraud scores from rule-based and ML-based engines
    to make a final decision on transaction fraudulence.
    """
    # Get score from rule-based engine
    rule_score = evaluate_transaction_rules(transaction_data)

    # Get score from ML-based engine
    ml_score = predict_fraud(transaction_data, ml_model)

    # Combine scores (example: weighted average, or taking the max)
    # This is a simplified combination logic
    final_fraud_score = max(rule_score, ml_score)

    # Determine status based on final score
    status = 'pending'
    if final_fraud_score >= 0.7:
        status = 'rejected' # High fraud risk
    elif final_fraud_score >= 0.4:
        status = 'review' # Moderate fraud risk
    else:
        status = 'approved' # Low fraud risk

    return {
        'final_fraud_score': final_fraud_score,
        'status': status,
        'rule_score': rule_score,
        'ml_score': ml_score
    }

print('app/decision_engine.py created successfully.')
