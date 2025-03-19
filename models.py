from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class DebitRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    description: Optional[str] = None
    transaction_reference: str = Field(..., min_length=5)

class CreditRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    description: Optional[str] = None
    transaction_reference: str = Field(..., min_length=5)

class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    account_id: str
    balance: Decimal
    timestamp: datetime

class BalanceResponse(BaseModel):
    account_id: str
    balance: Decimal
    currency: str