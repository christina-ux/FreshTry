"""
Intelligence Dashboard for PolicyEdgeAI.

Streamlit interface for live intelligence feeds and newspaper-style memos.
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="PolicyEdge Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .feed-item {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #F9FAFB;
    }
    .priority-high {
        border-left: 4px solid #EF4444;
    }
    .priority-medium {
        border-left: 4px solid #F59E0B;
    }
    .priority-low {
        border-left: 4px solid #10B981;
    }
    .priority-critical {
        border-left: 4px solid #DC2626;
        background-color: #FEF2F2;
    }
    .memo-section {
        margin: 20px 0;
        padding: 15px;
        border-radius: 8px;
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
    }
    .memo-headline {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #111827;
    }
    .memo-article {
        margin: 15px 0;
        padding: 10px;
        border-left: 2px solid #6B7280;
    }
</style>
""", unsafe_allow_html=True)

def call_api(endpoint: str, params: dict = None):
    """Call API endpoint with error handling."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def render_feed_item(item):
    """Render a single feed item."""
    priority_class = f"priority-{item.get('priority', 'low')}"
    
    with st.container():
        st.markdown(f"""
        <div class="feed-item {priority_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{item.get('title', 'No title')}</strong>
                    <span style="background-color: #E5E7EB; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 10px;">
                        {item.get('type', 'unknown').replace('_', ' ').title()}
                    </span>
                    <span style="background-color: #FEE2E2; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 5px;">
                        {item.get('priority', 'low').title()}
                    </span>
                </div>
                <div style="font-size: 0.75rem; color: #6B7280;">
                    {datetime.fromisoformat(item.get('timestamp', '')).strftime('%H:%M')}
                </div>
            </div>
            <div style="margin-top: 10px; color: #374151;">
                {item.get('summary', 'No summary available')}
            </div>
            <div style="margin-top: 5px; font-size: 0.75rem; color: #6B7280;">
                Category: {item.get('category', 'unknown').title()} | 
                Action Required: {'Yes' if item.get('action_required') else 'No'}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_memo_section(section):
    """Render a memo section."""
    st.markdown(f"""
    <div class="memo-section">
        <h3 style="color: #1F2937; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;">
            {section.get('title', 'Untitled Section')}
        </h3>
        <p style="color: #6B7280; font-style: italic; margin-bottom: 15px;">
            {section.get('subtitle', '')}
        </p>
    """, unsafe_allow_html=True)
    
    for article in section.get('articles', []):
        st.markdown(f"""
        <div class="memo-article">
            <h4 style="color: #111827; margin-bottom: 8px;">{article.get('title', 'Untitled Article')}</h4>
            <p style="line-height: 1.6; color: #374151; margin-bottom: 8px;">
                {article.get('content', 'No content available')}
            </p>
            <div style="font-size: 0.75rem; color: #6B7280; font-style: italic;">
                By {article.get('byline', 'Unknown')} - {datetime.fromisoformat(article.get('timestamp', '')).strftime('%B %d, %Y at %H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Intelligence Dashboard")
page = st.sidebar.radio(
    "Select View",
    ["Live Feed", "Intelligence Memo", "Data Explorer", "Analytics"]
)

# Main content
if page == "Live Feed":
    st.markdown('<h1 class="main-header">Live Intelligence Feed</h1>', unsafe_allow_html=True)
    
    # Feed controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        feed_type = st.selectbox(
            "Feed Type",
            ["comprehensive", "compliance", "security", "operations"],
            index=0
        )
    
    with col2:
        limit = st.slider("Number of Items", 5, 50, 20)
    
    with col3:
        auto_refresh = st.checkbox("Auto Refresh", value=False)
    
    # Get feed data
    if st.button("Refresh Feed") or auto_refresh:
        with st.spinner("Loading intelligence feed..."):
            feed_data = call_api("/api/intelligence/feed", {
                "feed_type": feed_type,
                "limit": limit
            })
        
        if feed_data:
            # Feed summary
            st.markdown('<h2 class="sub-header">Feed Summary</h2>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Items", feed_data.get("total_items", 0))
            with col2:
                action_items = len([item for item in feed_data.get("items", []) if item.get("action_required")])
                st.metric("Action Required", action_items)
            with col3:
                high_priority = len([item for item in feed_data.get("items", []) if item.get("priority") == "high"])
                st.metric("High Priority", high_priority)
            with col4:
                st.metric("Feed Type", feed_type.title())
            
            # Feed items
            st.markdown('<h2 class="sub-header">Feed Items</h2>', unsafe_allow_html=True)
            
            if feed_data.get("items"):
                for item in feed_data["items"]:
                    render_feed_item(item)
            else:
                st.info("No feed items available.")
        
        # Auto refresh
        if auto_refresh:
            st.experimental_rerun()

elif page == "Intelligence Memo":
    st.markdown('<h1 class="main-header">Intelligence Memo</h1>', unsafe_allow_html=True)
    
    # Memo controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        memo_type = st.selectbox(
            "Memo Type",
            ["daily", "weekly", "monthly", "incident", "compliance"],
            index=0
        )
    
    with col2:
        include_charts = st.checkbox("Include Charts", value=True)
    
    with col3:
        format_type = st.selectbox("Format", ["JSON", "HTML"])
    
    if st.button("Generate Memo"):
        with st.spinner("Generating intelligence memo..."):
            memo_data = call_api("/api/intelligence/memo", {
                "memo_type": memo_type,
                "include_charts": include_charts
            })
        
        if memo_data:
            if format_type == "HTML":
                # Display HTML version (simplified)
                st.markdown(f"""
                <div style="border: 2px solid #1F2937; padding: 30px; margin: 20px 0; background-color: #FFFFFF;">
                    <div class="memo-headline">{memo_data.get('headline', 'Intelligence Memo')}</div>
                    <div style="font-size: 1.1rem; color: #6B7280; margin-bottom: 20px;">
                        {memo_data.get('subheadline', '')}
                    </div>
                    <div style="font-size: 0.9rem; color: #9CA3AF; border-bottom: 1px solid #E5E7EB; padding-bottom: 15px; margin-bottom: 20px;">
                        Generated: {memo_data.get('generated_at', '')} | Type: {memo_data.get('memo_type', '').title()} | 
                        Classification: {memo_data.get('metadata', {}).get('classification', 'confidential').title()}
                    </div>
                    <div style="background-color: #F3F4F6; padding: 20px; margin: 20px 0; font-style: italic; border-left: 4px solid #3B82F6;">
                        <strong>Executive Summary:</strong> {memo_data.get('executive_summary', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render sections
                for section in memo_data.get('sections', []):
                    render_memo_section(section)
                
                # Sidebar info
                if memo_data.get('sidebar'):
                    sidebar = memo_data['sidebar']
                    st.markdown('<h2 class="sub-header">Quick Stats</h2>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    quick_stats = sidebar.get('quick_stats', {})
                    
                    with col1:
                        st.metric("Events (24h)", quick_stats.get('events_24h', 0))
                    with col2:
                        st.metric("High Priority", quick_stats.get('high_priority', 0))
                    with col3:
                        st.metric("Action Items", quick_stats.get('action_items', 0))
                    with col4:
                        st.metric("Frameworks", quick_stats.get('frameworks_updated', 0))
                    
                    if sidebar.get('highlights'):
                        st.markdown('<h3>Key Highlights</h3>', unsafe_allow_html=True)
                        for highlight in sidebar['highlights'][:5]:
                            st.markdown(f"• {highlight}")
            
            else:
                # JSON format
                st.json(memo_data)

elif page == "Data Explorer":
    st.markdown('<h1 class="main-header">Intelligence Data Explorer</h1>', unsafe_allow_html=True)
    
    # Data source selection
    data_source = st.selectbox(
        "Data Source",
        ["Summary", "Compliance Changes", "Asset Changes", "Contract Alerts", "Regulatory Updates", "Security Incidents", "Trends"]
    )
    
    if data_source == "Summary":
        if st.button("Load Intelligence Summary"):
            with st.spinner("Loading summary..."):
                summary_data = call_api("/api/intelligence/data/summary")
            
            if summary_data:
                st.json(summary_data)
    
    elif data_source == "Compliance Changes":
        hours_back = st.slider("Hours Back", 1, 168, 24)
        
        if st.button("Load Compliance Changes"):
            with st.spinner("Loading compliance changes..."):
                changes_data = call_api("/api/intelligence/data/compliance", {"hours_back": hours_back})
            
            if changes_data and changes_data.get("changes"):
                df = pd.DataFrame(changes_data["changes"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No compliance changes found.")
    
    elif data_source == "Asset Changes":
        hours_back = st.slider("Hours Back", 1, 168, 24)
        
        if st.button("Load Asset Changes"):
            with st.spinner("Loading asset changes..."):
                changes_data = call_api("/api/intelligence/data/assets", {"hours_back": hours_back})
            
            if changes_data and changes_data.get("changes"):
                df = pd.DataFrame(changes_data["changes"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No asset changes found.")
    
    # Add other data sources similarly...

elif page == "Analytics":
    st.markdown('<h1 class="main-header">Intelligence Analytics</h1>', unsafe_allow_html=True)
    
    # Analytics controls
    col1, col2 = st.columns(2)
    
    with col1:
        feed_type = st.selectbox("Feed Type", ["comprehensive", "compliance", "security", "operations"])
    
    with col2:
        hours_back = st.slider("Analysis Period (hours)", 1, 168, 24)
    
    if st.button("Generate Analytics"):
        with st.spinner("Generating analytics..."):
            metrics_data = call_api("/api/intelligence/feed/metrics", {
                "feed_type": feed_type,
                "hours_back": hours_back
            })
        
        if metrics_data:
            # Metrics overview
            st.markdown('<h2 class="sub-header">Metrics Overview</h2>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Items", metrics_data.get("total_items", 0))
            with col2:
                st.metric("Action Required", metrics_data.get("action_required", 0))
            with col3:
                st.metric("Unique Assets", metrics_data.get("unique_assets_affected", 0))
            with col4:
                period = metrics_data.get("period", {})
                st.metric("Analysis Period", f"{period.get('hours_back', 0)}h")
            
            # Charts
            st.markdown('<h2 class="sub-header">Distribution Charts</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Priority distribution
                priority_data = metrics_data.get("by_priority", {})
                if priority_data:
                    fig = px.pie(
                        values=list(priority_data.values()),
                        names=list(priority_data.keys()),
                        title="Items by Priority"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category distribution
                category_data = metrics_data.get("by_category", {})
                if category_data:
                    fig = px.bar(
                        x=list(category_data.keys()),
                        y=list(category_data.values()),
                        title="Items by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Type distribution
            type_data = metrics_data.get("by_type", {})
            if type_data:
                st.markdown('<h3>Items by Type</h3>')
                fig = px.bar(
                    x=list(type_data.values()),
                    y=list(type_data.keys()),
                    orientation='h',
                    title="Distribution by Item Type"
                )
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**PolicyEdge Intelligence Dashboard** | Real-time compliance and security intelligence")