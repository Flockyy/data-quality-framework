"""
Example: Basic Data Profiling
Demonstrates how to use the profiler to analyze a dataset.
"""

import numpy as np
import pandas as pd

from dqf import DataProfiler


# Create sample data
np.random.seed(42)

data = {
    "customer_id": range(1, 1001),
    "name": [f"Customer_{i}" for i in range(1, 1001)],
    "email": [f"customer{i}@example.com" if i % 10 != 0 else None for i in range(1, 1001)],
    "age": np.random.randint(18, 80, 1000),
    "income": np.random.lognormal(10, 1, 1000),
    "city": np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], 1000),
    "signup_date": pd.date_range("2020-01-01", periods=1000, freq="D"),
    "is_active": np.random.choice([True, False], 1000, p=[0.8, 0.2]),
    "purchase_count": np.random.poisson(5, 1000),
    "total_spent": np.random.gamma(2, 100, 1000),
}

df = pd.DataFrame(data)

# Add some data quality issues
df.loc[df["age"] > 75, "age"] = None  # Missing values
df.loc[np.random.choice(range(1000), 50), "income"] = df["income"].mean() * 10  # Outliers

print("=" * 80)
print("Data Profiling Example")
print("=" * 80)

# Initialize profiler
profiler = DataProfiler(
    enable_statistics=True,
    enable_distributions=True,
    enable_correlations=True,
    outlier_method="IQR",
)

# Generate profile
print("\n📊 Profiling dataset...")
profile = profiler.profile(df, dataset_name="customer_data")

# Display summary
print("\n" + profile.summary())

# Examine specific column
print("\n" + "=" * 80)
print("Detailed Analysis: 'income' column")
print("=" * 80)
income_profile = profile.columns["income"]
print(f"Mean: ${income_profile.mean:,.2f}")
print(f"Median: ${income_profile.median:,.2f}")
print(f"Std Dev: ${income_profile.std:,.2f}")
print(f"Outliers: {income_profile.outliers_count} ({income_profile.outliers_percentage:.1f}%)")
print(f"Skewness: {income_profile.skewness:.2f}")

# Export reports
print("\n📄 Generating reports...")
profile.to_html("reports/customer_profile.html")
profile.to_json("reports/customer_profile.json")

print("✅ HTML report: reports/customer_profile.html")
print("✅ JSON report: reports/customer_profile.json")

# Analyze specific patterns
print("\n" + "=" * 80)
print("Data Quality Insights")
print("=" * 80)

# Check for high null columns
high_null_cols = [col_name for col_name, col in profile.columns.items() if col.null_percentage > 5]
if high_null_cols:
    print("\n⚠️  Columns with >5% missing values:")
    for col in high_null_cols:
        print(f"   - {col}: {profile.columns[col].null_percentage:.1f}%")

# Check for potential ID columns
id_candidates = [col_name for col_name, col in profile.columns.items() if col.unique_percentage > 95]
if id_candidates:
    print("\n🔑 Potential ID columns (>95% unique):")
    for col in id_candidates:
        print(f"   - {col}: {profile.columns[col].unique_percentage:.1f}% unique")

# Check for skewed distributions
skewed_cols = [col_name for col_name, col in profile.columns.items() if col.skewness and abs(col.skewness) > 1]
if skewed_cols:
    print("\n📊 Highly skewed distributions (|skew| > 1):")
    for col in skewed_cols:
        print(f"   - {col}: skewness = {profile.columns[col].skewness:.2f}")

print("\n" + "=" * 80)
print("Example completed successfully!")
print("=" * 80)
