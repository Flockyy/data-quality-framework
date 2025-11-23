# Data Quality Framework - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Quality Framework                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           Data Sources                               │
├─────────────────────────────────────────────────────────────────────┤
│  CSV Files  │  Parquet  │  PostgreSQL  │  MySQL  │  MongoDB  │ APIs │
└──────┬──────────┬────────────┬────────────┬─────────┬──────────┬────┘
       │          │            │            │         │          │
       └──────────┴────────────┴────────────┴─────────┴──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Ingestion Layer                          │
├─────────────────────────────────────────────────────────────────────┤
│  • Data Loading                                                      │
│  • Schema Detection                                                  │
│  • Sampling (for large datasets)                                    │
│  • Type Inference                                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Core Processing Engine                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Data Profiler │  │   Data Validator │  │  Quality Monitor │  │
│  ├─────────────────┤  ├──────────────────┤  ├──────────────────┤  │
│  │ • Statistics    │  │ • Rules Engine   │  │ • Metrics Track  │  │
│  │ • Distributions │  │ • Built-in Rules │  │ • Anomaly Detect │  │
│  │ • Correlations  │  │ • Custom Rules   │  │ • Historical     │  │
│  │ • Missing Data  │  │ • Parallel Exec  │  │ • Trending       │  │
│  │ • Cardinality   │  │ • Severity Mgmt  │  │ • Score Calc     │  │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                    │                      │             │
│           └────────────────────┴──────────────────────┘             │
│                              │                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────┐  ┌────────────┐  ┌──────────────┐
    │  Reporters  │  │  Alerting  │  │  Dashboard   │
    ├─────────────┤  ├────────────┤  ├──────────────┤
    │ • HTML      │  │ • Email    │  │ • Streamlit  │
    │ • JSON      │  │ • Slack    │  │ • Real-time  │
    │ • PDF       │  │ • Webhooks │  │ • Interactive│
    │ • Custom    │  │ • PagerDuty│  │ • Visualize  │
    └─────────────┘  └────────────┘  └──────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Storage & Persistence                         │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Metadata)  │  Redis (Cache)  │  File System (Reports) │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Monitoring & Observability                     │
├─────────────────────────────────────────────────────────────────────┤
│  Prometheus (Metrics)  │  Grafana (Dashboards)  │  Logs (ELK)      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Profiler
```
Input: DataFrame
Output: ProfileReport

Operations:
- Calculate statistical summaries
- Analyze distributions
- Detect outliers (IQR, Z-score)
- Find correlations
- Identify missing patterns
- Suggest data types
```

### 2. Data Validator
```
Input: DataFrame + Validation Rules
Output: ValidationResult

Operations:
- Execute validation rules
- Parallel processing
- Severity classification
- Failure tracking
- Sample collection
```

### 3. Quality Monitor
```
Input: DataFrame + Metrics Config
Output: QualityMetrics + Alerts

Operations:
- Calculate quality dimensions
- Track metrics over time
- Detect anomalies
- Generate alerts
- Store history
```

## Data Flow

```
1. Data Ingestion
   └─> Load data from source
   └─> Detect schema
   └─> Sample if needed

2. Profiling (Optional)
   └─> Calculate statistics
   └─> Generate column profiles
   └─> Create correlations
   └─> Export reports

3. Validation (Optional)
   └─> Load rules from config
   └─> Execute validations
   └─> Collect failures
   └─> Generate validation report

4. Monitoring (Optional)
   └─> Calculate quality metrics
   └─> Compare with thresholds
   └─> Trigger alerts if needed
   └─> Store metrics history

5. Reporting
   └─> Generate HTML/JSON/PDF
   └─> Send notifications
   └─> Update dashboard
   └─> Log to database
```

## Integration Points

### Airflow Integration
```python
DAG
 ├─> Extract Task
 ├─> DQF Validation Task  ←── Framework Integration
 ├─> Transform Task
 ├─> DQF Quality Check    ←── Framework Integration
 └─> Load Task
```

### dbt Integration
```yaml
models:
  - name: my_model
    tests:
      - dqf_quality_check:  ←── Framework Integration
          severity: error
```

### Real-time Streaming
```
Kafka Topic
    │
    ▼
Stream Processor
    │
    ▼
DQF Validation  ←── Framework Integration
    │
    ├─> Valid Data → Sink
    └─> Invalid Data → Dead Letter Queue
```

## Deployment Architecture

