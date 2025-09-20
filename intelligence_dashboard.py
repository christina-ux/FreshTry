"""
Live Intelligence Feed Dashboard - Streamlit Demo
Professional intelligence newspaper-style interface
"""
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Configure page
st.set_page_config(
    page_title="Live Intelligence Feed Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 10px;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E40AF;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .intelligence-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .high-impact {
        border-left: 4px solid #DC2626;
    }
    .medium-impact {
        border-left: 4px solid #F59E0B;
    }
    .low-impact {
        border-left: 4px solid #10B981;
    }
    .score-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        font-size: 12px;
        margin-right: 5px;
    }
    .score-high {
        background-color: #DC2626;
    }
    .score-medium {
        background-color: #F59E0B;
    }
    .score-low {
        background-color: #10B981;
    }
    .memo-section {
        background-color: #FEFEFE;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .newspaper-title {
        font-family: 'Times New Roman', serif;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8001/api/intelligence"

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Make API request to intelligence system."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Connection Error: Could not connect to intelligence system. Please ensure the API server is running on port 8001.")
        return {}

def get_impact_class(score: float) -> str:
    """Get CSS class based on impact score."""
    if score >= 7:
        return "high-impact"
    elif score >= 4:
        return "medium-impact"
    else:
        return "low-impact"

def get_score_badge_class(score: float) -> str:
    """Get score badge CSS class."""
    if score >= 7:
        return "score-high"
    elif score >= 4:
        return "score-medium"
    else:
        return "score-low"

def format_score_badge(label: str, score: float) -> str:
    """Format score badge HTML."""
    badge_class = get_score_badge_class(score)
    return f'<span class="score-badge {badge_class}">{label}: {score:.1f}</span>'

