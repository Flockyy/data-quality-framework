-- Initialize Data Quality Framework Database

-- Create schemas
CREATE SCHEMA IF NOT EXISTS dqf;

-- Metrics history table
CREATE TABLE IF NOT EXISTS dqf.quality_metrics (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    measured_at TIMESTAMP NOT NULL DEFAULT NOW(),
    row_count INTEGER,
    completeness FLOAT,
    uniqueness FLOAT,
    validity FLOAT,
    consistency FLOAT,
    quality_score FLOAT,
    data_age_hours FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Validation results table
CREATE TABLE IF NOT EXISTS dqf.validation_results (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    validated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    total_rules INTEGER,
    passed_rules INTEGER,
    failed_rules INTEGER,
    is_valid BOOLEAN,
    failures JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS dqf.alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(255) UNIQUE NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    triggered_at TIMESTAMP NOT NULL,
    severity VARCHAR(50),
    condition TEXT,
    description TEXT,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    threshold FLOAT,
    status VARCHAR(50) DEFAULT 'active',
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    notifications_sent JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Profile reports table
CREATE TABLE IF NOT EXISTS dqf.profile_reports (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    profiled_at TIMESTAMP NOT NULL,
    row_count INTEGER,
    column_count INTEGER,
    memory_usage_mb FLOAT,
    overall_completeness FLOAT,
    overall_uniqueness FLOAT,
    duplicate_percentage FLOAT,
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_metrics_dataset_time ON dqf.quality_metrics(dataset_name, measured_at DESC);
CREATE INDEX idx_validation_dataset_time ON dqf.validation_results(dataset_name, validated_at DESC);
CREATE INDEX idx_alerts_status ON dqf.alerts(status, triggered_at DESC);
CREATE INDEX idx_alerts_dataset ON dqf.alerts(dataset_name, triggered_at DESC);
CREATE INDEX idx_profiles_dataset_time ON dqf.profile_reports(dataset_name, profiled_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA dqf TO dqf_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dqf TO dqf_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dqf TO dqf_user;

-- Insert sample data for testing
INSERT INTO dqf.quality_metrics (dataset_name, completeness, uniqueness, validity, quality_score, row_count)
VALUES
    ('test_dataset', 0.95, 0.88, 0.99, 0.94, 1000),
    ('test_dataset', 0.96, 0.89, 0.98, 0.95, 1100);

COMMENT ON TABLE dqf.quality_metrics IS 'Historical data quality metrics for monitoring';
COMMENT ON TABLE dqf.validation_results IS 'Validation run results and failures';
COMMENT ON TABLE dqf.alerts IS 'Data quality alerts and their lifecycle';
COMMENT ON TABLE dqf.profile_reports IS 'Dataset profiling reports';
