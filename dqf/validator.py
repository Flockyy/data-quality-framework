"""
Data Validator Module
Validation rules and validation engine for data quality checks.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import pandas as pd


class Severity(Enum):
    """Severity levels for validation failures"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationRule:
    """Validation rule definition"""

    column: str
    rule_type: str
    description: str
    severity: Severity = Severity.MEDIUM

    # Rule parameters
    params: dict[str, Any] = field(default_factory=dict)
    allow_null: bool = False

    # Custom validation function
    custom_func: Optional[Callable] = None

    def __post_init__(self):
        if isinstance(self.severity, str):
            self.severity = Severity(self.severity)


@dataclass
class ValidationFailure:
    """Details of a validation failure"""

    rule_name: str
    column: str
    rule_type: str
    description: str
    severity: Severity
    failure_count: int
    failure_percentage: float
    sample_failures: list[Any] = field(default_factory=list)
    details: Optional[str] = None


@dataclass
class ValidationResult:
    """Results from data validation"""

    dataset_name: str
    validated_at: datetime
    total_rows: int
    total_rules: int

    # Results
    passed_rules: int = 0
    failed_rules: int = 0
    is_valid: bool = True

    # Failures by severity
    critical_failures: list[ValidationFailure] = field(default_factory=list)
    high_failures: list[ValidationFailure] = field(default_factory=list)
    medium_failures: list[ValidationFailure] = field(default_factory=list)
    low_failures: list[ValidationFailure] = field(default_factory=list)

    def get_failures(self, severity: Optional[Severity] = None) -> list[ValidationFailure]:
        """Get failures, optionally filtered by severity"""
        if severity:
            if severity == Severity.CRITICAL:
                return self.critical_failures
            elif severity == Severity.HIGH:
                return self.high_failures
            elif severity == Severity.MEDIUM:
                return self.medium_failures
            elif severity == Severity.LOW:
                return self.low_failures

        return self.critical_failures + self.high_failures + self.medium_failures + self.low_failures

    @property
    def failure_count(self) -> int:
        """Total number of failures"""
        return len(self.get_failures())

    def summary(self) -> str:
        """Generate a text summary"""
        lines = [
            f"Validation Results: {self.dataset_name}",
            f"Validated at: {self.validated_at}",
            "",
            "Overview:",
            f"  Total Rows: {self.total_rows:,}",
            f"  Total Rules: {self.total_rules}",
            f"  Passed: {self.passed_rules}",
            f"  Failed: {self.failed_rules}",
            f"  Status: {'✅ VALID' if self.is_valid else '❌ INVALID'}",
            "",
        ]

        if self.critical_failures:
            lines.append(f"Critical Failures ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                lines.append(f"  🔴 {failure.column}: {failure.description}")
            lines.append("")

        if self.high_failures:
            lines.append(f"High Severity Failures ({len(self.high_failures)}):")
            for failure in self.high_failures[:5]:
                lines.append(f"  🟠 {failure.column}: {failure.description}")
            lines.append("")

        return "\n".join(lines)


class DataValidator:
    """Main validator class for data quality validation"""

    def __init__(
        self,
        fail_fast: bool = False,
        parallel: bool = True,
        max_workers: int = 4,
        sample_failures: int = 5,
    ):
        self.fail_fast = fail_fast
        self.parallel = parallel
        self.max_workers = max_workers
        self.sample_failures = sample_failures

        # Built-in validators
        self.validators = {
            "not_null": self._validate_not_null,
            "unique": self._validate_unique,
            "range": self._validate_range,
            "greater_than": self._validate_greater_than,
            "less_than": self._validate_less_than,
            "between": self._validate_between,
            "in_list": self._validate_in_list,
            "regex": self._validate_regex,
            "email": self._validate_email,
            "phone": self._validate_phone,
            "url": self._validate_url,
            "date_not_future": self._validate_date_not_future,
            "date_not_past": self._validate_date_not_past,
            "date_range": self._validate_date_range,
            "string_length": self._validate_string_length,
            "positive": self._validate_positive,
            "negative": self._validate_negative,
            "custom": self._validate_custom,
        }

    def validate(
        self,
        df: pd.DataFrame,
        rules: list[ValidationRule],
        dataset_name: str = "dataset",
    ) -> ValidationResult:
        """
        Validate dataframe against a list of rules

        Args:
            df: DataFrame to validate
            rules: List of validation rules
            dataset_name: Name of the dataset

        Returns:
            ValidationResult object
        """
        result = ValidationResult(
            dataset_name=dataset_name,
            validated_at=datetime.now(),
            total_rows=len(df),
            total_rules=len(rules),
        )

        if self.parallel and len(rules) > 1:
            # Parallel validation
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._validate_rule, df, rule): rule for rule in rules}

                for future in as_completed(futures):
                    failure = future.result()
                    self._add_failure_to_result(result, failure)

                    if self.fail_fast and failure is not None:
                        executor.shutdown(wait=False)
                        break
        else:
            # Sequential validation
            for rule in rules:
                failure = self._validate_rule(df, rule)
                self._add_failure_to_result(result, failure)

                if self.fail_fast and failure is not None:
                    break

        # Update result summary
        result.passed_rules = result.total_rules - result.failed_rules
        result.is_valid = result.failed_rules == 0

        return result

    def _validate_rule(
        self,
        df: pd.DataFrame,
        rule: ValidationRule,
    ) -> Optional[ValidationFailure]:
        """Validate a single rule"""

        # Get validator function
        validator = self.validators.get(rule.rule_type)
        if not validator:
            return ValidationFailure(
                rule_name=f"{rule.column}_{rule.rule_type}",
                column=rule.column,
                rule_type=rule.rule_type,
                description=f"Unknown rule type: {rule.rule_type}",
                severity=Severity.HIGH,
                failure_count=0,
                failure_percentage=0.0,
            )

        # Check if column exists
        if rule.column not in df.columns:
            return ValidationFailure(
                rule_name=f"{rule.column}_{rule.rule_type}",
                column=rule.column,
                rule_type=rule.rule_type,
                description=f"Column '{rule.column}' not found",
                severity=Severity.HIGH,
                failure_count=0,
                failure_percentage=0.0,
            )

        # Run validation
        try:
            invalid_mask = validator(df[rule.column], rule)

            if invalid_mask is None or invalid_mask.sum() == 0:
                return None

            failure_count = int(invalid_mask.sum())
            failure_percentage = (failure_count / len(df) * 100) if len(df) > 0 else 0

            # Get sample failures
            sample_values = df.loc[invalid_mask, rule.column].head(self.sample_failures).tolist()

            return ValidationFailure(
                rule_name=f"{rule.column}_{rule.rule_type}",
                column=rule.column,
                rule_type=rule.rule_type,
                description=rule.description,
                severity=rule.severity,
                failure_count=failure_count,
                failure_percentage=failure_percentage,
                sample_failures=sample_values,
            )

        except Exception as e:
            return ValidationFailure(
                rule_name=f"{rule.column}_{rule.rule_type}",
                column=rule.column,
                rule_type=rule.rule_type,
                description=f"Validation error: {e!s}",
                severity=Severity.HIGH,
                failure_count=0,
                failure_percentage=0.0,
            )

    def _add_failure_to_result(self, result: ValidationResult, failure: Optional[ValidationFailure]):
        """Add failure to result object"""
        if failure is None:
            return

        result.failed_rules += 1

        if failure.severity == Severity.CRITICAL:
            result.critical_failures.append(failure)
        elif failure.severity == Severity.HIGH:
            result.high_failures.append(failure)
        elif failure.severity == Severity.MEDIUM:
            result.medium_failures.append(failure)
        elif failure.severity == Severity.LOW:
            result.low_failures.append(failure)

    # Built-in validators

    def _validate_not_null(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate non-null values"""
        return series.isnull()

    def _validate_unique(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate uniqueness"""
        return series.duplicated(keep=False)

    def _validate_range(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate numeric range"""
        min_val = rule.params.get("min")
        max_val = rule.params.get("max")

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = (series[mask] < min_val) | (series[mask] > max_val)
            return result

        return (series < min_val) | (series > max_val)

    def _validate_greater_than(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate greater than value"""
        value = rule.params.get("value", 0)

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = series[mask] <= value
            return result

        return series <= value

    def _validate_less_than(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate less than value"""
        value = rule.params.get("value", 0)

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = series[mask] >= value
            return result

        return series >= value

    def _validate_between(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate value between min and max"""
        min_val = rule.params.get("min")
        max_val = rule.params.get("max")

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = (series[mask] < min_val) | (series[mask] > max_val)
            return result

        return (series < min_val) | (series > max_val)

    def _validate_in_list(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate value in allowed list"""
        allowed_values = rule.params.get("allowed_values", [])

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = ~series[mask].isin(allowed_values)
            return result

        return ~series.isin(allowed_values)

    def _validate_regex(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate regex pattern"""
        pattern = rule.params.get("pattern", ".*")

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = ~series[mask].astype(str).str.match(pattern, na=False)
            return result

        return ~series.astype(str).str.match(pattern, na=False)

    def _validate_email(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        rule.params["pattern"] = email_pattern
        return self._validate_regex(series, rule)

    def _validate_phone(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate phone number format"""
        phone_pattern = r"^\+?[1-9]\d{1,14}$"
        rule.params["pattern"] = phone_pattern
        return self._validate_regex(series, rule)

    def _validate_url(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate URL format"""
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        rule.params["pattern"] = url_pattern
        return self._validate_regex(series, rule)

    def _validate_date_not_future(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate date is not in the future"""
        now = pd.Timestamp.now()

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = pd.to_datetime(series[mask]) > now
            return result

        return pd.to_datetime(series) > now

    def _validate_date_not_past(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate date is not in the past"""
        now = pd.Timestamp.now()

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = pd.to_datetime(series[mask]) < now
            return result

        return pd.to_datetime(series) < now

    def _validate_date_range(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate date within range"""
        min_date = pd.to_datetime(rule.params.get("min_date"))
        max_date = pd.to_datetime(rule.params.get("max_date"))

        dates = pd.to_datetime(series)

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = (dates[mask] < min_date) | (dates[mask] > max_date)
            return result

        return (dates < min_date) | (dates > max_date)

    def _validate_string_length(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate string length"""
        min_length = rule.params.get("min_length", 0)
        max_length = rule.params.get("max_length", float("inf"))

        lengths = series.astype(str).str.len()

        if rule.allow_null:
            mask = ~series.isnull()
            result = pd.Series([False] * len(series), index=series.index)
            result[mask] = (lengths[mask] < min_length) | (lengths[mask] > max_length)
            return result

        return (lengths < min_length) | (lengths > max_length)

    def _validate_positive(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate positive numbers"""
        rule.params["value"] = 0
        return self._validate_greater_than(series, rule)

    def _validate_negative(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Validate negative numbers"""
        rule.params["value"] = 0
        return self._validate_less_than(series, rule)

    def _validate_custom(self, series: pd.Series, rule: ValidationRule) -> pd.Series:
        """Run custom validation function"""
        if rule.custom_func is None:
            return pd.Series([False] * len(series), index=series.index)

        return rule.custom_func(series)

    def register_validator(self, name: str, func: Callable):
        """Register a custom validator"""
        self.validators[name] = func
