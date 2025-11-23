"""
Data Profiler Module
Automatic statistical analysis and profiling of datasets.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats
from collections import Counter
import json


@dataclass
class ColumnProfile:
    """Profile for a single column"""
    
    name: str
    dtype: str
    
    # Basic statistics
    count: int = 0
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    unique_percentage: float = 0.0
    
    # Numeric statistics
    mean: Optional[float] = None
    std: Optional[float] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    median: Optional[float] = None
    percentiles: Dict[str, float] = field(default_factory=dict)
    
    # Distribution
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    is_normal: Optional[bool] = None
    
    # Categorical statistics
    mode: Optional[Any] = None
    mode_frequency: Optional[int] = None
    top_values: List[tuple] = field(default_factory=list)
    
    # String statistics
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    
    # Date statistics
    min_date: Optional[Any] = None
    max_date: Optional[Any] = None
    date_range_days: Optional[int] = None
    
    # Quality indicators
    outliers_count: int = 0
    outliers_percentage: float = 0.0
    
    # Warnings and recommendations
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ProfileReport:
    """Complete profiling report for a dataset"""
    
    dataset_name: str
    profiled_at: datetime
    
    # Dataset level statistics
    row_count: int
    column_count: int
    memory_usage_mb: float
    
    # Column profiles
    columns: Dict[str, ColumnProfile]
    
    # Correlations
    correlations: Optional[pd.DataFrame] = None
    high_correlations: List[tuple] = field(default_factory=list)
    
    # Data quality metrics
    overall_completeness: float = 0.0
    overall_uniqueness: float = 0.0
    duplicate_rows: int = 0
    duplicate_percentage: float = 0.0
    
    # Warnings
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate a text summary of the profile"""
        summary_lines = [
            f"Dataset Profile: {self.dataset_name}",
            f"Profiled at: {self.profiled_at}",
            f"",
            f"Dataset Overview:",
            f"  Rows: {self.row_count:,}",
            f"  Columns: {self.column_count}",
            f"  Memory Usage: {self.memory_usage_mb:.2f} MB",
            f"  Duplicate Rows: {self.duplicate_rows:,} ({self.duplicate_percentage:.2f}%)",
            f"",
            f"Data Quality Metrics:",
            f"  Overall Completeness: {self.overall_completeness:.2%}",
            f"  Overall Uniqueness: {self.overall_uniqueness:.2%}",
            f"",
        ]
        
        if self.warnings:
            summary_lines.append("Warnings:")
            for warning in self.warnings:
                summary_lines.append(f"  ⚠️  {warning}")
            summary_lines.append("")
        
        if self.high_correlations:
            summary_lines.append("High Correlations:")
            for col1, col2, corr in self.high_correlations[:5]:
                summary_lines.append(f"  {col1} <-> {col2}: {corr:.3f}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary"""
        return {
            "dataset_name": self.dataset_name,
            "profiled_at": self.profiled_at.isoformat(),
            "row_count": self.row_count,
            "column_count": self.column_count,
            "memory_usage_mb": self.memory_usage_mb,
            "overall_completeness": self.overall_completeness,
            "overall_uniqueness": self.overall_uniqueness,
            "duplicate_rows": self.duplicate_rows,
            "duplicate_percentage": self.duplicate_percentage,
            "columns": {
                name: {
                    "name": col.name,
                    "dtype": col.dtype,
                    "count": col.count,
                    "null_count": col.null_count,
                    "null_percentage": col.null_percentage,
                    "unique_count": col.unique_count,
                    "unique_percentage": col.unique_percentage,
                    "mean": col.mean,
                    "std": col.std,
                    "min_value": str(col.min_value) if col.min_value is not None else None,
                    "max_value": str(col.max_value) if col.max_value is not None else None,
                    "median": col.median,
                    "percentiles": col.percentiles,
                    "skewness": col.skewness,
                    "kurtosis": col.kurtosis,
                    "top_values": col.top_values,
                    "warnings": col.warnings,
                    "recommendations": col.recommendations,
                }
                for name, col in self.columns.items()
            },
            "high_correlations": [
                {"column1": c1, "column2": c2, "correlation": corr}
                for c1, c2, corr in self.high_correlations
            ],
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """Export report to JSON"""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_data)
        
        return json_data
    
    def to_html(self, filepath: str):
        """Export report to HTML"""
        from dqf.reporters import HTMLReporter
        reporter = HTMLReporter()
        reporter.generate_report(self, filepath)


class DataProfiler:
    """Main profiler class for data quality analysis"""
    
    def __init__(
        self,
        enable_statistics: bool = True,
        enable_distributions: bool = True,
        enable_correlations: bool = True,
        correlation_threshold: float = 0.7,
        outlier_method: str = "IQR",
        percentiles: List[float] = None,
    ):
        self.enable_statistics = enable_statistics
        self.enable_distributions = enable_distributions
        self.enable_correlations = enable_correlations
        self.correlation_threshold = correlation_threshold
        self.outlier_method = outlier_method
        self.percentiles = percentiles or [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    
    def profile(
        self,
        df: pd.DataFrame,
        dataset_name: str = "dataset",
        sample_size: Optional[int] = None,
    ) -> ProfileReport:
        """
        Generate comprehensive profile for a dataset
        
        Args:
            df: DataFrame to profile
            dataset_name: Name of the dataset
            sample_size: Optional sample size for large datasets
            
        Returns:
            ProfileReport object
        """
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
        
        # Dataset level metrics
        row_count = len(df)
        column_count = len(df.columns)
        memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / row_count * 100) if row_count > 0 else 0
        
        # Profile each column
        columns = {}
        for col_name in df.columns:
            columns[col_name] = self._profile_column(df[col_name], col_name)
        
        # Calculate correlations
        correlations = None
        high_correlations = []
        if self.enable_correlations:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlations = df[numeric_cols].corr()
                high_correlations = self._find_high_correlations(correlations)
        
        # Calculate overall metrics
        total_values = row_count * column_count
        null_values = sum(col.null_count for col in columns.values())
        overall_completeness = 1 - (null_values / total_values) if total_values > 0 else 0
        
        total_unique = sum(col.unique_count for col in columns.values())
        overall_uniqueness = total_unique / total_values if total_values > 0 else 0
        
        # Generate warnings
        warnings = self._generate_dataset_warnings(df, columns, duplicate_percentage)
        recommendations = self._generate_recommendations(columns)
        
        return ProfileReport(
            dataset_name=dataset_name,
            profiled_at=datetime.now(),
            row_count=row_count,
            column_count=column_count,
            memory_usage_mb=memory_usage_mb,
            columns=columns,
            correlations=correlations,
            high_correlations=high_correlations,
            overall_completeness=overall_completeness,
            overall_uniqueness=overall_uniqueness,
            duplicate_rows=int(duplicate_rows),
            duplicate_percentage=duplicate_percentage,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _profile_column(self, series: pd.Series, col_name: str) -> ColumnProfile:
        """Profile a single column"""
        profile = ColumnProfile(
            name=col_name,
            dtype=str(series.dtype),
            count=len(series),
            null_count=int(series.isnull().sum()),
        )
        
        profile.null_percentage = (profile.null_count / profile.count * 100) if profile.count > 0 else 0
        profile.unique_count = int(series.nunique())
        profile.unique_percentage = (profile.unique_count / profile.count * 100) if profile.count > 0 else 0
        
        # Remove nulls for further analysis
        series_clean = series.dropna()
        
        if len(series_clean) == 0:
            profile.warnings.append("Column is entirely null")
            return profile
        
        # Numeric profiling
        if pd.api.types.is_numeric_dtype(series):
            self._profile_numeric(series_clean, profile)
        
        # Categorical profiling
        elif pd.api.types.is_categorical_dtype(series) or pd.api.types.is_object_dtype(series):
            self._profile_categorical(series_clean, profile)
        
        # Datetime profiling
        elif pd.api.types.is_datetime64_any_dtype(series):
            self._profile_datetime(series_clean, profile)
        
        # Generate column-specific warnings
        profile.warnings.extend(self._generate_column_warnings(profile))
        profile.recommendations.extend(self._generate_column_recommendations(profile))
        
        return profile
    
    def _profile_numeric(self, series: pd.Series, profile: ColumnProfile):
        """Profile numeric column"""
        if self.enable_statistics:
            profile.mean = float(series.mean())
            profile.std = float(series.std())
            profile.min_value = float(series.min())
            profile.max_value = float(series.max())
            profile.median = float(series.median())
            
            # Percentiles
            for p in self.percentiles:
                profile.percentiles[f"p{int(p*100)}"] = float(series.quantile(p))
        
        if self.enable_distributions:
            # Skewness and kurtosis
            profile.skewness = float(series.skew())
            profile.kurtosis = float(series.kurtosis())
            
            # Normality test (for smaller samples)
            if len(series) < 5000:
                _, p_value = stats.normaltest(series)
                profile.is_normal = p_value > 0.05
            
            # Outlier detection
            if self.outlier_method == "IQR":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                outliers = series[(series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)]
                profile.outliers_count = len(outliers)
            elif self.outlier_method == "z-score":
                z_scores = np.abs(stats.zscore(series))
                outliers = series[z_scores > 3]
                profile.outliers_count = len(outliers)
            
            profile.outliers_percentage = (profile.outliers_count / len(series) * 100) if len(series) > 0 else 0
        
        # Mode
        mode_result = series.mode()
        if len(mode_result) > 0:
            profile.mode = float(mode_result.iloc[0])
            profile.mode_frequency = int((series == profile.mode).sum())
    
    def _profile_categorical(self, series: pd.Series, profile: ColumnProfile):
        """Profile categorical column"""
        # Value counts
        value_counts = series.value_counts()
        profile.top_values = [(str(val), int(count)) for val, count in value_counts.head(10).items()]
        
        # Mode
        if len(value_counts) > 0:
            profile.mode = str(value_counts.index[0])
            profile.mode_frequency = int(value_counts.iloc[0])
        
        # String length statistics
        if series.dtype == 'object':
            str_lengths = series.astype(str).str.len()
            profile.min_length = int(str_lengths.min())
            profile.max_length = int(str_lengths.max())
            profile.avg_length = float(str_lengths.mean())
    
    def _profile_datetime(self, series: pd.Series, profile: ColumnProfile):
        """Profile datetime column"""
        profile.min_date = series.min()
        profile.max_date = series.max()
        profile.date_range_days = (profile.max_date - profile.min_date).days
        
        # Mode
        mode_result = series.mode()
        if len(mode_result) > 0:
            profile.mode = mode_result.iloc[0]
            profile.mode_frequency = int((series == profile.mode).sum())
    
    def _find_high_correlations(self, corr_matrix: pd.DataFrame) -> List[tuple]:
        """Find highly correlated column pairs"""
        high_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= self.correlation_threshold:
                    high_corr.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        float(corr_value)
                    ))
        
        return sorted(high_corr, key=lambda x: abs(x[2]), reverse=True)
    
    def _generate_column_warnings(self, profile: ColumnProfile) -> List[str]:
        """Generate warnings for a column"""
        warnings = []
        
        if profile.null_percentage > 50:
            warnings.append(f"High null rate: {profile.null_percentage:.1f}%")
        
        if profile.unique_percentage < 1 and profile.count > 100:
            warnings.append(f"Very low uniqueness: {profile.unique_percentage:.2f}%")
        
        if profile.outliers_percentage > 5:
            warnings.append(f"High outlier rate: {profile.outliers_percentage:.1f}%")
        
        if profile.skewness and abs(profile.skewness) > 2:
            warnings.append(f"Highly skewed distribution: {profile.skewness:.2f}")
        
        return warnings
    
    def _generate_column_recommendations(self, profile: ColumnProfile) -> List[str]:
        """Generate recommendations for a column"""
        recommendations = []
        
        if profile.null_percentage > 20:
            recommendations.append("Consider imputation or investigating data source")
        
        if profile.unique_count == profile.count and profile.count > 10:
            recommendations.append("Consider using as primary key")
        
        if profile.outliers_percentage > 10:
            recommendations.append("Review outliers - may indicate data quality issues")
        
        return recommendations
    
    def _generate_dataset_warnings(
        self,
        df: pd.DataFrame,
        columns: Dict[str, ColumnProfile],
        duplicate_percentage: float
    ) -> List[str]:
        """Generate dataset-level warnings"""
        warnings = []
        
        if duplicate_percentage > 10:
            warnings.append(f"High duplicate row rate: {duplicate_percentage:.1f}%")
        
        high_null_cols = [col.name for col in columns.values() if col.null_percentage > 50]
        if high_null_cols:
            warnings.append(f"{len(high_null_cols)} columns have >50% null values")
        
        return warnings
    
    def _generate_recommendations(self, columns: Dict[str, ColumnProfile]) -> List[str]:
        """Generate dataset-level recommendations"""
        recommendations = []
        
        # Check for potential ID columns
        id_candidates = [
            col.name for col in columns.values()
            if col.unique_percentage > 95 and col.null_percentage < 5
        ]
        if id_candidates:
            recommendations.append(f"Potential ID columns: {', '.join(id_candidates)}")
        
        return recommendations