### Docker Compose (Development)
```
┌────────────────────────────────────┐
│     Docker Compose Network         │
├────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────┐ │
│  │  Dashboard   │  │ PostgreSQL │ │
│  │  (Streamlit) │  │            │ │
│  │  Port: 8501  │  │ Port: 5432 │ │
│  └──────────────┘  └────────────┘ │
│  ┌──────────────┐  ┌────────────┐ │
│  │  Prometheus  │  │   Redis    │ │
│  │  Port: 9090  │  │ Port: 6379 │ │
│  └──────────────┘  └────────────┘ │
│  ┌──────────────┐                  │
│  │   Grafana    │                  │
│  │  Port: 3000  │                  │
│  └──────────────┘                  │
└────────────────────────────────────┘
```

### Kubernetes (Production)
```
┌─────────────────────────────────────┐
│        Kubernetes Cluster           │
├─────────────────────────────────────┤
│  Namespace: data-quality            │
│                                      │
│  ┌───────────────────────────────┐ │
│  │  Pods                          │ │
│  │  ├─> dqf-api (3 replicas)     │ │
│  │  ├─> dqf-worker (5 replicas)  │ │
│  │  └─> dqf-dashboard (2)        │ │
│  └───────────────────────────────┘ │
│                                      │
│  ┌───────────────────────────────┐ │
│  │  Services                      │ │
│  │  ├─> LoadBalancer (dashboard) │ │
│  │  ├─> ClusterIP (api)          │ │
│  │  └─> ClusterIP (postgres)     │ │
│  └───────────────────────────────┘ │
│                                      │
│  ┌───────────────────────────────┐ │
│  │  StatefulSets                  │ │
│  │  ├─> PostgreSQL (3 replicas)  │ │
│  │  └─> Redis (3 replicas)       │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Performance Considerations

### Scalability Strategies
```
1. Horizontal Scaling
   - Multiple worker pods
   - Load balancing
   - Distributed caching

2. Vertical Scaling
   - Resource limits/requests
   - Memory optimization
   - CPU allocation

3. Data Partitioning
   - Chunk processing
   - Parallel validation
   - Distributed profiling

4. Caching
   - Redis for hot data
   - Profile result caching
   - Validation rule caching
```

### Processing Large Datasets
```
Size             Strategy
────────────────────────────────
< 100K rows   → In-memory processing
100K - 1M     → Sampling + chunking
1M - 10M      → Dask/Ray distributed
> 10M         → Spark integration
```

## Security Architecture

```
┌──────────────────────────────────┐
│     Authentication Layer         │
├──────────────────────────────────┤
│  • API Keys                      │
│  • OAuth 2.0                     │
│  • RBAC (Role-Based Access)     │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      Authorization Layer         │
├──────────────────────────────────┤
│  • Dataset-level permissions     │
│  • Operation permissions         │
│  • Alert access control          │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│        Encryption Layer          │
├──────────────────────────────────┤
│  • Data at rest (AES-256)       │
│  • Data in transit (TLS 1.3)    │
│  • Secrets management (Vault)    │
└──────────────────────────────────┘
```

## Extension Points

### Custom Validators
```python
class CustomValidator(BaseValidator):
    def validate(self, series):
        # Your logic
        return invalid_mask
```

### Custom Reporters
```python
class CustomReporter(BaseReporter):
    def generate(self, profile):
        # Your logic
        return report
```

### Custom Data Sources
```python
class CustomSource(BaseSource):
    def load(self, connection_string):
        # Your logic
        return dataframe
```

### Custom Alerts
```python
class CustomAlerter(BaseAlerter):
    def send(self, alert):
        # Your logic
        pass
```

## Technology Decisions

| Component      | Technology       | Reason                           |
|---------------|------------------|----------------------------------|
| Core Library  | Pandas          | Ubiquity, compatibility          |
| Validation    | Custom + GE     | Flexibility + standards          |
| Dashboard     | Streamlit       | Rapid development, interactive   |
| Database      | PostgreSQL      | Reliability, JSONB support       |
| Cache         | Redis           | Speed, simple interface          |
| Monitoring    | Prometheus      | Industry standard, integrations  |
| Visualization | Grafana         | Rich dashboards, alerting        |
| Containerization | Docker       | Portability, consistency         |

---

This architecture supports:
- ✅ Scalability (horizontal and vertical)
- ✅ Extensibility (plugins and custom components)
- ✅ Observability (monitoring and logging)
- ✅ Reliability (error handling and retries)
- ✅ Security (authentication and encryption)
