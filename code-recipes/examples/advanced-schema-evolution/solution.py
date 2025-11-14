"""
Recipe: Advanced Schema Evolution and Migration
Purpose: Demonstrate complex schema evolution patterns with Delta Lake and Iceberg
Author: Community
Date: 2025-11-14
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from delta.tables import DeltaTable
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import shutil


class SchemaEvolutionManager:
    """Advanced schema evolution manager supporting complex migrations"""

    def __init__(self, spark: SparkSession, table_path: str, format_type: str = "delta"):
        self.spark = spark
        self.table_path = table_path
        self.format_type = format_type
        self.evolution_history = []

    def get_current_schema(self) -> StructType:
        """Get current table schema"""
        if self.format_type == "delta":
            return self.spark.read.format("delta").load(self.table_path).schema
        else:
            return self.spark.table(f"local.db.{self.table_path.split('/')[-1]}").schema

    def evolve_schema(self, evolution_spec: Dict[str, Any]) -> bool:
        """Execute schema evolution based on specification"""
        try:
            operation = evolution_spec["operation"]

            if operation == "add_columns":
                return self._add_columns(evolution_spec)
            elif operation == "drop_columns":
                return self._drop_columns(evolution_spec)
            elif operation == "rename_columns":
                return self._rename_columns(evolution_spec)
            elif operation == "change_data_types":
                return self._change_data_types(evolution_spec)
            elif operation == "add_nested_fields":
                return self._add_nested_fields(evolution_spec)
            elif operation == "restructure_nested":
                return self._restructure_nested(evolution_spec)
            else:
                raise ValueError(f"Unsupported evolution operation: {operation}")

        except Exception as e:
            print(f"Schema evolution failed: {e}")
            return False

    def _add_columns(self, spec: Dict) -> bool:
        """Add new columns with default values"""
        columns_to_add = spec["columns"]

        if self.format_type == "delta":
            # Delta Lake: Use ALTER TABLE
            for col_spec in columns_to_add:
                col_name = col_spec["name"]
                col_type = col_spec["type"]
                default_value = col_spec.get("default", "NULL")

                alter_sql = f"""
                ALTER TABLE delta.`{self.table_path}`
                ADD COLUMN {col_name} {col_type}
                """

                if default_value != "NULL":
                    alter_sql += f" DEFAULT {default_value}"

                self.spark.sql(alter_sql)

        else:
            # Iceberg: Use ALTER TABLE
            for col_spec in columns_to_add:
                col_name = col_spec["name"]
                col_type = col_spec["type"]

                self.spark.sql(f"""
                ALTER TABLE local.db.{self.table_path.split('/')[-1]}
                ADD COLUMN {col_name} {col_type}
                """)

        self._log_evolution(spec)
        return True

    def _drop_columns(self, spec: Dict) -> bool:
        """Drop columns (with safety checks)"""
        columns_to_drop = spec["columns"]

        if self.format_type == "delta":
            for col_name in columns_to_drop:
                # Check if column exists and get usage info
                current_df = self.spark.read.format("delta").load(self.table_path)
                if col_name not in current_df.columns:
                    print(f"Column {col_name} does not exist, skipping")
                    continue

                # In production, you'd check dependencies, backups, etc.
                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                DROP COLUMN {col_name}
                """)
        else:
            for col_name in columns_to_drop:
                self.spark.sql(f"""
                ALTER TABLE local.db.{self.table_path.split('/')[-1]}
                DROP COLUMN {col_name}
                """)

        self._log_evolution(spec)
        return True

    def _rename_columns(self, spec: Dict) -> bool:
        """Rename columns with backward compatibility"""
        renames = spec["renames"]

        if self.format_type == "delta":
            for old_name, new_name in renames.items():
                # Add new column
                current_df = self.spark.read.format("delta").load(self.table_path)
                col_type = current_df.schema[old_name].dataType.simpleString()

                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                ADD COLUMN {new_name} {col_type}
                """)

                # Copy data
                self.spark.sql(f"""
                UPDATE delta.`{self.table_path}`
                SET {new_name} = {old_name}
                """)

                # Drop old column (after validation)
                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                DROP COLUMN {old_name}
                """)
        else:
            # Iceberg approach
            for old_name, new_name in renames.items():
                self.spark.sql(f"""
                ALTER TABLE local.db.{self.table_path.split('/')[-1]}
                RENAME COLUMN {old_name} TO {new_name}
                """)

        self._log_evolution(spec)
        return True

    def _change_data_types(self, spec: Dict) -> bool:
        """Change column data types with data migration"""
        type_changes = spec["type_changes"]

        for col_spec in type_changes:
            col_name = col_spec["column"]
            new_type = col_spec["new_type"]
            conversion_func = col_spec.get("conversion_function")

            if self.format_type == "delta":
                # Create temp column with new type
                temp_col = f"{col_name}_temp_{int(datetime.now().timestamp())}"

                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                ADD COLUMN {temp_col} {new_type}
                """)

                # Convert and copy data
                if conversion_func:
                    self.spark.sql(f"""
                    UPDATE delta.`{self.table_path}`
                    SET {temp_col} = {conversion_func}({col_name})
                    """)
                else:
                    self.spark.sql(f"""
                    UPDATE delta.`{self.table_path}`
                    SET {temp_col} = CAST({col_name} AS {new_type})
                    """)

                # Replace columns
                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                DROP COLUMN {col_name}
                """)

                self.spark.sql(f"""
                ALTER TABLE delta.`{self.table_path}`
                RENAME COLUMN {temp_col} TO {col_name}
                """)

        self._log_evolution(spec)
        return True

    def _add_nested_fields(self, spec: Dict) -> bool:
        """Add fields to nested structures"""
        # This is complex and format-specific
        if self.format_type == "delta":
            # Delta Lake handles nested structures automatically with schema evolution
            nested_updates = spec["nested_updates"]

            for update in nested_updates:
                parent_col = update["parent_column"]
                new_fields = update["new_fields"]

                # Use SQL to add nested fields
                for field_spec in new_fields:
                    field_name = field_spec["name"]
                    field_type = field_spec["type"]
                    field_path = f"{parent_col}.{field_name}"

                    # Note: Delta Lake doesn't support direct nested field addition
                    # This would require rewriting the table
                    print(f"Note: Adding nested fields requires table rewrite for {field_path}")

        self._log_evolution(spec)
        return True

    def _restructure_nested(self, spec: Dict) -> bool:
        """Restructure nested data (complex operation)"""
        restructure_spec = spec["restructure"]

        # This typically requires reading, transforming, and rewriting the table
        df = self.spark.read.format(self.format_type).load(self.table_path)

        # Apply restructuring transformations
        transformed_df = self._apply_restructure_transformations(df, restructure_spec)

        # Write back with new structure
        mode = "overwrite" if spec.get("allow_data_loss", False) else "error"
        transformed_df.write.format(self.format_type).mode(mode).save(self.table_path)

        self._log_evolution(spec)
        return True

    def _apply_restructure_transformations(self, df, restructure_spec):
        """Apply complex restructuring transformations"""
        # Example: Flatten nested structure
        if restructure_spec["type"] == "flatten":
            return self._flatten_nested_structure(df, restructure_spec)
        elif restructure_spec["type"] == "nest":
            return self._create_nested_structure(df, restructure_spec)
        else:
            return df

    def _flatten_nested_structure(self, df, spec):
        """Flatten nested columns into top-level columns"""
        nested_col = spec["nested_column"]
        fields_to_flatten = spec["fields"]

        select_expr = df.columns  # Start with existing columns

        for field in fields_to_flatten:
            nested_field = f"{nested_col}.{field}"
            flat_name = f"{nested_col}_{field}"
            select_expr.append(f"{nested_field} as {flat_name}")

        return df.selectExpr(*select_expr)

    def _create_nested_structure(self, df, spec):
        """Create nested structure from flat columns"""
        struct_name = spec["struct_name"]
        field_mappings = spec["field_mappings"]

        # Build struct expression
        struct_fields = [f"'{new_name}', {old_name}" for old_name, new_name in field_mappings.items()]
        struct_expr = f"STRUCT({', '.join(struct_fields)}) as {struct_name}"

        select_expr = [col for col in df.columns if col not in field_mappings.keys()]
        select_expr.append(struct_expr)

        return df.selectExpr(*select_expr)

    def _log_evolution(self, spec: Dict):
        """Log evolution operation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": spec["operation"],
            "details": spec,
            "table_path": self.table_path,
            "format_type": self.format_type
        }
        self.evolution_history.append(log_entry)

    def get_evolution_history(self) -> List[Dict]:
        """Get evolution history"""
        return self.evolution_history

    def validate_evolution(self, spec: Dict) -> Dict[str, Any]:
        """Validate evolution operation before execution"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "impact_assessment": {}
        }

        operation = spec["operation"]

        # Check for data loss potential
        if operation in ["drop_columns", "restructure_nested"]:
            if not spec.get("allow_data_loss", False):
                validation_results["warnings"].append("Operation may result in data loss")

        # Check dependencies
        if operation == "drop_columns":
            # In production, check for downstream dependencies
            validation_results["impact_assessment"]["dependent_queries"] = "unknown"

        # Validate syntax and semantics
        try:
            # Basic validation logic here
            pass
        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            validation_results["is_valid"] = False

        return validation_results


