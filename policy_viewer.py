import streamlit as st
import os

st.set_page_config(page_title="PolicyEdgeAI Demo", layout="wide")

st.title("PolicyEdgeAI Demo")

st.markdown("""
## Policy Analysis Demo

This is a demonstration of the PolicyEdgeAI capabilities. In this demo, you can see how the system analyzes a sample privacy policy.
""")

with st.expander("Sample Privacy Policy", expanded=True):
    st.markdown("""
    # DATA PRIVACY POLICY

    Last Updated: April 1, 2025

    ## 1. INTRODUCTION

    Welcome to our Data Privacy Policy. This policy explains how we collect, use, and protect your personal information when you use our services.

    ## 2. INFORMATION WE COLLECT

    We may collect the following types of information:
    - Personal information such as name, email address, and contact details
    - Usage information about how you interact with our services
    - Device information including IP address and browser type
    - Cookies and similar tracking technologies

    ## 3. HOW WE USE YOUR INFORMATION

    We use your information to:
    - Provide and improve our services
    - Communicate with you about updates or changes
    - Personalize content and recommendations
    - Maintain security and prevent fraud

    ## 4. DATA SHARING AND DISCLOSURE

    We may share your information with:
    - Service providers who help us deliver our services
    - Legal authorities when required by law
    - Business partners with your consent

    ## 5. YOUR RIGHTS AND CHOICES

    You have the right to:
    - Access your personal information
    - Correct inaccuracies in your data
    - Delete your data in certain circumstances
    - Opt out of marketing communications

    ## 6. SECURITY MEASURES

    We implement appropriate technical and organizational measures to protect your personal information.

    ## 7. INTERNATIONAL TRANSFERS

    Your information may be transferred to countries with different data protection laws.

    ## 8. RETENTION PERIOD

    We will retain your information only for as long as necessary to fulfill the purposes outlined in this policy.

    ## 9. CHANGES TO THIS POLICY

    We may update this policy from time to time. We will notify you of any significant changes.

    ## 10. CONTACT US

    If you have any questions about this policy, please contact us at privacy@example.com.
    """)

if st.button("Run Analysis"):
    # Show loading spinner
    with st.spinner("Analyzing policy..."):
        # Simulate processing time
        progress_bar = st.progress(0)
        for i in range(100):
            # Update progress bar
            progress_bar.progress(i + 1)
            # Add small delay
            if i < 70:
                # Move faster up to 70%
                st.empty().sleep(0.01)
            else:
                # Slower for last 30%
                st.empty().sleep(0.03)
    
    # Analysis results
    st.success("Analysis complete\!")
    
    st.markdown("## Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("GDPR Compliance", "87%")
    
    with col2:
        st.metric("CCPA Compliance", "92%")
    
    with col3:
        st.metric("Overall Readability", "Grade 12")
    
    st.markdown("### Policy Summary")
    st.info("This policy outlines data collection practices, user rights, and the company's data processing activities. It covers key areas required by modern privacy regulations including data collection, sharing, retention, and user rights.")
    
    st.markdown("### Compliance Issues")
    issues = {
        "Missing or Inadequate": [
            "Data retention periods are not specific enough",
            "No clear indication of legal basis for processing",
            "Lacks details on automated decision-making"
        ],
        "Unclear Language": [
            "Section 4 on data sharing uses vague terminology",
            "International transfer mechanisms not specified"
        ],
        "Potential Risks": [
            "Broad language in 'business partners' sharing may not satisfy GDPR requirements",
            "No mention of children's privacy provisions"
        ]
    }
    
    tab1, tab2, tab3 = st.tabs(["Missing or Inadequate", "Unclear Language", "Potential Risks"])
    
    with tab1:
        for issue in issues["Missing or Inadequate"]:
            st.markdown(f"- {issue}")
    
    with tab2:
        for issue in issues["Unclear Language"]:
            st.markdown(f"- {issue}")
    
    with tab3:
        for issue in issues["Potential Risks"]:
            st.markdown(f"- {issue}")
    
    st.markdown("### Recommendations")
    
    recommendations = [
        "Add specific retention periods for different data categories",
        "Clearly state the legal basis for each type of data processing",
        "Add details on international data transfer mechanisms",
        "Include a specific section on children's privacy",
        "Clarify the definition of 'business partners' and when data might be shared",
        "Add information on automated decision-making and profiling"
    ]
    
    for i, rec in enumerate(recommendations):
        st.markdown(f"{i+1}. {rec}")
    
    st.markdown("### Comparison to Industry Standards")
    
    comparison_data = {
        "Categories": ["Transparency", "User Rights", "Data Security", "Lawful Basis", "Breach Protocol"],
        "Your Score": [85, 90, 75, 65, 70],
        "Industry Average": [72, 68, 80, 60, 65]
    }
    
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    
    st.bar_chart(df.set_index("Categories").transpose())
    
    st.download_button(
        label="Download Full Report",
        data="This would be a PDF report in the real application",
        file_name="policy_analysis_report.pdf",
    )

st.markdown("---")
st.markdown("## How PolicyEdgeAI Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1. Document Processing")
    st.markdown("We extract and structure the content of your policy documents using advanced NLP techniques.")

with col2:
    st.markdown("### 2. Regulatory Analysis")
    st.markdown("Our AI compares your policy against requirements from GDPR, CCPA, HIPAA and other frameworks.")

with col3:
    st.markdown("### 3. Actionable Insights")
    st.markdown("You receive detailed reports with specific improvements to enhance compliance and clarity.")

st.markdown("---")
st.markdown("© 2025 PolicyEdgeAI. All rights reserved.")
