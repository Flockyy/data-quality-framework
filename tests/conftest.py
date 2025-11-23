"""
Pytest configuration and fixtures
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


@pytest.fixture(scope="session")
def sample_customers():
    """Create sample customer data for testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'customer_id': range(1, 101),
        'name': [f'Customer {i}' for i in range(1, 101)],
        'email': [f'customer{i}@example.com' if i % 10 != 0 else None for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'city': np.random.choice(['NYC', 'LA', 'Chicago', 'Houston'], 100),
        'signup_date': pd.date_range('2023-01-01', periods=100, freq='D'),
    })


@pytest.fixture(scope="session")
def sample_transactions():
    """Create sample transaction data for testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'transaction_id': range(1, 201),
        'customer_id': np.random.randint(1, 101, 200),
        'amount': np.random.uniform(10, 1000, 200),
        'transaction_date': pd.date_range('2024-01-01', periods=200, freq='H'),
        'status': np.random.choice(['completed', 'pending', 'failed'], 200, p=[0.8, 0.15, 0.05]),
    })


@pytest.fixture
def temp_csv_file(tmp_path, sample_customers):
    """Create a temporary CSV file for testing"""
    file_path = tmp_path / "test_data.csv"
    sample_customers.to_csv(file_path, index=False)
    return str(file_path)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
