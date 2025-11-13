# Production Readiness for Delta Lake and Apache Iceberg

This guide outlines best practices for running Delta Lake and Apache Iceberg in production environments.

## Table of Contents

1. [Data Organization](#data-organization)
2. [Performance Optimization](#performance-optimization)
3. [Operational Excellence](#operational-excellence)
4. [Security and Compliance](#security-and-compliance)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Disaster Recovery](#disaster-recovery)

## Data Organization

### Partitioning Strategy

**Key Principle**: Partition based on query patterns, not data volume.

#### Delta Lake Partitioning

```python
# Good: Partition by frequently filtered columns
df.write.format("delta") \
    .partitionBy("date", "region") \
    .save("/path/to/table")

# Avoid: Too many partitions
# Bad example: partitioning by user_id when you have millions of users
```

#### Iceberg Hidden Partitioning

```python
# Iceberg advantage: Change partitioning without rewriting data
spark.sql("""
    CREATE TABLE local.db.events (
        event_time TIMESTAMP,
        user_id STRING,
        event_type STRING
    ) 
    USING iceberg
    PARTITIONED BY (days(event_time))
""")

# Later, change partitioning
spark.sql("""
    ALTER TABLE local.db.events
    ADD PARTITION FIELD hours(event_time)
""")
```

### Schema Design

**Best Practices**:

1. **Use appropriate data types**
   ```python
   # Good
   schema = StructType([
       StructField("id", LongType(), False),
       StructField("timestamp", TimestampType(), False),
       StructField("amount", DecimalType(10, 2), False)
   ])
   
   # Avoid: Using String for everything
   ```

2. **Plan for evolution**
   ```python
   # Delta Lake: Enable schema evolution
   df.write.format("delta") \
       .option("mergeSchema", "true") \
       .mode("append") \
       .save("/path/to/table")
   
   # Iceberg: Schema evolution is built-in
   spark.sql("ALTER TABLE local.db.users ADD COLUMN email STRING")
   ```

3. **Document schema changes**
   ```python
   # Add comments to columns
   spark.sql("""
       ALTER TABLE delta.`/path/to/table` 
       ALTER COLUMN age COMMENT 'Age in years'
   """)
   ```

## Performance Optimization

### File Size Management

**Target**: 128 MB - 1 GB per file

#### Small File Problem

```python
# Delta Lake: Regular compaction
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/table")

# Optimize table
spark.sql("OPTIMIZE delta.`/path/to/table`")

# With Z-ordering
spark.sql("""
    OPTIMIZE delta.`/path/to/table`
    ZORDER BY (user_id, event_date)
""")
```

```python
# Iceberg: Rewrite data files
from org.apache.iceberg.actions import Actions

actions = Actions.forTable(spark, "local.db.table")
result = actions.rewriteDataFiles() \
    .option("target-file-size-bytes", str(512 * 1024 * 1024)) \
    .execute()
```

### Compaction Schedule

**Recommendation**: 
- **Streaming tables**: Daily compaction
- **Batch tables**: Weekly compaction
- **High-write tables**: Continuous auto-compaction (if available)

### Data Skipping Configuration

#### Delta Lake

```python
# Enable data skipping statistics
spark.conf.set("spark.databricks.delta.stats.skipping", "true")

# Configure statistics collection
spark.conf.set("spark.databricks.delta.stats.collect", "true")
spark.conf.set("spark.databricks.delta.stats.collect.limit", "1000")
```

#### Iceberg

```python
# Iceberg collects statistics automatically
# Optimize metadata refresh
spark.conf.set("spark.sql.iceberg.metadata.caching.enabled", "true")
```

### Query Performance

**Best Practices**:

1. **Predicate pushdown**
   ```python
   # Good: Filter early
   df = spark.read.format("delta").load("/path/to/table") \
       .filter("date >= '2024-01-01'") \
       .filter("region = 'US'")
   
   # Avoid: Filter after collecting
   ```

2. **Column pruning**
   ```python
   # Good: Select only needed columns
   df = spark.read.format("delta").load("/path/to/table") \
       .select("id", "name", "amount")
   
   # Avoid: SELECT *
   ```

3. **Broadcast joins**
   ```python
   from pyspark.sql.functions import broadcast
   
   # For small dimension tables
   large_df.join(broadcast(small_df), "key")
   ```

## Operational Excellence

### Table Maintenance

#### Vacuum Old Files

**Delta Lake**:
```python
# Clean up files older than 7 days
spark.sql("VACUUM delta.`/path/to/table` RETAIN 168 HOURS")

# Dry run to see what will be deleted
spark.sql("VACUUM delta.`/path/to/table` RETAIN 168 HOURS DRY RUN")
```

**Iceberg**:
```python
# Expire old snapshots
actions = Actions.forTable(spark, "local.db.table")
actions.expireSnapshots() \
    .expireOlderThan(System.currentTimeMillis() - (7 * 24 * 60 * 60 * 1000)) \
    .retainLast(5) \
    .execute()

# Remove orphan files
actions.removeOrphanFiles() \
    .olderThan(System.currentTimeMillis() - (3 * 24 * 60 * 60 * 1000)) \
    .execute()
```

### Maintenance Schedule

```yaml
# Recommended schedule
daily:
  - compact_streaming_tables
  - update_statistics
  - check_job_health

weekly:
  - optimize_batch_tables
  - vacuum_old_versions
  - review_performance_metrics

monthly:
  - deep_analysis
  - capacity_planning
  - cost_optimization_review
```

### Version Control for Table Metadata

**Best Practice**: Use Git to track table definitions

```sql
-- tables/users.sql
CREATE TABLE IF NOT EXISTS delta.`/path/to/users` (
    user_id BIGINT COMMENT 'Unique user identifier',
    username STRING COMMENT 'Username',
    email STRING COMMENT 'Email address',
    created_at TIMESTAMP COMMENT 'Account creation timestamp'
)
USING DELTA
PARTITIONED BY (created_date DATE)
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true'
);
```

## Security and Compliance

### Access Control

#### Table-Level Permissions

**Delta Lake (with Unity Catalog)**:
```sql
-- Grant permissions
GRANT SELECT ON TABLE delta.`/path/to/table` TO `data_analysts`;
GRANT INSERT, UPDATE ON TABLE delta.`/path/to/table` TO `data_engineers`;

-- Revoke permissions
REVOKE UPDATE ON TABLE delta.`/path/to/table` FROM `data_analysts`;
```

**Iceberg (with catalog integration)**:
```sql
-- Use your catalog's ACL system
GRANT SELECT ON TABLE iceberg.db.table TO ROLE analyst;
```

### Column-Level Security

```python
# Delta Lake: Use views for column filtering
spark.sql("""
    CREATE VIEW users_public AS
    SELECT user_id, username, created_at
    FROM delta.`/path/to/users`
    -- Excludes sensitive columns like email, ssn
""")
```

### Data Encryption

**At Rest**:
- Use cloud provider encryption (S3 SSE, Azure Storage Service Encryption)
- Enable bucket/container encryption by default

**In Transit**:
```python
# Enable SSL for Spark
spark.conf.set("spark.ssl.enabled", "true")
spark.conf.set("spark.ssl.protocol", "TLSv1.2")
```

### Audit Logging

**Delta Lake**:
```python
# Query table history for audit
history = DeltaTable.forPath(spark, "/path/to/table").history()
history.select("version", "timestamp", "operation", "operationParameters", "userName").show()
```

**Iceberg**:
```python
# Query snapshots for audit
spark.sql("SELECT * FROM local.db.table.snapshots").show()
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Storage Metrics**
   - Total table size
   - Number of files
   - Average file size
   - Partition count

2. **Performance Metrics**
   - Query latency
   - Write throughput
   - Compaction duration
   - Data skipping effectiveness

3. **Operational Metrics**
   - Failed jobs count
   - Vacuum/cleanup status
   - Concurrent operations
   - Version count

### Monitoring Implementation

```python
# Example: Delta Lake table metrics
def collect_delta_metrics(table_path):
    delta_table = DeltaTable.forPath(spark, table_path)
    
    # Get current version
    history = delta_table.history(1)
    current_version = history.select("version").collect()[0][0]
    
    # Get file statistics
    details = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
    num_files = details.numFiles
    size_in_bytes = details.sizeInBytes
    
    # Calculate metrics
    avg_file_size = size_in_bytes / num_files if num_files > 0 else 0
    
    metrics = {
        "table_path": table_path,
        "version": current_version,
        "num_files": num_files,
        "size_gb": size_in_bytes / (1024**3),
        "avg_file_size_mb": avg_file_size / (1024**2),
        "timestamp": datetime.now()
    }
    
    return metrics

# Send to monitoring system (Prometheus, CloudWatch, etc.)
```

### Alerting Rules

```yaml
# Example alerting rules
alerts:
  - name: SmallFilesProblem
    condition: avg_file_size_mb < 64
    severity: warning
    action: trigger_compaction
    
  - name: TableTooBig
    condition: size_gb > 10000
    severity: warning
    action: notify_team
    
  - name: TooManyVersions
    condition: version_count > 1000
    severity: critical
    action: run_vacuum
```

## Disaster Recovery

### Backup Strategy

**Delta Lake**:
```python
# Option 1: Deep Clone (copies data)
spark.sql("""
    CREATE TABLE delta.`/backup/users` 
    DEEP CLONE delta.`/prod/users`
""")

# Option 2: Shallow Clone (references same data)
spark.sql("""
    CREATE TABLE delta.`/backup/users` 
    SHALLOW CLONE delta.`/prod/users`
""")
```

**Iceberg**:
```python
# Snapshot-based backup
# Copy metadata and track snapshot IDs
current_snapshot = spark.sql("""
    SELECT snapshot_id 
    FROM local.db.table.snapshots 
    ORDER BY committed_at DESC 
    LIMIT 1
""").collect()[0][0]

# Store snapshot ID for potential restore
```

### Point-in-Time Recovery

**Delta Lake**:
```python
# Restore to previous version
spark.sql("""
    RESTORE TABLE delta.`/path/to/table` 
    TO VERSION AS OF 42
""")

# Or by timestamp
spark.sql("""
    RESTORE TABLE delta.`/path/to/table` 
    TO TIMESTAMP AS OF '2024-01-01 00:00:00'
""")
```

**Iceberg**:
```python
# Rollback to previous snapshot
spark.sql("""
    CALL local.system.rollback_to_snapshot('db.table', 1234567890)
""")

# Or rollback to timestamp
spark.sql("""
    CALL local.system.rollback_to_timestamp('db.table', TIMESTAMP '2024-01-01 00:00:00')
""")
```

### Cross-Region Replication

```python
# Example: Replicate Delta table to different region
source_table = DeltaTable.forPath(spark, "s3://us-east-1/prod/table")
source_df = source_table.toDF()

# Write to backup region
source_df.write.format("delta") \
    .mode("overwrite") \
    .save("s3://us-west-2/backup/table")
```

## Production Checklist

Before going to production, ensure:

### Data Layer
- [ ] Appropriate partitioning strategy defined
- [ ] Schema documented and versioned
- [ ] Data types optimized
- [ ] Compression enabled

### Performance
- [ ] Compaction schedule configured
- [ ] File sizes within target range
- [ ] Z-ordering/sorting applied (if needed)
- [ ] Statistics collection enabled

### Operations
- [ ] Vacuum/cleanup scheduled
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Runbooks documented

### Security
- [ ] Access controls configured
- [ ] Encryption enabled
- [ ] Audit logging active
- [ ] Compliance requirements met

### Testing
- [ ] Load tested with production volume
- [ ] Query performance validated
- [ ] Disaster recovery tested
- [ ] Concurrency tested

## Conclusion

Production readiness requires attention to multiple aspects: data organization, performance optimization, operational excellence, security, monitoring, and disaster recovery. Following these best practices will help ensure your Delta Lake or Apache Iceberg deployment runs smoothly in production.

## Additional Resources

- [Delta Lake Performance Tuning](https://docs.delta.io/latest/optimizations-oss.html)
- [Iceberg Performance](https://iceberg.apache.org/docs/latest/performance/)
- [Data Engineering Best Practices](../architecture/best-practices.md)

---

**Last Updated**: 2024-01-01  
**Maintainers**: Community
