"""
Recipe: Financial Transactions Processing and Analytics
Purpose: Demonstrate comprehensive financial data platform with Delta Lake
Author: Community
Date: 2025-11-14
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from delta.tables import DeltaTable
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import os
import shutil
import hashlib
from decimal import Decimal
import random


class FinancialTransactionProcessor:
    """Comprehensive financial transaction processing system"""

    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.audit_log = []
        self.compliance_rules = config.get("compliance_rules", {})

    def process_transaction_batch(self, transactions_df) -> Tuple[bool, Dict[str, Any]]:
        """Process a batch of financial transactions with full validation and compliance"""

        processing_results = {
            "processed_count": 0,
            "rejected_count": 0,
            "fraud_flags": 0,
            "compliance_violations": 0,
            "processing_time": 0
        }

        start_time = datetime.now()

        try:
            # Step 1: Data validation and cleansing
            validated_df = self._validate_transaction_data(transactions_df)
            processing_results["validated_count"] = validated_df.count()

            # Step 2: Fraud detection
            fraud_scored_df = self._apply_fraud_detection(validated_df)
            fraud_flags = fraud_scored_df.filter(col("fraud_score") > 0.7).count()
            processing_results["fraud_flags"] = fraud_flags

            # Step 3: Compliance checking
            compliant_df, violations = self._check_compliance(fraud_scored_df)
            processing_results["compliance_violations"] = len(violations)

            # Step 4: Regulatory reporting preparation
            reporting_df = self._prepare_regulatory_reporting(compliant_df)

            # Step 5: Store processed transactions
            success = self._store_transactions(reporting_df)
            processing_results["processed_count"] = reporting_df.count() if success else 0
            processing_results["rejected_count"] = validated_df.count() - processing_results["processed_count"]

            # Step 6: Update analytics tables
            self._update_analytics_tables(reporting_df)

            # Step 7: Audit logging
            self._log_audit_event("batch_processed", processing_results)

            processing_results["processing_time"] = (datetime.now() - start_time).total_seconds()

            return True, processing_results

        except Exception as e:
            self._log_audit_event("batch_failed", {"error": str(e)})
            processing_results["processing_time"] = (datetime.now() - start_time).total_seconds()
            return False, processing_results

    def _validate_transaction_data(self, df):
        """Comprehensive data validation for financial transactions"""

        # Required field validation
        required_fields = ["transaction_id", "account_id", "amount", "currency", "transaction_date"]
        for field in required_fields:
            df = df.filter(col(field).isNotNull())

        # Data type validation
        df = df.withColumn("amount", col("amount").cast(DecimalType(18, 4)))
        df = df.withColumn("transaction_date", col("transaction_date").cast(TimestampType()))

        # Business rule validation
        df = df.filter((col("amount") > 0) & (col("amount") < 1000000))  # Reasonable amount limits
        df = df.filter(col("currency").isin(["USD", "EUR", "GBP", "JPY", "CAD"]))  # Supported currencies

        # Duplicate detection
        window_spec = Window.partitionBy("transaction_id").orderBy(col("transaction_date").desc())
        df = df.withColumn("dup_rank", row_number().over(window_spec))
        df = df.filter(col("dup_rank") == 1).drop("dup_rank")

        # Add validation timestamp
        df = df.withColumn("validated_at", current_timestamp())
        df = df.withColumn("validation_status", lit("passed"))

        return df

    def _apply_fraud_detection(self, df):
        """Apply fraud detection scoring"""

        # Simple rule-based fraud detection (in production, use ML models)
        fraud_df = df.withColumn("fraud_score", lit(0.0))

        # High amount transactions
        fraud_df = fraud_df.withColumn("fraud_score",
            when(col("amount") > 50000, col("fraud_score") + 0.3)
            .otherwise(col("fraud_score"))
        )

        # Round number amounts (suspicious)
        fraud_df = fraud_df.withColumn("fraud_score",
            when((col("amount") % 1000) == 0, col("fraud_score") + 0.2)
            .otherwise(col("fraud_score"))
        )

        # International transactions
        fraud_df = fraud_df.withColumn("fraud_score",
            when(col("merchant_country") != col("account_country"), col("fraud_score") + 0.1)
            .otherwise(col("fraud_score"))
        )

        # Velocity checks (multiple transactions in short time)
        window_spec = Window.partitionBy("account_id").orderBy(col("transaction_date"))
        fraud_df = fraud_df.withColumn("prev_txn_time", lag("transaction_date").over(window_spec))
        fraud_df = fraud_df.withColumn("time_diff_hours",
            (unix_timestamp(col("transaction_date")) - unix_timestamp(col("prev_txn_time"))) / 3600)

        fraud_df = fraud_df.withColumn("fraud_score",
            when((col("time_diff_hours") < 1) & (col("amount") > 1000), col("fraud_score") + 0.4)
            .otherwise(col("fraud_score"))
        )

        # Cap fraud score at 1.0
        fraud_df = fraud_df.withColumn("fraud_score", least(col("fraud_score"), lit(1.0)))

        # Add fraud detection timestamp
        fraud_df = fraud_df.withColumn("fraud_checked_at", current_timestamp())

        return fraud_df

    def _check_compliance(self, df) -> Tuple:
        """Check regulatory compliance requirements"""

        violations = []

        # AML (Anti-Money Laundering) checks
        suspicious_patterns = df.filter(
            (col("amount") > 10000) &
            (col("merchant_category") == "cash_advance") &
            (col("account_country") != col("merchant_country"))
        )

        if suspicious_patterns.count() > 0:
            violations.append({
                "type": "AML_SUSPICIOUS_ACTIVITY",
                "description": "Large cash advances to foreign merchants",
                "affected_transactions": suspicious_patterns.count()
            })

        # OFAC (Office of Foreign Assets Control) checks
        # In production, check against OFAC sanctioned entities
        sanctioned_merchants = ["suspicious_merchant_1", "suspicious_merchant_2"]
        ofac_violations = df.filter(col("merchant_name").isin(sanctioned_merchants))

        if ofac_violations.count() > 0:
            violations.append({
                "type": "OFAC_SANCTIONED_ENTITY",
                "description": "Transactions with sanctioned entities",
                "affected_transactions": ofac_violations.count()
            })

        # Filter out violating transactions
        compliant_df = df.filter(
            ~((col("amount") > 10000) &
              (col("merchant_category") == "cash_advance") &
              (col("account_country") != col("merchant_country")))
        )

        compliant_df = compliant_df.filter(~col("merchant_name").isin(sanctioned_merchants))

        # Add compliance check timestamp
        compliant_df = compliant_df.withColumn("compliance_checked_at", current_timestamp())
        compliant_df = compliant_df.withColumn("compliance_status", lit("passed"))

        return compliant_df, violations

    def _prepare_regulatory_reporting(self, df):
        """Prepare data for regulatory reporting"""

        # Add required regulatory fields
        reporting_df = df.withColumn("reporting_date", date_format(current_date(), "yyyy-MM-dd"))
        reporting_df = df.withColumn("record_id", concat(lit("FIN_"), col("transaction_id")))
        reporting_df = df.withColumn("data_hash", sha2(concat_ws("||", *df.columns), 256))

        # Add audit trail
        reporting_df = reporting_df.withColumn("audit_trail", array(
            struct(
                lit("validation").alias("stage"),
                col("validated_at").alias("timestamp"),
                lit("passed").alias("status")
            ),
            struct(
                lit("fraud_check").alias("stage"),
                col("fraud_checked_at").alias("timestamp"),
                when(col("fraud_score") > 0.7, lit("flagged")).otherwise(lit("passed")).alias("status")
            ),
            struct(
                lit("compliance").alias("stage"),
                col("compliance_checked_at").alias("timestamp"),
                lit("passed").alias("status")
            )
        ))

        return reporting_df

    def _store_transactions(self, df) -> bool:
        """Store processed transactions in Delta table"""

        try:
            table_path = self.config.get("transactions_table", "/tmp/financial/transactions")

            # Enable Change Data Feed for audit purposes
            self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS delta.`{table_path}` (
                transaction_id STRING,
                account_id STRING,
                amount DECIMAL(18,4),
                currency STRING,
                transaction_date TIMESTAMP,
                merchant_name STRING,
                merchant_category STRING,
                merchant_country STRING,
                account_country STRING,
                fraud_score DOUBLE,
                compliance_status STRING,
                validation_status STRING,
                reporting_date STRING,
                record_id STRING,
                data_hash STRING,
                audit_trail ARRAY<STRUCT<stage: STRING, timestamp: TIMESTAMP, status: STRING>>,
                processed_at TIMESTAMP
            )
            USING DELTA
            TBLPROPERTIES (
                'delta.enableChangeDataFeed' = 'true',
                'delta.logRetentionDuration' = '365 days'
            )
            """)

            # Add processing timestamp
            df = df.withColumn("processed_at", current_timestamp())

            # Upsert transactions (handle duplicates)
            delta_table = DeltaTable.forPath(self.spark, table_path)

            merge_condition = "target.transaction_id = source.transaction_id"
            delta_table.alias("target").merge(
                df.alias("source"),
                merge_condition
            ).whenNotMatchedInsertAll().execute()

            return True

        except Exception as e:
            print(f"Failed to store transactions: {e}")
            return False

    def _update_analytics_tables(self, df):
        """Update analytics tables for real-time dashboards"""

        # Daily transaction summary
        daily_summary = df.groupBy(
            date_format(col("transaction_date"), "yyyy-MM-dd").alias("date"),
            col("currency"),
            col("merchant_category")
        ).agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            count(when(col("fraud_score") > 0.7, True)).alias("fraud_count")
        )

        # Store daily summary
        summary_path = self.config.get("daily_summary_table", "/tmp/financial/daily_summary")
        daily_summary.write.format("delta").mode("overwrite").save(summary_path)

        # Account risk scoring
        account_risk = df.groupBy("account_id").agg(
            count("*").alias("total_transactions"),
            sum("amount").alias("total_amount"),
            avg("fraud_score").alias("avg_fraud_score"),
            max("fraud_score").alias("max_fraud_score"),
            count(when(col("fraud_score") > 0.7, True)).alias("high_risk_transactions")
        ).withColumn("risk_level",
            when(col("avg_fraud_score") > 0.5, "HIGH")
            .when(col("avg_fraud_score") > 0.3, "MEDIUM")
            .otherwise("LOW")
        )

        # Store account risk
        risk_path = self.config.get("account_risk_table", "/tmp/financial/account_risk")
        account_risk.write.format("delta").mode("overwrite").save(risk_path)

    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit events for compliance"""

        audit_entry = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "details": details,
            "user": "system",  # In production, get from context
            "session_id": "batch_processing"
        }

        self.audit_log.append(audit_entry)

        # In production, write to audit table
        audit_df = self.spark.createDataFrame([audit_entry])
        audit_path = self.config.get("audit_table", "/tmp/financial/audit_log")
        audit_df.write.format("delta").mode("append").save(audit_path)

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""

        stats = {
            "total_audit_events": len(self.audit_log),
            "recent_events": self.audit_log[-10:] if self.audit_log else []
        }

        # Get table statistics
        try:
            transactions_path = self.config.get("transactions_table", "/tmp/financial/transactions")
            if os.path.exists(transactions_path):
                txn_df = self.spark.read.format("delta").load(transactions_path)
                stats["total_transactions"] = txn_df.count()
                stats["fraud_rate"] = txn_df.filter(col("fraud_score") > 0.7).count() / txn_df.count()
                stats["total_volume"] = txn_df.agg(sum("amount")).collect()[0][0]
        except:
            stats["total_transactions"] = 0

        return stats


def generate_sample_financial_data(num_transactions: int = 1000) -> List[Dict[str, Any]]:
    """Generate realistic sample financial transaction data"""

    merchants = [
        ("Amazon", "ecommerce", "USA"),
        ("Starbucks", "food", "USA"),
        ("Uber", "transport", "USA"),
        ("Walmart", "retail", "USA"),
        ("Netflix", "entertainment", "USA"),
        ("Shell", "fuel", "USA"),
        ("Foreign Merchant", "ecommerce", "GBR"),
        ("Cash Advance ATM", "cash_advance", "USA")
    ]

    currencies = ["USD", "EUR", "GBP"]
    countries = ["USA", "GBR", "DEU", "FRA"]

    transactions = []

    for i in range(num_transactions):
        merchant_name, category, merchant_country = random.choice(merchants)
        account_country = random.choice(countries)

        # Generate realistic amounts based on category
        if category == "fuel":
            amount = round(random.uniform(20, 80), 2)
        elif category == "food":
            amount = round(random.uniform(5, 50), 2)
        elif category == "ecommerce":
            amount = round(random.uniform(10, 500), 2)
        elif category == "cash_advance":
            amount = round(random.uniform(100, 1000), 2)
        else:
            amount = round(random.uniform(1, 200), 2)

        transaction = {
            "transaction_id": "04d",
            "account_id": "04d",
            "amount": amount,
            "currency": random.choice(currencies),
            "transaction_date": datetime.now() - timedelta(days=random.randint(0, 30)),
            "merchant_name": merchant_name,
            "merchant_category": category,
            "merchant_country": merchant_country,
            "account_country": account_country
        }

        transactions.append(transaction)

    return transactions


def demonstrate_financial_processing():
    """Demonstrate comprehensive financial transaction processing"""

    print("💰 Financial Transactions Processing Demo")
    print("=" * 50)

    # Configuration
    config = {
        "transactions_table": "/tmp/financial/transactions",
        "daily_summary_table": "/tmp/financial/daily_summary",
        "account_risk_table": "/tmp/financial/account_risk",
        "audit_table": "/tmp/financial/audit_log",
        "compliance_rules": {
            "aml_threshold": 10000,
            "ofac_check_enabled": True,
            "fraud_threshold": 0.7
        }
    }

    # Initialize Spark
    spark = (SparkSession.builder
             .appName("FinancialProcessingDemo")
             .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
             .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
             .getOrCreate())

    spark.sparkContext.setLogLevel("WARN")

    try:
        # Clean up previous run
        for table_path in [config["transactions_table"], config["daily_summary_table"],
                          config["account_risk_table"], config["audit_table"]]:
            if os.path.exists(table_path):
                shutil.rmtree(table_path)

        # Generate sample financial data
        print("\n📝 Generating sample financial transactions...")
        sample_data = generate_sample_financial_data(2000)
        transactions_df = spark.createDataFrame(sample_data)

        print(f"✅ Generated {len(sample_data)} sample transactions")
        transactions_df.show(5, truncate=False)

        # Initialize financial processor
        processor = FinancialTransactionProcessor(spark, config)

        # Process transactions
        print("\n🔄 Processing transactions...")
        success, results = processor.process_transaction_batch(transactions_df)

        if success:
            print("✅ Batch processing completed successfully!")
            print(f"   Processed: {results['processed_count']} transactions")
            print(f"   Rejected: {results['rejected_count']} transactions")
            print(f"   Fraud flags: {results['fraud_flags']}")
            print(f"   Compliance violations: {results['compliance_violations']}")
            print(".2f")
        else:
            print("❌ Batch processing failed!")
            return

        # Show processed data
        print("\n📊 Processed Transactions Sample:")
        processed_df = spark.read.format("delta").load(config["transactions_table"])
        processed_df.select("transaction_id", "amount", "fraud_score", "compliance_status").show(10)

        # Show analytics
        print("\n📈 Daily Summary:")
        summary_df = spark.read.format("delta").load(config["daily_summary_table"])
        summary_df.show()

        print("\n🎯 Account Risk Analysis:")
        risk_df = spark.read.format("delta").load(config["account_risk_table"])
        risk_df.show()

        # Show audit trail
        print("\n📜 Audit Log Sample:")
        audit_df = spark.read.format("delta").load(config["audit_table"])
        audit_df.select("timestamp", "event_type", "details").show(truncate=False)

        # Show processing statistics
        stats = processor.get_processing_stats()
        print("\n📊 Processing Statistics:")
        print(f"   Total transactions: {stats.get('total_transactions', 0)}")
        print(f"   Fraud rate: {stats.get('fraud_rate', 0):.2%}")
        print(f"   Total volume: ${stats.get('total_volume', 0):,.2f}")
        print(f"   Audit events: {stats['total_audit_events']}")

        print("\n✅ Financial processing demo completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    demonstrate_financial_processing()