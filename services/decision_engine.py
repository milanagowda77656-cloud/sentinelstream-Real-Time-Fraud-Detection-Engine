
from services.rule_engine import evaluate_transaction_rules
from services.ml_engine import predict_fraud

def make_fraud_decision(transaction_data: dict) -> dict:
    """
    Combines fraud scores from rule-based and ML-based engines
    to make a final decision on transaction fraudulence.
    """
    # Get score from rule-based engine
    rule_score = evaluate_transaction_rules(transaction_data)

    # Get score from ML-based engine
    ml_score = predict_fraud(transaction_data)

    # Combine scores (example: weighted average)
    final_fraud_score = (0.5 * rule_score) + (0.5 * ml_score)

    # Determine status based on final score
    status = 'approved'
    if final_fraud_score >= 0.7:
        status = 'rejected' # High fraud risk
    elif final_fraud_score >= 0.4:
        status = 'review' # Moderate fraud risk

    return {
        'final_fraud_score': final_fraud_score,
        'status': status,
        'rule_score': rule_score,
        'ml_score': ml_score
    }

print('services/decision_engine.py created successfully.')
