# Data Quality Framework 🎯

A comprehensive, production-ready framework for automated data quality validation, profiling, and monitoring. Built to ensure data reliability across your data pipelines and warehouses.

## 🚀 Features

### Data Profiling
- **Automatic statistical analysis** - Mean, median, std deviation, quartiles
- **Distribution analysis** - Detect skewness, outliers, and patterns
- **Data type inference** - Automatic schema detection
- **Missing data analysis** - Identify null patterns and completeness issues
- **Cardinality checks** - Unique values, duplicates detection

### Data Validation
- **Rule-based validation** - Custom validation rules with SQL-like syntax
- **Great Expectations integration** - Industry-standard expectations library
- **Schema validation** - Ensure data conforms to expected structure
- **Reference data checks** - Validate against lookup tables
- **Cross-field validation** - Complex multi-column rules
- **Custom validators** - Extensible validation framework

### Monitoring & Alerting
- **Real-time quality metrics** - Track data quality over time
- **Anomaly detection** - Identify unusual patterns automatically
- **Alert system** - Email, Slack, webhook notifications
- **Quality dashboards** - Interactive visualizations
- **Historical trending** - Track quality improvements/degradations
- **SLA monitoring** - Set and track data quality SLAs

### Reporting
- **HTML reports** - Detailed, shareable quality reports
- **JSON exports** - Machine-readable results
- **Data lineage tracking** - Understand data flow and impact
- **Executive summaries** - High-level quality scorecards

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL (optional, for metadata storage)
- Redis (optional, for caching)

## 🔧 Installation

### Quick Start with UV (Recommended - 10x Faster!)

```bash
# Install UV (fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# Or: pip install uv

# Clone the repository
git clone https://github.com/Flockyy/data-quality-framework.git
cd data-quality-framework

# Install with all dev tools (uses uv for speed)
make dev-setup

# Or manually:
uv pip install -e ".[dev]"
pre-commit install
```

### Traditional Installation

```bash
# Clone the repository
git clone https://github.com/Flockyy/data-quality-framework.git
cd data-quality-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## 🎯 Quick Start

### 1. Basic Data Profiling

```python
from dqf import DataProfiler
import pandas as pd

# Load your data
df = pd.read_csv('data/sales.csv')

# Create profiler
profiler = DataProfiler()

# Generate profile
profile = profiler.profile(df, dataset_name="sales_data")

# View results
print(profile.summary())

# Export report
profile.to_html('reports/sales_profile.html')
```

### 2. Data Validation

```python
from dqf import DataValidator, ValidationRule

# Create validator
validator = DataValidator()

# Define rules
rules = [
    ValidationRule("email", "is_email", "Email must be valid"),
    ValidationRule("age", "between", "Age must be 18-100", min=18, max=100),
    ValidationRule("price", "greater_than", "Price must be positive", value=0),
    ValidationRule(["city", "country"], "not_null", "Location required"),
]

# Validate data
results = validator.validate(df, rules)

# Check results
if results.is_valid:
    print("✅ All validations passed!")
else:
    print(f"❌ {results.failure_count} validations failed")
    print(results.get_failures())
```

### 3. Using Configuration Files

```python
from dqf import DQFramework

# Initialize from config
dqf = DQFramework.from_config('config/data_quality_config.yaml')

# Run complete quality check
results = dqf.run_quality_check(
    data_source='postgres://localhost/sales_db',
    dataset='orders',
    profile=True,
    validate=True,
    monitor=True
)

# Generate comprehensive report
results.generate_report('reports/orders_quality_report.html')
```

## 📁 Project Structure

```
data-quality-framework/
├── dqf/                          # Main package
│   ├── __init__.py
│   ├── profiler.py              # Data profiling engine
│   ├── validator.py             # Validation engine
│   ├── monitor.py               # Monitoring & alerting
│   ├── reporters.py             # Report generation
│   ├── rules/                   # Validation rules
│   │   ├── base.py
│   │   ├── builtin_rules.py
│   │   └── custom_rules.py
│   ├── utils/                   # Utilities
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── notifications.py
│   └── integrations/            # Third-party integrations
│       ├── great_expectations.py
│       ├── dbt.py
│       └── airflow.py
├── config/                       # Configuration files
│   ├── data_quality_config.yaml
│   └── alerting_config.yaml
├── examples/                     # Example implementations
│   ├── basic_profiling.py
│   ├── custom_validators.py
│   ├── pipeline_integration.py
│   └── dashboard_example.py
├── tests/                        # Test suite
│   ├── test_profiler.py
│   ├── test_validator.py
│   └── test_monitor.py
├── data/                         # Sample datasets
│   ├── customers.csv
│   ├── transactions.csv
│   └── products.csv
├── reports/                      # Generated reports
├── dashboard/                    # Streamlit dashboard
│   └── app.py
├── docker/                       # Docker setup
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── setup.py
└── README.md
```

## 🔍 Advanced Usage

### Custom Validation Rules

```python
from dqf.rules import BaseRule

class CustomBusinessRule(BaseRule):
    """Validate business-specific logic"""

    def validate(self, df):
        # Custom validation logic
        invalid = df[df['revenue'] < df['cost']]

        return {
            'valid': len(invalid) == 0,
            'failures': len(invalid),
            'details': invalid.to_dict('records')
        }

# Register and use
validator.register_rule('business_logic', CustomBusinessRule())
```

### Integration with Data Pipelines

```python
# Airflow DAG example
from airflow import DAG
from dqf.integrations.airflow import DataQualityOperator

dag = DAG('etl_with_quality_checks', ...)

quality_check = DataQualityOperator(
    task_id='validate_staging_data',
    config_file='config/staging_quality.yaml',
    fail_on_error=True,
    dag=dag
)
```

### Monitoring Dashboard

```bash
# Launch interactive dashboard
streamlit run dashboard/app.py

# Access at http://localhost:8501
```

## 📊 Configuration Example

```yaml
# config/data_quality_config.yaml
profiling:
  enabled: true
  statistics: true
  distributions: true
  correlations: true

validation:
  enabled: true
  rules:
    - column: customer_id
      type: not_null
      severity: critical

    - column: email
      type: regex
      pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      severity: high

    - column: amount
      type: range
      min: 0
      max: 1000000
      severity: medium

monitoring:
  enabled: true
  metrics:
    - completeness
    - uniqueness
    - validity
    - consistency

  alerts:
    - condition: completeness < 0.95
      channel: slack
      severity: high

    - condition: validity < 0.99
      channel: email
      recipients: [data-team@company.com]

reporting:
  format: html
  schedule: daily
  recipients: [team@company.com]
```

## 🧪 Testing

```bash
# Run tests (using pytest)
make test

# With coverage report
make test-cov

# Run tests in parallel (faster)
make test-parallel

# Run specific test
pytest tests/test_validator.py -k "test_email_validation" -v

# Run only unit tests
pytest tests/ -m unit

# Skip slow tests
pytest tests/ -m "not slow"
```

## 🛠️ Modern Development Tools

This project uses cutting-edge Python tooling for better performance and developer experience:

- **UV** - 10-100x faster than pip for package installation
- **Ruff** - Lightning-fast linter and formatter (replaces Black, Flake8, isort)
- **Pre-commit** - Automated code quality checks before each commit
- **Pytest** - Comprehensive test coverage with parallel execution

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.

### Quick Commands

```bash
# Code quality checks
make lint           # Run ruff linter
make format         # Format code with ruff
make typecheck      # Run mypy type checker
make check          # Run all checks (like CI)

# Development
make dev-setup      # Set up complete dev environment
make clean          # Clean build artifacts
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access dashboard
open http://localhost:8501

# View logs
docker-compose logs -f
```

## 🎓 Use Cases

1. **ETL Pipeline Validation** - Validate data at each stage of transformation
2. **Data Warehouse Quality** - Continuous monitoring of warehouse tables
3. **ML Feature Validation** - Ensure training data quality
4. **API Data Validation** - Validate external data sources
5. **Regulatory Compliance** - Document and prove data quality
6. **Data Migration** - Validate before/after migration

## 📈 Metrics & KPIs

The framework tracks key data quality dimensions:

- **Completeness**: % of non-null values
- **Uniqueness**: % of unique values
- **Validity**: % passing validation rules
- **Consistency**: Cross-field consistency checks
- **Accuracy**: Comparison with reference data
- **Timeliness**: Data freshness checks

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Related Projects

- [Great Expectations](https://greatexpectations.io/)
- [Pandera](https://pandera.readthedocs.io/)
- [dbt](https://www.getdbt.com/)

## 📧 Contact

- GitHub: [@Flockyy](https://github.com/Flockyy)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

**Built with ❤️ for reliable data engineering**
