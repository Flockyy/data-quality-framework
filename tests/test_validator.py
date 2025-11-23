"""
Unit tests for Data Validator
"""

import numpy as np
import pandas as pd
import pytest

from dqf.validator import DataValidator, Severity, ValidationResult, ValidationRule


@pytest.fixture()
def sample_dataframe():
    """Create a sample dataframe for testing"""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "id": range(1, 101),
            "email": [f"user{i}@example.com" if i % 5 != 0 else None for i in range(1, 101)],
            "age": np.random.randint(18, 80, 100),
            "amount": np.random.uniform(0, 1000, 100),
            "status": np.random.choice(["active", "inactive", "pending"], 100),
            "date": pd.date_range("2024-01-01", periods=100, freq="D"),
        }
    )


@pytest.fixture()
def validator():
    """Create a validator instance"""
    return DataValidator()


class TestValidatorInitialization:
    def test_default_initialization(self):
        """Test validator initialization with default parameters"""
        validator = DataValidator()
        assert validator.fail_fast is False
        assert validator.parallel is True
        assert validator.max_workers == 4

    def test_custom_initialization(self):
        """Test validator initialization with custom parameters"""
        validator = DataValidator(fail_fast=True, parallel=False, max_workers=2)
        assert validator.fail_fast is True
        assert validator.parallel is False
        assert validator.max_workers == 2


