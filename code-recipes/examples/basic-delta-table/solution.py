"""
Recipe: Creating a Basic Delta Lake Table
Purpose: Demonstrate how to create and write to a Delta Lake table
Author: Community
Date: 2024-01-01
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from datetime import datetime
import os

def create_spark_session():
    """
    Create a Spark session with Delta Lake configuration.
    
    Returns:
        SparkSession: Configured Spark session with Delta support
    """
    return (SparkSession.builder
            .appName("BasicDeltaTableExample")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .getOrCreate())

def create_sample_data(spark):
    """
    Create sample data for demonstration.
    
    Args:
        spark: SparkSession instance
        
    Returns:
        DataFrame: Sample data with user information
    """
    # Define schema explicitly for better control and documentation
    schema = StructType([
        StructField("user_id", IntegerType(), False),
        StructField("username", StringType(), False),
        StructField("email", StringType(), True),
        StructField("signup_date", TimestampType(), False)
    ])
    
    # Create sample records
    data = [
        (1, "alice", "alice@example.com", datetime(2024, 1, 1, 10, 0, 0)),
        (2, "bob", "bob@example.com", datetime(2024, 1, 2, 11, 30, 0)),
        (3, "charlie", "charlie@example.com", datetime(2024, 1, 3, 9, 15, 0)),
        (4, "diana", "diana@example.com", datetime(2024, 1, 4, 14, 45, 0)),
        (5, "eve", "eve@example.com", datetime(2024, 1, 5, 16, 20, 0))
    ]
    
    return spark.createDataFrame(data, schema)

def create_delta_table(df, table_path):
    """
    Write DataFrame to Delta Lake format.
    
    Args:
        df: DataFrame to write
        table_path: Location to store the Delta table
    """
    # Write as Delta format
    # mode="overwrite" will replace existing data
    # format="delta" specifies Delta Lake format
    (df.write
       .format("delta")
       .mode("overwrite")
       .save(table_path))
    
    print(f"✅ Delta table created successfully at: {table_path}")

def read_delta_table(spark, table_path):
    """
    Read and display the Delta table.
    
    Args:
        spark: SparkSession instance
        table_path: Location of the Delta table
        
    Returns:
        DataFrame: The Delta table as a DataFrame
    """
    df = spark.read.format("delta").load(table_path)
    
    print(f"\n📊 Table Statistics:")
    print(f"   Total Records: {df.count()}")
    print(f"   Schema: {df.schema.simpleString()}")
    
    print(f"\n📋 Sample Data:")
    df.show(truncate=False)
    
    return df

def demonstrate_delta_features(spark, table_path):
    """
    Demonstrate key Delta Lake features.
    
    Args:
        spark: SparkSession instance
        table_path: Location of the Delta table
    """
    # Register as temporary view for SQL queries
    df = spark.read.format("delta").load(table_path)
    df.createOrReplaceTempView("users")
    
    # Query using SQL
    print(f"\n🔍 SQL Query Example:")
    result = spark.sql("""
        SELECT username, email, signup_date
        FROM users
        WHERE signup_date >= '2024-01-03'
        ORDER BY signup_date
    """)
    result.show(truncate=False)
    
    # Show Delta table history (time travel capability)
    print(f"\n📜 Table History:")
    history_df = spark.sql(f"DESCRIBE HISTORY delta.`{table_path}`")
    history_df.select("version", "timestamp", "operation", "operationParameters").show(truncate=False)

def main():
    """
    Main function demonstrating Delta Lake table creation.
    
    Steps:
    1. Create Spark session with Delta configuration
    2. Generate sample data
    3. Write data as Delta table
    4. Read and verify the table
    5. Demonstrate Delta features
    """
    # Step 1: Initialize Spark with Delta support
    print("🚀 Initializing Spark session...")
    spark = create_spark_session()
    
    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")
    
    # Step 2: Define table location
    table_path = "/tmp/delta-tables/users"
    
    # Clean up any existing table for this example
    import shutil
    if os.path.exists(table_path):
        shutil.rmtree(table_path)
    
    # Step 3: Create sample data
    print("\n📝 Creating sample data...")
    df = create_sample_data(spark)
    
    # Step 4: Write as Delta table
    print(f"\n💾 Writing Delta table to {table_path}...")
    create_delta_table(df, table_path)
    
    # Step 5: Read and display the table
    print(f"\n📖 Reading Delta table...")
    read_delta_table(spark, table_path)
    
    # Step 6: Demonstrate Delta features
    demonstrate_delta_features(spark, table_path)
    
    print("\n✅ Recipe completed successfully!")
    print(f"\n💡 Next Steps:")
    print(f"   - Try updating records using MERGE")
    print(f"   - Explore time travel with VERSION AS OF")
    print(f"   - Add partitioning for better performance")
    print(f"   - Enable Change Data Feed for CDC")
    
    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main()
