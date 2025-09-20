import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PolicyEdgeAI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for user data
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "policies" not in st.session_state:
    st.session_state.policies = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# Custom CSS for better UI
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
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
        margin: 1rem 0;
        background-color: #F9FAFB;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 0.5rem;
        border-radius: 0.25rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6B7280;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=PolicyEdgeAI", width=200)
    st.markdown("### Navigate")
    
    # Different sidebar options based on authentication
    if not st.session_state.user_authenticated:
        navigation = st.radio("", ["Home", "Login", "Register", "About Us"])
    else:
        st.write(f"Welcome, {st.session_state.current_user}")
        navigation = st.radio("", ["Dashboard", "Upload Policy", "Analysis", "Settings", "Logout"])
    
    st.markdown("---")
    st.markdown("### Resources")
    st.markdown("- [Documentation]()")
    st.markdown("- [API Reference]()")
    st.markdown("- [Support]()")

# Mock Functions (replace with actual API calls)
def login_user(email, password):
    # Mock successful login
    st.session_state.user_authenticated = True
    st.session_state.current_user = email.split('@')[0]
    return True

def register_user(name, email, password):
    # Mock successful registration
    return True

def upload_policy(file_content, policy_name, policy_type):
    # Mock policy upload
    new_policy = {
        "id": len(st.session_state.policies) + 1,
        "name": policy_name,
        "type": policy_type,
        "status": "Uploaded",
        "date": "2025-04-02"
    }
    st.session_state.policies.append(new_policy)
    return True

def analyze_policy(policy_id, analysis_type):
    # Mock analysis results
    return {
        "policy_id": policy_id,
        "summary": "This policy outlines the data protection measures, user rights, and company responsibilities.",
        "compliance": {
            "GDPR": "87% compliant",
            "CCPA": "92% compliant",
            "HIPAA": "Not applicable"
        },
        "readability": "Grade 12 - College level",
        "insights": [
            "Consider simplifying language in Section 3.2",
            "Missing clear data retention guidelines",
            "Strong on consent mechanisms"
        ]
    }

# Page Content Based on Navigation
if navigation == "Home":
    st.markdown('<h1 class="main-header">PolicyEdgeAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered policy analysis for modern organizations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Transform Policy Analysis with AI
        
        PolicyEdgeAI uses cutting-edge artificial intelligence to help organizations:
        
        - **Analyze** complex policy documents in seconds
        - **Assess** compliance with regulations like GDPR, CCPA, HIPAA
        - **Improve** policy language clarity and readability
        - **Compare** policies against industry benchmarks
        - **Generate** actionable insights and recommendations
        """)
        
        st.button("Start Free Trial")
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=PolicyEdgeAI+Demo", use_column_width=True)
    
    st.markdown("---")
    
    st.markdown('<h2 class="sub-header">How it works</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 1. Upload Policies")
        st.markdown("Upload your policy documents in various formats (PDF, DOCX, TXT)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 2. AI Analysis")
        st.markdown("Our AI engine analyzes the content for compliance, clarity, and completeness")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 3. Actionable Insights")
        st.markdown("Receive detailed reports with concrete recommendations")
        st.markdown('</div>', unsafe_allow_html=True)

elif navigation == "Login":
    st.markdown('<h1 class="main-header">Login</h1>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if email and password:
                if login_user(email, password):
                    st.success("Login successful\!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.warning("Please enter both email and password")

elif navigation == "Register":
    st.markdown('<h1 class="main-header">Register</h1>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        submit = st.form_submit_button("Register")
        
        if submit:
            if not all([name, email, password, confirm_password]):
                st.warning("Please fill out all fields")
            elif password \!= confirm_password:
                st.error("Passwords do not match")
            elif not terms:
                st.warning("You must agree to the Terms of Service and Privacy Policy")
            else:
                if register_user(name, email, password):
                    st.success("Registration successful\! Please login.")
                else:
                    st.error("Registration failed. Please try again.")

elif navigation == "About Us":
    st.markdown('<h1 class="main-header">About PolicyEdgeAI</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Our Mission
    
    PolicyEdgeAI was created to streamline policy management and compliance for organizations of all sizes. Our mission is to make policy analysis accessible, efficient, and actionable through advanced AI.
    
    ### Our Team
    
    Our team consists of experts in:
    - Artificial Intelligence and Natural Language Processing
    - Legal and Regulatory Compliance
    - User Experience Design
    - Software Engineering
    
    ### Our Technology
    
    PolicyEdgeAI combines:
    - State-of-the-art Large Language Models
    - Domain-specific training for policy analysis
    - Continuous learning from user feedback
    - Rigorous privacy and security standards
    """)