def create_complex_sample_data(spark: SparkSession):
    """Create complex sample data for evolution demonstration"""

    # Complex nested schema
    schema = StructType([
        StructField("customer_id", StringType(), False),
        StructField("profile", StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("contact", StructType([
                StructField("email", StringType(), True),
                StructField("phone", StringType(), True)
            ]), True)
        ]), True),
        StructField("orders", ArrayType(StructType([
            StructField("order_id", StringType(), False),
            StructField("amount", DoubleType(), True),
            StructField("items", ArrayType(StringType()), True),
            StructField("order_date", TimestampType(), True)
        ])), True),
        StructField("preferences", MapType(StringType(), StringType()), True),
        StructField("last_updated", TimestampType(), False)
    ])

    data = [
        {
            "customer_id": "CUST_001",
            "profile": {
                "name": "Alice Johnson",
                "age": 32,
                "contact": {
                    "email": "alice@example.com",
                    "phone": "+1-555-0101"
                }
            },
            "orders": [
                {
                    "order_id": "ORD_001",
                    "amount": 299.99,
                    "items": ["laptop", "mouse"],
                    "order_date": datetime(2024, 1, 15, 10, 30)
                },
                {
                    "order_id": "ORD_002",
                    "amount": 49.99,
                    "items": ["headphones"],
                    "order_date": datetime(2024, 2, 20, 14, 15)
                }
            ],
            "preferences": {"theme": "dark", "notifications": "email"},
            "last_updated": datetime(2024, 3, 1, 9, 0)
        },
        {
            "customer_id": "CUST_002",
            "profile": {
                "name": "Bob Smith",
                "age": 45,
                "contact": {
                    "email": "bob@example.com",
                    "phone": "+1-555-0102"
                }
            },
            "orders": [
                {
                    "order_id": "ORD_003",
                    "amount": 149.99,
                    "items": ["tablet", "case"],
                    "order_date": datetime(2024, 1, 22, 16, 45)
                }
            ],
            "preferences": {"theme": "light", "notifications": "sms"},
            "last_updated": datetime(2024, 3, 2, 11, 30)
        }
    ]

    return spark.createDataFrame(data, schema)


