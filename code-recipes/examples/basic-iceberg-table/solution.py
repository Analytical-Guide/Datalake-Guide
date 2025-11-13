"""
Recipe: Creating a Basic Apache Iceberg Table
Purpose: Demonstrate how to create and work with Apache Iceberg tables
Author: Community
Date: 2024-01-01
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from datetime import datetime
import os
import shutil


def create_spark_session():
    """
    Create a Spark session with Iceberg configuration.
    
    Returns:
        SparkSession: Configured Spark session with Iceberg support
    """
    # Note: In production, you'd configure a proper catalog (Hive, Nessie, AWS Glue, etc.)
    # This example uses a simple Hadoop catalog for demonstration
    
    return (
        SparkSession.builder.appName("BasicIcebergTableExample")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", "/tmp/iceberg-warehouse")
        .getOrCreate()
    )


def create_sample_data(spark):
    """
    Create sample data for demonstration.
    
    Args:
        spark: SparkSession instance
        
    Returns:
        DataFrame: Sample data with user information
    """
    # Define schema explicitly
    schema = StructType(
        [
            StructField("user_id", IntegerType(), False),
            StructField("username", StringType(), False),
            StructField("email", StringType(), True),
            StructField("signup_date", TimestampType(), False),
        ]
    )

    # Create sample records
    data = [
        (1, "alice", "alice@example.com", datetime(2024, 1, 1, 10, 0, 0)),
        (2, "bob", "bob@example.com", datetime(2024, 1, 2, 11, 30, 0)),
        (3, "charlie", "charlie@example.com", datetime(2024, 1, 3, 9, 15, 0)),
        (4, "diana", "diana@example.com", datetime(2024, 1, 4, 14, 45, 0)),
        (5, "eve", "eve@example.com", datetime(2024, 1, 5, 16, 20, 0)),
    ]

    return spark.createDataFrame(data, schema)


def create_iceberg_table(spark, df, table_name):
    """
    Create an Iceberg table from DataFrame.
    
    Args:
        spark: SparkSession instance
        df: DataFrame to write
        table_name: Fully qualified table name (catalog.database.table)
    """
    # First, create the database if it doesn't exist
    spark.sql("CREATE DATABASE IF NOT EXISTS local.db")

    # Write DataFrame as Iceberg table
    # Using writeTo() API which is Iceberg-specific
    df.writeTo(table_name).create()

    print(f"✅ Iceberg table created successfully: {table_name}")


def read_iceberg_table(spark, table_name):
    """
    Read and display the Iceberg table.
    
    Args:
        spark: SparkSession instance
        table_name: Fully qualified table name
        
    Returns:
        DataFrame: The Iceberg table as a DataFrame
    """
    # Read using table() method
    df = spark.table(table_name)

    print(f"\n📊 Table Statistics:")
    print(f"   Total Records: {df.count()}")
    print(f"   Schema: {df.schema.simpleString()}")

    print(f"\n📋 Sample Data:")
    df.show(truncate=False)

    return df


def demonstrate_iceberg_features(spark, table_name):
    """
    Demonstrate key Apache Iceberg features.
    
    Args:
        spark: SparkSession instance
        table_name: Fully qualified table name
    """
    # 1. Query using SQL
    print(f"\n🔍 SQL Query Example:")
    result = spark.sql(
        f"""
        SELECT username, email, signup_date
        FROM {table_name}
        WHERE signup_date >= '2024-01-03'
        ORDER BY signup_date
    """
    )
    result.show(truncate=False)

    # 2. Show table metadata
    print(f"\n📜 Table Metadata:")
    metadata = spark.sql(f"DESCRIBE EXTENDED {table_name}")
    metadata.show(truncate=False)

    # 3. Show snapshots (Iceberg's version history)
    print(f"\n📸 Table Snapshots:")
    try:
        snapshots = spark.sql(f"SELECT * FROM {table_name}.snapshots")
        snapshots.select(
            "snapshot_id", "committed_at", "operation", "summary"
        ).show(truncate=False)
    except Exception as e:
        print(f"   Note: Snapshot metadata access may vary by Iceberg version")

    # 4. Show files in the table
    print(f"\n📁 Table Files:")
    try:
        files = spark.sql(f"SELECT * FROM {table_name}.files")
        files.select("file_path", "file_size_in_bytes", "record_count").show(
            truncate=False
        )
    except Exception as e:
        print(f"   Note: File metadata access may vary by Iceberg version")


def demonstrate_hidden_partitioning(spark, table_name):
    """
    Demonstrate Iceberg's hidden partitioning feature.
    
    Args:
        spark: SparkSession instance
        table_name: Fully qualified table name
    """
    print(f"\n🎭 Hidden Partitioning Demonstration:")
    print("   Iceberg supports 'hidden partitioning' where:")
    print("   - Partition transforms are applied automatically")
    print("   - Users don't need to specify partition columns in queries")
    print("   - Partition layout can evolve without rewriting data")

    # Example: Create a partitioned table
    partitioned_table = "local.db.events_partitioned"

    # Drop if exists
    spark.sql(f"DROP TABLE IF EXISTS {partitioned_table}")

    # Create with partition transforms
    spark.sql(
        f"""
        CREATE TABLE {partitioned_table} (
            event_id INT,
            event_time TIMESTAMP,
            user_id STRING,
            event_type STRING
        )
        USING iceberg
        PARTITIONED BY (days(event_time))
    """
    )

    print(f"   ✅ Created table with hidden partitioning: {partitioned_table}")
    print("      Partitioned by days(event_time)")
    print("      Users can query without knowing partition details!")


def main():
    """
    Main function demonstrating Iceberg table creation.
    
    Steps:
    1. Create Spark session with Iceberg configuration
    2. Generate sample data
    3. Create Iceberg table
    4. Read and verify the table
    5. Demonstrate Iceberg features
    6. Show hidden partitioning
    """
    # Clean up any existing warehouse
    warehouse_path = "/tmp/iceberg-warehouse"
    if os.path.exists(warehouse_path):
        shutil.rmtree(warehouse_path)

    # Step 1: Initialize Spark with Iceberg support
    print("🚀 Initializing Spark session with Iceberg support...")
    spark = create_spark_session()

    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")

    # Step 2: Create sample data
    print("\n📝 Creating sample data...")
    df = create_sample_data(spark)

    # Step 3: Define table name (catalog.database.table)
    table_name = "local.db.users"

    # Step 4: Create Iceberg table
    print(f"\n💾 Creating Iceberg table: {table_name}...")
    create_iceberg_table(spark, df, table_name)

    # Step 5: Read and display the table
    print(f"\n📖 Reading Iceberg table...")
    read_iceberg_table(spark, table_name)

    # Step 6: Demonstrate Iceberg features
    demonstrate_iceberg_features(spark, table_name)

    # Step 7: Demonstrate hidden partitioning
    demonstrate_hidden_partitioning(spark, table_name)

    print("\n✅ Recipe completed successfully!")
    print(f"\n💡 Next Steps:")
    print(f"   - Try updating records using MERGE")
    print(f"   - Explore time travel with snapshot IDs")
    print(f"   - Experiment with partition evolution")
    print(f"   - Test with different query engines (Trino, Flink)")

    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main()
