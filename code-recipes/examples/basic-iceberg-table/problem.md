# Problem: Creating a Basic Apache Iceberg Table

## Use Case

You need to create your first Apache Iceberg table to enable ACID transactions, hidden partitioning, and multi-engine compatibility for your data pipeline.

## Context

While Parquet provides efficient columnar storage, it lacks transactional capabilities. Apache Iceberg adds a metadata layer that provides ACID guarantees, schema evolution, and time travel. Unlike traditional partitioning, Iceberg's hidden partitioning allows you to change partition strategies without rewriting data.

## Requirements

- Apache Spark 3.x or later
- Apache Iceberg library installed
- Write access to a storage location (local or cloud)
- Sample data to work with

## Expected Outcome

After running this recipe, you will have:
- An Iceberg table created with proper catalog configuration
- Metadata files tracking table state
- Ability to query using multiple engines (Spark, Trino, Flink)
- Foundation for advanced features like hidden partitioning

## Real-World Applications

- Multi-engine data platforms
- Cross-cloud data architectures
- Vendor-neutral data lakes
- Large-scale analytics with partition evolution