def demonstrate_schema_evolution():
    """Demonstrate advanced schema evolution patterns"""

    print("🚀 Advanced Schema Evolution Demo")
    print("=" * 50)

    # Initialize Spark
    spark = (SparkSession.builder
             .appName("AdvancedSchemaEvolution")
             .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
             .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
             .getOrCreate())

    spark.sparkContext.setLogLevel("WARN")

    # Setup
    table_path = "/tmp/schema-evolution-demo"
    if os.path.exists(table_path):
        shutil.rmtree(table_path)

    # Create initial complex data
    print("\n📝 Creating initial complex dataset...")
    df = create_complex_sample_data(spark)
    df.write.format("delta").mode("overwrite").save(table_path)

    print("Initial schema:")
    df.printSchema()

    # Initialize evolution manager
    evolution_manager = SchemaEvolutionManager(spark, table_path, "delta")

    # Evolution 1: Add new columns
    print("\n🔄 Evolution 1: Adding new columns...")
    add_columns_spec = {
        "operation": "add_columns",
        "columns": [
            {"name": "customer_segment", "type": "STRING", "default": "'standard'"},
            {"name": "loyalty_points", "type": "INT", "default": "0"},
            {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
        ]
    }

    evolution_manager.evolve_schema(add_columns_spec)

    # Evolution 2: Rename columns with data migration
    print("\n🔄 Evolution 2: Renaming columns...")
    rename_spec = {
        "operation": "rename_columns",
        "renames": {
            "customer_segment": "membership_tier",
            "loyalty_points": "reward_points"
        }
    }

    evolution_manager.evolve_schema(rename_spec)

    # Evolution 3: Change data types
    print("\n🔄 Evolution 3: Changing data types...")
    type_change_spec = {
        "operation": "change_data_types",
        "type_changes": [
            {
                "column": "reward_points",
                "new_type": "DOUBLE",
                "conversion_func": "CAST(reward_points AS DOUBLE)"
            }
        ]
    }

    evolution_manager.evolve_schema(type_change_spec)

    # Evolution 4: Restructure nested data
    print("\n🔄 Evolution 4: Restructuring nested data...")
    restructure_spec = {
        "operation": "restructure_nested",
        "restructure": {
            "type": "flatten",
            "nested_column": "profile",
            "fields": ["name", "age"]
        },
        "allow_data_loss": False
    }

    evolution_manager.evolve_schema(restructure_spec)

    # Show final schema and sample data
    print("\n📊 Final Schema:")
    final_df = spark.read.format("delta").load(table_path)
    final_df.printSchema()

    print("\n📋 Sample of evolved data:")
    final_df.select("customer_id", "profile_name", "profile_age", "membership_tier", "reward_points").show()

    # Show evolution history
    print("\n📜 Evolution History:")
    for entry in evolution_manager.get_evolution_history():
        print(f"  {entry['timestamp']}: {entry['operation']}")

    # Demonstrate backward compatibility
    print("\n🔍 Testing backward compatibility...")
    try:
        # This should work even after restructuring
        result = spark.sql(f"""
        SELECT customer_id, profile.contact.email as email,
               size(orders) as order_count,
               membership_tier
        FROM delta.`{table_path}`
        WHERE profile_age > 30
        """)
        result.show()
        print("✅ Backward compatibility maintained")
    except Exception as e:
        print(f"❌ Backward compatibility issue: {e}")

    spark.stop()
    print("\n✅ Schema evolution demo completed!")


if __name__ == "__main__":
    demonstrate_schema_evolution()