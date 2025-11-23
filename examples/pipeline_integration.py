"""
Complete Pipeline Integration Example
Demonstrates end-to-end data quality framework usage in a data pipeline.
"""


import numpy as np
import pandas as pd

from dqf import DQFramework, ValidationRule
from dqf.validator import Severity


print("=" * 80)
print("Data Quality Framework - Complete Pipeline Example")
print("=" * 80)

# Simulate a data pipeline scenario
print("\n📦 Step 1: Simulating data ingestion from multiple sources...")

# Source 1: Customer data from CRM
np.random.seed(42)
customers_df = pd.DataFrame(
    {
        "customer_id": range(1, 501),
        "name": [f"Customer {i}" for i in range(1, 501)],
        "email": [f"customer{i}@example.com" if i % 15 != 0 else None for i in range(1, 501)],
        "phone": [f"+1555{i:07d}" if i % 20 != 0 else "invalid" for i in range(1, 501)],
        "signup_date": pd.date_range("2023-01-01", periods=500, freq="D"),
        "country": np.random.choice(["USA", "Canada", "UK", "Germany", None], 500, p=[0.4, 0.2, 0.2, 0.15, 0.05]),
        "age": np.random.randint(18, 80, 500),
        "source": "CRM",
    }
)

# Source 2: Transaction data from database
transactions_df = pd.DataFrame(
    {
        "transaction_id": range(1, 1001),
        "customer_id": np.random.randint(1, 501, 1000),
        "amount": np.random.gamma(2, 50, 1000),
        "transaction_date": pd.date_range("2024-01-01", periods=1000, freq="H"),
        "status": np.random.choice(["completed", "pending", "failed", "refunded"], 1000, p=[0.7, 0.15, 0.1, 0.05]),
        "payment_method": np.random.choice(
            ["credit_card", "debit_card", "paypal", None], 1000, p=[0.5, 0.3, 0.15, 0.05]
        ),
        "source": "Database",
    }
)

# Add some data quality issues
transactions_df.loc[transactions_df["amount"] > 400, "amount"] = -10  # Negative amounts
transactions_df.loc[::50, "customer_id"] = 9999  # Invalid customer IDs

print(f"✓ Loaded customers: {len(customers_df):,} rows")
print(f"✓ Loaded transactions: {len(transactions_df):,} rows")

# Step 2: Profile the data
print("\n📊 Step 2: Profiling datasets...")

dqf = DQFramework.from_config("config/data_quality_config.yaml")

# Profile customers
print("\nProfiling customer data...")
customer_profile = dqf.profiler.profile(customers_df, dataset_name="customers")
print(f"  Completeness: {customer_profile.overall_completeness:.2%}")
print(f"  Duplicate rows: {customer_profile.duplicate_rows}")

if customer_profile.warnings:
    print("  Warnings:")
    for warning in customer_profile.warnings[:3]:
        print(f"    ⚠️  {warning}")

# Profile transactions
print("\nProfiling transaction data...")
transaction_profile = dqf.profiler.profile(transactions_df, dataset_name="transactions")
print(f"  Completeness: {transaction_profile.overall_completeness:.2%}")
print(f"  Row count: {transaction_profile.row_count:,}")

# Step 3: Validate data quality
print("\n✅ Step 3: Validating data quality...")

# Customer validation rules
customer_rules = [
    ValidationRule("customer_id", "not_null", "Customer ID required", Severity.CRITICAL),
    ValidationRule("customer_id", "unique", "Customer IDs must be unique", Severity.CRITICAL),
    ValidationRule("email", "email", "Valid email required", Severity.HIGH, allow_null=True),
    ValidationRule("age", "range", "Age must be 18-100", Severity.MEDIUM, params={"min": 18, "max": 100}),
    ValidationRule("country", "not_null", "Country required", Severity.HIGH),
]

customer_validation = dqf.validator.validate(customers_df, customer_rules, dataset_name="customers")
print(f"\nCustomer validation: {'✅ PASS' if customer_validation.is_valid else '❌ FAIL'}")
print(f"  Rules passed: {customer_validation.passed_rules}/{customer_validation.total_rules}")

if customer_validation.failure_count > 0:
    print(f"  Failures: {customer_validation.failure_count}")
    for failure in customer_validation.get_failures()[:3]:
        print(f"    • {failure.column}: {failure.failure_count} issues ({failure.failure_percentage:.1f}%)")

# Transaction validation rules
transaction_rules = [
    ValidationRule("transaction_id", "not_null", "Transaction ID required", Severity.CRITICAL),
    ValidationRule("transaction_id", "unique", "Transaction IDs must be unique", Severity.CRITICAL),
    ValidationRule("customer_id", "not_null", "Customer ID required", Severity.CRITICAL),
    ValidationRule("amount", "positive", "Amount must be positive", Severity.CRITICAL),
    ValidationRule(
        "status",
        "in_list",
        "Valid status required",
        Severity.HIGH,
        params={"allowed_values": ["completed", "pending", "failed", "refunded"]},
    ),
    ValidationRule("payment_method", "not_null", "Payment method required", Severity.HIGH),
]

transaction_validation = dqf.validator.validate(transactions_df, transaction_rules, dataset_name="transactions")
print(f"\nTransaction validation: {'✅ PASS' if transaction_validation.is_valid else '❌ FAIL'}")
print(f"  Rules passed: {transaction_validation.passed_rules}/{transaction_validation.total_rules}")

