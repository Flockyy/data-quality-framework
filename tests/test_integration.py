"""
Integration tests for the Data Quality Framework
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dqf.framework import DQFramework
from dqf.monitor import DataQualityMonitor
from dqf.profiler import DataProfiler
from dqf.reporters import HTMLReporter, JSONReporter
from dqf.validator import DataValidator, Severity, ValidationRule


@pytest.fixture()
def sample_data():
    """Create comprehensive sample data"""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "customer_id": range(1, 101),
            "name": [f"Customer {i}" for i in range(1, 101)],
            "email": [f"customer{i}@example.com" if i % 5 != 0 else None for i in range(1, 101)],
            "age": np.random.randint(18, 80, 100),
            "city": np.random.choice(["NYC", "LA", "Chicago", "Houston"], 100),
            "amount": np.random.uniform(10, 1000, 100),
            "status": np.random.choice(["active", "inactive", "pending"], 100),
            "signup_date": pd.date_range("2023-01-01", periods=100, freq="D"),
        }
    )


@pytest.mark.integration()
class TestEndToEndWorkflow:
    def test_full_data_quality_pipeline(self, sample_data):
        """Test complete data quality workflow"""
        # 1. Profile the data
        profiler = DataProfiler()
        profile = profiler.profile(sample_data)

        assert profile is not None
        assert len(profile.column_profiles) > 0

        # 2. Validate the data
        validator = DataValidator()
        rules = [
            ValidationRule("customer_id", "not_null", "ID required", Severity.CRITICAL),
            ValidationRule("customer_id", "unique", "ID unique", Severity.CRITICAL),
            ValidationRule("email", "email", "Valid email", Severity.HIGH, allow_null=True),
            ValidationRule("age", "range", "Age range", Severity.MEDIUM, params={"min": 18, "max": 80}),
        ]

        validation_result = validator.validate(sample_data, rules)

        assert validation_result is not None
        assert validation_result.total_rules == 4

        # 3. Monitor quality metrics
        monitor = DataQualityMonitor()
        metrics = monitor.measure_quality(sample_data, dataset_name="customers")

        assert metrics is not None
        assert 0.0 <= metrics.quality_score <= 1.0
        assert metrics.row_count == 100

        # 4. Generate report
        reporter = HTMLReporter()
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            report_path = Path(tmp.name)

        reporter.generate(
            profile_result=profile,
            validation_result=validation_result,
            quality_metrics=metrics,
            output_path=report_path,
        )

        assert report_path.exists()
        report_path.unlink()  # Cleanup

    def test_framework_from_config(self, sample_data):
        """Test framework initialization from configuration"""
        # Create temporary config
        config = {
            "validation_rules": [
                {
                    "column": "customer_id",
                    "rule_type": "not_null",
                    "description": "ID required",
                    "severity": "critical",
                },
                {
                    "column": "email",
                    "rule_type": "email",
                    "description": "Valid email",
                    "severity": "high",
                    "allow_null": True,
                },
            ],
            "profiling": {"enable": True},
            "monitoring": {"enable": True},
            "reporting": {"formats": ["json"]},
        }

        # Initialize framework
        framework = DQFramework.from_config(config)

        # Run quality check
        result = framework.run_quality_check(sample_data, dataset_name="test")

        assert result is not None
        assert "validation_result" in result
        assert "profile_result" in result
        assert "quality_metrics" in result


@pytest.mark.integration()
class TestComponentIntegration:
    def test_profiler_validator_integration(self, sample_data):
        """Test integration between profiler and validator"""
        # Profile data to understand it
        profiler = DataProfiler()
        profile = profiler.profile(sample_data)

        # Use profile insights to create validation rules
        rules = []
        for col_name, col_profile in profile.column_profiles.items():
            if col_profile.null_percentage > 0:
                rules.append(
                    ValidationRule(
                        col_name, "not_null", f"{col_name} should not have nulls", Severity.MEDIUM, allow_null=True
                    )
                )

        # Validate
        validator = DataValidator()
        result = validator.validate(sample_data, rules)

        assert result is not None

    def test_validator_monitor_integration(self, sample_data):
        """Test integration between validator and monitor"""
        # Validate data
        validator = DataValidator()
        rules = [
            ValidationRule("customer_id", "not_null", "ID", Severity.HIGH),
            ValidationRule("email", "email", "Email", Severity.MEDIUM, allow_null=True),
        ]

        validation_result = validator.validate(sample_data, rules)

        # Monitor quality based on validation
        monitor = DataQualityMonitor()
        metrics = monitor.measure_quality(sample_data, dataset_name="customers")

        # Check consistency
        if validation_result.is_valid:
            assert metrics.validity >= 0.9
        else:
            assert metrics.validity < 1.0

    def test_monitor_reporter_integration(self, sample_data):
        """Test integration between monitor and reporter"""
        # Monitor data
        monitor = DataQualityMonitor(enable_history=True)

        # Multiple measurements
        for _ in range(3):
            monitor.measure_quality(sample_data, dataset_name="test")

        # Get history
        history = monitor.get_metrics_history("test", days=30)

        # Generate report with history
        reporter = JSONReporter()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            report_path = Path(tmp.name)

        reporter.generate(quality_metrics=history[-1], metrics_history=history, output_path=report_path)

        assert report_path.exists()

        # Verify content
        import json

        with open(report_path) as f:
            data = json.load(f)

        assert "quality_metrics" in data
        assert "metrics_history" in data

        report_path.unlink()  # Cleanup


@pytest.mark.integration()
class TestDataPipeline:
    def test_batch_processing(self, sample_data):
        """Test processing data in batches"""
        framework = DQFramework()

        # Split into batches
        batch_size = 25
        results = []

        for i in range(0, len(sample_data), batch_size):
            batch = sample_data.iloc[i : i + batch_size]
            result = framework.run_quality_check(batch, dataset_name=f"batch_{i}")
            results.append(result)

        assert len(results) == 4  # 100 rows / 25 per batch

        # Aggregate results
        total_rows = sum(r["quality_metrics"].row_count for r in results)
        assert total_rows == 100

    def test_incremental_data_quality(self, sample_data):
        """Test incremental data quality checks"""
        monitor = DataQualityMonitor(enable_history=True)

        # Initial measurement
        initial_metrics = monitor.measure_quality(sample_data, dataset_name="customers")

        # Simulate data update (add more nulls)
        updated_data = sample_data.copy()
        updated_data.loc[0:10, "email"] = None

        # New measurement
        updated_metrics = monitor.measure_quality(updated_data, dataset_name="customers")

        # Quality should degrade
        assert updated_metrics.completeness < initial_metrics.completeness
        assert updated_metrics.trend in ["degrading", "stable"]


@pytest.mark.integration()
class TestErrorHandling:
    def test_missing_columns_handling(self):
        """Test handling of missing columns"""
        df = pd.DataFrame({"col1": [1, 2, 3]})

        validator = DataValidator()
        rule = ValidationRule("nonexistent_col", "not_null", "Test", Severity.HIGH)

        result = validator.validate(df, [rule])

        assert result.failed_rules > 0

    def test_empty_data_handling(self):
        """Test handling of empty datasets"""
        df = pd.DataFrame()

        profiler = DataProfiler()
        profile = profiler.profile(df)

        assert profile.row_count == 0

        validator = DataValidator()
        result = validator.validate(df, [])

        assert result.is_valid is True

        monitor = DataQualityMonitor()
        metrics = monitor.measure_quality(df, dataset_name="empty")

        assert metrics.row_count == 0

    def test_invalid_configuration(self):
        """Test handling of invalid configurations"""
        with pytest.raises((ValueError, KeyError, TypeError)):
            DQFramework.from_config(
                {
                    "validation_rules": "invalid"  # Should be a list
                }
            )


@pytest.mark.slow()
@pytest.mark.integration()
class TestPerformance:
    def test_large_dataset_processing(self):
        """Test processing large datasets"""
        # Create large dataset
        np.random.seed(42)
        large_df = pd.DataFrame(
            {
                "id": range(100000),
                "value": np.random.randn(100000),
                "category": np.random.choice(["A", "B", "C"], 100000),
            }
        )

        # Profile
        profiler = DataProfiler()
        profile = profiler.profile(large_df)

        assert profile.row_count == 100000

        # Validate (with parallel processing)
        validator = DataValidator(parallel=True)
        rules = [
            ValidationRule("id", "unique", "ID unique", Severity.HIGH),
            ValidationRule("value", "not_null", "Value required", Severity.HIGH),
        ]

        result = validator.validate(large_df, rules)

        assert result.total_rows == 100000

    def test_concurrent_operations(self, sample_data):
        """Test concurrent quality checks"""
        import concurrent.futures

        framework = DQFramework()

        def process_batch(batch_id):
            return framework.run_quality_check(sample_data, dataset_name=f"batch_{batch_id}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_batch, i) for i in range(4)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
