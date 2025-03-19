from decimal import Decimal
import threading

# In-memory database for demonstration
accounts_db = {
    "12345": {"balance": Decimal("1000.00"), "currency": "USD", "version": 1}
}
transactions_db = {}

# Lock for thread safety
account_locks = {}

def get_account_lock(account_id: str):
    """Get or create a lock for the specified account."""
    if account_id not in account_locks:
        account_locks[account_id] = threading.RLock()
    return account_locks[account_id]

def get_account(account_id: str):
    """Get account by ID or None if not found."""
    return accounts_db.get(account_id)

def update_account_balance(account_id: str, new_balance: Decimal):
    """Update account balance and increment version."""
    if account_id in accounts_db:
        accounts_db[account_id]["balance"] = new_balance
        accounts_db[account_id]["version"] += 1
        return True
    return False

def create_transaction(transaction_id: str, transaction_data: dict):
    """Create a new transaction record."""
    transactions_db[transaction_id] = transaction_data
    return transaction_id