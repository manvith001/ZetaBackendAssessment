from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Literal

# Define transaction schema
TransactionSchema = Dict[str, Any]

def create_transaction_schema(
    account_id: str,
    transaction_type: Literal["DEBIT", "CREDIT"],
    amount: Decimal,
    currency: str,
    description: str = None,
    reference: str = None,
    status: Literal["PENDING", "COMPLETED", "FAILED"] = "COMPLETED"
) -> TransactionSchema:
    """Create a transaction schema object."""
    return {
        "account_id": account_id,
        "type": transaction_type,
        "amount": amount,
        "currency": currency,
        "description": description,
        "reference": reference,
        "status": status,
        "created_at": datetime.utcnow()
    }

# Define account schema
AccountSchema = Dict[str, Any]

def create_account_schema(
    balance: Decimal,
    currency: str,
    version: int = 1
) -> AccountSchema:
    """Create an account schema object."""
    return {
        "balance": balance,
        "currency": currency,
        "version": version
    }