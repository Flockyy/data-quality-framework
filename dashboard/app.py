"""
Interactive Dashboard for Data Quality Monitoring
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dqf import DQFramework, DataProfiler, DataValidator, ValidationRule
from dqf.validator import Severity

# Page config
st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None

# Sidebar
st.sidebar.title("⚙️ Configuration")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=['csv', 'parquet'],
    help="Upload your dataset for quality analysis"
)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        st.session_state.df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.parquet'):
        st.session_state.df = pd.read_parquet(uploaded_file)
    
    st.sidebar.success(f"✅ Loaded {len(st.session_state.df):,} rows")

# Analysis options
st.sidebar.subheader("Analysis Options")
run_profiling = st.sidebar.checkbox("Run Profiling", value=True)
run_validation = st.sidebar.checkbox("Run Validation", value=True)

# Main content
st.markdown('<h1 class="main-header">📊 Data Quality Dashboard</h1>', unsafe_allow_html=True)

if st.session_state.df is None:
    st.info("👆 Upload a dataset to get started")
    
    # Demo data option
    if st.button("🎯 Load Demo Data"):
        # Create demo data
        import numpy as np
        np.random.seed(42)
        
        demo_data = {
            'customer_id': range(1, 1001),
            'name': [f'Customer_{i}' for i in range(1, 1001)],
            'email': [f'customer{i}@example.com' if i % 10 != 0 else None for i in range(1, 1001)],
            'age': np.random.randint(18, 80, 1000),
            'income': np.random.lognormal(10, 1, 1000),
            'city': np.random.choice(['New York', 'LA', 'Chicago', 'Houston'], 1000),
            'signup_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'purchase_count': np.random.poisson(5, 1000),
        }
        st.session_state.df = pd.DataFrame(demo_data)
        st.rerun()
else:
    df = st.session_state.df
    
    # Dataset overview
    st.subheader("📋 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")
    with col4:
        duplicates = df.duplicated().sum()
        st.metric("Duplicate Rows", f"{duplicates:,}")
    
    # Show sample data
    with st.expander("🔍 Preview Data", expanded=False):
        st.dataframe(df.head(100), use_container_width=True)
    
    # Run Analysis
    if st.button("🚀 Run Quality Analysis", type="primary"):
        with st.spinner("Analyzing data quality..."):
            
            # Profiling
            if run_profiling:
                profiler = DataProfiler()
                st.session_state.profile = profiler.profile(df, dataset_name="uploaded_data")
            
            # Validation
            if run_validation:
                validator = DataValidator()
                
                # Create basic validation rules
                rules = []
                for col in df.columns:
                    # Not null rule for ID-like columns
                    if 'id' in col.lower():
                        rules.append(ValidationRule(
                            column=col,
                            rule_type='not_null',
                            description=f'{col} must not be null',
                            severity=Severity.CRITICAL
                        ))
                    
                    # Numeric validation
                    if pd.api.types.is_numeric_dtype(df[col]):
                        rules.append(ValidationRule(
                            column=col,
                            rule_type='not_null',
                            description=f'{col} should have values',
                            severity=Severity.MEDIUM,
                            allow_null=True
                        ))
                
                if rules:
                    st.session_state.validation_result = validator.validate(
                        df, rules, dataset_name="uploaded_data"
                    )
        
        st.success("✅ Analysis complete!")
        st.rerun()
    
    # Display results
    if st.session_state.profile or st.session_state.validation_result:
        st.divider()
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Quality Metrics",
            "📈 Profiling Results",
            "✅ Validation Results",
            "📉 Visualizations"
        ])
        
        with tab1:
            st.subheader("Overall Quality Metrics")
            
            if st.session_state.profile:
                profile = st.session_state.profile
                
                # Quality score calculation
                completeness = profile.overall_completeness
                uniqueness = profile.overall_uniqueness
                quality_score = (completeness * 0.5 + uniqueness * 0.5)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Quality Score",
                        f"{quality_score:.1%}",
                        delta=None,
                        help="Overall data quality score"
                    )
                
                with col2:
                    st.metric(
                        "Completeness",
                        f"{completeness:.1%}",
                        help="Percentage of non-null values"
                    )
                
                with col3:
                    st.metric(
                        "Uniqueness",
                        f"{uniqueness:.1%}",
                        help="Average uniqueness across columns"
                    )
                
                with col4:
                    dup_pct = profile.duplicate_percentage
                    st.metric(
                        "Duplicates",
                        f"{dup_pct:.1f}%",
                        help="Percentage of duplicate rows"
                    )
                
                # Warnings
                if profile.warnings:
                    st.warning("⚠️ Data Quality Warnings")
                    for warning in profile.warnings:
                        st.write(f"• {warning}")
        
        with tab2:
            st.subheader("Column Profiling Results")
            
            if st.session_state.profile:
                profile = st.session_state.profile
                
                # Column selector
                selected_col = st.selectbox(
                    "Select Column to Analyze",
                    options=list(profile.columns.keys())
                )
                
                if selected_col:
                    col_profile = profile.columns[selected_col]
                    
                    # Column metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Data Type", col_profile.dtype)
                    with col2:
                        st.metric("Null %", f"{col_profile.null_percentage:.1f}%")
                    with col3:
                        st.metric("Unique", f"{col_profile.unique_count:,}")
                    with col4:
                        st.metric("Unique %", f"{col_profile.unique_percentage:.1f}%")
                    
                    # Numeric statistics
                    if col_profile.mean is not None:
                        st.subheader("Statistical Summary")
                        stats_df = pd.DataFrame({
                            'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max'],
                            'Value': [
                                f"{col_profile.mean:.4f}",
                                f"{col_profile.median:.4f}",
                                f"{col_profile.std:.4f}",
                                f"{col_profile.min_value}",
                                f"{col_profile.max_value}"
                            ]
                        })
                        st.dataframe(stats_df, use_container_width=True, hide_index=True)
                        
                        if col_profile.outliers_count > 0:
                            st.warning(f"⚠️ {col_profile.outliers_count} outliers detected ({col_profile.outliers_percentage:.1f}%)")
                    
                    # Top values
                    if col_profile.top_values:
                        st.subheader("Top Values")
                        top_df = pd.DataFrame(
                            col_profile.top_values[:10],
                            columns=['Value', 'Count']
                        )
                        st.dataframe(top_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("Validation Results")
            
            if st.session_state.validation_result:
                result = st.session_state.validation_result
                
                # Validation summary
                if result.is_valid:
                    st.success("✅ All validation rules passed!")
                else:
                    st.error(f"❌ {result.failed_rules} validation rule(s) failed")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rules Passed", result.passed_rules)
                with col2:
                    st.metric("Rules Failed", result.failed_rules)
                with col3:
                    st.metric("Total Rules", result.total_rules)
                
                # Show failures
                failures = result.get_failures()
                if failures:
                    st.subheader("Validation Failures")
                    
                    failures_data = []
                    for failure in failures:
                        failures_data.append({
                            'Column': failure.column,
                            'Rule': failure.rule_type,
                            'Severity': failure.severity.value,
                            'Failures': failure.failure_count,
                            'Percentage': f"{failure.failure_percentage:.2f}%",
                            'Description': failure.description
                        })
                    
                    failures_df = pd.DataFrame(failures_data)
                    st.dataframe(failures_df, use_container_width=True, hide_index=True)
            else:
                st.info("No validation results available. Enable validation and run analysis.")
        
        with tab4:
            st.subheader("Data Visualizations")
            
            if st.session_state.profile:
                # Null percentage by column
                st.subheader("Missing Data by Column")
                null_data = {
                    col_name: col.null_percentage
                    for col_name, col in st.session_state.profile.columns.items()
                }
                null_df = pd.DataFrame(list(null_data.items()), columns=['Column', 'Null %'])
                null_df = null_df.sort_values('Null %', ascending=False)
                
                fig = px.bar(
                    null_df,
                    x='Column',
                    y='Null %',
                    title='Missing Data Percentage by Column'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Uniqueness chart
                st.subheader("Uniqueness by Column")
                unique_data = {
                    col_name: col.unique_percentage
                    for col_name, col in st.session_state.profile.columns.items()
                }
                unique_df = pd.DataFrame(list(unique_data.items()), columns=['Column', 'Unique %'])
                unique_df = unique_df.sort_values('Unique %', ascending=False)
                
                fig = px.bar(
                    unique_df,
                    x='Column',
                    y='Unique %',
                    title='Uniqueness Percentage by Column',
                    color='Unique %',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.divider()
st.sidebar.markdown("""
### 📚 About
Data Quality Framework Dashboard

Built with Streamlit and Plotly
""")
