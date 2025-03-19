
1. The "Invisible Bug" Challenge (Debugging & Problem-Solving) 

Reasons:
1.Deployment or Configuration Regression:

A recent code or configuration change may have inadvertently altered the fraud detection model’s parameters or logic. This could result in both decreased accuracy and increased processing times.
Debugging:

Compare the current deployment with the previous version to identify any changes in code or configuration files.
Revert to a previous deployment version in a staging environment to see if the issues resolve.
Run unit and integration tests focused on the fraud detection component to ensure that expected model parameters and thresholds are being used
Look for error messages or warnings during model initialization and during inference calls.


2.Data Pipeline or Integration Errors

 Changes in how transaction data, location, or device fingerprinting data are ingested or processed could lead to data anomalies. For instance, mismatches in data formats or missing fields can degrade the model’s performance and slow down processing as the system handles unexpected inputs.

Debugging:
Compare input data schemas pre- and post-deployment.
Validate data transformations (e.g., missing device fingerprints)
Log raw API input/output to identify discrepancies.
Test with Controlled Inputs: Run the API with known, controlled data inputs to isolate whether the issue stems from the data pipeline.

3.Performance Bottlenecks or Resource Constraints

 New logging, additional preprocessing, or inefficient code introduced in the deployment might be overloading system resources. This can cause unpredictable increases in response time and indirectly affect model accuracy if timeouts or data delays occur.

Debugging:
Monitor Resource Usage: Use performance monitoring tools to track CPU, memory, and network usage during peak times to identify potential bottlenecks.
Profiling: Profile the API code to pinpoint functions or queries that have become slower after the deployment.
Stress Testing: Simulate high loads to see if the response times degrade further or if the model behaves unpredictably.
Check for New Overheads: Review any new features or logging mechanisms that were added, and assess if they are causing additional processing delays.


New Feature:
Behavioral biometrics Integrations:
Aside from transaction history, location, and device fingerprinting, the inclusion of behavioral biometricss (e.g., typing speed, navigation patterns) can add an additional layer of security. Behavioral biometrics entails monitoring user interaction patterns—like typing rhythms, navigation patterns, and session dynamics—to create a profile of normal behavior.
Benefits:
Improved Anomaly Detection: Deviations in user behavior can be an early warning sign of fraud.
Complementary Data Source: When paired with current features, it provides a richer understanding of the user's identity and behavior.
Adaptive Learning: As time passes, the system can learn and adapt to valid changes in behavior, minimizing false positives while retaining high fraud detection accuracy.


2. Scalable Banking API - Transaction Processing & Consistency 

1. RESTful API Design:

Endpoints & Operations:
Debit Operation:
 POST /api/v1/accounts/{accountId}/debit
 Accepts the amount to withdraw. Returns the updated balance or a clear error (e.g., insufficient funds, account not found).


Credit Operation:
 POST /api/v1/accounts/{accountId}/credit
 Accepts the deposit amount. Returns the updated balance.


Balance Inquiry:
 GET /api/v1/accounts/{accountId}/balance
 Returns the current account balance.

Sample request/response for debit:
// Request
POST /api/v1/accounts/12345/debit
{
  "amount": 100.00,
  "currency": "USD",
  "description": "ATM withdrawal",
  "transactionReference": "TXN123456789"
}

// Success Response - 200 OK
{
  "transactionId": "7890123456",
  "status": "completed",
  "accountId": "12345",
  "balance": 900.00,
  "timestamp": "2025-03-12T15:04:32Z"
}

// Error Response - 400 Bad Request
{
  "error": "insufficient_funds",
  "message": "Account has insufficient funds for this transaction",
  "requestId": "REQ987654321",
  "timestamp": "2025-03-12T15:04:32Z"
}

Atomicity:
 Each operation is wrapped within a database transaction. This guarantees that either the entire operation succeeds or, if any error occurs, the transaction is rolled back (i.e., no partial updates).Use write-ahead logging (WAL) to recover from crashes


Concurrency:
 The API should efficiently handle multiple simultaneous requests by using proper locking (e.g., row-level locks with SELECT FOR UPDATE in a production-grade RDBMS) and connection pooling. This prevents race conditions when multiple requests attempt to update the same account.


Error Handling:
 Clear and concise error messages are returned if the account is not found, funds are insufficient, or if any unexpected errors occur during processing.


2.Database Schema:
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



b. Ensuring Consistency:
Use database transactions with proper isolation levels
Implement two-phase commit for cross-account transfers
Use optimistic locking with version field to prevent race conditions
Store transaction logs in a separate table for audit and recovery
Implement a transaction state machine with idempotent operations
Use write-ahead logging (WAL) to recover from crashes
c. Performance Optimizations:
Implement database sharding by account ID
Use read replicas for balance inquiries
Cache frequently accessed account information
Use a message queue for asynchronous processing of non-critical operations
Implement connection pooling to reduce database connection overhead
Use prepared statements to reduce SQL parsing overhead
3. Backend API Design - Rate Limiting for Banking Transactions
Two different approaches to rate limiting:
1. Token Bucket Algorithm
Conceptually represents each user having a bucket of tokens
Tokens are added at a constant rate (e.g., 5 tokens per second)
Each request consumes one token
If the bucket is empty, the request is rejected
Benefits:
Allows for bursts of traffic (up to bucket capacity)
Simple to implement and understand
Low memory footprint per user
Drawbacks:
Needs configuration of both rate and bucket size
May allow too many requests in short bursts
2. Sliding Window Counter
Tracks requests in small time windows (e.g., 100ms slices)
Counts requests in current window and proportion of previous window
Benefits:
More accurate rate limiting over time
Prevents bursts that might slip through fixed windows
Better handles edge cases around window boundaries
Drawbacks:
More complex to implement
Higher memory usage due to tracking multiple windows
Can be more CPU intensive
Trade-offs between the approaches:
Precision vs. Resource Usage
Token Bucket is less precise at the window boundaries but uses less memory
Sliding Window is more precise but requires storing timestamps for all recent requests
Burst Handling
Token Bucket naturally allows for controlled bursts (users can save up tokens)
Sliding Window strictly enforces the rate over the whole window, preventing bursts
Implementation Complexity
Token Bucket is simpler to implement and understand
Sliding Window requires more complex logic to handle the sliding aspect
Graceful Degradation
Token Bucket can be configured to allow occasional bursts during peak times
Sliding Window maintains stricter fairness between users under high load
Monitoring and Debugging
Token Bucket state is easier to inspect (just tokens remaining)

