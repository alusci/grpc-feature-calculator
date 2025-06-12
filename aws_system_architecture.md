# AWS Real-Time TELCO CDR Processing Architecture

A good Kinesis + Lambda setup for handling real-time TELCO CDR (Call Detail Record) traffic needs to account for high throughput, low latency, reliability, and cost-efficiency. Here's a battle-tested architecture that balances those goals:

## ✅ Recommended Architecture Overview

### 1. Kinesis Data Streams
- **Purpose**: Ingest real-time CDR events from network components or upstream systems
- **Shards**: Start with 1 shard per ~1MB/sec or ~1000 records/sec. Auto-scaling or custom scaling is advised for bursty traffic
- **Partition Key**: Use something like `phone_number` or `cell_tower_id` to ensure balanced distribution
- **Retention**: 24 hours to 7 days depending on replay/debug needs

### 2. AWS Lambda (Kinesis Consumer)
- **Trigger**: Connected to the Kinesis stream using the enhanced fan-out or polling method
- **Batch Size**: Typically 100–1000 records per batch
- **Batch Window**: Keep it low (e.g., 1–5 sec) for real-time needs
- **Timeout**: 1–3 minutes max to avoid retries on timeout
- **Concurrency**: Use parallelization factor (up to 10 per shard) if needed to boost throughput

### 3. Processing Logic (Inside Lambda)
- Parse and validate CDRs
- Normalize time zones, phone numbers, durations, etc.
- Perform real-time aggregations (counts, velocities) using:
  - DynamoDB (as in your example, using minute-bucketed keys)
  - Optional: Use TTLs to auto-expire old aggregation rows
- Optionally: Perform fraud scoring or rule matching
- Emit downstream:
  - To another Kinesis stream, S3, or EventBridge for further processing

### 4. Downstream / Analytics Integration
- Push enriched or scored records to:
  - S3 (for Athena/Glue/EMR batch analytics)
  - OpenSearch / Elasticsearch (for real-time dashboards)
  - Redshift / Snowflake (for periodic aggregations)
  - Another Lambda or Step Function (for complex workflows or alerts)

### 5. Monitoring & Observability
- Use CloudWatch metrics for:
  - Lambda duration, errors, throttles
  - Kinesis iterator age (to detect lag)
- Enable DLQ (Dead Letter Queue) for failed Lambda records
- Optionally, write parsing or validation failures to a separate stream or log bucket

## 💡 Optimizations & Best Practices

- **Avoid "hot shards"**: Choose a partition key that spreads traffic evenly
- **Minimize Lambda cold starts**: Use provisioned concurrency if needed
- **Error Isolation**: Use try/except around record-level logic to avoid failing the whole batch
- **Schema Evolution**: Consider using Protobuf or Avro for versioned payloads, possibly with a schema registry
- **Backpressure Handling**: Monitor `GetRecords.IteratorAgeMilliseconds` — if it's high, consider more shards or parallelization