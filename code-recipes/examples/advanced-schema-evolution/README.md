---
title: Advanced Schema Evolution Recipe
permalink: /code-recipes/examples/advanced-schema-evolution/
description: Hands-on guide for managing complex schema evolution workflows using Delta Lake and Apache Iceberg.
---

# Advanced Schema Evolution Recipe

This recipe demonstrates advanced schema evolution patterns for complex data structures in Delta Lake and Apache Iceberg tables.

## Overview

Schema evolution is crucial for maintaining data lakes as business requirements change. This example shows how to:

- Add/remove columns with data migration
- Rename columns while maintaining compatibility
- Change data types safely
- Restructure nested data
- Maintain backward compatibility for queries

## Key Features Demonstrated

### 1. Complex Schema Management
- Nested structures with arrays and maps
- Multi-level nesting
- Complex data type handling

### 2. Evolution Operations
- **Add Columns**: With default values and constraints
- **Drop Columns**: With safety checks and dependency analysis
- **Rename Columns**: With data migration and aliasing
- **Type Changes**: Safe type conversions with validation
- **Nested Restructuring**: Flatten or create nested structures

### 3. Safety & Validation
- Pre-evolution validation
- Impact assessment
- Backward compatibility checks
- Data integrity validation

## Running the Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the evolution demo
python solution.py
```

## Expected Output

The script will:
1. Create a complex initial schema with nested customer data
2. Apply multiple evolution operations
3. Show schema changes at each step
4. Demonstrate backward compatibility
5. Display evolution history

## Key Classes

### `SchemaEvolutionManager`
Main class handling all evolution operations:

- `evolve_schema()`: Execute evolution based on specification
- `validate_evolution()`: Pre-validate operations
- `get_evolution_history()`: Track all changes

### Evolution Operations

#### Add Columns
```python
{
    "operation": "add_columns",
    "columns": [
        {"name": "new_field", "type": "STRING", "default": "'default_value'"}
    ]
}
```

#### Rename Columns
```python
{
    "operation": "rename_columns",
    "renames": {"old_name": "new_name"}
}
```

#### Type Changes
```python
{
    "operation": "change_data_types",
    "type_changes": [
        {
            "column": "field_name",
            "new_type": "DOUBLE",
            "conversion_func": "CAST(field_name AS DOUBLE)"
        }
    ]
}
```

## Production Considerations

### Safety Measures
- Always backup before evolution
- Test on sample data first
- Validate downstream impacts
- Use transactions for atomic changes

### Performance Impact
- Some operations require full table rewrites
- Plan for downtime or use blue-green deployments
- Consider partitioning strategies

### Compatibility
- Maintain query compatibility across versions
- Use views for complex migrations
- Document breaking changes

## Troubleshooting

### Common Issues

1. **Column Not Found**: Check column name spelling and case
2. **Type Conversion Errors**: Validate data before conversion
3. **Nested Structure Issues**: Ensure proper field paths
4. **Permission Errors**: Verify write access to table location

### Recovery
- Use time travel to revert changes
- Restore from backups if needed
- Check evolution history for debugging

## Next Steps

- Explore conditional evolution based on data patterns
- Implement automated evolution pipelines
- Add support for custom transformation functions
- Integrate with schema registries