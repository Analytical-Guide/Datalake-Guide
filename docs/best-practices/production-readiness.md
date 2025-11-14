---
title: Production Readiness for Delta Lake and Apache Iceberg
description: Detailed checklist covering data organization, performance, operations, and governance for production deployments.
permalink: /docs/best-practices/production-readiness/
---

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

### Advanced Compaction Strategies

#### Intelligent Compaction Based on Access Patterns

**Delta Lake - Adaptive Optimization**:
```python
# Analyze query patterns to determine optimization strategy
from delta.tables import DeltaTable

def optimize_based_on_usage(table_path, days_to_analyze=30):
    """Optimize table based on recent query patterns"""
    
    # Get recent query history (requires system access logs)
    recent_queries = get_recent_queries(table_path, days_to_analyze)
    
    # Analyze access patterns
    frequently_filtered_cols = analyze_filter_columns(recent_queries)
    access_patterns = analyze_access_patterns(recent_queries)
    
    # Apply appropriate optimization
    if access_patterns["point_queries"] > 0.7:
        # Point queries dominant - optimize for seek performance
        spark.sql(f"""
            OPTIMIZE delta.`{table_path}`
            ZORDER BY ({','.join(frequently_filtered_cols[:3])})
        """)
    elif access_patterns["range_scans"] > 0.6:
        # Range scans dominant - optimize for sequential reads
        spark.sql(f"""
            OPTIMIZE delta.`{table_path}`
            ZORDER BY (date_col, {','.join(frequently_filtered_cols[:2])})
        """)
    else:
        # Balanced workload - standard optimization
        spark.sql(f"OPTIMIZE delta.`{table_path}`")
```

**Iceberg - Multi-Level Compaction**:
```python
from org.apache.iceberg.actions import Actions

def multi_level_compaction(table_name):
    """Apply different compaction strategies based on data characteristics"""
    
    actions = Actions.forTable(spark, table_name)
    
    # Level 1: Small file compaction
    actions.rewriteDataFiles() \
        .option("target-file-size-bytes", "134217728") \  # 128MB
        .option("min-file-size-bytes", "1048576") \      # 1MB
        .execute()
    
    # Level 2: Partition-level optimization
    actions.rewriteManifests().execute()
    
    # Level 3: Statistics refresh
    actions.updateStatistics().execute()
```

#### Automated Compaction Pipelines

**Scheduled Optimization Workflow**:
```yaml
# GitHub Actions workflow for automated maintenance
name: Table Maintenance
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday 2 AM
  workflow_dispatch:

jobs:
  optimize-tables:
    runs-on: ubuntu-latest
    steps:
      - name: Optimize Delta Tables
        run: |
          # Get tables needing optimization
          tables=$(databricks tables list --format json | jq -r '.[] | select(.size_bytes > 1000000000) | .name')
          
          for table in $tables; do
            echo "Optimizing $table..."
            databricks sql execute --query "OPTIMIZE $table ZORDER BY (date_col, user_id)"
          done
```

#### Compaction Monitoring & Alerting

```python
def monitor_compaction_health(table_path):
    """Monitor compaction effectiveness and alert if needed"""
    
    # Get current table statistics
    details = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
    
    metrics = {
        "total_files": details.numFiles,
        "total_size": details.sizeInBytes,
        "avg_file_size": details.sizeInBytes / details.numFiles if details.numFiles > 0 else 0,
        "small_files_ratio": calculate_small_files_ratio(table_path)
    }
    
    # Alert thresholds
    if metrics["avg_file_size"] < 64 * 1024 * 1024:  # 64MB
        alert(f"Table {table_path} needs compaction - avg file size: {metrics['avg_file_size'] / (1024*1024):.1f}MB")
    
    if metrics["small_files_ratio"] > 0.3:  # 30% small files
        alert(f"Table {table_path} has {metrics['small_files_ratio']*100:.1f}% small files")
    
    return metrics

def calculate_small_files_ratio(table_path):
    """Calculate ratio of small files (< 128MB)"""
    files_df = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
    small_files = files_df.filter("size < 134217728").count()  # 128MB
    total_files = files_df.count()
    return small_files / total_files if total_files > 0 else 0
```

