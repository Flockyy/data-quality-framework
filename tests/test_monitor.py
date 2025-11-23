"""
Unit tests for Data Quality Monitor
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from dqf.monitor import DataQualityMonitor, QualityMetrics, Alert


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'id': range(1, 101),
        'value': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
        'amount': np.random.uniform(0, 1000, 100),
    })


@pytest.fixture
def monitor():
    """Create a monitor instance"""
    return DataQualityMonitor()


class TestQualityMetrics:
    def test_metrics_initialization(self):
        """Test QualityMetrics initialization"""
        metrics = QualityMetrics(
            dataset_name='test',
            measured_at=datetime.now(),
            row_count=100
        )

        assert metrics.dataset_name == 'test'
        assert metrics.row_count == 100
        assert metrics.quality_score == 0.0

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        metrics = QualityMetrics(
            dataset_name='test',
            measured_at=datetime.now(),
            row_count=100,
            completeness=0.95,
            uniqueness=0.90,
            validity=0.98,
            consistency=0.92,
        )

        score = metrics.calculate_quality_score()

        assert 0.0 <= score <= 1.0
        assert metrics.quality_score == score

    def test_custom_weights(self):
        """Test quality score with custom weights"""
        metrics = QualityMetrics(
            dataset_name='test',
            measured_at=datetime.now(),
            row_count=100,
            completeness=1.0,
            uniqueness=1.0,
            validity=1.0,
            consistency=1.0,
        )

        custom_weights = {
            'completeness': 0.5,
            'uniqueness': 0.2,
            'validity': 0.2,
            'consistency': 0.05,
            'timeliness': 0.05,
        }

        score = metrics.calculate_quality_score(weights=custom_weights)

        assert 0.0 <= score <= 1.0


class TestDataQualityMonitor:
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        monitor = DataQualityMonitor(
            enable_history=True,
            history_retention_days=90
        )

        assert monitor.enable_history is True
        assert monitor.history_retention_days == 90
        assert isinstance(monitor.metrics_history, dict)

    def test_measure_quality(self, monitor, sample_dataframe):
        """Test basic quality measurement"""
        metrics = monitor.measure_quality(
            sample_dataframe,
            dataset_name='test_data'
        )

        assert isinstance(metrics, QualityMetrics)
        assert metrics.dataset_name == 'test_data'
        assert metrics.row_count == len(sample_dataframe)
        assert 0.0 <= metrics.completeness <= 1.0
        assert 0.0 <= metrics.quality_score <= 1.0

    def test_completeness_calculation(self, monitor):
        """Test completeness metric calculation"""
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': [1, None, None, 4],
        })

        metrics = monitor.measure_quality(df, dataset_name='test')

        # 75% completeness (6 non-null out of 8 values)
        assert 0.7 <= metrics.completeness <= 0.8

    def test_uniqueness_calculation(self, monitor):
        """Test uniqueness metric calculation"""
        df = pd.DataFrame({
            'col1': [1, 1, 1, 1],  # All same
            'col2': [1, 2, 3, 4],  # All unique
        })

        metrics = monitor.measure_quality(df, dataset_name='test')

        assert 0.0 <= metrics.uniqueness <= 1.0

    def test_timeliness_check(self, monitor):
        """Test data freshness checking"""
        # Recent data
        df_fresh = pd.DataFrame({
            'timestamp': [datetime.now() - timedelta(hours=1)]
        })

        metrics_fresh = monitor.measure_quality(
            df_fresh,
            dataset_name='test',
            timestamp_column='timestamp',
            max_age_hours=24
        )

        assert metrics_fresh.is_fresh is True
        assert metrics_fresh.data_age_hours < 24

    def test_metrics_history(self, monitor, sample_dataframe):
        """Test metrics history tracking"""
        monitor.enable_history = True

        # Measure multiple times
        for i in range(3):
            monitor.measure_quality(
                sample_dataframe,
                dataset_name='test_data'
            )

        history = monitor.get_metrics_history('test_data', days=30)

        assert len(history) == 3
        assert all(isinstance(m, QualityMetrics) for m in history)

    def test_trend_detection(self, monitor, sample_dataframe):
        """Test trend detection in quality metrics"""
        monitor.enable_history = True

        # First measurement
        metrics1 = monitor.measure_quality(
            sample_dataframe,
            dataset_name='test_data'
        )

        # Add some nulls to degrade quality
        df_degraded = sample_dataframe.copy()
        df_degraded.loc[0:10, 'value'] = None

        # Second measurement
        metrics2 = monitor.measure_quality(
            df_degraded,
            dataset_name='test_data'
        )

        assert metrics2.previous_score is not None
        assert metrics2.score_change is not None
        assert metrics2.trend in ['improving', 'degrading', 'stable']


class TestAlerts:
    def test_alert_creation(self):
        """Test Alert object creation"""
        alert = Alert(
            alert_id='test-001',
            dataset_name='test',
            triggered_at=datetime.now(),
            severity='high',
            condition='completeness < 0.9',
            description='Low completeness',
            metric_name='completeness',
            metric_value=0.85,
            threshold=0.9
        )

        assert alert.alert_id == 'test-001'
        assert alert.severity == 'high'
        assert alert.status == 'active'

    def test_alert_acknowledgement(self):
        """Test alert acknowledgement"""
        alert = Alert(
            alert_id='test-001',
            dataset_name='test',
            triggered_at=datetime.now(),
            severity='high',
            condition='test',
            description='test',
            metric_name='test',
            metric_value=0.5,
            threshold=0.9
        )

        alert.acknowledge()

        assert alert.status == 'acknowledged'
        assert alert.acknowledged_at is not None

    def test_alert_resolution(self):
        """Test alert resolution"""
        alert = Alert(
            alert_id='test-001',
            dataset_name='test',
            triggered_at=datetime.now(),
            severity='high',
            condition='test',
            description='test',
            metric_name='test',
            metric_value=0.5,
            threshold=0.9
        )

        alert.resolve()

        assert alert.status == 'resolved'
        assert alert.resolved_at is not None

    def test_alert_triggering(self):
        """Test alert triggering based on conditions"""
        alert_config = {
            'alerts': [
                {
                    'condition': 'completeness < 0.9',
                    'severity': 'high',
                    'channels': ['email'],
                    'description': 'Low completeness'
                }
            ]
        }

        monitor = DataQualityMonitor(alert_config=alert_config)

        # Create data with low completeness
        df = pd.DataFrame({
            'col1': [None] * 50 + [1] * 50,  # 50% completeness
        })

        monitor.measure_quality(df, dataset_name='test')

        # Check if alert was triggered
        active_alerts = monitor.get_active_alerts()

        assert len(active_alerts) > 0
        assert active_alerts[0].severity == 'high'

    def test_get_active_alerts(self):
        """Test getting active alerts"""
        monitor = DataQualityMonitor()

        # Add some test alerts
        alert1 = Alert(
            alert_id='test-001',
            dataset_name='test1',
            triggered_at=datetime.now(),
            severity='high',
            condition='test',
            description='test',
            metric_name='test',
            metric_value=0.5,
            threshold=0.9
        )

        alert2 = Alert(
            alert_id='test-002',
            dataset_name='test2',
            triggered_at=datetime.now(),
            severity='critical',
            condition='test',
            description='test',
            metric_name='test',
            metric_value=0.5,
            threshold=0.9
        )

        monitor.active_alerts = [alert1, alert2]

        # Get all active alerts
        all_alerts = monitor.get_active_alerts()
        assert len(all_alerts) == 2

        # Filter by dataset
        test1_alerts = monitor.get_active_alerts(dataset_name='test1')
        assert len(test1_alerts) == 1
        assert test1_alerts[0].dataset_name == 'test1'

        # Filter by severity
        critical_alerts = monitor.get_active_alerts(severity='critical')
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == 'critical'


class TestHistoryManagement:
    def test_history_cleanup(self, monitor, sample_dataframe):
        """Test automatic history cleanup"""
        monitor.enable_history = True
        monitor.history_retention_days = 7

        # Create old metric
        old_metrics = QualityMetrics(
            dataset_name='test',
            measured_at=datetime.now() - timedelta(days=10),
            row_count=100
        )

        # Create recent metric
        recent_metrics = QualityMetrics(
            dataset_name='test',
            measured_at=datetime.now(),
            row_count=100
        )

        monitor.metrics_history['test'] = [old_metrics, recent_metrics]

        # Trigger cleanup
        monitor._cleanup_history()

        # Only recent metrics should remain
        assert len(monitor.metrics_history['test']) == 1
        assert monitor.metrics_history['test'][0].measured_at == recent_metrics.measured_at

    def test_get_metrics_history_with_days(self, monitor):
        """Test getting metrics history with day filter"""
        monitor.enable_history = True

        # Create metrics at different times
        for days_ago in [1, 5, 10, 20]:
            metrics = QualityMetrics(
                dataset_name='test',
                measured_at=datetime.now() - timedelta(days=days_ago),
                row_count=100
            )
            if 'test' not in monitor.metrics_history:
                monitor.metrics_history['test'] = []
            monitor.metrics_history['test'].append(metrics)

        # Get last 7 days
        recent_history = monitor.get_metrics_history('test', days=7)

        assert len(recent_history) == 2  # Only 1 and 5 days ago


class TestEdgeCases:
    def test_empty_dataframe(self, monitor):
        """Test monitoring empty dataframe"""
        df = pd.DataFrame()

        metrics = monitor.measure_quality(df, dataset_name='empty')

        assert metrics.row_count == 0
        assert metrics.completeness == 0.0

    def test_all_null_dataframe(self, monitor):
        """Test monitoring dataframe with all nulls"""
        df = pd.DataFrame({
            'col1': [None, None, None],
            'col2': [None, None, None],
        })

        metrics = monitor.measure_quality(df, dataset_name='nulls')

        assert metrics.completeness == 0.0
        assert metrics.null_percentage == 100.0

    def test_perfect_quality_dataframe(self, monitor):
        """Test monitoring dataframe with perfect quality"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
        })

        metrics = monitor.measure_quality(df, dataset_name='perfect')

        assert metrics.completeness == 1.0
        assert metrics.null_percentage == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