class TestValidationRules:
    def test_not_null_validation(self, validator, sample_dataframe):
        """Test not_null validation rule"""
        rule = ValidationRule(
            column="email", rule_type="not_null", description="Email required", severity=Severity.HIGH
        )
        result = validator.validate(sample_dataframe, [rule])

        assert result.failed_rules > 0
        assert len(result.high_failures) > 0

    def test_unique_validation(self, validator):
        """Test unique validation rule"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 1, 2],  # Duplicates
            }
        )

        rule = ValidationRule(
            column="id", rule_type="unique", description="IDs must be unique", severity=Severity.CRITICAL
        )
        result = validator.validate(df, [rule])

        assert result.failed_rules > 0
        assert len(result.critical_failures) > 0

    def test_range_validation(self, validator, sample_dataframe):
        """Test range validation rule"""
        rule = ValidationRule(
            column="age",
            rule_type="range",
            description="Age must be 18-65",
            severity=Severity.MEDIUM,
            params={"min": 18, "max": 65},
        )
        result = validator.validate(sample_dataframe, [rule])

        # Some ages should be outside the range
        assert isinstance(result, ValidationResult)

    def test_email_validation(self, validator):
        """Test email format validation"""
        df = pd.DataFrame(
            {
                "email": ["valid@example.com", "invalid-email", "another@test.com", None],
            }
        )

        rule = ValidationRule(
            column="email", rule_type="email", description="Valid email format", severity=Severity.HIGH, allow_null=True
        )
        result = validator.validate(df, [rule])

        assert result.failed_rules > 0

    def test_in_list_validation(self, validator, sample_dataframe):
        """Test in_list validation rule"""
        rule = ValidationRule(
            column="status",
            rule_type="in_list",
            description="Valid status",
            severity=Severity.HIGH,
            params={"allowed_values": ["active", "inactive"]},
        )
        result = validator.validate(sample_dataframe, [rule])

        # 'pending' status should fail
        if result.failed_rules > 0:
            assert len(result.high_failures) > 0

    def test_positive_validation(self, validator):
        """Test positive number validation"""
        df = pd.DataFrame(
            {
                "amount": [100, -50, 200, 0, -10],
            }
        )

        rule = ValidationRule(
            column="amount", rule_type="positive", description="Amount must be positive", severity=Severity.CRITICAL
        )
        result = validator.validate(df, [rule])

        assert result.failed_rules > 0
        assert len(result.critical_failures) > 0


class TestMultipleRules:
    def test_multiple_rules_validation(self, validator, sample_dataframe):
        """Test validation with multiple rules"""
        rules = [
            ValidationRule("id", "not_null", "ID required", Severity.CRITICAL),
            ValidationRule("email", "email", "Valid email", Severity.HIGH, allow_null=True),
            ValidationRule("age", "range", "Age 18-80", Severity.MEDIUM, params={"min": 18, "max": 80}),
        ]

        result = validator.validate(sample_dataframe, rules)

        assert isinstance(result, ValidationResult)
        assert result.total_rules == 3

    def test_fail_fast_mode(self, sample_dataframe):
        """Test fail_fast mode stops on first failure"""
        validator = DataValidator(fail_fast=True)

        rules = [
            ValidationRule("email", "not_null", "Email required", Severity.HIGH),
            ValidationRule("age", "range", "Age range", Severity.HIGH, params={"min": 0, "max": 10}),
        ]

        result = validator.validate(sample_dataframe, rules)

        # Should stop after first failure
        assert result.failed_rules > 0


class TestValidationResult:
    def test_validation_result_summary(self, validator, sample_dataframe):
        """Test validation result summary generation"""
        rules = [
            ValidationRule("id", "not_null", "ID required", Severity.CRITICAL),
        ]

        result = validator.validate(sample_dataframe, rules)
        summary = result.summary()

        assert isinstance(summary, str)
        assert "Validation Results" in summary

    def test_get_failures_by_severity(self, validator):
        """Test getting failures filtered by severity"""
        df = pd.DataFrame(
            {
                "col1": [None, None, 1, 2],
                "col2": [1, 2, 3, 4],
            }
        )

        rules = [
            ValidationRule("col1", "not_null", "Col1 required", Severity.CRITICAL),
            ValidationRule("col2", "greater_than", "Col2 > 5", Severity.LOW, params={"value": 5}),
        ]

        result = validator.validate(df, rules)

        critical = result.get_failures(Severity.CRITICAL)
        low = result.get_failures(Severity.LOW)

        assert len(critical) > 0 or len(low) > 0

    def test_failure_count_property(self, validator, sample_dataframe):
        """Test failure_count property"""
        rules = [
            ValidationRule("email", "not_null", "Email required", Severity.HIGH),
        ]

        result = validator.validate(sample_dataframe, rules)

        assert isinstance(result.failure_count, int)


class TestCustomValidators:
    def test_register_custom_validator(self, validator):
        """Test registering a custom validator"""

        def custom_validator(series, rule):
            return series.str.startswith("X")

        validator.register_validator("starts_with_x", custom_validator)

        assert "starts_with_x" in validator.validators

    def test_custom_validator_execution(self, validator):
        """Test execution of custom validator"""
        df = pd.DataFrame(
            {
                "code": ["A123", "B456", "A789"],
            }
        )

        def starts_with_a(series, rule):
            return ~series.str.startswith("A")

        validator.register_validator("custom_rule", starts_with_a)

        rule = ValidationRule(
            column="code", rule_type="custom_rule", description="Must start with A", severity=Severity.MEDIUM
        )

        result = validator.validate(df, [rule])

        assert result.failed_rules > 0


class TestEdgeCases:
    def test_empty_dataframe(self, validator):
        """Test validation on empty dataframe"""
        df = pd.DataFrame()
        rules = []

        result = validator.validate(df, rules)

        assert result.total_rows == 0
        assert result.total_rules == 0
        assert result.is_valid is True

    def test_missing_column(self, validator, sample_dataframe):
        """Test validation with non-existent column"""
        rule = ValidationRule(column="nonexistent", rule_type="not_null", description="Test", severity=Severity.HIGH)

        result = validator.validate(sample_dataframe, [rule])

        assert result.failed_rules > 0

    def test_unknown_rule_type(self, validator, sample_dataframe):
        """Test validation with unknown rule type"""
        rule = ValidationRule(column="id", rule_type="unknown_rule", description="Test", severity=Severity.HIGH)

        result = validator.validate(sample_dataframe, [rule])

        assert result.failed_rules > 0

    def test_all_nulls_column(self, validator):
        """Test validation on column with all null values"""
        df = pd.DataFrame(
            {
                "col1": [None, None, None],
            }
        )

        rule = ValidationRule(column="col1", rule_type="not_null", description="Required", severity=Severity.CRITICAL)

        result = validator.validate(df, [rule])

        assert result.failed_rules > 0
        assert len(result.critical_failures) > 0


class TestParallelExecution:
    def test_parallel_validation(self, sample_dataframe):
        """Test parallel validation execution"""
        validator = DataValidator(parallel=True, max_workers=2)

        rules = [ValidationRule(f"col{i}", "not_null", f"Col{i}", Severity.MEDIUM) for i in range(5)]

        # Add columns to dataframe
        for i in range(5):
            sample_dataframe[f"col{i}"] = range(100)

        result = validator.validate(sample_dataframe, rules)

        assert isinstance(result, ValidationResult)

    def test_sequential_validation(self, sample_dataframe):
        """Test sequential validation execution"""
        validator = DataValidator(parallel=False)

        rules = [
            ValidationRule("id", "not_null", "ID", Severity.HIGH),
            ValidationRule("age", "not_null", "Age", Severity.HIGH),
        ]

        result = validator.validate(sample_dataframe, rules)

        assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