### Table Maintenance Automation

#### Predictive Maintenance System

```python
class TableMaintenancePredictor:
    """Predict when tables need maintenance based on usage patterns"""
    
    def __init__(self, monitoring_window_days=30):
        self.monitoring_window = monitoring_window_days
        self.performance_thresholds = {
            "query_slowdown_ratio": 1.5,  # 50% slowdown
            "file_count_growth": 0.2,     # 20% file count increase
            "avg_file_size_degradation": 0.3  # 30% size reduction
        }
    
    def predict_maintenance_needs(self, table_path):
        """Analyze table metrics and predict maintenance requirements"""
        
        # Collect historical metrics
        historical_metrics = self.get_historical_metrics(table_path)
        
        predictions = {}
        
        # Compaction prediction
        if self.needs_compaction(historical_metrics):
            predictions["compaction"] = {
                "urgency": "high",
                "estimated_benefit": "25% query performance improvement",
                "recommended_schedule": "within 24 hours"
            }
        
        # Vacuum prediction
        if self.needs_vacuum(historical_metrics):
            predictions["vacuum"] = {
                "urgency": "medium",
                "estimated_benefit": "15% storage reduction",
                "recommended_schedule": "within 7 days"
            }
        
        # Reorganization prediction
        if self.needs_reorganization(historical_metrics):
            predictions["reorganization"] = {
                "urgency": "low",
                "estimated_benefit": "10% performance improvement",
                "recommended_schedule": "within 30 days"
            }
        
        return predictions
    
    def needs_compaction(self, metrics):
        """Determine if table needs compaction"""
        recent_avg_size = metrics["avg_file_size"][-7:]  # Last 7 days
        baseline_avg = sum(metrics["avg_file_size"][:-7]) / len(metrics["avg_file_size"][:-7])
        
        return min(recent_avg_size) < baseline_avg * 0.7  # 30% degradation
    
    def needs_vacuum(self, metrics):
        """Determine if table needs vacuum"""
        recent_versions = len(metrics["versions"][-30:])  # Last 30 days
        return recent_versions > 100  # Too many versions
    
    def needs_reorganization(self, metrics):
        """Determine if table needs reorganization"""
        recent_query_time = metrics["avg_query_time"][-7:]
        baseline_time = sum(metrics["avg_query_time"][:-7]) / len(metrics["avg_query_time"][:-7])
        
        return max(recent_query_time) > baseline_time * self.performance_thresholds["query_slowdown_ratio"]
```

#### Snapshot Management Strategies

**Delta Lake - Intelligent Version Control**:
```python
def manage_delta_versions(table_path, retention_policy):
    """Implement intelligent version retention"""
    
    delta_table = DeltaTable.forPath(spark, table_path)
    history = delta_table.history()
    
    # Categorize versions
    versions_to_keep = []
    
    for row in history.collect():
        version_age_days = (current_timestamp() - row.committedAt).days
        
        # Always keep recent versions
        if version_age_days <= retention_policy["recent_days"]:
            versions_to_keep.append(row.version)
            continue
        
        # Keep important milestones
        if is_milestone_version(row):
            versions_to_keep.append(row.version)
            continue
        
        # Keep versions with significant changes
        if has_significant_changes(row):
            versions_to_keep.append(row.version)
            continue
    
    # Vacuum old versions not in keep list
    all_versions = [row.version for row in history.collect()]
    versions_to_remove = set(all_versions) - set(versions_to_keep)
    
    if versions_to_remove:
        # Careful vacuum - only remove versions older than safety threshold
        safe_versions = [v for v in versions_to_remove 
                        if get_version_age(v) > retention_policy["safety_days"]]
        
        for version in safe_versions:
            # Note: Delta doesn't support selective version deletion
            # This would require full vacuum with careful retention settings
            pass

def is_milestone_version(version_info):
    """Check if version represents a milestone"""
    # Check commit message for keywords
    return "milestone" in version_info.operationParameters.get("commit_message", "").lower()

def has_significant_changes(version_info):
    """Check if version contains significant data changes"""
    # Analyze operation metrics
    operation = version_info.operation
    operation_metrics = version_info.operationMetrics
    
    if operation == "MERGE":
        return operation_metrics.get("numTargetRowsUpdated", 0) > 10000
    elif operation == "DELETE":
        return operation_metrics.get("numDeletedRows", 0) > 5000
    
    return False
```

