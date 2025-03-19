from fastapi import FastAPI, HTTPException, Request, Header
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from collections import deque
import time
from models import DebitRequest, TransactionResponse, BalanceResponse
from database import (
    get_account, get_account_lock, update_account_balance, 
    create_transaction, accounts_db
)
from schemas import create_transaction_schema


app = FastAPI(title="Banking Transaction API")


# 2. Scalable Banking API - Transaction Processing & Consistency


#the below api is for debit 
@app.post("/api/v1/accounts/{account_id}/debit", response_model=TransactionResponse)
async def debit_account(account_id: str, request: DebitRequest):
    lock = get_account_lock(account_id)
    
    with lock:
        account = get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account["currency"] != request.currency:
            raise HTTPException(status_code=400, detail="Currency mismatch")
        
        if account["balance"] < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        transaction_id = str(uuid.uuid4())
        
        new_balance = account["balance"] - request.amount
        update_account_balance(account_id, new_balance)
        
        timestamp = datetime.utcnow()
        transaction_data = create_transaction_schema(
            account_id=account_id,
            transaction_type="DEBIT",
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            reference=request.transaction_reference
        )
        create_transaction(transaction_id, transaction_data)
        
        return TransactionResponse(
            transaction_id=transaction_id,
            status="completed",
            account_id=account_id,
            balance=new_balance,
            timestamp=timestamp
        )

##the below api retrives the current account balance of the user
@app.get("/api/v1/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_balance(account_id: str):
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return BalanceResponse(
        account_id=account_id,
        balance=account["balance"],
        currency=account["currency"]
    )


#the below api is for the credit 

@app.post("/api/v1/accounts/{account_id}/credit", response_model=TransactionResponse)
async def credit_account(account_id: str, request: DebitRequest):
    lock = get_account_lock(account_id)
    
    with lock:
        account = get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account["currency"] != request.currency:
            raise HTTPException(status_code=400, detail="Currency mismatch")
        
        transaction_id = str(uuid.uuid4())
        
        new_balance = account["balance"] + request.amount
        update_account_balance(account_id, new_balance)
        
        timestamp = datetime.utcnow()
        transaction_data = create_transaction_schema(
            account_id=account_id,
            transaction_type="CREDIT",
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            reference=request.transaction_reference
        )
        create_transaction(transaction_id, transaction_data)
        
        return TransactionResponse(
            transaction_id=transaction_id,
            status="completed",
            account_id=account_id,
            balance=new_balance,
            timestamp=timestamp
        )


##3. Rate Limiting for Banking Transactions 
## the approach used here is Sliding Window approach to rate limiting.

rate_limit_data = {}

REQUEST_LIMIT = 5
TIME_WINDOW = 1

def rate_limiter(user_id: str):
    current_time = time.time()
    if user_id not in rate_limit_data:
        rate_limit_data[user_id] = deque()
    
    while rate_limit_data[user_id] and rate_limit_data[user_id][0] < current_time - TIME_WINDOW:
        rate_limit_data[user_id].popleft()
    
    if len(rate_limit_data[user_id]) >= REQUEST_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    rate_limit_data[user_id].append(current_time)

@app.get("/api/v1/transactions")
async def process_transaction(request: Request, x_api_key: Optional[str] = Header(None)):
    user_id = x_api_key if x_api_key else request.client.host
    rate_limiter(user_id)
    return {"message": "Transaction processed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)