def main():
    # Header
    st.markdown('<div class="main-header">Live Intelligence Feed Pro</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #64748B; margin-bottom: 30px;">AI-Powered Intelligence Newspaper • Real-Time Analysis • Professional Insights</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Select View",
        ["🏠 Dashboard", "📊 Live Feed", "📰 Intelligence Memo", "⚡ Tripwires", "🧠 Learning System", "⚙️ Settings"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Live Feed":
        show_live_feed()
    elif page == "📰 Intelligence Memo":
        show_memo_generation()
    elif page == "⚡ Tripwires":
        show_tripwires()
    elif page == "🧠 Learning System":
        show_learning_system()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Show main dashboard with system overview."""
    st.markdown('<div class="sub-header">📊 System Overview</div>', unsafe_allow_html=True)
    
    # Get system status
    status = make_api_request("/status")
    
    if status:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Data Sources", status["sources"]["total"], 
                     delta=f"{status['sources']['enabled']} active")
        
        with col2:
            st.metric("Intelligence Feeds", status["feeds"]["total"],
                     delta=f"{status['feeds']['premium']} premium")
        
        with col3:
            st.metric("Tripwire Rules", status["tripwires"]["total"],
                     delta=f"{status['tripwires']['active']} active")
        
        with col4:
            st.metric("Learning Actions", status["learning"]["total_actions"],
                     delta=f"{status['learning']['unique_users']} users")
    
    # Available Feeds
    st.markdown('<div class="sub-header">📡 Available Intelligence Feeds</div>', unsafe_allow_html=True)
    
    feeds = make_api_request("/feeds")
    
    if feeds:
        for feed in feeds:
            premium_badge = "🏆 PREMIUM" if feed["is_premium"] else "🆓 FREE"
            
            st.markdown(f"""
            <div class="intelligence-card">
                <h4>{feed['name']} {premium_badge}</h4>
                <p>{feed['description']}</p>
                <p><strong>Categories:</strong> {', '.join([cat.replace('_', ' ').title() for cat in feed['categories']])}</p>
                <p><strong>Items:</strong> {len(feed['items'])} | <strong>Last Updated:</strong> {feed['last_updated'][:19]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown('<div class="sub-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Trigger Collection", use_container_width=True):
            result = make_api_request("/collect", "POST", {})
            if result:
                st.success("Intelligence collection initiated!")
    
    with col2:
        if st.button("📰 Generate Memo", use_container_width=True):
            st.info("Redirecting to memo generation...")
            # This would trigger memo generation
    
    with col3:
        if st.button("🧠 Run Learning Cycle", use_container_width=True):
            result = make_api_request("/learning/cycle", "POST")
            if result:
                st.success(f"Learning cycle completed! Generated {result.get('deltas_generated', 0)} deltas.")

def show_live_feed():
    """Show live intelligence feed."""
    st.markdown('<div class="sub-header">📊 Live Intelligence Feed</div>', unsafe_allow_html=True)
    
    # Feed selection
    feeds = make_api_request("/feeds")
    if feeds:
        feed_options = {f"{feed['name']} ({'Premium' if feed['is_premium'] else 'Free'})": feed['id'] for feed in feeds}
        selected_feed_name = st.selectbox("Select Feed", list(feed_options.keys()))
        selected_feed_id = feed_options[selected_feed_name]
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            hours_back = st.slider("Hours Back", 1, 168, 24)
        with col2:
            min_impact = st.slider("Min Impact Score", 0.0, 10.0, 3.0)
        with col3:
            limit = st.slider("Max Items", 10, 100, 20)
        
        # Get feed items
        items = make_api_request(f"/feed/{selected_feed_id}/items?hours_back={hours_back}&min_impact={min_impact}&limit={limit}")
        
        if items:
            st.info(f"Found {len(items)} intelligence items")
            
            for item in items:
                impact_class = get_impact_class(item["impact_score"])
                
                # Score badges
                score_html = (
                    format_score_badge("Impact", item["impact_score"]) +
                    format_score_badge("Urgency", item["urgency_score"]) +
                    format_score_badge("Risk", item["risk_score"]) +
                    format_score_badge("Confidence", item["confidence_score"] * 10)
                )
                
                st.markdown(f"""
                <div class="intelligence-card {impact_class}">
                    <h4>{item['title']}</h4>
                    <p>{score_html}</p>
                    <p><strong>Category:</strong> {item['category'].replace('_', ' ').title()} | 
                       <strong>Source:</strong> {item['source'].replace('_', ' ').title()}</p>
                    <p>{item['summary']}</p>
                    <p><small><strong>Tags:</strong> {', '.join(item['tags'][:5])} | 
                       <strong>Time:</strong> {item['timestamp'][:19]}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Track user action (view)
                if st.button(f"📖 Read Full Article", key=f"read_{item['id']}"):
                    track_action("demo_user", "click", item['id'], "intelligence_item", 
                               {"category": item['category'], "source": item['source']})
                    st.info("Article interaction tracked for learning system.")
        else:
            st.warning("No intelligence items found for the selected criteria.")

def show_memo_generation():
    """Show memo generation interface."""
    st.markdown('<div class="newspaper-title">INTELLIGENCE MEMO GENERATION</div>', unsafe_allow_html=True)
    
    # Memo configuration
    col1, col2 = st.columns(2)
    
    with col1:
        memo_type = st.selectbox("Memo Type", ["daily", "weekly", "alert"])
        target_audience = st.selectbox("Target Audience", ["executive", "analyst", "operations"])
        
    with col2:
        hours_back = st.slider("Data Window (Hours)", 1, 168, 24)
        min_impact = st.slider("Minimum Impact Score", 0.0, 10.0, 3.0)
    
    # Categories filter
    all_categories = ["market_shock", "regulatory_change", "ai_development", "political_event", "risk_exposure"]
    selected_categories = st.multiselect("Include Categories", all_categories, default=all_categories)
    
    if st.button("📰 Generate Intelligence Memo", use_container_width=True):
        with st.spinner("Generating professional intelligence memo..."):
            memo_request = {
                "memo_type": memo_type,
                "target_audience": target_audience,
                "hours_back": hours_back,
                "min_impact_score": min_impact,
                "categories": selected_categories
            }
            
            memo = make_api_request("/memo/generate", "POST", memo_request)
            
            if memo:
                st.success("Memo generated successfully!")
                
                # Display memo
                st.markdown(f"""
                <div class="memo-section">
                    <h2>{memo['title']}</h2>
                    <p><strong>Generated:</strong> {memo['generated_at'][:19]} | 
                       <strong>Type:</strong> {memo['memo_type'].title()} | 
                       <strong>Audience:</strong> {memo['target_audience'].title()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Executive Summary
                st.markdown('<div class="memo-section">', unsafe_allow_html=True)
                st.markdown(memo['executive_summary'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Key Insights
                if memo.get('key_insights'):
                    st.markdown('<div class="memo-section">', unsafe_allow_html=True)
                    st.markdown("**KEY INSIGHTS**")
                    for insight in memo['key_insights']:
                        st.markdown(f"• {insight}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Risk Assessment
                if memo.get('risk_assessment'):
                    st.markdown('<div class="memo-section">', unsafe_allow_html=True)
                    st.markdown(memo['risk_assessment'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Recommendations
                if memo.get('recommendations'):
                    st.markdown('<div class="memo-section">', unsafe_allow_html=True)
                    st.markdown("**RECOMMENDATIONS**")
                    for rec in memo['recommendations']:
                        st.markdown(f"• {rec}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Market Analysis
                if memo.get('market_analysis'):
                    st.markdown('<div class="memo-section">', unsafe_allow_html=True)
                    st.markdown(memo['market_analysis'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Track memo generation
                track_action("demo_user", "generate", memo['id'], "memo")

def show_tripwires():
    """Show tripwire management interface."""
    st.markdown('<div class="sub-header">⚡ Tripwire Alert System</div>', unsafe_allow_html=True)
    
    # Get existing tripwires
    tripwires = make_api_request("/tripwires")
    
    if tripwires:
        st.markdown("**Active Tripwire Rules:**")
        
        for tripwire in tripwires:
            status_color = "🟢" if tripwire["status"] == "active" else "🔴"
            
            st.markdown(f"""
            <div class="intelligence-card">
                <h4>{status_color} {tripwire['name']}</h4>
                <p><strong>Description:</strong> {tripwire['description']}</p>
                <p><strong>Pattern:</strong> <code>{tripwire['pattern']}</code></p>
                <p><strong>Category:</strong> {tripwire['category'].replace('_', ' ').title()} | 
                   <strong>Threshold:</strong> {tripwire['threshold']}</p>
                <p><strong>Triggered:</strong> {tripwire['trigger_count']} times | 
                   <strong>Last:</strong> {tripwire.get('last_triggered', 'Never')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Create new tripwire
    st.markdown("**Create New Tripwire:**")
    
    with st.form("new_tripwire"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Tripwire Name")
            pattern = st.text_input("Pattern/Keywords")
            
        with col2:
            category = st.selectbox("Category", ["market_shock", "regulatory_change", "ai_development", "political_event", "risk_exposure"])
            threshold = st.slider("Trigger Threshold", 1.0, 10.0, 6.0)
        
        description = st.text_area("Description")
        
        if st.form_submit_button("🚀 Create Tripwire"):
            tripwire_data = {
                "name": name,
                "description": description,
                "pattern": pattern,
                "category": category,
                "threshold": threshold
            }
            
            result = make_api_request("/tripwire/create", "POST", tripwire_data)
            if result:
                st.success(f"Tripwire '{name}' created successfully!")
                st.experimental_rerun()

def show_learning_system():
    """Show learning system interface."""
    st.markdown('<div class="sub-header">🧠 Self-Evolving Learning System</div>', unsafe_allow_html=True)
    
    # Get learning health
    health = make_api_request("/learning/health")
    
    if health:
        # Learning metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Actions Tracked", health["total_actions_tracked"])
            st.metric("Learning Deltas", health["total_learning_deltas"])
        
        with col2:
            st.metric("Unique Users", health["unique_users"])
            st.metric("Deltas Per Day", health["avg_deltas_per_day"])
        
        with col3:
            should_run = health["learning_orchestrator"]["should_run_cycle"]
            st.metric("Learning Cycle", "Due" if should_run else "On Schedule")
            if health["learning_orchestrator"]["last_cycle"]:
                st.text(f"Last: {health['learning_orchestrator']['last_cycle'][:19]}")
    
    # Recent learning deltas
    st.markdown("**Recent Learning Deltas:**")
    
    deltas = make_api_request("/learning/deltas?hours_back=168&limit=10")
    
    if deltas:
        for delta in deltas:
            confidence_badge = format_score_badge("Confidence", delta["confidence"] * 10)
            
            st.markdown(f"""
            <div class="intelligence-card">
                <h5>{delta['change_type'].replace('_', ' ').title()}</h5>
                <p>{confidence_badge}</p>
                <p>{delta['description']}</p>
                <p><small><strong>Applied:</strong> {delta['applied_at'][:19]} | 
                   <strong>Source Actions:</strong> {len(delta['source_actions'])}</small></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent learning deltas found.")

def show_settings():
    """Show system settings and configuration."""
    st.markdown('<div class="sub-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    # Monetization tiers
    st.markdown("**Monetization Tiers:**")
    
    tiers = {
        "🆓 Free": {
            "price": "$0/month",
            "feeds": "2 feeds",
            "memos": "1 memo/day",
            "api": "No API access",
            "features": ["AI Development Monitor", "Regulatory Watch"]
        },
        "💼 Basic": {
            "price": "$29.99/month", 
            "feeds": "5 feeds",
            "memos": "3 memos/day",
            "api": "API access included",
            "features": ["All free features", "Market Intelligence", "Custom tripwires"]
        },
        "🏆 Premium": {
            "price": "$99.99/month",
            "feeds": "10 feeds", 
            "memos": "10 memos/day",
            "api": "Full API access",
            "features": ["All basic features", "Executive Brief", "Risk Intelligence", "Priority support"]
        },
        "🏢 Enterprise": {
            "price": "Custom pricing",
            "feeds": "Unlimited",
            "memos": "Unlimited", 
            "api": "Full API + webhooks",
            "features": ["All premium features", "Custom integrations", "Dedicated support", "SLA guarantees"]
        }
    }
    
    cols = st.columns(4)
    for i, (tier, details) in enumerate(tiers.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="intelligence-card">
                <h4>{tier}</h4>
                <h3>{details['price']}</h3>
                <p><strong>{details['feeds']}</strong></p>
                <p><strong>{details['memos']}</strong></p>
                <p><strong>{details['api']}</strong></p>
                <hr>
                <ul>
                    {''.join([f'<li>{feature}</li>' for feature in details['features']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # System information
    st.markdown("**System Information:**")
    st.info("""
    **Live Intelligence Feed Pro** - Enterprise-grade intelligence automation platform
    
    **Version:** 1.0.0  
    **Built with:** PolicyEdgeAI framework, FastAPI, Streamlit
    **Features:** Real-time data ingestion, AI-powered analysis, self-evolving tripwires
    **Integrations:** RSS feeds, web scraping, Google Drive, AIPRM, custom agents
    """)

def track_action(user_id: str, action_type: str, target_id: str, target_type: str, metadata: dict = None):
    """Track user action for learning system."""
    action_data = {
        "user_id": user_id,
        "action_type": action_type,
        "target_id": target_id,
        "target_type": target_type,
        "metadata": metadata or {}
    }
    
    make_api_request("/action/track", "POST", action_data)

if __name__ == "__main__":
    main()