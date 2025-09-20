import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
import time
from utils.api_client import APIClient
from utils.cache import cached

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("streamlit_app")

# Get API URL from environment variable or use default
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Create API client with efficient connection management
api_client = APIClient(base_url=API_URL, timeout=10, max_retries=3)

# Cache decorator for API calls
@cached(prefix="api", max_age=300)  # Cache for 5 minutes
def call_api(endpoint, use_cache=True):
    """
    Efficient API call handler with caching and error handling
    """
    try:
        return api_client.get(endpoint, use_cache=use_cache)
    except Exception as e:
        logger.error(f"Error calling API at {endpoint}: {str(e)}")
        st.error(f"Error connecting to API: {str(e)}")
        return None

# Page configuration
st.set_page_config(
    page_title="PolicyEdgeAI Dashboard", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache app version info for display
@st.cache_data(ttl=3600)
def get_app_info():
    try:
        return api_client.get("")
    except Exception:
        return {"version": "Unknown", "build": "Unknown"}

# Sidebar navigation
st.sidebar.title("PolicyEdgeAI Navigation")
page = st.sidebar.radio(
    "Select a Page",
    ["Dashboard", "Compliance Scoring", "AI Licensing", "Risk Ontology", "Technical Debt"]
)

# Show API connection status
with st.sidebar.expander("Connection Info"):
    try:
        start_time = time.time()
        health = api_client.get("health")
        response_time = time.time() - start_time
        if health and health.get("status") == "healthy":
            st.sidebar.success(f"✅ Connected to API at {API_URL} ({response_time:.2f}s)")
            
            # Get app info
            app_info = get_app_info()
            if app_info:
                st.sidebar.info(f"Version: {app_info.get('version', 'Unknown')}")
                st.sidebar.info(f"Build: {app_info.get('build', 'Unknown')}")
        else:
            st.sidebar.error(f"❌ API returned unhealthy status")
    except Exception as e:
        st.sidebar.error(f"❌ Cannot connect to API at {API_URL}: {str(e)}")
    
    st.sidebar.info("Change API URL by setting the API_URL environment variable")

# DASHBOARD PAGE
if page == "Dashboard":
    st.title("⚖️ PolicyEdgeAI Live Dashboard")
    
    # Create 2x2 metrics layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # Use cached API calls for better performance
    with st.spinner("Loading compliance score data..."):
        score_data = call_api("/score/report")
    
    with col1:
        # Compliance Score Summary
        if score_data:
            st.metric(
                label="Overall Compliance Score", 
                value=f"{score_data.get('total_score', 0)}%",
                delta=f"{score_data.get('score_change', 0)}%" 
            )
            
            frameworks = score_data.get('framework_scores', {})
            if frameworks:
                # Create a bar chart for framework scores
                df = pd.DataFrame({
                    'Framework': list(frameworks.keys()),
                    'Score': list(frameworks.values())
                })
                
                fig = px.bar(
                    df, 
                    x='Framework', 
                    y='Score',
                    title="Framework Compliance Scores",
                    color='Score',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[0, 100]
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Technical Debt Summary
        with st.spinner("Loading technical debt data..."):
            debt_data = call_api("/debt/summary")
            
        if debt_data:
            total_issues = sum(debt_data.get('counts', {}).values())
            st.metric(
                label="Technical Debt Issues", 
                value=total_issues,
                delta=debt_data.get('change', 0), 
                delta_color="inverse"
            )
            
            # Create a pie chart of debt categories
            if 'counts' in debt_data:
                df = pd.DataFrame({
                    'Category': list(debt_data['counts'].keys()),
                    'Count': list(debt_data['counts'].values())
                })
                
                fig = px.pie(
                    df, 
                    values='Count', 
                    names='Category',
                    title="Technical Debt Distribution",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # License Metrics
        with st.spinner("Loading license data..."):
            license_data = call_api("/ai/license-metrics")
            
        if license_data:
            if 'license_count' in license_data:
                st.metric(
                    label="Active AI Licenses", 
                    value=license_data.get('license_count', 0)
                )
            
            if 'compliance_rate' in license_data:
                st.metric(
                    label="License Compliance Rate", 
                    value=f"{license_data.get('compliance_rate', 0)}%"
                )
            
            # Create a chart for licensing metrics
            if 'metrics' in license_data:
                metrics = license_data['metrics']
                df = pd.DataFrame({
                    'Metric': list(metrics.keys()),
                    'Value': list(metrics.values())
                })
                
                fig = px.bar(
                    df, 
                    x='Metric', 
                    y='Value',
                    title="Key License Metrics",
                    color='Value',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        # Risk Ontology
        with st.spinner("Loading risk data..."):
            risk_data = call_api("/ai/risk-ontology")
            
        if risk_data and 'categories' in risk_data:
            categories = risk_data['categories']
            # Count risks by severity
            severity_counts = {}
            
            for category in categories:
                for risk in category.get('risks', []):
                    severity = risk.get('severity', 'Unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            total_risks = sum(severity_counts.values())
            st.metric(
                label="Total AI Risks Identified", 
                value=total_risks
            )
            
            # Create a chart for risk severity distribution
            df = pd.DataFrame({
                'Severity': list(severity_counts.keys()),
                'Count': list(severity_counts.values())
            })
            
            # Sort by severity level
            severity_order = ['Critical', 'High', 'Medium', 'Low', 'Unknown']
            df['Severity'] = pd.Categorical(df['Severity'], categories=severity_order, ordered=True)
            df = df.sort_values('Severity')
            
            fig = px.bar(
                df, 
                x='Severity', 
                y='Count',
                title="AI Risks by Severity",
                color='Severity',
                color_discrete_map={
                    'Critical': 'red',
                    'High': 'orange', 
                    'Medium': 'yellow',
                    'Low': 'green',
                    'Unknown': 'grey'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity Timeline
    st.subheader("Recent Activity")
    
    # This would typically come from an API endpoint
    # For demo, we'll create sample data
    activities = [
        {"timestamp": "2025-04-02T10:30:00", "type": "compliance_check", "description": "Automated compliance check completed"},
        {"timestamp": "2025-04-01T16:45:00", "type": "license_update", "description": "New AI license added for LLM-based analytics"},
        {"timestamp": "2025-04-01T14:15:00", "type": "risk_assessment", "description": "Risk assessment completed for model drift vulnerability"},
        {"timestamp": "2025-03-31T09:20:00", "type": "technical_update", "description": "Technical debt reduction plan implemented"}
    ]
    
    for activity in activities:
        timestamp = datetime.fromisoformat(activity["timestamp"])
        formatted_time = timestamp.strftime("%b %d, %Y at %H:%M")
        
        # Style based on activity type
        if activity["type"] == "compliance_check":
            icon = "✅"
        elif activity["type"] == "license_update":
            icon = "📝"
        elif activity["type"] == "risk_assessment":
            icon = "⚠️"
        elif activity["type"] == "technical_update":
            icon = "🔧"
        else:
            icon = "ℹ️"
            
        st.markdown(f"{icon} **{formatted_time}**: {activity['description']}")

# COMPLIANCE SCORING PAGE
elif page == "Compliance Scoring":
    st.title("✅ Compliance Scoring Dashboard")
    
    # Get scoring data with caching
    with st.spinner("Loading compliance scoring data..."):
        score_data = call_api("/score/report")
        
    if not score_data:
        st.error("Unable to load compliance scoring data")
        st.stop()
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Overall Compliance", 
            value=f"{score_data.get('total_score', 0)}%",
            delta=f"{score_data.get('score_change', 0)}%"
        )
    
    with col2:
        # Calculate controls implementation rate
        controls = score_data.get('controls', {})
        implemented = sum(1 for c in controls.values() if c.get('implemented', False))
        total = len(controls)
        implementation_rate = round((implemented / total) * 100) if total > 0 else 0
        
        st.metric(
            label="Controls Implementation", 
            value=f"{implementation_rate}%",
            help="Percentage of controls that are fully implemented"
        )
    
    with col3:
        # Last assessment date
        if 'last_assessment' in score_data:
            st.metric(
                label="Last Assessment",
                value=score_data.get('last_assessment', 'Never')
            )
        else:
            st.metric(
                label="Last Assessment",
                value="April 2, 2025"  # Demo data
            )
    
    # Framework scores
    st.subheader("Framework Compliance Scores")
    frameworks = score_data.get('framework_scores', {})
    
    if frameworks:
        # Create a horizontal bar chart for framework scores
        df = pd.DataFrame({
            'Framework': list(frameworks.keys()),
            'Score': list(frameworks.values())
        })
        
        fig = px.bar(
            df, 
            y='Framework', 
            x='Score',
            orientation='h',
            title="Framework Compliance Scores",
            color='Score',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[0, 100],
            height=400
        )
        
        fig.update_layout(xaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    # Controls by category
    st.subheader("Controls by Category")
    controls = score_data.get('controls', {})
    
    if controls:
        # Group controls by family/category
        categories = {}
        for control_id, control in controls.items():
            category = control.get('family', 'Other')
            if category not in categories:
                categories[category] = {'total': 0, 'implemented': 0}
            
            categories[category]['total'] += 1
            if control.get('implemented', False):
                categories[category]['implemented'] += 1
        
        # Calculate implementation percentage for each category
        df = pd.DataFrame([
            {
                'Category': category,
                'Implementation Rate': (stats['implemented'] / stats['total']) * 100 if stats['total'] > 0 else 0,
                'Total Controls': stats['total'],
                'Implemented': stats['implemented']
            }
            for category, stats in categories.items()
        ])
        
        # Sort by implementation rate
        df = df.sort_values('Implementation Rate', ascending=False)
        
        fig = px.bar(
            df,
            y='Category',
            x='Implementation Rate',
            orientation='h',
            color='Implementation Rate',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[0, 100],
            height=500,
            hover_data=['Total Controls', 'Implemented']
        )
        
        fig.update_layout(xaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical trend chart
    st.subheader("Compliance Score Trend")
    
    # This would typically come from a historical API endpoint
    # For demo, we'll create sample data
    history = [
        {"date": "2024-11-01", "score": 65},
        {"date": "2024-12-01", "score": 68},
        {"date": "2025-01-01", "score": 72},
        {"date": "2025-02-01", "score": 76},
        {"date": "2025-03-01", "score": 82},
        {"date": "2025-04-01", "score": score_data.get('total_score', 85)}
    ]
    
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['date'])
    
    fig = px.line(
        df,
        x='date',
        y='score',
        title='Compliance Score Trend',
        markers=True
    )
    
    fig.update_layout(
        yaxis_range=[0, 100],
        xaxis_title="Date",
        yaxis_title="Compliance Score (%)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Rest of the code remains largely the same...
# Additional pages would be similarly optimized with caching and better API client usage

# Always close the API client when the app is done
# For Streamlit this doesn't matter as much since it's a long-running process
# But it's good practice

# Clean up function for session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Register cleanup function for when app restarts
    def cleanup():
        api_client.close()
    
    # Note: This might not be called reliably in Streamlit
    import atexit
    atexit.register(cleanup)
