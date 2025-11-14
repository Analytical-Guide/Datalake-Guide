# Problem: Advanced Schema Evolution and Migration

## Use Case

You need to evolve a complex e-commerce schema through multiple versions while maintaining data integrity, supporting zero-downtime migrations, and handling backward compatibility for analytics queries.

## Context

Schema evolution is critical in modern data lakes where business requirements change frequently. This recipe demonstrates advanced patterns for evolving complex schemas with nested structures, arrays, and maps while maintaining query compatibility across versions.

## Requirements

- Apache Spark 3.x or later
- Delta Lake or Apache Iceberg
- Complex nested data structures
- Version compatibility requirements
- Zero-downtime migration capabilities

## Expected Outcome

After running this recipe, you will have:
- A schema evolution framework supporting complex changes
- Backward-compatible query patterns
- Automated migration scripts
- Data integrity validation across versions
- Performance-optimized evolution strategies

## Real-World Applications

- E-commerce platform schema updates
- Customer data platform evolution
- Product catalog management
- User profile enhancement
- Analytics schema standardization

## Complexity Level: Advanced

This recipe covers:
- Nested structure evolution
- Array and map modifications
- Column renaming with aliases
- Data type migrations
- Partitioning strategy changes
- Multi-version compatibility