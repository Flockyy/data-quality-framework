"""
Unit tests for Data Profiler
"""


import numpy as np
import pandas as pd
import pytest

from dqf.profiler import DataProfiler, ProfileReport


@pytest.fixture()
def sample_dataframe():
    """Create a sample dataframe for testing"""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "id": range(1, 101),
            "name": [f"Item_{i}" for i in range(1, 101)],
            "value": np.random.randn(100),
            "category": np.random.choice(["A", "B", "C"], 100),
            "date": pd.date_range("2024-01-01", periods=100, freq="D"),
            "nullable": [None if i % 10 == 0 else i for i in range(100)],
        }
    )


@pytest.fixture()
def profiler():
    """Create a profiler instance"""
    return DataProfiler()


def test_profiler_initialization():
    """Test profiler initialization with various configurations"""
    profiler = DataProfiler(
        enable_statistics=True,
        enable_distributions=True,
        enable_correlations=True,
    )

    assert profiler.enable_statistics is True
    assert profiler.enable_distributions is True
    assert profiler.enable_correlations is True


def test_profile_basic(profiler, sample_dataframe):
    """Test basic profiling functionality"""
    profile = profiler.profile(sample_dataframe, dataset_name="test")

    assert isinstance(profile, ProfileReport)
    assert profile.dataset_name == "test"
    assert profile.row_count == 100
    assert profile.column_count == 6
    assert len(profile.columns) == 6


def test_profile_numeric_column(profiler, sample_dataframe):
    """Test profiling of numeric columns"""
    profile = profiler.profile(sample_dataframe)

    value_profile = profile.columns["value"]

    assert value_profile.dtype == "float64"
    assert value_profile.mean is not None
    assert value_profile.std is not None
    assert value_profile.min_value is not None
    assert value_profile.max_value is not None
    assert value_profile.median is not None


def test_profile_categorical_column(profiler, sample_dataframe):
    """Test profiling of categorical columns"""
    profile = profiler.profile(sample_dataframe)

    category_profile = profile.columns["category"]

    assert category_profile.unique_count == 3
    assert len(category_profile.top_values) > 0
    assert category_profile.mode is not None


def test_profile_null_handling(profiler, sample_dataframe):
    """Test handling of null values"""
    profile = profiler.profile(sample_dataframe)

    nullable_profile = profile.columns["nullable"]

    assert nullable_profile.null_count == 10
    assert nullable_profile.null_percentage == 10.0


def test_profile_uniqueness(profiler, sample_dataframe):
    """Test uniqueness detection"""
    profile = profiler.profile(sample_dataframe)

    id_profile = profile.columns["id"]

    assert id_profile.unique_count == 100
    assert id_profile.unique_percentage == 100.0


def test_profile_correlations(sample_dataframe):
    """Test correlation analysis"""
    profiler = DataProfiler(enable_correlations=True)
    profile = profiler.profile(sample_dataframe)

    assert profile.correlations is not None


def test_profile_summary(profiler, sample_dataframe):
    """Test profile summary generation"""
    profile = profiler.profile(sample_dataframe)
    summary = profile.summary()

    assert isinstance(summary, str)
    assert "test" in summary or "dataset" in summary
    assert "100" in summary  # row count


def test_profile_to_dict(profiler, sample_dataframe):
    """Test profile conversion to dictionary"""
    profile = profiler.profile(sample_dataframe)
    profile_dict = profile.to_dict()

    assert isinstance(profile_dict, dict)
    assert "dataset_name" in profile_dict
    assert "row_count" in profile_dict
    assert "columns" in profile_dict


def test_profile_to_json(profiler, sample_dataframe, tmp_path):
    """Test profile export to JSON"""
    profile = profiler.profile(sample_dataframe)

    json_file = tmp_path / "profile.json"
    profile.to_json(str(json_file))

    assert json_file.exists()


def test_outlier_detection(sample_dataframe):
    """Test outlier detection"""
    # Add outliers
    sample_dataframe.loc[0, "value"] = 100.0

    profiler = DataProfiler(outlier_method="IQR")
    profile = profiler.profile(sample_dataframe)

    value_profile = profile.columns["value"]
    assert value_profile.outliers_count > 0


def test_empty_dataframe(profiler):
    """Test profiling empty dataframe"""
    empty_df = pd.DataFrame()
    profile = profiler.profile(empty_df)

    assert profile.row_count == 0
    assert profile.column_count == 0


def test_dataframe_with_all_nulls(profiler):
    """Test profiling dataframe with all null values"""
    df = pd.DataFrame(
        {
            "col1": [None] * 10,
            "col2": [None] * 10,
        }
    )

    profile = profiler.profile(df)

    assert profile.columns["col1"].null_percentage == 100.0
    assert profile.columns["col2"].null_percentage == 100.0


def test_large_dataframe_sampling(profiler):
    """Test sampling for large dataframes"""
    large_df = pd.DataFrame(
        {
            "col1": range(10000),
            "col2": np.random.randn(10000),
        }
    )

    profile = profiler.profile(large_df, sample_size=1000)

    # Profile should be generated from sample
    assert profile.row_count <= 1000


def test_datetime_profiling(profiler, sample_dataframe):
    """Test datetime column profiling"""
    profile = profiler.profile(sample_dataframe)

    date_profile = profile.columns["date"]

    assert date_profile.min_date is not None
    assert date_profile.max_date is not None
    assert date_profile.date_range_days is not None


def test_skewness_detection():
    """Test skewness detection in distributions"""
    # Create skewed data
    skewed_df = pd.DataFrame({"skewed": np.random.exponential(1, 1000)})

    profiler = DataProfiler(enable_distributions=True)
    profile = profiler.profile(skewed_df)

    skewed_profile = profile.columns["skewed"]
    assert skewed_profile.skewness is not None
    assert abs(skewed_profile.skewness) > 0


def test_duplicate_detection(profiler):
    """Test duplicate row detection"""
    df = pd.DataFrame(
        {
            "a": [1, 2, 3, 1, 2],
            "b": [4, 5, 6, 4, 5],
        }
    )

    profile = profiler.profile(df)

    assert profile.duplicate_rows == 2
    assert profile.duplicate_percentage == 40.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
