# The "Invisible Bug" Challenge (Debugging & Problem-Solving)

## Deployment or Configuration Regression
A recent code or configuration change may have inadvertently altered the fraud detection model’s parameters or logic, resulting in both decreased accuracy and increased processing times.

### Debugging:
- Compare the current deployment with the previous version to identify any changes in code or configuration files.
- Revert to a previous deployment version in a staging environment to see if the issues resolve.
- Run unit and integration tests focused on the fraud detection component to ensure that expected model parameters and thresholds are being used.
- Look for error messages or warnings during model initialization and inference calls.

## Data Pipeline or Integration Errors
Changes in how transaction data, location, or device fingerprinting data are ingested or processed could lead to data anomalies. Mismatches in data formats or missing fields can degrade the model’s performance and slow down processing.

### Debugging:
- Compare input data schemas pre- and post-deployment.
- Validate data transformations (e.g., missing device fingerprints).
- Log raw API input/output to identify discrepancies.
- Test with controlled inputs: Run the API with known, controlled data inputs to isolate whether the issue stems from the data pipeline.

## Performance Bottlenecks or Resource Constraints
New logging, additional preprocessing, or inefficient code introduced in the deployment might be overloading system resources. This can cause unpredictable increases in response time and indirectly affect model accuracy if timeouts or data delays occur.

### Debugging:
- Monitor resource usage: Use performance monitoring tools to track CPU, memory, and network usage during peak times to identify potential bottlenecks.
- Profiling: Profile the API code to pinpoint functions or queries that have become slower after deployment.
- Stress testing: Simulate high loads to see if response times degrade further or if the model behaves unpredictably.
- Check for new overheads: Review any new features or logging mechanisms that were added and assess if they are causing additional processing delays.

## New Feature: Behavioral Biometrics Integrations
Behavioral biometrics (e.g., typing speed, navigation patterns) can add an additional layer of security. Monitoring user interaction patterns helps create a profile of normal behavior.

### Benefits:
- Improved anomaly detection: Deviations in user behavior can be an early warning sign of fraud.
- Complementary data source: Enhances existing fraud detection mechanisms.
- Adaptive learning: The system learns and adapts to valid changes in behavior, minimizing false positives while maintaining high fraud detection accuracy.

# Scalable Banking API - Transaction Processing & Consistency

## RESTful API Design

### Endpoints & Operations
#### Debit Operation:
**POST /api/v1/accounts/{accountId}/debit**
Accepts the amount to withdraw and returns the updated balance or an error message.

#### Credit Operation:
**POST /api/v1/accounts/{accountId}/credit**
Accepts the deposit amount and returns the updated balance.

#### Balance Inquiry:
**GET /api/v1/accounts/{accountId}/balance**
Returns the current account balance.

### Sample Request/Response for Debit:
#### Request:
```json
POST /api/v1/accounts/12345/debit
{
  "amount": 100.00,
  "currency": "USD",
  "description": "ATM withdrawal",
  "transactionReference": "TXN123456789"
}
```

#### Success Response:
```json
{
  "transactionId": "7890123456",
  "status": "completed",
  "accountId": "12345",
  "balance": 900.00,
  "timestamp": "2025-03-12T15:04:32Z"
}
```

#### Error Response:
```json
{
  "error": "insufficient_funds",
  "message": "Account has insufficient funds for this transaction",
  "requestId": "REQ987654321",
  "timestamp": "2025-03-12T15:04:32Z"
}
```

### Atomicity
- Each operation is wrapped within a database transaction.
- Ensures complete success or rollback.
- Uses write-ahead logging (WAL) for crash recovery.

### Concurrency
- Handles multiple requests efficiently using row-level locks (e.g., SELECT FOR UPDATE).
- Uses connection pooling to prevent race conditions.

### Error Handling
- Returns clear and concise error messages.

## Database Schema
```sql
CREATE TABLE accounts (
  account_id VARCHAR(50) PRIMARY KEY,
  balance DECIMAL(19, 4) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  version INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE transactions (
  transaction_id VARCHAR(50) PRIMARY KEY,
  account_id VARCHAR(50) NOT NULL,
  transaction_type ENUM('DEBIT', 'CREDIT') NOT NULL,
  amount DECIMAL(19, 4) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  description TEXT,
  reference VARCHAR(100),
  status ENUM('PENDING', 'COMPLETED', 'FAILED') NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX idx_account_id ON transactions(account_id);
CREATE INDEX idx_created_at ON transactions(created_at);
```

## Ensuring Consistency
- Use database transactions with proper isolation levels.
- Implement two-phase commit for cross-account transfers.
- Use optimistic locking with a version field.
- Store transaction logs for audit and recovery.
- Implement a transaction state machine with idempotent operations.
- Use write-ahead logging (WAL) for crash recovery.

## Performance Optimizations
- Implement database sharding by account ID.
- Use read replicas for balance inquiries.
- Cache frequently accessed account information.
- Use a message queue for asynchronous processing.
- Implement connection pooling to reduce overhead.
- Use prepared statements to optimize SQL parsing.

# Backend API Design - Rate Limiting for Banking Transactions

## Approaches to Rate Limiting

### Token Bucket Algorithm
- Users have a bucket of tokens.
- Tokens replenish at a constant rate.
- Requests consume tokens; if empty, requests are rejected.

#### Benefits:
- Allows controlled bursts.
- Simple to implement with low memory overhead.

#### Drawbacks:
- Needs rate and bucket size configuration.
- May allow too many short bursts.

### Sliding Window Counter
- Tracks requests in time windows.
- Counts requests in current and previous windows proportionally.

#### Benefits:
- More accurate over time.
- Prevents excessive bursts.

#### Drawbacks:
- More complex to implement.
- Higher memory and CPU usage.

## Trade-offs
- **Precision vs. Resource Usage:** Token Bucket is less precise but lightweight; Sliding Window is more accurate but resource-intensive.
- **Burst Handling:** Token Bucket allows bursts; Sliding Window strictly enforces rate limits.
- **Implementation Complexity:** Token Bucket is simpler; Sliding Window is more complex.
- **Monitoring:** Token Bucket is easier to inspect; Sliding Window tracks detailed request timestamps.

