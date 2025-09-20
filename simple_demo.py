import streamlit as st

st.set_page_config(
    page_title="PolicyEdgeAI Demo",
    page_icon="🔍",
    layout="wide"
)

# Add custom styling
st.markdown("""
<style>
    .title {
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #1E3A8A;
    }
    .subtitle {
        font-size: 24px;
        margin-bottom: 30px;
        color: #3B82F6;
    }
    .section-header {
        font-size: 28px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
        color: #1E3A8A;
    }
    .card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .feature-card {
        background-color: #F0F9FF;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        margin-bottom: 15px;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 3px 6px;
        border-radius: 4px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 14px;
        color: #64748B;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="title">PolicyEdgeAI Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered policy document analysis for compliance and readability</div>', unsafe_allow_html=True)

# Introduction
st.markdown("""
# Welcome to PolicyEdgeAI

PolicyEdgeAI helps organizations analyze, improve, and maintain their policy documents for compliance and clarity.

This demo showcases the core capabilities of our SaaS platform:
""")

# Main features in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📋 Policy Analysis")
    st.markdown("""
    - Upload any policy document
    - Multiple formats supported
    - Fast, accurate analysis
    - Clear visual results
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Compliance Checking")
    st.markdown("""
    - GDPR, CCPA, HIPAA compliance
    - Legal requirement validation
    - Gap identification
    - Risk assessment
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💡 AI-Powered Recommendations")
    st.markdown("""
    - Specific improvement guidance
    - Readability enhancements
    - Template suggestions
    - Industry benchmarking
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Demo analysis results
st.markdown('<div class="section-header">Sample Analysis Results</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.write("### Demo Privacy Policy Analysis")

# Compliance scores in columns
metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    st.markdown('<div class="metric-value">87%</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">GDPR COMPLIANCE</div>', unsafe_allow_html=True)

with metrics_col2:
    st.markdown('<div class="metric-value">92%</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">CCPA COMPLIANCE</div>', unsafe_allow_html=True)

with metrics_col3:
    st.markdown('<div class="metric-value">79%</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">CLARITY SCORE</div>', unsafe_allow_html=True)

with metrics_col4:
    st.markdown('<div class="metric-value">12th</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">GRADE LEVEL</div>', unsafe_allow_html=True)

# Policy summary
st.write("#### Summary")
st.info("This privacy policy outlines data collection practices, user rights, and company processing activities. It covers most areas required by modern privacy regulations but has some gaps in specificity and clarity.")

# Tabs for different analysis aspects
tab1, tab2, tab3 = st.tabs(["Compliance Issues", "Recommendations", "Risk Analysis"])

with tab1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("**Missing or Inadequate**")
    st.markdown("""
    - Data retention periods are not specific enough
    - No clear indication of legal basis for processing
    - Lacks details on automated decision-making
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("**Unclear Language**")
    st.markdown("""
    - Section 4 on data sharing uses vague terminology
    - International transfer mechanisms not specified
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### How to Improve Your Policy")
    
    st.markdown("#### 1. Add specific retention periods")
    st.markdown("""
    Change:
    > *"We will retain your information only for as long as necessary."*
    
    To:
    > *"We retain different types of data for different periods: contact information for 3 years after account closure, usage data for 12 months, and payment information as required by applicable tax laws (typically 7 years)."*
    """)
    
    st.markdown("#### 2. Clarify international transfers")
    st.markdown("""
    Add:
    > *"When we transfer personal data outside the EU/EEA, we rely on Standard Contractual Clauses approved by the European Commission and additional safeguards including encryption and access controls."*
    """)

with tab3:
    st.markdown("### Risk Assessment")
    
    risk_data = {
        "Risk Area": ["Non-specific retention policy", "Vague third-party sharing", "Missing legal basis"],
        "Potential Impact": ["Medium", "High", "Medium"],
        "Regulatory Exposure": ["GDPR Article 5(1)(e)", "GDPR Article 13, CCPA Section 1798.110", "GDPR Article 6"]
    }
    
    # Display as a table with custom formatting
    for i in range(len(risk_data["Risk Area"])):
        cols = st.columns([3, 2, 3])
        with cols[0]:
            st.write(f"**{risk_data['Risk Area'][i]}**")
        with cols[1]:
            impact = risk_data["Potential Impact"][i]
            if impact == "High":
                st.markdown(f"<span style='color:red'>⚠️ {impact}</span>", unsafe_allow_html=True)
            elif impact == "Medium":
                st.markdown(f"<span style='color:orange'>⚠️ {impact}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:green'>✓ {impact}</span>", unsafe_allow_html=True)
        with cols[2]:
            st.write(risk_data["Regulatory Exposure"][i])

st.markdown('</div>', unsafe_allow_html=True)  # Close card

# Industry comparison
st.markdown('<div class="section-header">Industry Benchmarking</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### How Your Policy Compares to Industry Standards")

# The visual comparison
st.markdown("""
| Category | Your Score | Industry Average | Comparison |
|----------|------------|-----------------|------------|
| Transparency | 85% | 72% | ✅ Above average |
| User Rights | 90% | 68% | ✅ Well above average |
| Data Security | 75% | 80% | ⚠️ Below average |
| Lawful Basis | 65% | 60% | ✅ Slightly above |
| Breach Protocol | 70% | 65% | ✅ Slightly above |
""")

st.markdown("### Key Advantages")
st.markdown("- **Strong in user rights documentation**: Your policy clearly outlines the rights available to users")
st.markdown("- **Above average transparency**: Your policy has good clarity in explaining how data is used")

st.markdown("### Areas for Improvement")
st.markdown("- **Data security descriptions**: Consider adding more detail about security measures")
st.markdown("- **Breach notification process**: Could be more specific about timelines and processes")

st.markdown('</div>', unsafe_allow_html=True)  # Close card

# Call to action
st.markdown('<div class="section-header">Get Started with PolicyEdgeAI</div>', unsafe_allow_html=True)

st.markdown("""
PolicyEdgeAI offers comprehensive policy analysis as a service:

- **Unlimited Policy Analysis**: Upload and analyze all your policy documents
- **Continuous Monitoring**: Get alerts when regulations change that affect your policies
- **Collaboration Tools**: Work with your legal and compliance teams
- **Export & Integration**: Generate reports and integrate with your existing systems

Contact us to learn more about our pricing plans and how PolicyEdgeAI can help your organization.
""")

# Footer
st.markdown("---")
st.markdown("© 2025 PolicyEdgeAI. All rights reserved.")
