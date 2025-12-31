---
title: Data Lake Migration Guide
description: Strategies and checklists for migrating Parquet lakes to Delta Lake or Apache Iceberg with minimal risk.
permalink: /docs/tutorials/migration-guide/
estimated_time: 45 min
difficulty: Intermediate
---

# Data Lake Migration Guide: From Parquet to Delta Lake & Apache Iceberg

## Overview

Migrating from traditional Parquet-based data lakes to modern table formats like Delta Lake and Apache Iceberg unlocks ACID transactions, schema evolution, and time travel capabilities. This guide provides practical, step-by-step migration strategies with validation techniques and performance optimization tips.

## Migration Scenarios

### Scenario 1: Parquet → Delta Lake (Recommended for Databricks Users)

#### When to Choose This Path
- You're migrating to Databricks ecosystem
- Need immediate ACID guarantees and time travel
- Require Change Data Feed for downstream systems
- Want built-in optimization features

#### Step-by-Step Migration Process

**Step 1: Assess Your Current Parquet Lake**
```python
# Analyze existing Parquet structure
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Get file listing and sizes
parquet_files = spark.sql("SHOW FILES IN 's3://your-bucket/data/'")
file_stats = spark.sql("""
    SELECT
        size,
        modificationTime,
        path
    FROM (
        DESCRIBE DETAIL 's3://your-bucket/data/'
    )
""")

# Check for partitioning patterns
partitioned_data = spark.read.parquet("s3://your-bucket/data/")
print(f"Partition columns: {partitioned_data.columns}")
```

**Step 2: Convert Parquet to Delta**
```python
# Method 1: Direct conversion (fastest)
spark.sql("""
    CONVERT TO DELTA parquet.`s3://your-bucket/data/`
    PARTITIONED BY (date_col STRING, region STRING)
""")

# Method 2: Read and rewrite (for transformations)
df = spark.read.parquet("s3://your-bucket/data/")
df.write \
    .format("delta") \
    .partitionBy("date_col", "region") \
    .save("s3://your-bucket/delta-data/")
```

**Step 3: Enable Advanced Features**
```python
# Enable Change Data Feed
spark.sql("""
    ALTER TABLE delta.`s3://your-bucket/delta-data/`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Add table constraints
spark.sql("""
    ALTER TABLE delta.`s3://your-bucket/delta-data/`
    ADD CONSTRAINT valid_age CHECK (age >= 0)
""")
```

**Step 4: Validation and Testing**
```python
# Compare row counts
original_count = spark.read.parquet("s3://your-bucket/data/").count()
delta_count = spark.read.format("delta").load("s3://your-bucket/delta-data/").count()

assert original_count == delta_count, "Row count mismatch!"

# Check data integrity
original_sum = spark.read.parquet("s3://your-bucket/data/").agg({"amount": "sum"}).collect()[0][0]
delta_sum = spark.read.format("delta").load("s3://your-bucket/delta-data/").agg({"amount": "sum"}).collect()[0][0]

assert abs(original_sum - delta_sum) < 0.01, "Data integrity check failed!"
```

#### Performance Optimizations
```python
# Optimize for query patterns
spark.sql("""
    OPTIMIZE delta.`s3://your-bucket/delta-data/`
    ZORDER BY (user_id, event_time)
""")

