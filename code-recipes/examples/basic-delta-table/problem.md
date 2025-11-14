---
title: Problem – Creating a Basic Delta Lake Table
permalink: /code-recipes/examples/basic-delta-table/problem/
description: Business challenge describing the need to stand up an ACID-compliant Delta Lake table.
---

# Problem: Creating a Basic Delta Lake Table

## Use Case

You need to create your first Delta Lake table from a DataFrame, enabling ACID transactions, time travel, and schema enforcement for your data pipeline.

## Context

Traditional Parquet files don't provide ACID guarantees or support for updates/deletes. Delta Lake adds these capabilities by maintaining a transaction log alongside your data files. This recipe demonstrates the fundamental operation of creating a Delta table.

## Requirements

- Apache Spark 3.x or later
- Delta Lake library installed
- Write access to a storage location (local or cloud)
- Sample data to work with

## Expected Outcome

After running this recipe, you will have:
- A Delta table created at the specified location
- Transaction log (`_delta_log/`) automatically maintained
- Ability to query the table using Spark SQL
- Foundation for ACID operations (updates, deletes, merges)

## Real-World Applications

- Initial data lake setup
- Converting existing Parquet tables to Delta format
- Starting point for CDC pipelines
- Foundation for lakehouse architecture
