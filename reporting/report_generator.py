"""
Compliance Report Generator

Generates detailed compliance reports in HTML and PDF formats.
"""
import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
import jinja2
import pdfkit
import markdown
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
import base64
from dataclasses import dataclass, field

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for generating reports."""
    title: str
    framework: str
    organization: str = "Your Organization"
    author: str = "PolicyEdgeAI"
    logo_path: Optional[str] = None
    include_executive_summary: bool = True
    include_gap_analysis: bool = True
    include_implementation_status: bool = True
    include_zta_mapping: bool = False
    include_appendices: bool = True
    template_name: str = "standard_report.html"
    output_format: str = "pdf"  # 'pdf' or 'html'


class ReportGenerator:
    """Generates compliance reports from control data."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.report_dir = os.path.join(os.getcwd(), "data", "reports")
        self.template_dir = os.path.join(os.getcwd(), "reporting", "templates")
        
        # Create directories if they don't exist
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Configure Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add filters
        self.jinja_env.filters['markdown'] = self._markdown_to_html
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _markdown_to_html(self, text):
        """Convert markdown to HTML."""
        return markdown.markdown(text)
    
    def _create_default_templates(self):
        """Create default report templates if they don't exist."""
        # Standard report template
        standard_template_path = os.path.join(self.template_dir, "standard_report.html")
        if not os.path.exists(standard_template_path):
            with open(standard_template_path, 'w') as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #f5f5f5;
            padding: 20px;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
        }
        header .logo {
            max-height: 80px;
        }
        h1, h2, h3, h4 {
            color: #1a73e8;
            margin-top: 20px;
        }
        h1 {
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 10px;
        }
        h2 {
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        .metadata {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata table {
            width: 100%;
            border-collapse: collapse;
        }
        .metadata th {
            text-align: left;
            width: 200px;
            padding: 5px;
        }
        .metadata td {
            padding: 5px;
        }
        .section {
            margin-bottom: 30px;
        }
        .control-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .control-table th,
        .control-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .control-table th {
            background-color: #f2f2f2;
        }
        .control-table tr:hover {
            background-color: #f9f9f9;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        .compliance-status {
            font-weight: bold;
        }
        .status-compliant {
            color: green;
        }
        .status-partially-compliant {
            color: orange;
        }
        .status-non-compliant {
            color: red;
        }
        .status-not-applicable {
            color: gray;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        .page-break {
            page-break-after: always;
        }
        .appendix {
            margin-top: 30px;
        }
        .toc {
            margin: 20px 0;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 20px;
        }
        .toc a {
            text-decoration: none;
            color: #1a73e8;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            {% if report.logo_url %}
                <img src="{{ report.logo_url }}" alt="Organization Logo" class="logo">
            {% endif %}
            <h1>{{ report.title }}</h1>
        </header>

        <div class="metadata">
            <table>
                <tr>
                    <th>Organization:</th>
                    <td>{{ report.organization }}</td>
                </tr>
                <tr>
                    <th>Framework:</th>
                    <td>{{ report.framework }}</td>
                </tr>
                <tr>
                    <th>Report Generated:</th>
                    <td>{{ report.generated_date }}</td>
                </tr>
                <tr>
                    <th>Generated By:</th>
                    <td>{{ report.author }}</td>
                </tr>
            </table>
        </div>

        <!-- Table of Contents -->
        <div class="section">
            <h2>Table of Contents</h2>
            <div class="toc">
                <ul>
                    <li><a href="#executive-summary">1. Executive Summary</a></li>
                    <li><a href="#compliance-overview">2. Compliance Overview</a></li>
                    <li><a href="#compliance-by-control-family">3. Compliance by Control Family</a></li>
                    {% if report.include_gap_analysis %}
                    <li><a href="#gap-analysis">4. Gap Analysis</a></li>
                    {% endif %}
                    {% if report.include_implementation_status %}
                    <li><a href="#implementation-status">5. Implementation Status</a></li>
                    {% endif %}
                    {% if report.include_zta_mapping %}
                    <li><a href="#zta-mapping">6. Zero Trust Architecture Mapping</a></li>
                    {% endif %}
                    {% if report.include_appendices %}
                    <li><a href="#appendices">7. Appendices</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>

        <!-- Executive Summary -->
        {% if report.include_executive_summary %}
        <div class="section page-break" id="executive-summary">
            <h2>1. Executive Summary</h2>
            <p>{{ report.executive_summary | markdown }}</p>
            
            {% if report.compliance_score_chart %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ report.compliance_score_chart }}" alt="Compliance Score">
                </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Compliance Overview -->
        <div class="section" id="compliance-overview">
            <h2>2. Compliance Overview</h2>
            <p>This section provides an overview of the compliance status for {{ report.framework }}.</p>
            
            <table class="control-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Controls</td>
                    <td>{{ report.compliance_summary.total_controls }}</td>
                </tr>
                <tr>
                    <td>Compliant Controls</td>
                    <td>{{ report.compliance_summary.compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Partially Compliant Controls</td>
                    <td>{{ report.compliance_summary.partially_compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Non-Compliant Controls</td>
                    <td>{{ report.compliance_summary.non_compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Not Applicable Controls</td>
                    <td>{{ report.compliance_summary.not_applicable_controls }}</td>
                </tr>
                <tr>
                    <td>Overall Compliance Score</td>
                    <td>{{ report.compliance_summary.compliance_score }}%</td>
                </tr>
            </table>
            
            {% if report.compliance_by_status_chart %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ report.compliance_by_status_chart }}" alt="Compliance by Status">
                </div>
            {% endif %}
        </div>

        <!-- Compliance by Control Family -->
        <div class="section page-break" id="compliance-by-control-family">
            <h2>3. Compliance by Control Family</h2>
            <p>This section breaks down compliance status by control family.</p>
            
            {% if report.compliance_by_family_chart %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ report.compliance_by_family_chart }}" alt="Compliance by Family">
                </div>
            {% endif %}
            
            <table class="control-table">
                <tr>
                    <th>Control Family</th>
                    <th>Total Controls</th>
                    <th>Compliant</th>
                    <th>Partially Compliant</th>
                    <th>Non-Compliant</th>
                    <th>Not Applicable</th>
                    <th>Compliance Score</th>
                </tr>
                {% for family in report.family_summaries %}
                <tr>
                    <td>{{ family.name }}</td>
                    <td>{{ family.total_controls }}</td>
                    <td>{{ family.compliant_controls }}</td>
                    <td>{{ family.partially_compliant_controls }}</td>
                    <td>{{ family.non_compliant_controls }}</td>
                    <td>{{ family.not_applicable_controls }}</td>
                    <td>{{ family.compliance_score }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- Gap Analysis -->
        {% if report.include_gap_analysis %}
        <div class="section page-break" id="gap-analysis">
            <h2>4. Gap Analysis</h2>
            <p>This section identifies compliance gaps that need to be addressed.</p>
            
            <!-- Non-Compliant Controls -->
            <h3>Non-Compliant Controls</h3>
            <p>The following controls are currently non-compliant and require attention:</p>
            
            <table class="control-table">
                <tr>
                    <th>Control ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Priority</th>
                </tr>
                {% for control in report.non_compliant_controls %}
                <tr>
                    <td>{{ control.id }}</td>
                    <td>{{ control.title }}</td>
                    <td>{{ control.description | truncate(100) }}</td>
                    <td>{{ control.priority }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <!-- Partially Compliant Controls -->
            <h3>Partially Compliant Controls</h3>
            <p>The following controls are partially implemented and require further attention:</p>
            
            <table class="control-table">
                <tr>
                    <th>Control ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Gap Notes</th>
                </tr>
                {% for control in report.partially_compliant_controls %}
                <tr>
                    <td>{{ control.id }}</td>
                    <td>{{ control.title }}</td>
                    <td>{{ control.description | truncate(100) }}</td>
                    <td>{{ control.gap_notes }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        <!-- Implementation Status -->
        {% if report.include_implementation_status %}
        <div class="section page-break" id="implementation-status">
            <h2>5. Implementation Status</h2>
            <p>This section provides details on the implementation status of all controls.</p>
            
            {% for family in report.control_families %}
            <h3>{{ family.name }}</h3>
            <table class="control-table">
                <tr>
                    <th>Control ID</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Implementation Notes</th>
                </tr>
                {% for control in family.controls %}
                <tr>
                    <td>{{ control.id }}</td>
                    <td>{{ control.title }}</td>
                    <td class="compliance-status status-{{ control.status | lower }}">{{ control.status }}</td>
                    <td>{{ control.implementation_notes }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Zero Trust Architecture Mapping -->
        {% if report.include_zta_mapping %}
        <div class="section page-break" id="zta-mapping">
            <h2>6. Zero Trust Architecture Mapping</h2>
            <p>This section maps controls to Zero Trust Architecture components.</p>
            
            {% if report.zta_coverage_chart %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ report.zta_coverage_chart }}" alt="ZTA Coverage">
                </div>
            {% endif %}
            
            <h3>ZTA Component Coverage</h3>
            <table class="control-table">
                <tr>
                    <th>ZTA Component</th>
                    <th>Category</th>
                    <th>Mapped Controls</th>
                    <th>Coverage Score</th>
                </tr>
                {% for component in report.zta_components %}
                <tr>
                    <td>{{ component.name }}</td>
                    <td>{{ component.category }}</td>
                    <td>{{ component.mapped_controls_count }}</td>
                    <td>{{ component.coverage_score }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            <h3>Control to ZTA Mapping</h3>
            <p>The following table shows how controls map to Zero Trust Architecture components:</p>
            
            <table class="control-table">
                <tr>
                    <th>Control ID</th>
                    <th>ZTA Components</th>
                    <th>Relevance</th>
                </tr>
                {% for mapping in report.control_zta_mappings %}
                <tr>
                    <td>{{ mapping.control_id }}</td>
                    <td>{{ mapping.zta_components | join(', ') }}</td>
                    <td>{{ mapping.relevance_score }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        <!-- Appendices -->
        {% if report.include_appendices %}
        <div class="section page-break" id="appendices">
            <h2>7. Appendices</h2>
            
            <!-- Appendix A: Control Details -->
            <div class="appendix">
                <h3>Appendix A: Control Details</h3>
                <p>This appendix provides detailed information about each control in the framework.</p>
                
                {% for control in report.all_controls %}
                <div class="control-detail">
                    <h4>{{ control.id }}: {{ control.title }}</h4>
                    <p><strong>Description:</strong> {{ control.description }}</p>
                    <p><strong>Family:</strong> {{ control.family }}</p>
                    <p><strong>Status:</strong> <span class="compliance-status status-{{ control.status | lower }}">{{ control.status }}</span></p>
                    {% if control.implementation_notes %}
                    <p><strong>Implementation Notes:</strong> {{ control.implementation_notes }}</p>
                    {% endif %}
                    {% if control.related_controls %}
                    <p><strong>Related Controls:</strong> {{ control.related_controls | join(', ') }}</p>
                    {% endif %}
                </div>
                <hr>
                {% endfor %}
            </div>
            
            <!-- Appendix B: Glossary -->
            <div class="appendix">
                <h3>Appendix B: Glossary</h3>
                <p>This appendix provides definitions for key terms used in this report.</p>
                
                <table class="control-table">
                    <tr>
                        <th>Term</th>
                        <th>Definition</th>
                    </tr>
                    {% for term in report.glossary %}
                    <tr>
                        <td>{{ term.name }}</td>
                        <td>{{ term.definition }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>Report generated on {{ report.generated_date }} by {{ report.author }}</p>
            <p>PolicyEdgeAI - Compliance Automation and Analysis Tool</p>
        </div>
    </div>
</body>
</html>""")
            logger.info(f"Created default standard report template at {standard_template_path}")
        
        # Executive summary template
        executive_template_path = os.path.join(self.template_dir, "executive_summary.html")
        if not os.path.exists(executive_template_path):
            with open(executive_template_path, 'w') as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }} - Executive Summary</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #f5f5f5;
            padding: 20px;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
        }
        header .logo {
            max-height: 80px;
        }
        h1, h2, h3 {
            color: #1a73e8;
        }
        h1 {
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 10px;
        }
        .metadata {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        .summary-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .summary-table th,
        .summary-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .summary-table th {
            background-color: #f2f2f2;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            {% if report.logo_url %}
                <img src="{{ report.logo_url }}" alt="Organization Logo" class="logo">
            {% endif %}
            <h1>{{ report.title }} - Executive Summary</h1>
        </header>

        <div class="metadata">
            <p><strong>Organization:</strong> {{ report.organization }}</p>
            <p><strong>Framework:</strong> {{ report.framework }}</p>
            <p><strong>Report Generated:</strong> {{ report.generated_date }}</p>
        </div>

        <div class="section">
            <h2>Compliance Summary</h2>
            <p>{{ report.executive_summary | markdown }}</p>
            
            {% if report.compliance_score_chart %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ report.compliance_score_chart }}" alt="Compliance Score">
                </div>
            {% endif %}
            
            <table class="summary-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Controls</td>
                    <td>{{ report.compliance_summary.total_controls }}</td>
                </tr>
                <tr>
                    <td>Compliant Controls</td>
                    <td>{{ report.compliance_summary.compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Partially Compliant Controls</td>
                    <td>{{ report.compliance_summary.partially_compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Non-Compliant Controls</td>
                    <td>{{ report.compliance_summary.non_compliant_controls }}</td>
                </tr>
                <tr>
                    <td>Not Applicable Controls</td>
                    <td>{{ report.compliance_summary.not_applicable_controls }}</td>
                </tr>
                <tr>
                    <td>Overall Compliance Score</td>
                    <td>{{ report.compliance_summary.compliance_score }}%</td>
                </tr>
            </table>
        </div>

        <div class="section">
            <h2>Key Findings</h2>
            <ul>
                {% for finding in report.key_findings %}
                <li>{{ finding }}</li>
                {% endfor %}
            </ul>
        </div>

        <div class="section">
            <h2>Recommendations</h2>
            <ol>
                {% for recommendation in report.recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ol>
        </div>

        <div class="footer">
            <p>This executive summary is part of a detailed compliance report generated on {{ report.generated_date }}.</p>
            <p>For complete details, refer to the full compliance report.</p>
        </div>
    </div>
</body>
</html>""")
            logger.info(f"Created default executive summary template at {executive_template_path}")
    
    def _generate_chart(self, chart_type, data):
        """Generate a chart using Plotly."""
        plt_figure = None
        
        if chart_type == "compliance_score":
            # Create a gauge chart for compliance score
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["compliance_score"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Compliance Score"},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 80], 'color': "orange"},
                        {'range': [80, 100], 'color': "green"},
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': data["compliance_score"]
                    }
                }
            ))
            fig.update_layout(height=400, width=500)
            plt_figure = fig
            
        elif chart_type == "compliance_by_status":
            # Create a pie chart for compliance status distribution
            labels = ["Compliant", "Partially Compliant", "Non-Compliant", "Not Applicable"]
            values = [
                data["compliant_controls"],
                data["partially_compliant_controls"],
                data["non_compliant_controls"],
                data["not_applicable_controls"]
            ]
            colors = ['green', 'orange', 'red', 'gray']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                hole=0.4
            )])
            fig.update_layout(
                title_text="Compliance Status Distribution",
                height=400,
                width=500
            )
            plt_figure = fig
            
        elif chart_type == "compliance_by_family":
            # Create a bar chart for compliance by family
            df = pd.DataFrame(data)
            df['compliant_pct'] = df['compliant_controls'] / df['total_controls'] * 100
            
            fig = px.bar(
                df,
                x='name',
                y='compliance_score',
                title="Compliance Score by Control Family",
                labels={'name': 'Control Family', 'compliance_score': 'Compliance Score (%)'},
                color='compliance_score',
                color_continuous_scale=['red', 'orange', 'green'],
                range_color=[0, 100]
            )
            fig.update_layout(height=500, width=700)
            plt_figure = fig
            
        elif chart_type == "zta_coverage":
            # Create a radar chart for ZTA coverage
            categories = [comp['name'] for comp in data]
            values = [comp['coverage_score'] for comp in data]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='ZTA Coverage'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Zero Trust Architecture Coverage",
                height=500,
                width=700
            )
            plt_figure = fig
        
        if plt_figure:
            # Convert the figure to a base64 encoded PNG
            img_bytes = io.BytesIO()
            plt_figure.write_image(img_bytes, format='png')
            img_bytes.seek(0)
            return base64.b64encode(img_bytes.read()).decode('utf-8')
        
        return None
    
    def generate_report(self, controls: List[Dict[str, Any]], config: ReportConfig, 
                        zta_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate a compliance report.
        
        Args:
            controls (List[Dict[str, Any]]): List of controls to include in report
            config (ReportConfig): Report configuration
            zta_data (Dict[str, Any], optional): Zero Trust mapping data
            
        Returns:
            Dict[str, str]: Paths to generated reports (HTML and PDF if requested)
        """
        try:
            report_data = self._prepare_report_data(controls, config, zta_data)
            
            # Generate HTML from template
            template = self.jinja_env.get_template(config.template_name)
            html_content = template.render(report=report_data)
            
            # Create output filename based on title and date
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            filename_base = f"{config.framework.replace(' ', '_')}_{date_str}"
            
            # Save HTML report
            html_path = os.path.join(self.report_dir, f"{filename_base}.html")
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            result = {"html": html_path}
            
            # Generate PDF if requested
            if config.output_format == "pdf":
                pdf_path = os.path.join(self.report_dir, f"{filename_base}.pdf")
                
                # Convert HTML to PDF using pdfkit
                pdfkit.from_string(html_content, pdf_path)
                result["pdf"] = pdf_path
            
            logger.info(f"Generated compliance report: {html_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    def _prepare_report_data(self, controls: List[Dict[str, Any]], config: ReportConfig, 
                           zta_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for the report template."""
        # Initialize report data
        report_data = {
            "title": config.title,
            "organization": config.organization,
            "framework": config.framework,
            "author": config.author,
            "generated_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "include_executive_summary": config.include_executive_summary,
            "include_gap_analysis": config.include_gap_analysis,
            "include_implementation_status": config.include_implementation_status,
            "include_zta_mapping": config.include_zta_mapping,
            "include_appendices": config.include_appendices,
        }
        
        # Add logo if provided
        if config.logo_path and os.path.exists(config.logo_path):
            with open(config.logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode('utf-8')
                report_data["logo_url"] = f"data:image/png;base64,{encoded_logo}"
        
        # Calculate compliance metrics
        total_controls = len(controls)
        compliant = sum(1 for c in controls if c.get("status") == "Compliant")
        partially_compliant = sum(1 for c in controls if c.get("status") == "Partially Compliant")
        non_compliant = sum(1 for c in controls if c.get("status") == "Non-Compliant")
        not_applicable = sum(1 for c in controls if c.get("status") == "Not Applicable")
        
        # Calculate overall compliance score
        applicable_controls = total_controls - not_applicable
        if applicable_controls > 0:
            compliance_score = (compliant + (partially_compliant * 0.5)) / applicable_controls * 100
        else:
            compliance_score = 0
        
        # Add compliance summary
        compliance_summary = {
            "total_controls": total_controls,
            "compliant_controls": compliant,
            "partially_compliant_controls": partially_compliant,
            "non_compliant_controls": non_compliant,
            "not_applicable_controls": not_applicable,
            "compliance_score": round(compliance_score, 1)
        }
        report_data["compliance_summary"] = compliance_summary
        
        # Generate compliance score chart
        report_data["compliance_score_chart"] = self._generate_chart(
            "compliance_score", 
            {"compliance_score": compliance_score}
        )
        
        # Generate compliance by status chart
        report_data["compliance_by_status_chart"] = self._generate_chart(
            "compliance_by_status", 
            compliance_summary
        )
        
        # Group controls by family
        families = {}
        for control in controls:
            family = control.get("family", "Other")
            if family not in families:
                families[family] = []
            families[family].append(control)
        
        # Calculate family summaries
        family_summaries = []
        for family_name, family_controls in families.items():
            family_total = len(family_controls)
            family_compliant = sum(1 for c in family_controls if c.get("status") == "Compliant")
            family_partial = sum(1 for c in family_controls if c.get("status") == "Partially Compliant")
            family_non = sum(1 for c in family_controls if c.get("status") == "Non-Compliant")
            family_na = sum(1 for c in family_controls if c.get("status") == "Not Applicable")
            
            family_applicable = family_total - family_na
            if family_applicable > 0:
                family_score = (family_compliant + (family_partial * 0.5)) / family_applicable * 100
            else:
                family_score = 0
            
            family_summaries.append({
                "name": family_name,
                "total_controls": family_total,
                "compliant_controls": family_compliant,
                "partially_compliant_controls": family_partial,
                "non_compliant_controls": family_non,
                "not_applicable_controls": family_na,
                "compliance_score": round(family_score, 1)
            })
        
        # Sort by family name
        family_summaries.sort(key=lambda x: x["name"])
        report_data["family_summaries"] = family_summaries
        
        # Generate compliance by family chart
        report_data["compliance_by_family_chart"] = self._generate_chart(
            "compliance_by_family", 
            family_summaries
        )
        
        # Add control family details
        control_families = []
        for family_name, family_controls in families.items():
            # Sort controls by ID
            family_controls.sort(key=lambda x: x["id"])
            control_families.append({
                "name": family_name,
                "controls": family_controls
            })
        
        # Sort by family name
        control_families.sort(key=lambda x: x["name"])
        report_data["control_families"] = control_families
        
        # Add non-compliant and partially compliant controls
        report_data["non_compliant_controls"] = [c for c in controls if c.get("status") == "Non-Compliant"]
        report_data["partially_compliant_controls"] = [c for c in controls if c.get("status") == "Partially Compliant"]
        
        # Set all controls
        all_controls = sorted(controls, key=lambda x: x["id"])
        report_data["all_controls"] = all_controls
        
        # Add ZTA mapping if provided
        if config.include_zta_mapping and zta_data:
            # ZTA component coverage
            zta_components = []
            for component_id, component_data in zta_data.get("component_coverage", {}).items():
                component_info = zta_data.get("components", {}).get(component_id, {})
                if component_info:
                    zta_components.append({
                        "id": component_id,
                        "name": component_info.get("name", "Unknown"),
                        "category": component_info.get("category", "Other"),
                        "description": component_info.get("description", ""),
                        "mapped_controls_count": component_data.get("control_count", 0),
                        "coverage_score": round(component_data.get("average_relevance", 0) * 100, 1)
                    })
            
            # Sort by component name
            zta_components.sort(key=lambda x: x["name"])
            report_data["zta_components"] = zta_components
            
            # Generate ZTA coverage chart
            report_data["zta_coverage_chart"] = self._generate_chart(
                "zta_coverage", 
                zta_components
            )
            
            # Control to ZTA mappings
            control_zta_mappings = []
            for control in controls:
                control_id = control.get("id")
                # Find all mappings for this control
                component_mappings = []
                for component_id, component_data in zta_data.get("component_coverage", {}).items():
                    for mapped_control in component_data.get("controls", []):
                        if mapped_control.get("id") == control_id:
                            component_info = zta_data.get("components", {}).get(component_id, {})
                            if component_info:
                                component_mappings.append({
                                    "component_id": component_id,
                                    "component_name": component_info.get("name", "Unknown"),
                                    "relevance": mapped_control.get("relevance", 0)
                                })
                
                if component_mappings:
                    # Calculate average relevance
                    total_relevance = sum(m["relevance"] for m in component_mappings)
                    avg_relevance = total_relevance / len(component_mappings)
                    
                    control_zta_mappings.append({
                        "control_id": control_id,
                        "zta_components": [m["component_name"] for m in component_mappings],
                        "relevance_score": round(avg_relevance * 100, 1)
                    })
            
            # Sort by control ID
            control_zta_mappings.sort(key=lambda x: x["control_id"])
            report_data["control_zta_mappings"] = control_zta_mappings
        
        # Add glossary
        report_data["glossary"] = [
            {"name": "Compliant", "definition": "The control is fully implemented and meets all requirements."},
            {"name": "Partially Compliant", "definition": "The control is partially implemented but does not fully meet all requirements."},
            {"name": "Non-Compliant", "definition": "The control is not implemented or does not meet requirements."},
            {"name": "Not Applicable", "definition": "The control is not applicable to the system or environment."},
            {"name": "Control Family", "definition": "A logical grouping of controls related to the same security aspect."},
            {"name": "Zero Trust Architecture (ZTA)", "definition": "A security model that requires strict identity verification for every person and device trying to access resources on a network."},
        ]
        
        # Generate an executive summary (in a real implementation, this might be AI-generated)
        report_data["executive_summary"] = f"""
This compliance report evaluates {config.organization}'s compliance with {config.framework}. 
The assessment covers {total_controls} controls across multiple control families.

Overall, the organization achieves a compliance score of {round(compliance_score, 1)}%, with {compliant} controls fully compliant, 
{partially_compliant} controls partially compliant, and {non_compliant} controls non-compliant. 
{not_applicable} controls were determined to be not applicable to the organization's environment.

The analysis reveals strengths in certain control families and areas for improvement in others. 
This report provides detailed information about compliance status, gaps, and recommended actions.
"""
        
        # Add key findings
        report_data["key_findings"] = [
            f"Overall compliance score is {round(compliance_score, 1)}%",
            f"{compliant} out of {total_controls} controls are fully compliant",
            f"{non_compliant} controls are non-compliant and require immediate attention",
        ]
        
        # Add recommendations (in a real implementation, these might be AI-generated)
        report_data["recommendations"] = [
            "Prioritize implementation of non-compliant controls",
            "Develop remediation plans for partially compliant controls",
            "Establish regular compliance monitoring and assessment processes",
            "Document and review not applicable controls regularly",
        ]
        
        return report_data
    
    def generate_executive_summary(self, report_path: str) -> str:
        """
        Generate an executive summary from a full report.
        
        Args:
            report_path (str): Path to the full report HTML file
            
        Returns:
            str: Path to executive summary HTML file
        """
        try:
            # Read the full report
            with open(report_path, 'r') as f:
                full_report_html = f.read()
            
            # Parse relevant sections from the full report
            # (In a real implementation, this would be more sophisticated)
            
            # Generate executive summary using template
            template = self.jinja_env.get_template("executive_summary.html")
            
            # Extract basic info from filename
            filename = os.path.basename(report_path)
            framework = filename.split('_')[0].replace('_', ' ')
            
            # Create placeholder data
            exec_data = {
                "title": f"{framework} Compliance",
                "organization": "Your Organization",
                "framework": framework,
                "generated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "executive_summary": "This is an executive summary of the compliance report.",
                "compliance_summary": {
                    "total_controls": 100,
                    "compliant_controls": 70,
                    "partially_compliant_controls": 15,
                    "non_compliant_controls": 10,
                    "not_applicable_controls": 5,
                    "compliance_score": 77.5
                },
                "key_findings": [
                    "Overall compliance is moderate",
                    "Several high-priority controls require attention",
                    "Documentation needs improvement"
                ],
                "recommendations": [
                    "Address non-compliant controls within 30 days",
                    "Improve security documentation",
                    "Establish regular compliance reviews"
                ]
            }
            
            html_content = template.render(report=exec_data)
            
            # Save executive summary
            exec_path = report_path.replace('.html', '_executive_summary.html')
            with open(exec_path, 'w') as f:
                f.write(html_content)
            
            logger.info(f"Generated executive summary: {exec_path}")
            return exec_path
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise