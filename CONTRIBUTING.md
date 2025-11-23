# Contributing to Data Quality Framework

First off, thank you for considering contributing to Data Quality Framework! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, package versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Provide specific examples to demonstrate the use case**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Write a clear commit message

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/data-quality-framework.git
cd data-quality-framework

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
make dev-setup
# OR
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

## Development Workflow

```bash
# Create a new branch
git checkout -b feature/my-new-feature

# Make your changes and add tests
# ...

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Commit changes
git commit -m "Add some feature"

# Push to your fork
git push origin feature/my-new-feature
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=dqf --cov-report=html

# Run specific test file
pytest tests/test_profiler.py -v

# Run specific test
pytest tests/test_profiler.py::test_profile_basic -v
```

## Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black dqf/ examples/ tests/
isort dqf/ examples/ tests/

# Run linters
flake8 dqf/ --max-line-length=120
mypy dqf/
```

## Documentation

- Update docstrings for new functions/classes
- Update README.md if needed
- Add examples for new features
- Update configuration documentation

## Adding New Validators

```python
# In dqf/rules/custom_rules.py

from dqf.rules.base import BaseRule

class MyCustomRule(BaseRule):
    """Custom validation rule"""

    def validate(self, series, **kwargs):
        """
        Validate the series

        Args:
            series: pandas Series to validate
            **kwargs: Additional parameters

        Returns:
            Boolean Series indicating invalid rows
        """
        # Your validation logic
        return series.apply(lambda x: x is invalid)
```

## Adding New Data Sources

```python
# In dqf/utils/database.py

def load_from_mysource(connection_string, query):
    """Load data from custom source"""
    # Implementation
    return dataframe
```

## Project Structure

```
data-quality-framework/
├── dqf/                    # Main package
│   ├── profiler.py        # Data profiling
│   ├── validator.py       # Validation engine
│   ├── monitor.py         # Monitoring & alerting
│   ├── reporters.py       # Report generation
│   ├── rules/             # Validation rules
│   ├── utils/             # Utilities
│   └── integrations/      # Third-party integrations
├── examples/              # Usage examples
├── tests/                 # Test suite
├── config/                # Configuration files
├── dashboard/             # Streamlit dashboard
└── docker/                # Docker setup
```

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests

Examples:
```
feat: Add email validation rule
fix: Handle null values in profiler
docs: Update installation instructions
test: Add tests for custom validators
refactor: Simplify validation engine
```

## Release Process

Maintainers will:

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Publish to PyPI

## Questions?

Feel free to:
- Open an issue with the `question` label
- Reach out to maintainers
- Join discussions

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🙏
