
# rules.py

def evaluate_transaction_rules(transaction: dict) -> float:
    """
    Evaluates a transaction against a set of predefined rules to determine a fraud score.
    Returns a preliminary fraud score (0.0 to 1.0).
    """
    fraud_score = 0.0

    # Rule 1: High amount transaction
    # If amount is greater than 1000, add 0.3 to fraud score
    if transaction.get('amount', 0) > 1000:
        fraud_score += 0.3

    # Rule 2: Unusual location (example: location is 'Unknown' or 'International')
    # If location is 'Unknown' or 'International', add 0.2 to fraud score
    if transaction.get('location') in ['Unknown', 'International']:
        fraud_score += 0.2

    # Rule 3: High frequency of transactions (placeholder for actual implementation)
    # This would typically involve checking historical transactions for the user_id
    # For this example, we'll simulate a simple check.
    # If a transaction has a 'high_frequency_flag' (hypothetical), add 0.2
    if transaction.get('high_frequency_flag', False):
        fraud_score += 0.2

    # Rule 4: Device ID blacklisting (placeholder for actual implementation)
    # Hypothetically, if device_id is in a blacklist, add 0.3
    if transaction.get('device_id') == 'BLACKLISTED_DEVICE_123':
        fraud_score += 0.3

    # Ensure fraud_score does not exceed 1.0
    return min(fraud_score, 1.0)

print('app/rules.py created successfully.')
