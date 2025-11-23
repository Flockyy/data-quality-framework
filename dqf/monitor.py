"""
Data Quality Monitor Module
Real-time monitoring, metrics tracking, and alerting.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


@dataclass
class QualityMetrics:
    """Data quality metrics"""

    dataset_name: str
    measured_at: datetime

    # Completeness
    completeness: float = 0.0
    null_percentage: float = 0.0

    # Uniqueness
    uniqueness: float = 0.0
    duplicate_percentage: float = 0.0

    # Validity
    validity: float = 0.0
    validation_failures: int = 0

    # Consistency
    consistency: float = 0.0

    # Timeliness
    data_age_hours: float = 0.0
    is_fresh: bool = True

    # Volume
    row_count: int = 0

    # Overall score
    quality_score: float = 0.0

    # Historical comparison
    previous_score: Optional[float] = None
    score_change: Optional[float] = None
    trend: Optional[str] = None  # improving, degrading, stable

    def calculate_quality_score(self, weights: Optional[dict[str, float]] = None) -> float:
        """Calculate weighted quality score"""
        if weights is None:
            weights = {
                "completeness": 0.25,
                "uniqueness": 0.15,
                "validity": 0.30,
                "consistency": 0.20,
                "timeliness": 0.10,
            }

        timeliness_score = 1.0 if self.is_fresh else 0.5

        self.quality_score = (
            weights["completeness"] * self.completeness
            + weights["uniqueness"] * self.uniqueness
            + weights["validity"] * self.validity
            + weights["consistency"] * self.consistency
            + weights["timeliness"] * timeliness_score
        )

        return self.quality_score


@dataclass
class Alert:
    """Data quality alert"""

    alert_id: str
    dataset_name: str
    triggered_at: datetime
    severity: str  # critical, high, medium, low
    condition: str
    description: str
    metric_name: str
    metric_value: float
    threshold: float

    # Status
    status: str = "active"  # active, acknowledged, resolved
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Actions taken
    notifications_sent: list[str] = field(default_factory=list)

    def acknowledge(self):
        """Acknowledge the alert"""
        self.status = "acknowledged"
        self.acknowledged_at = datetime.now()

    def resolve(self):
        """Resolve the alert"""
        self.status = "resolved"
        self.resolved_at = datetime.now()


class DataQualityMonitor:
    """Monitor data quality metrics and trigger alerts"""

    def __init__(
        self,
        alert_config: Optional[dict] = None,
        enable_history: bool = True,
        history_retention_days: int = 90,
    ):
        self.alert_config = alert_config or {}
        self.enable_history = enable_history
        self.history_retention_days = history_retention_days

        # Metrics history storage (in real implementation, use database)
        self.metrics_history: dict[str, list[QualityMetrics]] = {}
        self.active_alerts: list[Alert] = []
        self.alert_history: list[Alert] = []

    def measure_quality(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        validation_result: Optional[Any] = None,
        max_age_hours: float = 24,
        timestamp_column: Optional[str] = None,
    ) -> QualityMetrics:
        """
        Measure data quality metrics

        Args:
            df: DataFrame to measure
            dataset_name: Name of the dataset
            validation_result: Optional ValidationResult object
            max_age_hours: Maximum data age in hours
            timestamp_column: Column to check data freshness

        Returns:
            QualityMetrics object
        """
        metrics = QualityMetrics(
            dataset_name=dataset_name,
            measured_at=datetime.now(),
            row_count=len(df),
        )

        # Calculate completeness
        total_values = len(df) * len(df.columns)
        null_values = df.isnull().sum().sum()
        metrics.completeness = 1 - (null_values / total_values) if total_values > 0 else 0
        metrics.null_percentage = (null_values / total_values * 100) if total_values > 0 else 0

        # Calculate uniqueness
        total_unique = sum(df[col].nunique() for col in df.columns)
        metrics.uniqueness = total_unique / total_values if total_values > 0 else 0

        # Calculate duplicates
        metrics.duplicate_percentage = (df.duplicated().sum() / len(df) * 100) if len(df) > 0 else 0

        # Validity from validation results
        if validation_result:
            total_failures = sum(f.failure_count for f in validation_result.get_failures())
            metrics.validation_failures = total_failures
            metrics.validity = (
                1 - (total_failures / (len(df) * len(validation_result.total_rules))) if len(df) > 0 else 0
            )
        else:
            metrics.validity = 1.0

        # Consistency (placeholder - implement cross-field checks)
        metrics.consistency = 1.0

        # Timeliness
        if timestamp_column and timestamp_column in df.columns:
            latest_timestamp = pd.to_datetime(df[timestamp_column]).max()
            metrics.data_age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
            metrics.is_fresh = metrics.data_age_hours <= max_age_hours

        # Calculate overall quality score
        metrics.calculate_quality_score()

        # Compare with history
        if self.enable_history and dataset_name in self.metrics_history:
            previous_metrics = self.metrics_history[dataset_name][-1]
            metrics.previous_score = previous_metrics.quality_score
            metrics.score_change = metrics.quality_score - previous_metrics.quality_score

            if abs(metrics.score_change) < 0.01:
                metrics.trend = "stable"
            elif metrics.score_change > 0:
                metrics.trend = "improving"
            else:
                metrics.trend = "degrading"

        # Store in history
        if self.enable_history:
            if dataset_name not in self.metrics_history:
                self.metrics_history[dataset_name] = []

            self.metrics_history[dataset_name].append(metrics)
            self._cleanup_history()

        # Check for alerts
        self._check_alerts(metrics)

        return metrics

    def _check_alerts(self, metrics: QualityMetrics):
        """Check if any alert conditions are met"""
        alert_rules = self.alert_config.get("alerts", [])

        for rule in alert_rules:
            condition = rule.get("condition", "")
            severity = rule.get("severity", "medium")
            channels = rule.get("channels", [])

            # Evaluate condition
            triggered = self._evaluate_condition(condition, metrics)

            if triggered:
                alert = Alert(
                    alert_id=f"{metrics.dataset_name}_{datetime.now().timestamp()}",
                    dataset_name=metrics.dataset_name,
                    triggered_at=datetime.now(),
                    severity=severity,
                    condition=condition,
                    description=rule.get("description", condition),
                    metric_name=self._extract_metric_name(condition),
                    metric_value=self._get_metric_value(condition, metrics),
                    threshold=self._extract_threshold(condition),
                )

                self.active_alerts.append(alert)
                self.alert_history.append(alert)

                # Send notifications
                self._send_notifications(alert, channels)

    def _evaluate_condition(self, condition: str, metrics: QualityMetrics) -> bool:
        """Evaluate alert condition"""
        try:
            # Create evaluation context with metrics
            context = {
                "completeness": metrics.completeness,
                "null_percentage": metrics.null_percentage,
                "uniqueness": metrics.uniqueness,
                "duplicate_percentage": metrics.duplicate_percentage,
                "validity": metrics.validity,
                "validation_failures": metrics.validation_failures,
                "consistency": metrics.consistency,
                "data_age_hours": metrics.data_age_hours,
                "quality_score": metrics.quality_score,
                "row_count": metrics.row_count,
            }

            # Safely evaluate condition
            return eval(condition, {"__builtins__": {}}, context)
        except Exception:
            return False

    def _extract_metric_name(self, condition: str) -> str:
        """Extract metric name from condition"""
        # Simple extraction - in production, use proper parsing
        for metric in ["completeness", "validity", "quality_score", "data_age_hours"]:
            if metric in condition:
                return metric
        return "unknown"

    def _get_metric_value(self, condition: str, metrics: QualityMetrics) -> float:
        """Get metric value from condition"""
        metric_name = self._extract_metric_name(condition)
        return getattr(metrics, metric_name, 0.0)

    def _extract_threshold(self, condition: str) -> float:
        """Extract threshold from condition"""
        # Simple extraction - in production, use proper parsing
        import re

        numbers = re.findall(r"\d+\.?\d*", condition)
        return float(numbers[0]) if numbers else 0.0

    def _send_notifications(self, alert: Alert, channels: list[str]):
        """Send alert notifications"""
        # In production, implement actual notification sending
        for channel in channels:
            alert.notifications_sent.append(channel)
            # TODO: Implement email, Slack, webhook notifications

    def _cleanup_history(self):
        """Clean up old metrics history"""
        cutoff_date = datetime.now() - timedelta(days=self.history_retention_days)

        for dataset_name in self.metrics_history:
            self.metrics_history[dataset_name] = [
                m for m in self.metrics_history[dataset_name] if m.measured_at >= cutoff_date
            ]

    def get_metrics_history(self, dataset_name: str, days: int = 30) -> list[QualityMetrics]:
        """Get metrics history for a dataset"""
        if dataset_name not in self.metrics_history:
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        return [m for m in self.metrics_history[dataset_name] if m.measured_at >= cutoff_date]

    def get_active_alerts(self, dataset_name: Optional[str] = None, severity: Optional[str] = None) -> list[Alert]:
        """Get active alerts"""
        alerts = [a for a in self.active_alerts if a.status == "active"]

        if dataset_name:
            alerts = [a for a in alerts if a.dataset_name == dataset_name]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledge()
                break

    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolve()
                self.active_alerts.remove(alert)
                break
