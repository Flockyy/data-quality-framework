"""
Example: Data Validation with Custom Rules
Demonstrates validation rules and custom validators.
"""

import numpy as np
import pandas as pd

from dqf import DataValidator, ValidationRule
from dqf.validator import Severity


# Create sample sales data
np.random.seed(42)

data = {
    "order_id": range(1, 501),
    "customer_email": [f"customer{i}@example.com" if i % 20 != 0 else f"invalid_email_{i}" for i in range(1, 501)],
    "product_name": np.random.choice(["Laptop", "Phone", "Tablet", "Monitor"], 500),
    "quantity": np.random.randint(-2, 20, 500),  # Some negative quantities
    "unit_price": np.random.uniform(10, 2000, 500),
    "discount_percentage": np.random.uniform(-5, 50, 500),  # Some invalid discounts
    "order_date": pd.date_range("2024-01-01", periods=500, freq="H"),
    "delivery_date": pd.date_range("2024-01-01", periods=500, freq="H") + pd.Timedelta(days=3),
    "status": np.random.choice(
        ["pending", "confirmed", "shipped", "delivered", "invalid"], 500, p=[0.2, 0.3, 0.3, 0.15, 0.05]
    ),
    "payment_method": np.random.choice(["credit_card", "debit_card", "paypal", None], 500, p=[0.4, 0.3, 0.25, 0.05]),
}

# Add some nulls
data["customer_email"][::50] = None
data["quantity"][::100] = None

df = pd.DataFrame(data)

# Calculate total amount
df["total_amount"] = df["quantity"] * df["unit_price"] * (1 - df["discount_percentage"] / 100)

print("=" * 80)
print("Data Validation Example")
print("=" * 80)
print(f"\nDataset: {len(df)} orders")

# Initialize validator
validator = DataValidator(
    fail_fast=False,
    parallel=True,
    max_workers=4,
    sample_failures=5,
)

# Define validation rules
rules = [
    # Completeness checks
    ValidationRule(
        column="order_id",
        rule_type="not_null",
        description="Order ID must be present",
        severity=Severity.CRITICAL,
    ),
    ValidationRule(
        column="customer_email",
        rule_type="not_null",
        description="Customer email is required",
        severity=Severity.HIGH,
    ),
    ValidationRule(
        column="payment_method",
        rule_type="not_null",
        description="Payment method is required",
        severity=Severity.HIGH,
    ),
    # Format validation
    ValidationRule(
        column="customer_email",
        rule_type="email",
        description="Email must be valid format",
        severity=Severity.HIGH,
        allow_null=True,
    ),
    # Range validation
    ValidationRule(
        column="quantity",
        rule_type="range",
        description="Quantity must be between 1 and 100",
        severity=Severity.CRITICAL,
        params={"min": 1, "max": 100},
    ),
    ValidationRule(
        column="unit_price",
        rule_type="greater_than",
        description="Unit price must be positive",
        severity=Severity.CRITICAL,
        params={"value": 0},
    ),
    ValidationRule(
        column="discount_percentage",
        rule_type="range",
        description="Discount must be between 0 and 50%",
        severity=Severity.MEDIUM,
        params={"min": 0, "max": 50},
    ),
    ValidationRule(
        column="total_amount",
        rule_type="greater_than",
        description="Total amount must be positive",
        severity=Severity.HIGH,
        params={"value": 0},
    ),
    # Categorical validation
    ValidationRule(
        column="status",
        rule_type="in_list",
        description="Status must be valid",
        severity=Severity.HIGH,
        params={"allowed_values": ["pending", "confirmed", "shipped", "delivered", "cancelled"]},
    ),
    # Uniqueness
    ValidationRule(
        column="order_id",
        rule_type="unique",
        description="Order IDs must be unique",
        severity=Severity.CRITICAL,
    ),
]

# Run validation
print("\n🔍 Running validation...")
results = validator.validate(df, rules, dataset_name="sales_orders")

# Display results
print("\n" + results.summary())

# Detailed failure analysis
if results.failure_count > 0:
    print("\n" + "=" * 80)
    print("Detailed Failure Analysis")
    print("=" * 80)

    for failure in results.get_failures():
        print(f"\n❌ {failure.column} - {failure.rule_type}")
        print(f"   Description: {failure.description}")
        print(f"   Severity: {failure.severity.value}")
        print(f"   Failures: {failure.failure_count} ({failure.failure_percentage:.2f}%)")
        if failure.sample_failures:
            print(f"   Sample values: {failure.sample_failures[:3]}")

# Demonstrate custom validator
print("\n" + "=" * 80)
print("Custom Validator Example")
print("=" * 80)


def validate_delivery_after_order(series: pd.Series) -> pd.Series:
    """Custom validator: delivery date must be after order date"""
    df_context = series.to_frame()
    if "order_date" not in df.columns or "delivery_date" not in df.columns:
        return pd.Series([False] * len(series), index=series.index)

    return df["delivery_date"] <= df["order_date"]


# Register custom validator
validator.register_validator("delivery_after_order", validate_delivery_after_order)

# Create custom rule
custom_rule = ValidationRule(
    column="delivery_date",
    rule_type="delivery_after_order",
    description="Delivery date must be after order date",
    severity=Severity.HIGH,
)

# Validate with custom rule
custom_result = validator.validate(df, [custom_rule], dataset_name="sales_orders")
print("\nCustom validation result:")
if custom_result.is_valid:
    print("✅ All delivery dates are valid")
else:
    print(f"❌ {custom_result.failure_count} invalid delivery dates")

print("\n" + "=" * 80)
print("Example completed!")
print("=" * 80)
