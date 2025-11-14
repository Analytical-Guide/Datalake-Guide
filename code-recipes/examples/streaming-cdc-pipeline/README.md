---
title: Streaming CDC Pipeline Recipe
permalink: /code-recipes/examples/streaming-cdc-pipeline/
description: End-to-end guide for building a streaming CDC pipeline on Delta Lake with Structured Streaming.
---

# Streaming CDC Pipeline Recipe

This recipe demonstrates building a complete real-time Change Data Capture (CDC) pipeline using Delta Lake and Apache Spark Structured Streaming.

## Overview

Change Data Capture is essential for keeping analytical datasets synchronized with operational systems. This example shows how to:

- Ingest CDC events from various sources (Kafka, files)
- Process events with exactly-once semantics
- Apply changes to target tables using MERGE operations
- Handle schema evolution in streaming contexts
- Monitor pipeline health and performance

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source DB     │    │   CDC Capture    │    │   Message Bus   │
│   (MySQL, etc.) │───▶│   (Debezium)     │───▶│   (Kafka)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  File System    │    │                  │    │  Streaming      │
│  (JSON files)   │───▶│  Spark Streaming │───▶│  Processing    │
└─────────────────┘    │                  │    └─────────────────┘
                       │                  │             │
┌─────────────────┐    │  CDC Processor   │    ┌─────────────────┐
│  Batch Files    │───▶│                  │    │  Deduplication  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Delta Lake    │    │   Schema         │    │   Target        │
│   Tables        │◀───│   Evolution      │◀───│   Tables        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Change Data    │    │   Monitoring     │    │   Alerting      │
│  Feed           │◀───│   Dashboard      │───▶│   System        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Pipeline Flow:**
1. **Ingestion**: CDC events from Kafka topics or JSON files
2. **Parsing**: Extract table name, operation type, before/after states
3. **Processing**: Add metadata, handle schema evolution, deduplication
4. **Storage**: Write to Delta tables with ACID guarantees
5. **Monitoring**: Track pipeline health and performance metrics

## Key Features Demonstrated

### 1. Streaming Data Ingestion
- **Kafka Integration**: Real-time event consumption
- **File-based Sources**: For testing and development
- **Schema Evolution**: Handle changing data structures
- **Watermarking**: Handle late-arriving data

### 2. CDC Processing Patterns
- **Deduplication**: Remove duplicate events
- **Idempotent Processing**: Handle reprocessed events
- **Transaction Ordering**: Maintain data consistency
- **Error Handling**: Graceful failure recovery

### 3. Target Table Updates
- **MERGE Operations**: Upsert/delete patterns
- **Primary Key Handling**: Complex key structures
- **Change Data Feed**: Track all modifications
- **ACID Guarantees**: Transactional consistency

### 4. Monitoring & Observability
- **Pipeline Health**: Query status monitoring
- **Performance Metrics**: Throughput and latency tracking
- **Error Reporting**: Comprehensive error handling
- **Alerting**: Automated issue detection

## Running the Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CDC pipeline demo
python solution.py
```

## Expected Output

The script will:
1. Generate sample CDC events for customers and orders
2. Start streaming pipelines for both tables
3. Process events in real-time
4. Apply changes to target Delta tables
5. Display pipeline health and final results

## Key Classes

### `StreamingCDCProcessor`
Main class managing the CDC pipeline:

- `start_cdc_pipeline()`: Initialize all streaming queries
- `_process_cdc_events()`: Handle event processing and deduplication
- `apply_changes_to_target()`: Apply changes via MERGE operations
- `monitor_pipeline_health()`: Track pipeline status

### CDC Event Structure
```json
{
  "table_name": "customers",
  "operation": "INSERT",
  "before": null,
  "after": "{\"customer_id\": \"CUST_0001\", \"name\": \"John Doe\"}",
  "timestamp": "2024-01-01T10:00:00Z",
  "transaction_id": "TXN_1001",
  "primary_key": "{\"customer_id\": \"CUST_0001\"}"
}
```

## Configuration

### Pipeline Configuration
```python
config = {
    "checkpoint_dir": "/tmp/cdc-checkpoints",
    "tables": {
        "customers": {
            "source_type": "kafka",  # or "file"
            "kafka": {
                "topic": "cdc.customers",
                "bootstrap_servers": "localhost:9092"
            },
            "target_table": "/path/to/customers",
            "primary_key": ["customer_id"]
        }
    }
}
```

### Source Types Supported

1. **Kafka**: Production-ready event streaming
2. **File**: Development and testing
3. **Custom**: Extensible for other sources

## Production Considerations

### Scalability
- **Partitioning**: Distribute load across workers
- **Batch Sizing**: Optimize micro-batch intervals
- **Resource Allocation**: Configure appropriate memory/CPU

### Reliability
- **Checkpointing**: Enable fault tolerance
- **Idempotency**: Handle duplicate processing
- **Backpressure**: Handle load spikes gracefully

### Monitoring
- **Metrics Collection**: Track throughput and latency
- **Health Checks**: Automated pipeline validation
- **Alerting**: Proactive issue notification

## Troubleshooting

### Common Issues

1. **Checkpoint Conflicts**: Clear checkpoints for fresh starts
2. **Schema Mismatches**: Validate source/target schemas
3. **Memory Issues**: Adjust batch sizes and intervals
4. **Network Timeouts**: Configure appropriate timeouts

### Recovery Procedures
- **Restart from Checkpoint**: Automatic recovery
- **Manual Replay**: Reprocess specific time ranges
- **Data Repair**: Fix corrupted target tables

## Performance Tuning

### Streaming Optimizations
```python
# Optimize batch processing
spark.conf.set("spark.sql.streaming.fileSink.log.cleanupDelay", "86400000")
spark.conf.set("spark.sql.streaming.fileSink.log.deletion", "true")

# Memory management
spark.conf.set("spark.sql.streaming.stateStore.minDeltasForSnapshot", "10")
```

### CDC-Specific Tuning
- **Deduplication Windows**: Balance accuracy vs performance
- **Merge Optimization**: Use partition pruning
- **Caching**: Cache frequently accessed data

## Integration Patterns

### With Kafka
```python
# Consumer configuration
kafka_options = {
    "kafka.bootstrap.servers": "broker1:9092,broker2:9092",
    "kafka.group.id": "cdc-consumer",
    "kafka.auto.offset.reset": "earliest",
    "kafka.enable.auto.commit": "false"
}
```

### With Delta Live Tables
- **Incremental Processing**: Build on CDC foundation
- **Quality Enforcement**: Add data validation rules
- **Lineage Tracking**: End-to-end data lineage

## Next Steps

- Implement custom CDC sources (Debezium, etc.)
- Add data quality validation rules
- Integrate with schema registries
- Implement advanced monitoring dashboards
- Add support for complex transformations