# Set table properties for auto-optimization
spark.sql("""
    ALTER TABLE delta.`s3://your-bucket/delta-data/`
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

### Scenario 2: Parquet → Apache Iceberg (Multi-Engine Migration)

#### When to Choose This Path
- Need vendor-neutral table format
- Require multi-engine compatibility (Spark + Trino + Flink)
- Want hidden partitioning flexibility
- Planning cross-cloud deployments

#### Step-by-Step Migration Process

**Step 1: Set Up Iceberg Catalog**
```python
# Configure Spark for Iceberg
spark = (SparkSession.builder
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.my_catalog.type", "hadoop")
    .config("spark.sql.catalog.my_catalog.warehouse", "s3://your-bucket/iceberg-warehouse/")
    .getOrCreate())
```

**Step 2: Migrate with Hidden Partitioning**
```python
# Create Iceberg table with hidden partitioning
spark.sql("""
    CREATE TABLE my_catalog.db.events (
        event_id BIGINT,
        event_time TIMESTAMP,
        user_id STRING,
        event_type STRING,
        payload STRING
    )
    USING iceberg
    PARTITIONED BY (days(event_time), bucket(16, user_id))
""")

# Migrate data
spark.sql("""
    INSERT INTO my_catalog.db.events
    SELECT * FROM parquet.`s3://your-bucket/parquet-data/`
""")
```

**Step 3: Leverage Iceberg Advantages**
```python
# Add partition field without rewriting data
spark.sql("""
    ALTER TABLE my_catalog.db.events
    ADD PARTITION FIELD hours(event_time)
""")

# Set table properties for optimization
spark.sql("""
    ALTER TABLE my_catalog.db.events SET TBLPROPERTIES (
        'write.wap.enabled' = 'true',
        'write.metadata.delete-after-commit.enabled' = 'true'
    )
""")
```

**Step 4: Multi-Engine Validation**
```python
# Validate in Spark
spark_count = spark.table("my_catalog.db.events").count()

# Validate in Trino (external validation)
# Run: SELECT COUNT(*) FROM iceberg.my_catalog.events
# Assert trino_count == spark_count
```

### Scenario 3: Hive → Modern Table Formats

#### Challenges with Hive Migration
- Metastore dependencies
- Legacy partitioning schemes
- SerDe configurations
- Authorization policies

#### Migration Strategy
```python
# Export Hive table metadata
hive_metadata = spark.sql("DESCRIBE FORMATTED my_hive_table")

# Create modern table with same schema
spark.sql("""
    CREATE TABLE modern_table (
        col1 STRING,
        col2 INT,
        col3 TIMESTAMP
    )
    USING delta
    PARTITIONED BY (date_col)
""")

# Migrate data with validation
spark.sql("""
    INSERT INTO modern_table
    SELECT * FROM my_hive_table
""")

# Update downstream references
# - Update ETL jobs
# - Update BI tools
# - Update permissions
```

## Common Migration Pitfalls & Solutions

### Pitfall 1: Partitioning Inconsistencies
**Problem**: Parquet partitioning doesn't match modern format requirements
**Solution**: Use hidden partitioning in Iceberg or re-partition during migration

### Pitfall 2: Schema Evolution Conflicts
**Problem**: Column additions/deletions break downstream consumers
**Solution**: Implement gradual rollout with feature flags

### Pitfall 3: Performance Regressions
**Problem**: Queries run slower after migration
**Solution**: Apply appropriate optimization (Z-ordering, compaction)

### Pitfall 4: Storage Cost Increases
**Problem**: Metadata overhead increases storage costs
**Solution**: Configure retention policies and compaction schedules

## Performance Benchmarking Post-Migration

### Benchmark Setup
```python
def benchmark_query_performance(table_path, format_type):
    """Benchmark query performance across formats"""
    start_time = time.time()
    
    if format_type == "parquet":
        df = spark.read.parquet(table_path)
    elif format_type == "delta":
        df = spark.read.format("delta").load(table_path)
    elif format_type == "iceberg":
        df = spark.table(table_path)
    
    result = df.groupBy("category").agg({"amount": "sum"}).collect()
    end_time = time.time()
    
    return end_time - start_time, len(result)
```

### Expected Performance Improvements
- **Point Queries**: 2-5x faster with statistics-based pruning
- **Range Queries**: 3-10x faster with partition pruning
- **Concurrent Reads**: 10x+ improvement with snapshot isolation
- **Updates**: Previously impossible, now sub-second

## Validation Framework

### Automated Validation Script
```bash
#!/bin/bash
# Migration validation script

echo "🔍 Validating migration..."

# Row count validation
original_count=$(spark-submit count_rows.py --table parquet_table)
new_count=$(spark-submit count_rows.py --table modern_table)

if [ "$original_count" -ne "$new_count" ]; then
    echo "❌ Row count mismatch: $original_count vs $new_count"
    exit 1
fi

# Data integrity checks
original_hash=$(spark-submit data_hash.py --table parquet_table --columns "col1,col2")
new_hash=$(spark-submit data_hash.py --table modern_table --columns "col1,col2")

if [ "$original_hash" != "$new_hash" ]; then
    echo "❌ Data integrity check failed"
    exit 1
fi

echo "✅ Migration validation passed!"
```

## Rollback Strategies

### Delta Lake Rollback
```python
# Rollback to previous version
spark.sql("""
    RESTORE TABLE delta.`/path/to/table`
    TO VERSION AS OF 0
""")
```

### Iceberg Rollback
```python
# Rollback to snapshot
spark.sql("""
    CALL system.rollback_to_snapshot('db.table', 123456789)
""")
```

## Cost Considerations

### Storage Costs
- **Metadata Overhead**: ~5-10% increase for transaction logs
- **Optimization Benefits**: Reduced storage through compaction
- **Time Travel**: Configurable retention to control costs

### Compute Costs
- **Initial Migration**: One-time cost for data conversion
- **Ongoing Operations**: Reduced compute through better pruning
- **Optimization Jobs**: Scheduled compaction and vacuum operations

## Next Steps

1. **Pilot Migration**: Start with non-critical tables
2. **Performance Testing**: Benchmark before/after migration
3. **Team Training**: Educate on new capabilities
4. **Gradual Rollout**: Migrate tables incrementally
5. **Monitoring Setup**: Implement observability for new tables

## Resources

- [Delta Lake Migration Guide](https://docs.delta.io/latest/delta-migration.html)
- [Apache Iceberg Migration](https://iceberg.apache.org/docs/latest/spark-migrating/)
- [AWS Glue Migration Patterns](https://aws.amazon.com/blogs/big-data/migrate-from-apache-hive-to-delta-lake/)

---

**Last Updated**: 2025-11-14
**Maintainers**: Community</content>
<parameter name="filePath">c:\Users\Moshe\Analytical_Guide\Datalake-Guide\docs\tutorials\migration-guide.md