if transaction_validation.failure_count > 0:
    print(f"  Failures: {transaction_validation.failure_count}")
    for failure in transaction_validation.get_failures()[:3]:
        print(f"    • {failure.column}: {failure.failure_count} issues ({failure.failure_percentage:.1f}%)")

# Step 4: Monitor quality metrics
print("\n📈 Step 4: Monitoring quality metrics...")

customer_metrics = dqf.monitor.measure_quality(
    customers_df, dataset_name="customers", validation_result=customer_validation, timestamp_column="signup_date"
)

transaction_metrics = dqf.monitor.measure_quality(
    transactions_df,
    dataset_name="transactions",
    validation_result=transaction_validation,
    timestamp_column="transaction_date",
)

print("\nCustomer Data Quality:")
print(f"  Quality Score: {customer_metrics.quality_score:.2%}")
print(f"  Completeness: {customer_metrics.completeness:.2%}")
print(f"  Validity: {customer_metrics.validity:.2%}")
print(f"  Data Age: {customer_metrics.data_age_hours:.1f} hours")

print("\nTransaction Data Quality:")
print(f"  Quality Score: {transaction_metrics.quality_score:.2%}")
print(f"  Completeness: {transaction_metrics.completeness:.2%}")
print(f"  Validity: {transaction_metrics.validity:.2%}")
print(f"  Validation Failures: {transaction_metrics.validation_failures}")

# Step 5: Generate comprehensive reports
print("\n📄 Step 5: Generating quality reports...")

# Generate customer report
customer_profile.to_html("reports/pipeline_customers_profile.html")
customer_profile.to_json("reports/pipeline_customers_profile.json")
print("✓ Customer reports generated")

# Generate transaction report
transaction_profile.to_html("reports/pipeline_transactions_profile.html")
transaction_profile.to_json("reports/pipeline_transactions_profile.json")
print("✓ Transaction reports generated")

# Step 6: Check for alerts
print("\n🚨 Step 6: Checking for quality alerts...")

active_alerts = dqf.monitor.get_active_alerts()
if active_alerts:
    print(f"\n⚠️  {len(active_alerts)} active alert(s):")
    for alert in active_alerts[:5]:
        print(f"  • [{alert.severity}] {alert.dataset_name}: {alert.description}")
else:
    print("✅ No active alerts")

# Step 7: Data quality decision
print("\n🎯 Step 7: Pipeline decision making...")

# Define quality thresholds
QUALITY_THRESHOLD = 0.90
CRITICAL_FAILURES_ALLOWED = 0

print("\nQuality Gates:")
print(f"  Minimum Quality Score: {QUALITY_THRESHOLD:.0%}")
print(f"  Critical Failures Allowed: {CRITICAL_FAILURES_ALLOWED}")

# Check if data passes quality gates
customer_passes = (
    customer_metrics.quality_score >= QUALITY_THRESHOLD
    and len(customer_validation.critical_failures) == CRITICAL_FAILURES_ALLOWED
)

transaction_passes = (
    transaction_metrics.quality_score >= QUALITY_THRESHOLD
    and len(transaction_validation.critical_failures) == CRITICAL_FAILURES_ALLOWED
)

print(f"\nCustomer Data: {'✅ APPROVED' if customer_passes else '❌ REJECTED'}")
print(f"Transaction Data: {'✅ APPROVED' if transaction_passes else '❌ REJECTED'}")

if customer_passes and transaction_passes:
    print("\n✅ All quality gates passed - proceeding with data pipeline")
    print("   → Data loaded to warehouse")
    print("   → Downstream processes triggered")
    print("   → Quality metrics logged")
else:
    print("\n❌ Quality gates failed - data pipeline halted")
    print("   → Data quarantined for review")
    print("   → Alerts sent to data team")
    print("   → Rollback initiated")

    # Show detailed failure reasons
    if not customer_passes:
        print("\n   Customer issues:")
        print(f"   - Quality score: {customer_metrics.quality_score:.2%} (threshold: {QUALITY_THRESHOLD:.0%})")
        if customer_validation.critical_failures:
            print(f"   - Critical failures: {len(customer_validation.critical_failures)}")

    if not transaction_passes:
        print("\n   Transaction issues:")
        print(f"   - Quality score: {transaction_metrics.quality_score:.2%} (threshold: {QUALITY_THRESHOLD:.0%})")
        if transaction_validation.critical_failures:
            print(f"   - Critical failures: {len(transaction_validation.critical_failures)}")

# Summary
print("\n" + "=" * 80)
print("Pipeline Execution Summary")
print("=" * 80)
print("Total datasets processed: 2")
print(f"Total rows analyzed: {len(customers_df) + len(transactions_df):,}")
print(f"Validation rules executed: {customer_validation.total_rules + transaction_validation.total_rules}")
print("Reports generated: 4")
print("Quality metrics tracked: 2")
print(f"Overall status: {'✅ SUCCESS' if customer_passes and transaction_passes else '❌ FAILED'}")
print("=" * 80)

print("\n📊 View detailed reports:")
print("  • reports/pipeline_customers_profile.html")
print("  • reports/pipeline_transactions_profile.html")
print("\n🎓 This example demonstrates:")
print("  ✓ Multi-source data profiling")
print("  ✓ Comprehensive validation rules")
print("  ✓ Quality metrics monitoring")
print("  ✓ Alert detection")
print("  ✓ Quality gate enforcement")
print("  ✓ Pipeline decision making")
print("\n" + "=" * 80)
