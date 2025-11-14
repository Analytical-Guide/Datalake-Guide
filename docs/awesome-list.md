---
title: Awesome Delta Lake & Apache Iceberg Resources
description: Curated list of high-quality learning materials and tools for Delta Lake and Apache Iceberg practitioners.
permalink: /docs/awesome-list/
---

# Awesome Delta Lake & Apache Iceberg Resources

A curated list of articles, blog posts, videos, and resources about Delta Lake and Apache Iceberg, automatically maintained by our community and AI-powered aggregator.

## 🌟 Featured Resources

### Official Documentation

- [Delta Lake Official Docs](https://docs.delta.io/) - Comprehensive Delta Lake documentation
- [Apache Iceberg Official Docs](https://iceberg.apache.org/docs/latest/) - Complete Iceberg documentation
- [Delta Lake GitHub](https://github.com/delta-io/delta) - Delta Lake source code
- [Apache Iceberg GitHub](https://github.com/apache/iceberg) - Iceberg source code

### Specifications

- [Delta Transaction Log Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md) - Delta's ACID transaction protocol
- [Iceberg Table Spec](https://iceberg.apache.org/spec/) - Apache Iceberg's table format specification

## Recent Articles

*This section is automatically updated by our resource aggregator bot. New articles are added weekly and reviewed by the community.*

### [Introducing Delta Lake 3.0](https://delta.io/blog/delta-lake-3-0/)

*Discovered: 2024-01-01*

Delta Lake 3.0 brings significant improvements including better performance, enhanced schema evolution capabilities, and improved compatibility with Apache Spark 3.5.

---

### [Apache Iceberg: The Definitive Guide](https://iceberg.apache.org/blogs/iceberg-guide/)

*Discovered: 2024-01-01*

Comprehensive guide covering Iceberg architecture, design decisions, and best practices for production deployments.

---

## 📚 Learning Resources

### Tutorials

- [Delta Lake Quickstart](../tutorials/getting-started.md) - Get started with Delta Lake
- [Iceberg Quickstart](../tutorials/getting-started.md) - Get started with Apache Iceberg
- [Migration Guide: Parquet to Delta/Iceberg](../tutorials/migration.md) - Convert existing data lakes

### Video Content

- [Databricks YouTube Channel](https://www.youtube.com/@Databricks) - Delta Lake videos and webinars
- [Apache Iceberg Talks](https://iceberg.apache.org/community/#talks) - Conference presentations

### Books

- "Delta Lake: The Definitive Guide" by Denny Lee and Tristen Wentling
- "Building the Data Lakehouse" by Bill Inmon, et al.

## 🛠️ Tools and Libraries

### Delta Lake Ecosystem

- [delta-rs](https://github.com/delta-io/delta-rs) - Native Rust implementation
- [kafka-delta-ingest](https://github.com/delta-io/kafka-delta-ingest) - Stream from Kafka to Delta
- [delta-sharing](https://github.com/delta-io/delta-sharing) - Open protocol for data sharing

### Iceberg Ecosystem

- [PyIceberg](https://py.iceberg.apache.org/) - Python library for Iceberg
- [Iceberg Go](https://github.com/apache/iceberg-go) - Go implementation
- [Nessie](https://projectnessie.org/) - Git-like version control for data lakes

### Query Engines

- [Apache Spark](https://spark.apache.org/) - Both Delta and Iceberg
- [Trino](https://trino.io/) - Both Delta and Iceberg
- [Apache Flink](https://flink.apache.org/) - Excellent Iceberg support
- [Dremio](https://www.dremio.com/) - Iceberg-native query engine
- [Athena](https://aws.amazon.com/athena/) - AWS-managed, supports both

## 🏢 Case Studies

### Delta Lake

- **Netflix**: Processing petabytes of data with Delta Lake
- **Comcast**: Real-time streaming analytics
- **Adobe**: Marketing analytics at scale
- **Riot Games**: Gaming analytics and ML pipelines

### Apache Iceberg

- **Netflix**: Original creator, uses Iceberg for data warehousing
- **Apple**: Large-scale data processing
- **LinkedIn**: Data platform modernization
- **Expedia**: Travel data analytics

## 📊 Comparisons and Benchmarks

- [Feature Comparison Matrix](comparisons/feature-matrix.md) - Side-by-side comparison
- [TPC-DS Benchmarks](https://www.databricks.com/blog/2023/04/14/delta-lake-3-0-performance.html) - Performance benchmarks
- [Onehouse Benchmark](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison) - Multi-format comparison

## 🎓 Courses and Training

### Free Courses

- [Databricks Academy](https://academy.databricks.com/) - Free Delta Lake courses
- [Apache Iceberg Tutorials](https://iceberg.apache.org/docs/latest/spark-getting-started/) - Official tutorials

### Paid Courses

- [Udemy: Delta Lake Deep Dive](https://www.udemy.com/topic/delta-lake/)
- [Coursera: Data Engineering with Databricks](https://www.coursera.org/specializations/data-engineering-databricks)

## 🔧 Integration Guides

### Cloud Platforms

- [Delta Lake on AWS](https://docs.delta.io/latest/delta-lake-on-aws.html)
- [Delta Lake on Azure](https://docs.delta.io/latest/delta-lake-on-azure.html)
- [Delta Lake on GCP](https://docs.delta.io/latest/delta-lake-on-gcp.html)
- [Iceberg on AWS](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-iceberg.html)
- [Iceberg on Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/iceberg/)
- [Iceberg on GCP](https://cloud.google.com/dataproc/docs/tutorials/iceberg-hms)

### BI Tools

- [Tableau with Delta Lake](https://docs.delta.io/latest/delta-utility.html#tableau-integration)
- [Power BI with Delta Lake](https://docs.microsoft.com/en-us/power-bi/connect-data/desktop-connect-delta-lake)
- [Looker with Iceberg](https://cloud.google.com/looker/docs/other-databases)

## 🎤 Community

### Slack Channels

- [Delta Lake Slack](https://delta-users.slack.com/)
- [Apache Iceberg Slack](https://apache-iceberg.slack.com/)

### Mailing Lists

- [Delta Lake Mailing List](https://groups.google.com/g/delta-users)
- [Iceberg Dev List](mailto:dev@iceberg.apache.org)

### Meetups and Conferences

- [Data + AI Summit](https://www.databricks.com/dataaisummit/) - Annual Databricks conference
- [ApacheCon](https://www.apachecon.com/) - Apache Software Foundation conference
- Local Data Engineering Meetups

## 🔬 Research Papers

- [Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)
- [Apache Iceberg: Unlocking the Power of Open Standards](https://iceberg.apache.org/assets/iceberg-sigmod.pdf)

## 🤝 Contributing

This awesome list is community-maintained. To add a resource:

1. Check if it's already listed
2. Ensure it's relevant and high-quality
3. Submit a PR with your addition
4. Include a brief description

Our AI-powered aggregator also discovers new content weekly and creates PRs for review.

See our [Contributing Guide](../CONTRIBUTING.md) for details.

## 📜 License

This awesome list is part of the Delta Lake & Apache Iceberg Knowledge Hub, licensed under Apache 2.0.

---

**Last Updated**: 2025-11-14  
**Maintained By**: Community + AI Aggregator 🤖