**Iceberg - Flexible Snapshot Policies**:
```python
def iceberg_snapshot_strategy(table_name, strategy_config):
    """Implement flexible snapshot retention strategies"""
    
    actions = Actions.forTable(spark, table_name)
    
    if strategy_config["strategy"] == "time_based":
        # Keep snapshots for specified duration
        actions.expireSnapshots() \
            .expireOlderThan(System.currentTimeMillis() - 
                           strategy_config["retention_days"] * 24 * 60 * 60 * 1000) \
            .retainLast(strategy_config["min_snapshots"]) \
            .execute()
    
    elif strategy_config["strategy"] == "size_based":
        # Keep snapshots until total size exceeds limit
        total_size = get_table_size(table_name)
        if total_size > strategy_config["max_size_bytes"]:
            actions.expireSnapshots() \
                .expireOldestOlderThan(System.currentTimeMillis() - 
                                     strategy_config["min_age_days"] * 24 * 60 * 60 * 1000) \
                .execute()
    
    elif strategy_config["strategy"] == "branch_based":
        # Keep snapshots for specific branches/tags
        branches_to_keep = strategy_config["protected_branches"]
        # Implementation would filter snapshots by branch metadata
        pass
```

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

## Data Validation Patterns

### Automated Data Quality Framework

#### Schema Validation Pipeline

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import logging

