# grpc-feature-calculator

A feature engineering system for TELCO Call Detail Record (CDR) processing that combines batch feature computation with real-time gRPC services and AWS streaming analytics.

## Overview

This repository contains:
- **Batch Feature Processing**: Spark-based feature engineering for CDR data
- **gRPC Feature Service**: Real-time feature serving with Redis caching
- **Real-time Processing**: AWS Kinesis + Lambda for streaming CDR analytics
- **Sample Data Generation**: Synthetic CDR data for testing

## Architecture

- **Batch Layer**: PySpark processes historical CDR data to compute aggregated features (counts, velocities) over multiple time windows (1d, 7d, 30d, 90d)
- **Serving Layer**: gRPC service provides low-latency feature lookups with Redis caching
- **Stream Layer**: AWS Kinesis streams process real-time CDR events with Lambda functions for velocity calculations

## Prerequisites

- Python 3.8+
- Apache Spark 3.x
- Redis server
- AWS CLI (for real-time processing)
- Protocol Buffers compiler (`protoc`)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd grpc-feature-calculator
   ```

2. **Install Python dependencies**:
   ```bash
   pip install pyspark grpcio grpcio-tools redis boto3
   ```

3. **Generate gRPC code**:
   ```bash
   python -m grpc_tools.protoc --proto_path=proto --python_out=server --grpc_python_out=server proto/feature.proto
   ```

4. **Start Redis** (if using locally):
   ```bash
   redis-server
   ```

## Usage

### 1. Generate Sample Data

```bash
cd cdr-data
python generate-data.py
```

### 2. Run Batch Feature Processing

```bash
cd batch-feature-processing
python feature_calculator.py
```
This will:
- Load CDR sample data
- Compute phone, prefix, and range-level features
- Save results to `features/phone_features/`

### 3. Start gRPC Feature Service

```bash
cd server
python feature_service.py
```
The service will run on port 50051 and serve features with Redis caching.

### 4. Real-time Processing (AWS)

Deploy the Lambda function for real-time velocity calculations:
```bash
cd real-time-feature-processing
# Deploy count_velocity_lambda.py to AWS Lambda
# Configure Kinesis Data Streams trigger
```

## Project Structure

```
├── batch-feature-processing/
│   └── feature_calculator.py    # Spark-based batch feature engineering
├── cdr-data/
│   ├── generate-data.py         # Synthetic CDR data generator
│   └── cdr_sample/             # Generated parquet files
├── features/
│   └── phone_features/         # Computed feature outputs
├── proto/
│   └── feature.proto           # gRPC service definition
├── server/
│   ├── feature_service.py      # gRPC server implementation
│   └── feature_logic.py        # Feature computation logic
└── real-time-feature-processing/
    ├── count_velocity_lambda.py      # AWS Lambda for real-time processing
    └── aws_system_architecture.md    # Architecture documentation
```

## Features Computed

- **Phone-level**: Call counts, active days, velocity over 1d/7d/30d/90d windows
- **Prefix-level**: Aggregated metrics by phone prefix
- **Range-level**: Aggregated metrics by phone range
- **Real-time**: Velocity calculations using DynamoDB time-bucketed aggregations

## API Usage

The gRPC service accepts requests with `user_id` and `ip_address` and returns computed features:

```python
# Example client usage
import grpc
import feature_pb2
import feature_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = feature_pb2_grpc.FeatureServiceStub(channel)

request = feature_pb2.FeatureRequest(user_id="123", ip_address="192.168.1.1")
response = stub.GetFeatures(request)
print(response.features)
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.