elif navigation == "Dashboard" and st.session_state.user_authenticated:
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Policies Uploaded", len(st.session_state.policies))
    with col2:
        st.metric("Analyses Performed", len(st.session_state.policies) // 2)
    with col3:
        st.metric("Compliance Score", "85%")
    
    st.markdown("---")
    
    st.markdown('<h2 class="sub-header">Recent Policies</h2>', unsafe_allow_html=True)
    
    if not st.session_state.policies:
        st.info("No policies uploaded yet. Go to 'Upload Policy' to get started.")
    else:
        for policy in st.session_state.policies[-3:]:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{policy['name']}**")
            with col2:
                st.write(policy['type'])
            with col3:
                st.write(policy['date'])
            with col4:
                if st.button("Analyze", key=f"analyze_{policy['id']}"):
                    st.session_state.analysis_results = analyze_policy(policy['id'], "standard")
                    navigation = "Analysis"
                    st.experimental_rerun()

elif navigation == "Upload Policy" and st.session_state.user_authenticated:
    st.markdown('<h1 class="main-header">Upload Policy</h1>', unsafe_allow_html=True)
    
    with st.form("upload_form"):
        policy_name = st.text_input("Policy Name")
        policy_type = st.selectbox("Policy Type", ["Privacy Policy", "Terms of Service", "Cookie Policy", "EULA", "Other"])
        
        file_upload = st.file_uploader("Upload Policy File", type=["pdf", "docx", "txt"])
        
        additional_notes = st.text_area("Additional Notes (optional)")
        
        submit = st.form_submit_button("Upload Policy")
        
        if submit:
            if not policy_name:
                st.warning("Please enter a policy name")
            elif not file_upload:
                st.warning("Please upload a policy file")
            else:
                file_content = file_upload.read()
                if upload_policy(file_content, policy_name, policy_type):
                    st.success(f"Policy '{policy_name}' uploaded successfully\!")
                else:
                    st.error("Failed to upload policy. Please try again.")

elif navigation == "Analysis" and st.session_state.user_authenticated:
    st.markdown('<h1 class="main-header">Analysis Results</h1>', unsafe_allow_html=True)
    
    if not st.session_state.policies:
        st.info("No policies to analyze. Please upload a policy first.")
    elif st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Summary")
        st.write(results["summary"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Compliance Assessment")
            for regulation, score in results["compliance"].items():
                st.write(f"**{regulation}**: {score}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Readability")
            st.write(f"**Score**: {results['readability']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Key Insights")
        for insight in results["insights"]:
            st.markdown(f"- {insight}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.download_button("Download PDF Report", "Report content", "report.pdf")
        with col2:
            st.button("Share Results")
    else:
        # Policy selection for analysis
        st.markdown("### Select a Policy to Analyze")
        
        policy_id = st.selectbox("Choose Policy", 
                             options=[p["id"] for p in st.session_state.policies],
                             format_func=lambda x: next((p["name"] for p in st.session_state.policies if p["id"] == x), ""))
        
        analysis_type = st.radio("Analysis Type", ["Standard", "Advanced", "Compliance Focus"])
        
        if st.button("Start Analysis"):
            st.session_state.analysis_results = analyze_policy(policy_id, analysis_type.lower())
            st.experimental_rerun()

elif navigation == "Settings" and st.session_state.user_authenticated:
    st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Account", "API Keys", "Notifications"])
    
    with tab1:
        st.markdown("### Account Settings")
        
        with st.form("account_settings"):
            name = st.text_input("Name", value=st.session_state.current_user)
            email = st.text_input("Email", value=f"{st.session_state.current_user}@example.com")
            company = st.text_input("Company")
            
            st.markdown("### Change Password")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            save = st.form_submit_button("Save Changes")
            
            if save:
                st.success("Account settings updated successfully\!")
    
    with tab2:
        st.markdown("### API Keys")
        
        st.markdown("Connect your AI service providers:")
        
        openai_key = st.text_input("OpenAI API Key", type="password", value="sk-...")
        anthropic_key = st.text_input("Anthropic API Key", type="password", value="sk-ant-...")
        
        if st.button("Save API Keys"):
            st.success("API keys updated successfully\!")
    
    with tab3:
        st.markdown("### Notification Preferences")
        
        st.checkbox("Email notifications for completed analyses", value=True)
        st.checkbox("Weekly summary reports", value=True)
        st.checkbox("Product updates and new features", value=False)
        
        if st.button("Update Preferences"):
            st.success("Notification preferences updated successfully\!")

elif navigation == "Logout" and st.session_state.user_authenticated:
    st.session_state.user_authenticated = False
    st.session_state.current_user = None
    st.experimental_rerun()

# Footer
st.markdown('<div class="footer">© 2025 PolicyEdgeAI. All rights reserved.</div>', unsafe_allow_html=True)