class DataValidator:
    """Comprehensive data validation framework"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        self.validation_results = []
        
    def validate_table_schema(self, table_path, expected_schema):
        """Validate table schema against expected structure"""
        
        try:
            # Read table with schema inference
            df = self.spark.read.format("delta").load(table_path)
            actual_schema = df.schema
            
            # Compare schemas
            schema_issues = self.compare_schemas(expected_schema, actual_schema)
            
            if schema_issues:
                self.log_validation_error("schema_mismatch", 
                                        f"Schema issues found: {schema_issues}")
                return False
            
            return True
            
        except Exception as e:
            self.log_validation_error("schema_read_error", str(e))
            return False
    
    def validate_data_quality(self, table_path, quality_rules):
        """Apply data quality rules to table"""
        
        df = self.spark.read.format("delta").load(table_path)
        
        quality_results = {}
        
        for rule_name, rule_config in quality_rules.items():
            rule_type = rule_config["type"]
            
            if rule_type == "not_null":
                quality_results[rule_name] = self.check_not_null(df, rule_config["columns"])
            
            elif rule_type == "unique":
                quality_results[rule_name] = self.check_unique(df, rule_config["columns"])
            
            elif rule_type == "range":
                quality_results[rule_name] = self.check_range(df, rule_config["column"], 
                                                            rule_config["min"], rule_config["max"])
            
            elif rule_type == "regex":
                quality_results[rule_name] = self.check_regex(df, rule_config["column"], 
                                                            rule_config["pattern"])
            
            elif rule_type == "referential_integrity":
                quality_results[rule_name] = self.check_referential_integrity(
                    df, rule_config["column"], rule_config["reference_table"], 
                    rule_config["reference_column"])
        
        return quality_results
    
    def check_not_null(self, df, columns):
        """Check for null values in specified columns"""
        results = {}
        
        for column in columns:
            null_count = df.filter(col(column).isNull()).count()
            total_count = df.count()
            
            results[column] = {
                "null_count": null_count,
                "null_percentage": (null_count / total_count) * 100 if total_count > 0 else 0,
                "passed": null_count == 0
            }
        
        return results
    
    def check_unique(self, df, columns):
        """Check for uniqueness in specified columns"""
        results = {}
        
        for column in columns:
            total_count = df.count()
            distinct_count = df.select(column).distinct().count()
            
            results[column] = {
                "total_count": total_count,
                "distinct_count": distinct_count,
                "duplicates": total_count - distinct_count,
                "passed": total_count == distinct_count
            }
        
        return results
    
    def check_range(self, df, column, min_val, max_val):
        """Check if values fall within specified range"""
        total_count = df.count()
        out_of_range_count = df.filter(~col(column).between(min_val, max_val)).count()
        
        return {
            "total_count": total_count,
            "out_of_range_count": out_of_range_count,
            "out_of_range_percentage": (out_of_range_count / total_count) * 100 if total_count > 0 else 0,
            "passed": out_of_range_count == 0
        }
    
    def check_regex(self, df, column, pattern):
        """Check if values match regex pattern"""
        from pyspark.sql.functions import regexp_extract
        
        total_count = df.count()
        matching_count = df.filter(col(column).rlike(pattern)).count()
        
        return {
            "total_count": total_count,
            "matching_count": matching_count,
            "non_matching_count": total_count - matching_count,
            "passed": total_count == matching_count
        }
    
    def check_referential_integrity(self, df, column, ref_table, ref_column):
        """Check referential integrity between tables"""
        ref_df = self.spark.table(ref_table)
        
        # Get distinct values from both tables
        source_values = df.select(column).distinct()
        ref_values = ref_df.select(ref_column).distinct()
        
        # Find orphan records
        orphans = source_values.join(ref_values, 
                                   source_values[column] == ref_values[ref_column], 
                                   "left_anti")
        
        orphan_count = orphans.count()
        total_count = source_values.count()
        
        return {
            "total_values": total_count,
            "orphan_count": orphan_count,
            "orphan_percentage": (orphan_count / total_count) * 100 if total_count > 0 else 0,
            "passed": orphan_count == 0
        }
    
    def compare_schemas(self, expected, actual):
        """Compare expected vs actual schema"""
        issues = []
        
        expected_fields = {field.name: field for field in expected.fields}
        actual_fields = {field.name: field for field in actual.fields}
        
        # Check for missing fields
        for field_name in expected_fields:
            if field_name not in actual_fields:
                issues.append(f"Missing field: {field_name}")
        
        # Check for extra fields
        for field_name in actual_fields:
            if field_name not in expected_fields:
                issues.append(f"Unexpected field: {field_name}")
        
        # Check field types
        for field_name in expected_fields:
            if field_name in actual_fields:
                expected_type = expected_fields[field_name].dataType
                actual_type = actual_fields[field_name].dataType
                
                if expected_type != actual_type:
                    issues.append(f"Type mismatch for {field_name}: expected {expected_type}, got {actual_type}")
        
        return issues
    
    def log_validation_error(self, error_type, message):
        """Log validation errors"""
        logging.error(f"Data Validation Error [{error_type}]: {message}")
        self.validation_results.append({
            "type": "error",
            "category": error_type,
            "message": message,
            "timestamp": datetime.now()
```

#### Usage Example

```python
# Initialize validator
validator = DataValidator(spark)

# Define expected schema
expected_schema = StructType([
    StructField("user_id", IntegerType(), False),
    StructField("username", StringType(), False),
    StructField("email", StringType(), True),
    StructField("signup_date", TimestampType(), False)
])

# Validate schema
schema_valid = validator.validate_table_schema("/path/to/users_table", expected_schema)

# Define quality rules
quality_rules = {
    "user_id_not_null": {
        "type": "not_null",
        "columns": ["user_id"]
    },
    "username_unique": {
        "type": "unique", 
        "columns": ["username"]
    },
    "email_format": {
        "type": "regex",
        "column": "email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    },
    "signup_date_range": {
        "type": "range",
        "column": "signup_date",
        "min": "2020-01-01",
        "max": "2025-12-31"
    }
}

# Validate data quality
quality_results = validator.validate_data_quality("/path/to/users_table", quality_rules)

# Check results
if not schema_valid:
    print("Schema validation failed!")
    
for rule_name, result in quality_results.items():
    if not result.get("passed", True):
        print(f"Quality rule '{rule_name}' failed: {result}")
```

### Statistical Data Profiling

```python
from pyspark.sql.functions import col, count, mean, stddev, min, max, approx_count_distinct

class DataProfiler:
    """Generate statistical profiles for data quality assessment"""
    
    def profile_table(self, table_path):
        """Generate comprehensive data profile"""
        
        df = spark.read.format("delta").load(table_path)
        
        profile = {
            "row_count": df.count(),
            "column_profiles": {}
        }
        
        # Profile each column
        for column in df.columns:
            col_profile = self.profile_column(df, column)
            profile["column_profiles"][column] = col_profile
        
        return profile
    
    def profile_column(self, df, column_name):
        """Profile individual column"""
        
        col_stats = df.select(
            count(col(column_name)).alias("non_null_count"),
            (count(col(column_name)) / df.count()).alias("completeness"),
            approx_count_distinct(col(column_name)).alias("distinct_count"),
            mean(col(column_name)).alias("mean"),
            stddev(col(column_name)).alias("stddev"),
            min(col(column_name)).alias("min"),
            max(col(column_name)).alias("max")
        ).collect()[0]
        
        # Data type specific profiling
        data_type = df.schema[column_name].dataType
        
        if isinstance(data_type, StringType):
            # String-specific metrics
            string_stats = df.select(
                avg(length(col(column_name))).alias("avg_length"),
                max(length(col(column_name))).alias("max_length"),
                min(length(col(column_name))).alias("min_length")
            ).collect()[0]
            
            col_stats = col_stats.asDict()
            col_stats.update(string_stats.asDict())
            
            # Most/least frequent values
            frequent_values = df.groupBy(column_name).count().orderBy("count", ascending=False).limit(5).collect()
            col_stats["top_values"] = [(row[column_name], row["count"]) for row in frequent_values]
        
        elif isinstance(data_type, NumericType):
            # Numeric-specific metrics
            percentile_stats = df.approxQuantile(column_name, [0.25, 0.5, 0.75], 0.01)
            col_stats = col_stats.asDict()
            col_stats.update({
                "q25": percentile_stats[0],
                "median": percentile_stats[1], 
                "q75": percentile_stats[2]
            })
        
        return col_stats.asDict()
    
    def detect_anomalies(self, profile, baseline_profile):
        """Detect data anomalies compared to baseline"""
        
        anomalies = {}
        
        # Check for significant changes
        for column, stats in profile["column_profiles"].items():
            if column in baseline_profile["column_profiles"]:
                baseline_stats = baseline_profile["column_profiles"][column]
                
                # Completeness change
                completeness_change = abs(stats["completeness"] - baseline_stats["completeness"])
                if completeness_change > 0.05:  # 5% change
                    anomalies[column] = {
                        "type": "completeness_change",
                        "current": stats["completeness"],
                        "baseline": baseline_stats["completeness"],
                        "change": completeness_change
                    }
                
                # Distribution change (for numeric columns)
                if "mean" in stats and stats["mean"] is not None:
                    mean_change = abs(stats["mean"] - baseline_stats["mean"]) / baseline_stats["mean"]
                    if mean_change > 0.1:  # 10% change
                        anomalies[column] = {
                            "type": "distribution_shift",
                            "current_mean": stats["mean"],
                            "baseline_mean": baseline_stats["mean"],
                            "change_percent": mean_change * 100
                        }
        
        return anomalies
```

### Continuous Data Validation Pipeline

```python
class ContinuousValidator:
    """Continuous validation for streaming data"""
    
    def __init__(self, spark_session, alert_thresholds):
        self.spark = spark_session
        self.alert_thresholds = alert_thresholds
        self.baseline_profiles = {}
    
    def validate_streaming_batch(self, batch_df, batch_id, table_name):
        """Validate each streaming batch"""
        
        # Quick validation checks
        validation_results = {
            "batch_id": batch_id,
            "timestamp": datetime.now(),
            "checks": {}
        }
        
        # Row count check
        row_count = batch_df.count()
        validation_results["checks"]["row_count"] = {
            "value": row_count,
            "status": "ok" if row_count > 0 else "error"
        }
        
        # Schema consistency check
        if table_name in self.baseline_profiles:
            schema_issues = self.check_schema_consistency(batch_df.schema, 
                                                        self.baseline_profiles[table_name]["schema"])
            validation_results["checks"]["schema_consistency"] = {
                "issues": schema_issues,
                "status": "ok" if not schema_issues else "warning"
            }
        
        # Data quality checks
        quality_issues = self.check_data_quality(batch_df)
        validation_results["checks"]["data_quality"] = {
            "issues": quality_issues,
            "status": "ok" if not quality_issues else "error"
        }
        
        # Alert if needed
        if self.should_alert(validation_results):
            self.send_alert(validation_results)
        
        return validation_results
    
    def check_schema_consistency(self, current_schema, baseline_schema):
        """Check if schema matches baseline"""
        # Implementation similar to DataValidator.compare_schemas
        pass
    
    def check_data_quality(self, df):
        """Quick data quality checks for streaming data"""
        issues = []
        
        # Check for null primary keys
        if "id" in df.columns:
            null_ids = df.filter(col("id").isNull()).count()
            if null_ids > 0:
                issues.append(f"{null_ids} null IDs found")
        
        # Check for invalid timestamps
        if "timestamp" in df.columns:
            invalid_timestamps = df.filter(col("timestamp").isNull() | 
                                         (col("timestamp") > datetime.now())).count()
            if invalid_timestamps > 0:
                issues.append(f"{invalid_timestamps} invalid timestamps")
        
        return issues
    
    def should_alert(self, validation_results):
        """Determine if validation results warrant an alert"""
        for check_name, check_result in validation_results["checks"].items():
            if check_result["status"] in ["error", "warning"]:
                return True
        return False
    
    def send_alert(self, validation_results):
        """Send alert notification"""
        # Implementation for email, Slack, PagerDuty, etc.
        print(f"ALERT: Data validation issues detected: {validation_results}")
```

### Validation Dashboard & Monitoring

```python
class ValidationDashboard:
    """Dashboard for monitoring data validation results"""
    
    def generate_report(self, validation_history):
        """Generate comprehensive validation report"""
        
        report = {
            "summary": {
                "total_validations": len(validation_history),
                "success_rate": self.calculate_success_rate(validation_history),
                "most_common_issues": self.find_common_issues(validation_history)
            },
            "trends": self.analyze_trends(validation_history),
            "recommendations": self.generate_recommendations(validation_history)
        }
        
        return report
    
    def calculate_success_rate(self, history):
        """Calculate overall validation success rate"""
        successful = sum(1 for result in history if result["status"] == "passed")
        return (successful / len(history)) * 100 if history else 0
    
    def find_common_issues(self, history):
        """Identify most common validation issues"""
        issue_counts = {}
        
        for result in history:
            if result["status"] == "failed":
                for issue in result.get("issues", []):
                    issue_type = issue.get("type", "unknown")
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        return sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
    
    def analyze_trends(self, history):
        """Analyze validation trends over time"""
        # Group by time periods and analyze patterns
        pass
    
    def generate_recommendations(self, history):
        """Generate actionable recommendations"""
        recommendations = []
        
        success_rate = self.calculate_success_rate(history)
        if success_rate < 95:
            recommendations.append("Consider implementing automated data quality gates")
        
        common_issues = self.find_common_issues(history)
        if common_issues:
            top_issue = common_issues[0][0]
            recommendations.append(f"Address most common issue: {top_issue}")
        
        return recommendations
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

**Last Updated**: 2025-11-14  
**Maintainers**: Community
