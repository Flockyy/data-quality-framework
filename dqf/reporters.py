"""
Reporters Module
Generate reports in various formats (HTML, JSON, PDF).
"""

from typing import Optional
from datetime import datetime
import json
from pathlib import Path


class HTMLReporter:
    """Generate HTML reports"""
    
    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path
    
    def generate_report(
        self,
        profile_report,
        output_path: str,
        include_charts: bool = True,
    ):
        """Generate HTML report from profile"""
        html_content = self._generate_html(profile_report, include_charts)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, report, include_charts: bool) -> str:
        """Generate HTML content"""
        
        # Build column details
        columns_html = []
        for col_name, col_profile in report.columns.items():
            col_html = f"""
            <div class="column-section">
                <h3>{col_name} <span class="badge">{col_profile.dtype}</span></h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Count</div>
                        <div class="stat-value">{col_profile.count:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Null %</div>
                        <div class="stat-value">{col_profile.null_percentage:.2f}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Unique</div>
                        <div class="stat-value">{col_profile.unique_count:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Unique %</div>
                        <div class="stat-value">{col_profile.unique_percentage:.2f}%</div>
                    </div>
                </div>
            """
            
            # Add numeric statistics
            if col_profile.mean is not None:
                col_html += f"""
                <div class="numeric-stats">
                    <h4>Statistical Summary</h4>
                    <table>
                        <tr><td>Mean</td><td>{col_profile.mean:.4f}</td></tr>
                        <tr><td>Std Dev</td><td>{col_profile.std:.4f}</td></tr>
                        <tr><td>Min</td><td>{col_profile.min_value}</td></tr>
                        <tr><td>Median</td><td>{col_profile.median:.4f}</td></tr>
                        <tr><td>Max</td><td>{col_profile.max_value}</td></tr>
                        {f'<tr><td>Skewness</td><td>{col_profile.skewness:.4f}</td></tr>' if col_profile.skewness else ''}
                        {f'<tr><td>Outliers</td><td>{col_profile.outliers_count} ({col_profile.outliers_percentage:.2f}%)</td></tr>' if col_profile.outliers_count else ''}
                    </table>
                </div>
                """
            
            # Add top values
            if col_profile.top_values:
                col_html += """
                <div class="top-values">
                    <h4>Top Values</h4>
                    <table>
                        <thead><tr><th>Value</th><th>Count</th></tr></thead>
                        <tbody>
                """
                for value, count in col_profile.top_values[:5]:
                    col_html += f"<tr><td>{value}</td><td>{count:,}</td></tr>"
                col_html += "</tbody></table></div>"
            
            # Add warnings
            if col_profile.warnings:
                col_html += '<div class="warnings"><h4>⚠️ Warnings</h4><ul>'
                for warning in col_profile.warnings:
                    col_html += f'<li>{warning}</li>'
                col_html += '</ul></div>'
            
            col_html += "</div>"
            columns_html.append(col_html)
        
        # Complete HTML template
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Profile Report - {report.dataset_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 32px;
        }}
        .metadata {{
            color: #7f8c8d;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .summary-card .value {{
            font-size: 28px;
            font-weight: bold;
        }}
        .quality-score {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .warnings-section {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .warnings-section h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .warnings-section ul {{
            list-style-position: inside;
            color: #856404;
        }}
        .column-section {{
            margin-bottom: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .column-section h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .badge {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: normal;
            margin-left: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .stat-label {{
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 6px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .warnings {{
            margin-top: 15px;
        }}
        .warnings h4 {{
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        .warnings ul {{
            list-style-position: inside;
            color: #c0392b;
        }}
        .numeric-stats, .top-values {{
            margin-top: 15px;
        }}
        h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Data Profile Report</h1>
        <div class="metadata">
            <strong>Dataset:</strong> {report.dataset_name} | 
            <strong>Profiled:</strong> {report.profiled_at.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Rows</h3>
                <div class="value">{report.row_count:,}</div>
            </div>
            <div class="summary-card">
                <h3>Total Columns</h3>
                <div class="value">{report.column_count}</div>
            </div>
            <div class="summary-card">
                <h3>Memory Usage</h3>
                <div class="value">{report.memory_usage_mb:.1f} MB</div>
            </div>
            <div class="summary-card quality-score">
                <h3>Completeness</h3>
                <div class="value">{report.overall_completeness:.1%}</div>
            </div>
            <div class="summary-card">
                <h3>Duplicates</h3>
                <div class="value">{report.duplicate_percentage:.1f}%</div>
            </div>
        </div>
        
        {f'''<div class="warnings-section">
            <h3>⚠️ Warnings</h3>
            <ul>{''.join(f'<li>{w}</li>' for w in report.warnings)}</ul>
        </div>''' if report.warnings else ''}
        
        <h2 style="margin-bottom: 20px;">Column Details</h2>
        {''.join(columns_html)}
        
        {f'''<div style="margin-top: 40px;">
            <h2>High Correlations</h2>
            <table>
                <thead><tr><th>Column 1</th><th>Column 2</th><th>Correlation</th></tr></thead>
                <tbody>
                    {''.join(f'<tr><td>{c1}</td><td>{c2}</td><td>{corr:.3f}</td></tr>' 
                    for c1, c2, corr in report.high_correlations[:10])}
                </tbody>
            </table>
        </div>''' if report.high_correlations else ''}
    </div>
</body>
</html>
"""
        return html


class JSONReporter:
    """Generate JSON reports"""
    
    def generate_report(self, profile_report, output_path: str):
        """Generate JSON report from profile"""
        json_data = profile_report.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)


class PDFReporter:
    """Generate PDF reports"""
    
    def generate_report(self, profile_report, output_path: str):
        """Generate PDF report from profile"""
        # First generate HTML
        html_reporter = HTMLReporter()
        temp_html = output_path.replace('.pdf', '_temp.html')
        html_reporter.generate_report(profile_report, temp_html)
        
        # Convert HTML to PDF (requires weasyprint)
        try:
            from weasyprint import HTML
            HTML(temp_html).write_pdf(output_path)
            
            # Clean up temp file
            Path(temp_html).unlink()
        except ImportError:
            print("weasyprint not installed. Install with: pip install weasyprint")
            print(f"HTML report saved to: {temp_html}")
