"""
Main Framework Module
Unified interface for data quality framework.
"""

from typing import Any, Optional

import pandas as pd
import yaml

from dqf.monitor import DataQualityMonitor
from dqf.profiler import DataProfiler
from dqf.reporters import HTMLReporter, JSONReporter, PDFReporter
from dqf.validator import DataValidator, ValidationRule


class DQFramework:
    """
    Main data quality framework class
    Provides unified interface for profiling, validation, and monitoring
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize framework

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.profiler = DataProfiler(
            enable_statistics=self.config.get("profiling", {}).get("statistics", {}).get("enabled", True),
            enable_distributions=self.config.get("profiling", {}).get("distributions", {}).get("enabled", True),
            enable_correlations=self.config.get("profiling", {}).get("correlations", {}).get("enabled", True),
        )

        self.validator = DataValidator(
            fail_fast=self.config.get("validation", {}).get("fail_fast", False),
            parallel=self.config.get("validation", {}).get("parallel", True),
            max_workers=self.config.get("validation", {}).get("max_workers", 4),
        )

        self.monitor = DataQualityMonitor(
            alert_config=self.config.get("monitoring", {}),
            enable_history=self.config.get("monitoring", {}).get("history", {}).get("enabled", True),
        )

    @classmethod
    def from_config(cls, config_path: str) -> "DQFramework":
        """
        Create framework from configuration file

        Args:
            config_path: Path to YAML configuration file

        Returns:
            DQFramework instance
        """
        with open(config_path) as f:
            config = yaml.safe_load(f)

        return cls(config=config)

    def run_quality_check(
        self,
        df: Optional[pd.DataFrame] = None,
        data_source: Optional[str] = None,
        dataset: str = "dataset",
        profile: bool = True,
        validate: bool = True,
        monitor: bool = True,
    ) -> dict[str, Any]:
        """
        Run complete data quality check

        Args:
            df: DataFrame to check (if not provided, load from data_source)
            data_source: Data source connection string
            dataset: Dataset name
            profile: Run profiling
            validate: Run validation
            monitor: Run monitoring

        Returns:
            Dictionary with results
        """
        results = {
            "dataset": dataset,
            "profile": None,
            "validation": None,
            "metrics": None,
        }

        # Load data if needed
        if df is None and data_source:
            df = self._load_data(data_source, dataset)

        if df is None:
            raise ValueError("Either df or data_source must be provided")

        # Profiling
        if profile:
            results["profile"] = self.profiler.profile(df, dataset_name=dataset)

        # Validation
        validation_result = None
        if validate:
            rules = self._load_validation_rules()
            if rules:
                validation_result = self.validator.validate(df, rules, dataset_name=dataset)
                results["validation"] = validation_result

        # Monitoring
        if monitor:
            results["metrics"] = self.monitor.measure_quality(
                df,
                dataset_name=dataset,
                validation_result=validation_result,
            )

        return results

    def _load_data(self, data_source: str, dataset: str) -> pd.DataFrame:
        """Load data from source"""
        if data_source.startswith("postgres://"):
            return self._load_from_postgres(data_source, dataset)
        elif data_source.endswith(".csv"):
            return pd.read_csv(data_source)
        elif data_source.endswith(".parquet"):
            return pd.read_parquet(data_source)
        else:
            raise ValueError(f"Unsupported data source: {data_source}")

    def _load_from_postgres(self, connection_string: str, table: str) -> pd.DataFrame:
        """Load data from PostgreSQL"""
        from sqlalchemy import create_engine

        engine = create_engine(connection_string)
        return pd.read_sql_table(table, engine)

    def _load_validation_rules(self) -> list[ValidationRule]:
        """Load validation rules from config"""
        rules = []

        validation_config = self.config.get("validation", {})
        rule_configs = validation_config.get("rules", [])

        for rule_config in rule_configs:
            rule = ValidationRule(
                column=rule_config.get("column"),
                rule_type=rule_config.get("type"),
                description=rule_config.get("description", ""),
                severity=rule_config.get("severity", "medium"),
                params=rule_config,
                allow_null=rule_config.get("allow_null", False),
            )
            rules.append(rule)

        return rules

    def generate_report(
        self,
        results: dict[str, Any],
        output_path: str,
        format: str = "html",
    ):
        """
        Generate quality report

        Args:
            results: Results from run_quality_check
            output_path: Output file path
            format: Report format (html, json, pdf)
        """
        if format == "html":
            reporter = HTMLReporter()
        elif format == "json":
            reporter = JSONReporter()
        elif format == "pdf":
            reporter = PDFReporter()
        else:
            raise ValueError(f"Unsupported format: {format}")

        profile_report = results.get("profile")
        if profile_report:
            reporter.generate_report(profile_report, output_path)
