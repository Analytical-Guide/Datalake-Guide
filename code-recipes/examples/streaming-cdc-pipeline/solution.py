"""
Recipe: Streaming CDC Pipeline with Change Data Capture
Purpose: Demonstrate real-time CDC pipeline with Delta Lake and Iceberg
Author: Community
Date: 2025-11-14
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.streaming import StreamingQuery
from delta.tables import DeltaTable
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import shutil
from dataclasses import dataclass


@dataclass
class CDCEvent:
    """Represents a Change Data Capture event"""
    table_name: str
    operation: str  # INSERT, UPDATE, DELETE
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    timestamp: datetime
    transaction_id: str
    primary_key: Dict[str, Any]


class StreamingCDCProcessor:
    """Streaming CDC processor for real-time data pipelines"""

    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.checkpoint_dir = config.get("checkpoint_dir", "/tmp/cdc-checkpoints")
        self.table_configs = config.get("tables", {})
        self.active_queries: List[StreamingQuery] = []

    def start_cdc_pipeline(self) -> List[StreamingQuery]:
        """Start the complete CDC streaming pipeline"""

        print("🚀 Starting CDC Streaming Pipeline")

        # Ensure checkpoint directory exists
        os.makedirs(self.checkpoint_dir, exist_ok=True)

        # Start processing for each configured table
        for table_name, table_config in self.table_configs.items():
            query = self._start_table_stream(table_name, table_config)
            if query:
                self.active_queries.append(query)

        print(f"✅ Started {len(self.active_queries)} streaming queries")
        return self.active_queries

    def _start_table_stream(self, table_name: str, table_config: Dict) -> Optional[StreamingQuery]:
        """Start streaming for a specific table"""

        source_type = table_config.get("source_type", "kafka")
        target_table = table_config.get("target_table", f"/tmp/cdc-tables/{table_name}")

        try:
            if source_type == "kafka":
                return self._process_kafka_stream(table_name, table_config, target_table)
            elif source_type == "file":
                return self._process_file_stream(table_name, table_config, target_table)
            else:
                print(f"⚠️  Unsupported source type: {source_type}")
                return None

        except Exception as e:
            print(f"❌ Failed to start stream for {table_name}: {e}")
            return None

    def _process_kafka_stream(self, table_name: str, config: Dict, target_table: str) -> StreamingQuery:
        """Process CDC events from Kafka"""

        kafka_config = config.get("kafka", {})
        topic = kafka_config.get("topic", f"cdc.{table_name}")
        bootstrap_servers = kafka_config.get("bootstrap_servers", "localhost:9092")

        # Read from Kafka
        kafka_df = (self.spark.readStream
                   .format("kafka")
                   .option("kafka.bootstrap.servers", bootstrap_servers)
                   .option("subscribe", topic)
                   .option("startingOffsets", "latest")
                   .option("failOnDataLoss", "false")
                   .load())

        # Parse CDC events
        try:
            cdc_df = kafka_df.select(
                from_json(col("value").cast("string"), self._get_cdc_schema()).alias("cdc")
            ).select("cdc.*")
        except Exception as e:
            print(f"❌ Failed to parse CDC events from Kafka: {e}")
            return None

        # Process CDC events
        try:
            processed_df = self._process_cdc_events(cdc_df, table_name, config)
        except Exception as e:
            print(f"❌ Failed to process CDC events: {e}")
            return None

        # Write to Delta table with CDC
        query = (processed_df.writeStream
                .format("delta")
                .outputMode("append")
                .option("checkpointLocation", f"{self.checkpoint_dir}/{table_name}")
                .option("mergeSchema", "true")
                .start(target_table))

        print(f"✅ Started Kafka CDC stream for {table_name}")
        return query

    def _process_file_stream(self, table_name: str, config: Dict, target_table: str) -> StreamingQuery:
        """Process CDC events from files (for testing/demo)"""

        source_dir = config.get("source_dir", f"/tmp/cdc-input/{table_name}")

        # Read JSON files
        try:
            file_df = (self.spark.readStream
                      .format("json")
                      .schema(self._get_cdc_schema())
                      .load(source_dir))
        except Exception as e:
            print(f"❌ Failed to read CDC files from {source_dir}: {e}")
            return None

        # Process CDC events
        try:
            processed_df = self._process_cdc_events(file_df, table_name, config)
        except Exception as e:
            print(f"❌ Failed to process CDC events: {e}")
            return None

        # Write to Delta table
        query = (processed_df.writeStream
                .format("delta")
                .outputMode("append")
                .option("checkpointLocation", f"{self.checkpoint_dir}/{table_name}")
                .start(target_table))

        print(f"✅ Started file-based CDC stream for {table_name}")
        return query

    def _get_cdc_schema(self) -> StructType:
        """Get schema for CDC events"""
        return StructType([
            StructField("table_name", StringType(), True),
            StructField("operation", StringType(), True),  # INSERT, UPDATE, DELETE
            StructField("before", StringType(), True),     # JSON string
            StructField("after", StringType(), True),      # JSON string
            StructField("timestamp", TimestampType(), True),
            StructField("transaction_id", StringType(), True),
            StructField("primary_key", StringType(), True)  # JSON string
        ])

    def _process_cdc_events(self, cdc_df, table_name: str, config: Dict):
        """Process CDC events with deduplication and transformation"""

        # Parse JSON fields
        processed_df = cdc_df.withColumn("before_parsed",
                                       from_json(col("before"), self._get_table_schema(table_name)))
        processed_df = processed_df.withColumn("after_parsed",
                                             from_json(col("after"), self._get_table_schema(table_name)))
        processed_df = processed_df.withColumn("pk_parsed",
                                             from_json(col("primary_key"), MapType(StringType(), StringType())))

        # Extract primary key value for deduplication
        processed_df = processed_df.withColumn("pk_value",
                                             col("primary_key"))  # Keep as string for deduplication

        # Add processing metadata
        processed_df = processed_df.withColumn("processed_at", current_timestamp())
        processed_df = processed_df.withColumn("batch_id", monotonically_increasing_id())

        # Handle different operations
        processed_df = processed_df.withColumn("operation_type",
            when(col("operation") == "INSERT", "I")
            .when(col("operation") == "UPDATE", "U")
            .when(col("operation") == "DELETE", "D")
            .otherwise("U")  # Default to UPDATE for unknown ops
        )

        # Add watermark for late data handling
        processed_df = processed_df.withWatermark("timestamp", "10 minutes")

        # Deduplicate based on primary key and transaction
        window_spec = Window.partitionBy("transaction_id", "pk_value").orderBy(col("timestamp").desc())
        deduped_df = processed_df.withColumn("row_num", row_number().over(window_spec))
        deduped_df = deduped_df.filter(col("row_num") == 1).drop("row_num")

        return deduped_df.select(
            "table_name",
            "operation_type",
            "before_parsed",
            "after_parsed",
            "timestamp",
            "transaction_id",
            "processed_at",
            "batch_id"
        )

    def _get_table_schema(self, table_name: str) -> StructType:
        """Get target table schema"""
        # In production, this would come from a schema registry
        schemas = {
            "customers": StructType([
                StructField("customer_id", StringType(), False),
                StructField("name", StringType(), True),
                StructField("email", StringType(), True),
                StructField("phone", StringType(), True),
                StructField("address", StringType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("updated_at", TimestampType(), True)
            ]),
            "orders": StructType([
                StructField("order_id", StringType(), False),
                StructField("customer_id", StringType(), True),
                StructField("order_date", TimestampType(), True),
                StructField("total_amount", DoubleType(), True),
                StructField("status", StringType(), True),
                StructField("items", ArrayType(StructType([
                    StructField("product_id", StringType(), True),
                    StructField("quantity", IntegerType(), True),
                    StructField("price", DoubleType(), True)
                ])), True)
            ])
        }
        return schemas.get(table_name, StructType([]))

    def monitor_pipeline_health(self) -> Dict[str, Any]:
        """Monitor pipeline health and performance"""

        health_status = {
            "timestamp": datetime.now(),
            "active_queries": len(self.active_queries),
            "queries_status": {},
            "performance_metrics": {}
        }

        for i, query in enumerate(self.active_queries):
            try:
                status = query.status
                health_status["queries_status"][f"query_{i}"] = {
                    "is_active": query.isActive,
                    "status": status,
                    "recent_progress": query.recentProgress
                }
            except Exception as e:
                health_status["queries_status"][f"query_{i}"] = {
                    "error": str(e)
                }

        return health_status

    def stop_pipeline(self):
        """Stop all streaming queries"""
        print("🛑 Stopping CDC Pipeline")

        for query in self.active_queries:
            try:
                query.stop()
                print("✅ Stopped streaming query")
            except Exception as e:
                print(f"❌ Error stopping query: {e}")

        self.active_queries.clear()


def generate_sample_cdc_events(output_dir: str, table_name: str, num_events: int = 100):
    """Generate sample CDC events for testing"""

    os.makedirs(output_dir, exist_ok=True)

    # Sample data templates
    if table_name == "customers":
        template = {
            "customer_id": "CUST_{:04d}",
            "name": "Customer {:03d}",
            "email": "customer{:03d}@example.com",
            "phone": "+1-555-{:04d}",
            "address": "Address {:03d}",
            "created_at": "2024-01-{:02d}T10:00:00Z",
            "updated_at": "2024-01-{:02d}T10:00:00Z"
        }
    else:
        template = {
            "order_id": "ORD_{:04d}",
            "customer_id": "CUST_{:04d}",
            "order_date": "2024-01-{:02d}T10:00:00Z",
            "total_amount": 100.0,
            "status": "pending",
            "items": [{"product_id": "PROD_{:03d}", "quantity": 1, "price": 50.0}]
        }

    operations = ["INSERT", "UPDATE", "DELETE"]
    transaction_id = 1000

    for i in range(num_events):
        operation = operations[i % len(operations)]
        record_id = i % 50 + 1  # Repeat some IDs for updates/deletes

        # Create CDC event
        event = {
            "table_name": table_name,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "transaction_id": f"TXN_{transaction_id + i}"
        }

        if table_name == "customers":
            data = {
                "customer_id": f"CUST_{record_id:04d}",
                "name": f"Customer {record_id:03d}",
                "email": f"customer{record_id:03d}@example.com",
                "phone": f"+1-555-{record_id:04d}",
                "address": f"Address {record_id:03d}",
                "created_at": f"2024-01-{record_id%28+1:02d}T10:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
        else:
            data = {
                "order_id": f"ORD_{record_id:04d}",
                "customer_id": f"CUST_{record_id%10+1:04d}",
                "order_date": f"2024-01-{record_id%28+1:02d}T10:00:00Z",
                "total_amount": round(50 + (record_id * 10.5), 2),
                "status": ["pending", "processing", "completed"][record_id % 3],
                "items": [
                    {
                        "product_id": f"PROD_{record_id%20+1:03d}",
                        "quantity": record_id % 5 + 1,
                        "price": round(25 + (record_id * 2.5), 2)
                    }
                ]
            }

        if operation == "INSERT":
            event["after"] = json.dumps(data)
            event["before"] = None
        elif operation == "UPDATE":
            event["before"] = json.dumps({**data, "status": "old_status"})
            event["after"] = json.dumps(data)
        else:  # DELETE
            event["before"] = json.dumps(data)
            event["after"] = None

        event["primary_key"] = json.dumps({"id": data[list(data.keys())[0]]})

        # Write event to file
        with open(f"{output_dir}/cdc_event_{i:04d}.json", "w") as f:
            json.dump(event, f, indent=2)


def demonstrate_streaming_cdc():
    """Demonstrate streaming CDC pipeline"""

    print("🚀 Streaming CDC Pipeline Demo")
    print("=" * 50)

    # Configuration
    config = {
        "checkpoint_dir": "/tmp/cdc-checkpoints",
        "tables": {
            "customers": {
                "source_type": "file",
                "source_dir": "/tmp/cdc-input/customers",
                "target_table": "/tmp/cdc-tables/customers",
                "primary_key": ["customer_id"]
            },
            "orders": {
                "source_type": "file",
                "source_dir": "/tmp/cdc-input/orders",
                "target_table": "/tmp/cdc-tables/orders",
                "primary_key": ["order_id"]
            }
        }
    }

    # Initialize Spark
    spark = (SparkSession.builder
             .appName("StreamingCDCDemo")
             .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
             .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
             .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints")
             .getOrCreate())

    spark.sparkContext.setLogLevel("WARN")

    try:
        # Clean up previous run
        for table_config in config["tables"].values():
            target_table = table_config["target_table"]
            if os.path.exists(target_table):
                shutil.rmtree(target_table)

            source_dir = table_config.get("source_dir")
            if source_dir and os.path.exists(source_dir):
                shutil.rmtree(source_dir)

        # Generate sample CDC events
        print("\n📝 Generating sample CDC events...")
        for table_name, table_config in config["tables"].items():
            source_dir = table_config["source_dir"]
            generate_sample_cdc_events(source_dir, table_name, 50)
            print(f"  Generated events for {table_name}")

        # Initialize CDC processor
        cdc_processor = StreamingCDCProcessor(spark, config)

        # Start pipeline
        print("\n🔄 Starting CDC streaming pipeline...")
        queries = cdc_processor.start_cdc_pipeline()

        # Let it run for a bit
        print("\n⏳ Processing events...")
        time.sleep(10)

        # Check pipeline health
        health = cdc_processor.monitor_pipeline_health()
        print(f"\n📊 Pipeline Health: {health['active_queries']} active queries")

        # Wait a bit more for processing
        time.sleep(5)

        # Show results
        print("\n📋 Results:")
        for table_name, table_config in config["tables"].items():
            target_table = table_config["target_table"]
            try:
                df = spark.read.format("delta").load(target_table)
                count = df.count()
                print(f"  {table_name}: {count} records")
                df.show(5, truncate=False)
            except Exception as e:
                print(f"  {table_name}: Error reading - {e}")

        # Stop pipeline
        cdc_processor.stop_pipeline()

        print("\n✅ Streaming CDC demo completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    demonstrate_streaming_cdc()