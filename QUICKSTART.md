# Data Quality Framework - Quick Start Guide

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/Flockyy/data-quality-framework.git
cd data-quality-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
# OR
pip install -r requirements.txt
pip install -e .
```

## 📖 Quick Examples

### 1. Profile Your Data (5 minutes)

```python
from dqf import DataProfiler
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')

# Profile it
profiler = DataProfiler()
profile = profiler.profile(df, dataset_name="my_data")

# View summary
print(profile.summary())

# Generate HTML report
profile.to_html('my_report.html')
```

### 2. Validate Data Quality (10 minutes)

```python
from dqf import DataValidator, ValidationRule
from dqf.validator import Severity

# Create validator
validator = DataValidator()

# Define rules
rules = [
    ValidationRule("email", "email", "Email must be valid", Severity.HIGH),
    ValidationRule("age", "range", "Age must be 18-100", 
                   severity=Severity.HIGH, params={'min': 18, 'max': 100}),
    ValidationRule("customer_id", "unique", "IDs must be unique", Severity.CRITICAL),
]

# Validate
results = validator.validate(df, rules)

# Check results
if results.is_valid:
    print("✅ All checks passed!")
else:
    print(f"❌ {results.failed_rules} rules failed")
    for failure in results.get_failures():
        print(f"  - {failure.column}: {failure.description}")
```

### 3. Complete Quality Check with Config (15 minutes)

Create `config/my_config.yaml`:
```yaml
validation:
  rules:
    - column: email
      type: email
      severity: high
      description: "Email must be valid"
    
    - column: amount
      type: greater_than
      value: 0
      severity: critical
      description: "Amount must be positive"
```

Run quality check:
```python
from dqf import DQFramework

# Initialize from config
dqf = DQFramework.from_config('config/my_config.yaml')

# Run complete check
results = dqf.run_quality_check(
    df=df,
    dataset='my_dataset',
    profile=True,
    validate=True,
    monitor=True
)

# Generate report
dqf.generate_report(results, 'quality_report.html')
```

### 4. Interactive Dashboard (5 minutes)

```bash
# Run the dashboard
streamlit run dashboard/app.py

# Or use make
make run-dashboard

# Access at http://localhost:8501
```

### 5. Command Line Interface

```bash
# Profile a dataset
dqf profile data/customers.csv --output report.html

# Validate with config
dqf validate data/sales.csv --config config/validation_rules.yaml

# Complete quality check
dqf check data/orders.csv --config config/data_quality_config.yaml
```

## 🐳 Docker Deployment (5 minutes)

```bash
# Start all services
make docker-up

# Access:
# - Dashboard: http://localhost:8501
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090

# Stop services
make docker-down
```

## 📊 Real-World Example

```python
import pandas as pd
from dqf import DQFramework, DataValidator, ValidationRule
from dqf.validator import Severity

# Load e-commerce data
df = pd.read_csv('orders.csv')

# Initialize framework
dqf = DQFramework.from_config('config/data_quality_config.yaml')

# Run quality check
results = dqf.run_quality_check(
    df=df,
    dataset='ecommerce_orders',
    profile=True,
    validate=True,
    monitor=True
)

# Check metrics
metrics = results['metrics']
print(f"Quality Score: {metrics.quality_score:.2%}")
print(f"Completeness: {metrics.completeness:.2%}")
print(f"Validity: {metrics.validity:.2%}")

# Generate report
dqf.generate_report(results, 'reports/ecommerce_quality.html')

# Check for alerts
if dqf.monitor.get_active_alerts():
    print("⚠️ Active data quality alerts!")
    for alert in dqf.monitor.get_active_alerts():
        print(f"  - {alert.description} ({alert.severity})")
```

## 🔗 Integration Examples

### With Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from dqf import DQFramework

def validate_data(**context):
    dqf = DQFramework.from_config('config/data_quality_config.yaml')
    
    df = pd.read_sql_table('staging_table', engine)
    
    results = dqf.run_quality_check(
        df=df,
        dataset='staging_data',
        profile=True,
        validate=True
    )
    
    if not results['validation'].is_valid:
        raise ValueError("Data validation failed!")
    
    return True

dag = DAG('data_quality_check', ...)

quality_check = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data,
    dag=dag
)
```

### With dbt

```python
# In dbt test
# tests/assert_data_quality.py

from dqf import DQFramework
import pandas as pd

def test_data_quality(model_name):
    dqf = DQFramework.from_config('config/dqf_config.yaml')
    
    df = ref(model_name)
    
    results = dqf.run_quality_check(
        df=df,
        dataset=model_name,
        validate=True
    )
    
    return results['validation'].is_valid
```

## 📈 Monitoring Setup

### Prometheus Metrics

The framework exposes metrics for monitoring:

```yaml
# config/data_quality_config.yaml
integrations:
  prometheus:
    enabled: true
    port: 9090
```

Available metrics:
- `dqf_quality_score` - Overall quality score
- `dqf_completeness` - Data completeness
- `dqf_validity` - Validation pass rate
- `dqf_validation_failures` - Number of failures
- `dqf_null_percentage` - Missing data percentage

### Grafana Dashboard

Import the pre-built dashboard:
1. Access Grafana at `http://localhost:3000`
2. Login (admin/admin)
3. Import `monitoring/grafana/dashboards/data_quality.json`

## 🧪 Testing Your Data

```bash
# Run tests
make test

# With coverage
make test-cov

# Run linters
make lint

# Format code
make format
```

## 📚 Next Steps

1. **Customize Validation Rules** - Add your own business logic validators
2. **Set Up Alerts** - Configure Slack/email notifications
3. **Automate Checks** - Integrate with your data pipelines
4. **Monitor Trends** - Track quality metrics over time
5. **Scale Up** - Deploy with Docker for production use

## 🆘 Getting Help

- Check the [full documentation](https://github.com/Flockyy/data-quality-framework)
- See [examples/](examples/) for more use cases
- Review [config/data_quality_config.yaml](config/data_quality_config.yaml) for all options

## 🎯 Common Use Cases

### Data Migration Validation
```python
# Validate source and target match
source_profile = profiler.profile(source_df, "source")
target_profile = profiler.profile(target_df, "target")

# Compare row counts, schemas, statistics
assert source_profile.row_count == target_profile.row_count
```

### ML Feature Validation
```python
# Ensure training data quality
rules = [
    ValidationRule("target", "not_null", "Target required", Severity.CRITICAL),
    ValidationRule("features", "no_missing", "Features complete", Severity.HIGH),
]
results = validator.validate(training_df, rules)
```

### API Data Quality
```python
# Validate external API responses
api_data = fetch_from_api()
df = pd.DataFrame(api_data)

results = dqf.run_quality_check(df, dataset='api_response')
if results['metrics'].quality_score < 0.95:
    alert_team("Low quality API data detected!")
```

---

**Ready to ensure your data quality? Let's get started! 🚀**
