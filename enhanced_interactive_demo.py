import streamlit as st
import time
import random

st.set_page_config(
    page_title="PolicyEdgeAI Interactive Demo",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state variables
if 'uploaded_policy' not in st.session_state:
    st.session_state.uploaded_policy = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'sample_policies' not in st.session_state:
    st.session_state.sample_policies = [
        {"name": "Privacy Policy", "type": "Privacy", "date": "2025-03-15"},
        {"name": "Terms of Service", "type": "Terms", "date": "2025-02-28"},
        {"name": "Cookie Policy", "type": "Cookies", "date": "2025-01-10"}
    ]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Navigation function
def navigate_to(page):
    st.session_state.current_page = page
    st.experimental_rerun()

# Custom CSS
st.markdown("""
<style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .subtitle {
        font-size: 24px;
        color: #3B82F6;
    }
    .btn-primary {
        background-color: #3B82F6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: bold;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        border: none;
        cursor: pointer;
    }
    .card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #F0F9FF;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        margin-bottom: 15px;
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
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80?text=PolicyEdgeAI", width=200)
    st.markdown("### Menu")
    
    if st.session_state.logged_in:
        page = st.radio("", ["Dashboard", "Upload Policy", "Analyze Policy", "Reports", "Settings", "Logout"], key="nav_radio")
        if page \!= st.session_state.current_page:
            st.session_state.current_page = page
            st.experimental_rerun()
    else:
        page = st.radio("", ["Home", "Login", "Register", "Samples"], key="nav_radio")
        if page \!= st.session_state.current_page:
            st.session_state.current_page = page
            st.experimental_rerun()
    
    st.markdown("---")
    
    # Demo account shortcut
    if not st.session_state.logged_in:
        if st.button("➡️ One-Click Demo Login", type="primary"):
            st.session_state.logged_in = True
            st.session_state.username = "Demo User"
            st.session_state.current_page = "Dashboard"
            st.experimental_rerun()
        st.markdown("---")
    
    st.markdown("### Quick Links")
    st.markdown("- [Documentation](#)")
    st.markdown("- [API Reference](#)")
    st.markdown("- [Pricing](#)")
    st.markdown("- [Support](#)")

# Login functionality
def login(username, password):
    # Simple demo login - in a real app you'd check against a database
    if username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

# Generate mock analysis results
def analyze_policy(policy_content, policy_type):
    # Simulate processing delay
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.02)  # Simulate processing time
        progress_bar.progress(i + 1)
    
    # Return mock results based on policy type
    if policy_type == "Privacy":
        return {
            "compliance": {
                "GDPR": random.randint(75, 95),
                "CCPA": random.randint(70, 90),
                "HIPAA": random.randint(50, 85)
            },
            "readability": {
                "grade_level": random.randint(10, 14),
                "clarity_score": random.randint(65, 85)
            },
            "issues": [
                "Data retention periods not clearly specified",
                "Missing details on international data transfers",
                "Vague description of third-party sharing",
                "Unclear consent mechanisms for cookies"
            ],
            "recommendations": [
                "Add specific retention periods for each data category",
                "Include details on data transfer safeguards",
                "List specific third parties with whom data is shared",
                "Clarify how users can withdraw consent"
            ]
        }
    elif policy_type == "Terms":
        return {
            "compliance": {
                "E-Commerce Regulations": random.randint(75, 95),
                "Consumer Protection": random.randint(70, 90),
                "Digital Services": random.randint(65, 85)
            },
            "readability": {
                "grade_level": random.randint(12, 16),
                "clarity_score": random.randint(60, 80)
            },
            "issues": [
                "Liability limitations may be too broad",
                "Dispute resolution process not clearly defined",
                "Missing information on service modifications",
                "Jurisdiction and governing law section needs clarity"
            ],
            "recommendations": [
                "Specify liability limits with more precision",
                "Add step-by-step dispute resolution process",
                "Include notice period for service changes",
                "Clarify which laws govern the agreement"
            ]
        }
    else:
        return {
            "compliance": {
                "General Compliance": random.randint(70, 90),
                "Best Practices": random.randint(65, 85)
            },
            "readability": {
                "grade_level": random.randint(9, 14),
                "clarity_score": random.randint(70, 90)
            },
            "issues": [
                "Some sections use overly complex language",
                "Structure could be improved for readability",
                "Missing references to related policies"
            ],
            "recommendations": [
                "Simplify language in technical sections",
                "Add headings and subheadings for better structure",
                "Include links to related policy documents"
            ]
        }

# Page Content - based on the current page
page = st.session_state.current_page

if page == "Home":
    st.markdown('<div class="title">PolicyEdgeAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-powered policy document analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Transform Policy Analysis with AI
        
        PolicyEdgeAI helps organizations:
        
        - **Analyze** complex policy documents in seconds
        - **Check** compliance with GDPR, CCPA, and other regulations
        - **Improve** readability and clarity
        - **Compare** against industry benchmarks
        - **Generate** actionable recommendations
        
        Our platform uses advanced AI to scan your policies and provide insights that would take legal teams days to produce.
        """)
        
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("Try Demo (No Login)", type="primary", key="home_demo_btn"):
                st.session_state.logged_in = True
                st.session_state.username = "Demo User"
                st.session_state.current_page = "Analyze Policy"
                st.experimental_rerun()
        with col1b:
            if st.button("See Sample Analysis", key="sample_analysis_btn"):
                st.session_state.current_page = "Samples"
                st.experimental_rerun()
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=PolicyEdgeAI+Demo", use_column_width=True)
    
    st.markdown("---")
    
    st.markdown('<div class="subtitle">How It Works</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 1. Upload")
        st.markdown("""
        - Upload your policy document
        - Supported formats: PDF, DOCX, TXT
        - Secure and confidential processing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 2. Analyze")
        st.markdown("""
        - AI scans for compliance issues
        - Regulatory requirements checked
        - Readability and clarity assessed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 3. Improve")
        st.markdown("""
        - Detailed recommendations
        - Specific improvement suggestions
        - Compliance gap identification
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Customer testimonials
    st.markdown("### What Our Customers Say")
    
    testimonials = st.columns(3)
    
    with testimonials[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        "PolicyEdgeAI saved our legal team weeks of work reviewing our privacy policies for GDPR compliance."
        
        **- Sarah J., Legal Counsel at TechCorp**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with testimonials[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        "The readability analysis helped us simplify our terms of service, reducing customer support inquiries by 40%."
        
        **- Mark T., Product Manager at CloudSolutions**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with testimonials[2]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        "We identified critical compliance gaps in our policies that would have caused regulatory issues down the road."
        
        **- Jennifer L., Data Protection Officer at HealthTech**
        """)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Login":
    st.markdown('<div class="title">Login</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("login_form"):
            username = st.text_input("Email or Username")
            password = st.text_input("Password", type="password")
            
            col1a, col1b = st.columns([1, 1])
            with col1a:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if login(username, password):
                    st.success("Login successful\!")
                    st.session_state.current_page = "Dashboard"
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials. For this demo, enter any non-empty username and password.")
        
        st.markdown("Don't have an account? [Register](#Register)")
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Quick Demo Access")
        st.markdown("""
        Experience PolicyEdgeAI without signing up:
        """)
        if st.button("Access Demo Account", type="primary", use_container_width=True):
            login("demo_user", "password")
            st.session_state.current_page = "Dashboard"
            st.experimental_rerun()
        
        st.markdown("---")
        
        st.markdown("### Enterprise Single Sign-On")
        st.markdown("We support:")
        st.markdown("- Google Workspace")
        st.markdown("- Microsoft 365")
        st.markdown("- Okta")
        st.markdown("- SAML 2.0")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Register":
    st.markdown('<div class="title">Create an Account</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.form("register_form"):
            col1a, col1b = st.columns(2)
            
            with col1a:
                first_name = st.text_input("First Name")
            
            with col1b:
                last_name = st.text_input("Last Name")
            
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            company = st.text_input("Company Name (optional)")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            marketing = st.checkbox("Keep me updated with product news and offers")
            
            submit = st.form_submit_button("Create Account")
            
            if submit:
                if not all([first_name, last_name, email, password, confirm_password]):
                    st.error("Please fill out all required fields.")
                elif password \!= confirm_password:
                    st.error("Passwords do not match.")
                elif not agree_terms:
                    st.warning("You must agree to the Terms of Service and Privacy Policy.")
                else:
                    st.success("Account created successfully\! You can now log in.")
                    # In a real app, you would save the user data to a database here
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Why Register?")
        st.markdown("""
        - Full access to all PolicyEdgeAI features
        - Save and track policy analyses over time
        - Compliance monitoring and alerts
        - Export detailed reports
        - Team collaboration tools
        """)
        
        st.markdown("### Already have an account?")
        
        if st.button("Login Instead", use_container_width=True):
            st.session_state.current_page = "Login"
            st.experimental_rerun()
        
        st.markdown("### Try without registering")
        
        if st.button("Use Demo Account", type="primary", use_container_width=True):
            login("demo_user", "password")
            st.session_state.current_page = "Dashboard"
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Dashboard" and st.session_state.logged_in:
    st.markdown('<div class="title">Dashboard</div>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown(f"### Welcome, {st.session_state.username}\!")
    st.markdown("Here's an overview of your policy analysis status.")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Policies", len(st.session_state.sample_policies))
    
    with col2:
        st.metric("Avg. Compliance", "83%")
    
    with col3:
        st.metric("Issues Found", "12")
    
    with col4:
        st.metric("Improvements Made", "8")
    
    # Recent policies
    st.markdown("### Recent Policies")
    
    for policy in st.session_state.sample_policies:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**{policy['name']}**")
        
        with col2:
            st.write(policy['type'])
        
        with col3:
            st.write(policy['date'])
        
        with col4:
            if st.button("Analyze", key=f"view_{policy['name']}"):
                st.session_state.selected_policy = policy
                st.session_state.current_page = "Analyze Policy"
                st.experimental_rerun()
    
    # Add policy button
    if st.button("+ Upload New Policy", type="primary", key="dash_add_policy"):
        st.session_state.current_page = "Upload Policy"
        st.experimental_rerun()
    
    st.markdown("---")
    
    # Activity and compliance summary
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Compliance Status")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Regulatory Compliance")
        
        regulations = {
            "GDPR": {"score": 85, "trend": "↑"},
            "CCPA": {"score": 92, "trend": "↑"},
            "HIPAA": {"score": 73, "trend": "→"},
            "CPRA": {"score": 78, "trend": "↑"}
        }
        
        for reg, data in regulations.items():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"**{reg}**")
                st.progress(data["score"]/100)
            with col_b:
                st.markdown(f"**{data['score']}%**")
            with col_c:
                trend_color = "green" if data["trend"] == "↑" else "orange" if data["trend"] == "→" else "red"
                st.markdown(f"<span style='color:{trend_color}'>{data['trend']}</span>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Recent Activity")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        activity = [
            {"action": "Policy Analyzed", "item": "Privacy Policy", "date": "Today"},
            {"action": "New Policy Added", "item": "EULA", "date": "Yesterday"},
            {"action": "Compliance Alert", "item": "GDPR Update", "date": "3 days ago"},
            {"action": "Policy Improved", "item": "Terms of Service", "date": "Last week"},
            {"action": "Report Generated", "item": "Quarterly Compliance", "date": "Last week"}
        ]
        
        for item in activity:
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"**{item['action']}**")
            
            with col2:
                st.write(item['item'])
            
            with col3:
                st.write(item['date'])
        
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Upload Policy" and st.session_state.logged_in:
    st.markdown('<div class="title">Upload Policy</div>', unsafe_allow_html=True)
    
    # Form to upload policy
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("policy_upload_form"):
            policy_name = st.text_input("Policy Name")
            policy_type = st.selectbox("Policy Type", ["Privacy Policy", "Terms of Service", "Cookie Policy", "EULA", "Other"])
            
            uploaded_file = st.file_uploader("Upload Policy Document", type=["pdf", "docx", "txt"])
            
            description = st.text_area("Description (optional)")
            
            submit = st.form_submit_button("Upload Policy")
            
            if submit:
                if not policy_name:
                    st.error("Please enter a policy name.")
                elif not uploaded_file:
                    st.error("Please upload a policy document.")
                else:
                    # In a real app, you would save the file to storage
                    st.success(f"'{policy_name}' uploaded successfully\!")
                    
                    # Add to sample policies
                    policy_type_short = policy_type.split()[0]
                    st.session_state.sample_policies.append({
                        "name": policy_name,
                        "type": policy_type_short,
                        "date": "Today"
                    })
                    
                    # Set flag for successful upload
                    st.session_state.uploaded_policy = True
                    st.session_state.current_policy = {
                        "name": policy_name,
                        "type": policy_type_short
                    }
                    
                    # Option to analyze
                    if st.button("Analyze Now"):
                        st.session_state.current_page = "Analyze Policy"
                        st.experimental_rerun()
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Supported Formats")
        st.markdown("""
        - PDF documents
        - Word documents (.docx)
        - Plain text (.txt)
        
        Files should be under 10MB.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Tips")
        st.markdown("""
        - Upload the most recent version
        - Ensure document is not password protected
        - Include the full policy, not excerpts
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sample policy option
    st.markdown("### No policy to upload?")
    
    if st.button("Use Sample Policy"):
        st.session_state.uploaded_policy = True
        st.session_state.current_policy = {
            "name": "Sample Privacy Policy",
            "type": "Privacy"
        }
        st.success("Sample policy loaded\!")
        
        if st.button("Analyze Sample"):
            st.session_state.current_page = "Analyze Policy"
            st.experimental_rerun()

elif page == "Analyze Policy" and st.session_state.logged_in:
    st.markdown('<div class="title">Policy Analysis</div>', unsafe_allow_html=True)
    
    # If no analysis has been run yet
    if not st.session_state.analysis_results:
        # Policy selection
        if not hasattr(st.session_state, 'current_policy'):
            st.markdown("### Select a Policy to Analyze")
            
            policies = st.session_state.sample_policies
            policy_names = [p["name"] for p in policies]
            
            selected_policy = st.selectbox("Choose Policy", policy_names)
            policy_type = next((p["type"] for p in policies if p["name"] == selected_policy), "Privacy")
            
            analysis_type = st.radio("Analysis Type", ["Standard", "Comprehensive", "Compliance Focus"])
            
            if st.button("Start Analysis", type="primary"):
                with st.spinner("Analyzing policy..."):
                    # Use the selected policy for analysis
                    analysis_results = analyze_policy("Sample content", policy_type)
                    st.session_state.analysis_results = analysis_results
                    st.session_state.analyzed_policy = selected_policy
                st.experimental_rerun()
        else:
            # We have a current policy from upload or sample
            st.markdown(f"### Analyze: {st.session_state.current_policy['name']}")
            
            analysis_type = st.radio("Analysis Type", ["Standard", "Comprehensive", "Compliance Focus"])
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                if st.button("Start Analysis", type="primary", use_container_width=True):
                    with st.spinner("Analyzing policy..."):
                        # Use the current policy for analysis
                        analysis_results = analyze_policy("Sample content", st.session_state.current_policy["type"])
                        st.session_state.analysis_results = analysis_results
                        st.session_state.analyzed_policy = st.session_state.current_policy["name"]
                    st.experimental_rerun()
                    
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"Selected policy: **{st.session_state.current_policy['name']}**")
                st.markdown(f"Type: **{st.session_state.current_policy['type']}**")
                st.markdown(f"Analysis type: **{analysis_type}**")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display analysis results
        st.markdown(f"### Analysis Results: {st.session_state.analyzed_policy}")
        
        # Compliance scores
        st.markdown("#### Compliance Scores")
        
        col_layout = []
        compliance_scores = st.session_state.analysis_results["compliance"]
        for _ in range(len(compliance_scores)):
            col_layout.append(1)
        
        cols = st.columns(col_layout)
        
        i = 0
        for regulation, score in compliance_scores.items():
            with cols[i]:
                st.metric(label=regulation, value=f"{score}%")
                # Color-coded progress bar
                if score >= 90:
                    color = "green"
                elif score >= 75:
                    color = "blue" 
                elif score >= 60:
                    color = "orange"
                else:
                    color = "red"
                
                st.markdown(f"<div style='width:100%;background-color:#ddd;height:10px;border-radius:5px'><div style='width:{score}%;background-color:{color};height:10px;border-radius:5px'></div></div>", unsafe_allow_html=True)
            i += 1
        
        # Readability metrics
        st.markdown("#### Readability")
        
        col1, col2 = st.columns(2)
        
        with col1:
            grade_level = st.session_state.analysis_results["readability"]["grade_level"]
            st.metric("Grade Level", f"{grade_level}th")
            
            if grade_level > 12:
                st.warning("Your policy may be too complex for the average reader.")
            else:
                st.success("Your policy's reading level is appropriate for most users.")
        
        with col2:
            clarity = st.session_state.analysis_results["readability"]["clarity_score"]
            st.metric("Clarity Score", f"{clarity}%")
            
            if clarity < 70:
                st.warning("Consider improving clarity with simpler language and structure.")
            else:
                st.success("Your policy is clearly written and well-structured.")
        
        # Issues and recommendations
        tab1, tab2 = st.tabs(["Issues Identified", "Recommendations"])
        
        with tab1:
            for i, issue in enumerate(st.session_state.analysis_results["issues"]):
                severity = "high" if i < 2 else "medium" if i < 3 else "low"
                color = "red" if severity == "high" else "orange" if severity == "medium" else "blue"
                severity_label = "⚠️ High Priority" if severity == "high" else "⚠️ Medium Priority" if severity == "medium" else "ℹ️ Low Priority"
                
                st.markdown(f"<div style='padding:10px; margin-bottom:10px; border-left:4px solid {color}; background-color:#f8f9fa;'><span style='color:{color};font-weight:bold;'>{severity_label}</span><br/>{issue}</div>", unsafe_allow_html=True)
        
        with tab2:
            for i, rec in enumerate(st.session_state.analysis_results["recommendations"]):
                st.markdown(f"**{i+1}. {rec}**")
                
                # Create mock examples for recommendations
                if "specific retention periods" in rec:
                    st.markdown("""
                    **Example Improvement:**
                    ```
                    We retain different types of data for different periods:
                    - Contact information: 3 years after account closure
                    - Usage data: 12 months from collection
                    - Payment information: 7 years (as required by tax laws)
                    ```
                    """)
                elif "international data transfer" in rec:
                    st.markdown("""
                    **Example Improvement:**
                    ```
                    When we transfer personal data outside the EU/EEA, we rely on:
                    - Standard Contractual Clauses approved by the European Commission
                    - Additional safeguards including encryption and access controls
                    ```
                    """)
                elif "third parties" in rec:
                    st.markdown("""
                    **Example Improvement:**
                    ```
                    We share your data with the following categories of third parties:
                    - Payment processors (e.g., Stripe, PayPal)
                    - Analytics providers (e.g., Google Analytics)
                    - Cloud service providers (e.g., AWS, Microsoft Azure)
                    ```
                    """)
        
        # Actions
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Download PDF Report", type="primary", use_container_width=True):
                st.success("Report would be downloaded in the real application.")
        
        with col2:
            if st.button("Save Analysis", use_container_width=True):
                st.success("Analysis saved successfully.")
        
        with col3:
            if st.button("New Analysis", use_container_width=True):
                st.session_state.analysis_results = None
                st.experimental_rerun()

elif page == "Reports" and st.session_state.logged_in:
    st.markdown('<div class="title">Reports</div>', unsafe_allow_html=True)
    
    report_types = ["Compliance Summary", "Detailed Analysis", "Comparison Report"]
    selected_report = st.selectbox("Report Type", report_types)
    
    if selected_report == "Compliance Summary":
        st.markdown("### Compliance Summary Report")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            policy_filter = st.multiselect("Policies", [p["name"] for p in st.session_state.sample_policies], default=[p["name"] for p in st.session_state.sample_policies])
        
        with col2:
            regulation_filter = st.multiselect("Regulations", ["GDPR", "CCPA", "HIPAA", "E-Commerce"], default=["GDPR", "CCPA"])
        
        with col3:
            date_range = st.date_input("Date Range", value=[])
        
        # Generate report button
        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                time.sleep(1)  # Simulate processing
            
            # Show mock report
            st.success("Report generated successfully\!")
            
            st.markdown("#### Overall Compliance Scores")
            
            # Mock data for the report
            report_data = {
                "Privacy Policy": {"GDPR": 87, "CCPA": 92},
                "Terms of Service": {"GDPR": 75, "CCPA": 80},
                "Cookie Policy": {"GDPR": 95, "CCPA": 88}
            }
            
            # Filter to selected policies
            filtered_data = {k: v for k, v in report_data.items() if k in policy_filter}
            
            # Create a table
            st.markdown("| Policy | " + " | ".join(regulation_filter) + " |")
            st.markdown("|--------|" + "|".join(["---" for _ in regulation_filter]) + "|")
            
            for policy, scores in filtered_data.items():
                row = [policy]
                for reg in regulation_filter:
                    if reg in scores:
                        row.append(f"{scores[reg]}%")
                    else:
                        row.append("N/A")
                st.markdown("|" + "|".join(row) + "|")
            
            # Average scores
            st.markdown("#### Average Scores by Regulation")
            
            for reg in regulation_filter:
                scores = [scores[reg] for policy, scores in filtered_data.items() if reg in scores]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    st.metric(f"Average {reg} Compliance", f"{avg_score:.1f}%")
            
            # Download option
            st.download_button("Download Report", "Report content would go here", "compliance_report.pdf", "application/pdf")
    
    elif selected_report == "Detailed Analysis":
        st.markdown("### Detailed Analysis Report")
        
        # Policy selection
        selected_policy = st.selectbox("Select Policy", [p["name"] for p in st.session_state.sample_policies])
        
        # Generate button
        if st.button("Generate Report"):
            with st.spinner("Generating detailed analysis..."):
                time.sleep(1.5)  # Simulate processing
            
            st.success("Detailed analysis complete\!")
            
            # Mock detailed report
            st.markdown(f"#### Detailed Analysis: {selected_policy}")
            
            tab1, tab2, tab3 = st.tabs(["Compliance", "Readability", "Recommendations"])
            
            with tab1:
                st.markdown("##### Compliance Analysis")
                
                st.markdown("""
                | Section | Requirement | Status | Notes |
                |---------|-------------|--------|-------|
                | Data Collection | Clear description of data collected | ✅ Compliant | Well-documented list of data types |
                | Purpose | Explain why data is collected | ✅ Compliant | Purposes clearly linked to data types |
                | Sharing | List of third parties | ⚠️ Partial | Third parties mentioned but not specified |
                | Retention | Data retention periods | ❌ Missing | No specific retention periods mentioned |
                | Legal Basis | Basis for processing | ⚠️ Partial | Mentioned but not for all processing activities |
                | User Rights | Description of rights | ✅ Compliant | Comprehensive rights explanation |
                """)
            
            with tab2:
                st.markdown("##### Readability Analysis")
                
                st.markdown("""
                | Metric | Score | Industry Average | Status |
                |--------|-------|------------------|--------|
                | Flesch Reading Ease | 42.3 | 38.5 | ✅ Above Average |
                | Grade Level | 11.2 | 12.8 | ✅ Better than Average |
                | Average Sentence Length | 18.4 words | 22.1 words | ✅ Better than Average |
                | Complex Word Percentage | 21.5% | 18.9% | ⚠️ Slightly Worse |
                | Passive Voice Usage | 15.3% | 12.7% | ⚠️ Slightly Worse |
                """)
                
                st.markdown("**Most Complex Sections:**")
                st.markdown("1. Data Processing Activities (Grade 14.3)")
                st.markdown("2. International Transfers (Grade 13.8)")
                st.markdown("3. Legal Bases for Processing (Grade 13.2)")
            
            with tab3:
                st.markdown("##### Recommendations")
                
                st.markdown("""
                **High Priority:**
                1. Add specific retention periods for each category of data
                2. List specific third parties or categories that receive data
                3. Simplify the Data Processing Activities section
                
                **Medium Priority:**
                1. Reduce passive voice usage throughout
                2. Add examples to clarify technical concepts
                3. Improve structure with more subheadings
                
                **Low Priority:**
                1. Add a glossary of terms
                2. Include visual elements to improve comprehension
                3. Add links to related policies
                """)
            
            # Download option
            st.download_button("Download Full Analysis", "Detailed analysis would go here", "detailed_analysis.pdf", "application/pdf")
    
    else:  # Comparison Report
        st.markdown("### Comparison Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            policy1 = st.selectbox("First Policy", [p["name"] for p in st.session_state.sample_policies])
        
        with col2:
            remaining_policies = [p["name"] for p in st.session_state.sample_policies if p["name"] \!= policy1]
            policy2 = st.selectbox("Second Policy", remaining_policies)
        
        # Generate button
        if st.button("Generate Comparison"):
            with st.spinner("Comparing policies..."):
                time.sleep(1.3)  # Simulate processing
            
            st.success("Comparison complete\!")
            
            # Mock comparison data
            comparison_data = {
                "Overall Compliance": {"Privacy Policy": 85, "Terms of Service": 78},
                "GDPR Compliance": {"Privacy Policy": 87, "Terms of Service": 75},
                "CCPA Compliance": {"Privacy Policy": 92, "Terms of Service": 80},
                "Readability": {"Privacy Policy": 79, "Terms of Service": 68},
                "Comprehensiveness": {"Privacy Policy": 90, "Terms of Service": 85},
            }
            
            # Update with selected policies
            comparison_data = {k: {policy1: v["Privacy Policy"], policy2: v["Terms of Service"]} for k, v in comparison_data.items()}
            
            # Display comparison
            st.markdown(f"#### Comparing: {policy1} vs {policy2}")
            
            # Create metrics for each comparison point
            for metric, values in comparison_data.items():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(f"{policy1} - {metric}", f"{values[policy1]}%")
                
                with col2:
                    st.metric(f"{policy2} - {metric}", f"{values[policy2]}%")
                
                # Visual difference
                diff = values[policy1] - values[policy2]
                bar_width = abs(diff) / 2  # Scale for display
                
                if diff > 0:
                    st.markdown(f"<div style='display:flex;'><div style='flex:1;text-align:right;'><div style='display:inline-block;width:{bar_width}%;background-color:#3B82F6;height:5px;'></div></div><div style='flex:1;'></div></div>", unsafe_allow_html=True)
                elif diff < 0:
                    st.markdown(f"<div style='display:flex;'><div style='flex:1;'></div><div style='flex:1;'><div style='display:inline-block;width:{bar_width}%;background-color:#3B82F6;height:5px;'></div></div></div>", unsafe_allow_html=True)
                
                st.markdown("---")
            
            # Key differences
            st.markdown("#### Key Differences")
            
            st.markdown("""
            **Content Coverage:**
            - Privacy Policy includes more details on data collection methods
            - Terms of Service has stronger liability clauses
            
            **Compliance Focus:**
            - Privacy Policy has better GDPR & CCPA compliance
            - Terms of Service focuses more on contractual protections
            
            **Writing Style:**
            - Privacy Policy uses simpler language (Grade 11.2 vs Grade 13.5)
            - Terms of Service has more legal terminology
            """)
            
            # Download option
            st.download_button("Download Comparison", "Comparison report would go here", "comparison_report.pdf", "application/pdf")

elif page == "Settings" and st.session_state.logged_in:
    st.markdown('<div class="title">Settings</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Account", "API Keys", "Notifications", "Team"])
    
    with tabs[0]:  # Account
        st.markdown("### Account Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Name", value="Demo User")
            st.text_input("Email", value="demo@example.com")
        
        with col2:
            st.text_input("Company", value="Demo Company")
            st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Education", "Other"])
        
        st.markdown("### Change Password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Current Password", type="password")
        
        with col2:
            st.text_input("New Password", type="password")
        
        if st.button("Save Account Settings"):
            st.success("Account settings updated successfully\!")
    
    with tabs[1]:  # API Keys
        st.markdown("### API Keys")
        
        st.markdown("""
        Connect your own AI service providers to enhance analysis capabilities:
        """)
        
        st.text_input("OpenAI API Key", type="password", value="sk-...")
        st.text_input("Anthropic API Key", type="password", value="sk-ant-...")
        
        if st.button("Save API Keys"):
            st.success("API keys updated successfully\!")
            
        st.markdown("---")
        
        st.markdown("### PolicyEdgeAI API")
        st.markdown("Access your PolicyEdgeAI data programmatically:")
        
        st.code("YOUR_API_KEY = pc_01234567890abcdef", language="python")
        
        st.markdown("**Permissions:**")
        permissions = [
            ("Read Policies", True),
            ("Read Analysis Results", True),
            ("Create Policies", False),
            ("Run Analysis", False)
        ]
        
        for perm, enabled in permissions:
            st.checkbox(perm, value=enabled, disabled=True)
            
        if st.button("Regenerate API Key"):
            st.info("This would regenerate your API key in the real application.")
    
    with tabs[2]:  # Notifications
        st.markdown("### Notification Settings")
        
        st.checkbox("Email notifications for completed analyses", value=True)
        st.checkbox("Weekly summary reports", value=True)
        st.checkbox("Compliance alerts", value=True)
        st.checkbox("Product updates and new features", value=False)
        
        st.markdown("### Notification Schedule")
        st.radio("Summary Report Frequency", ["Daily", "Weekly", "Monthly"])
        
        if st.button("Save Notification Settings"):
            st.success("Notification settings updated successfully\!")
    
    with tabs[3]:  # Team
        st.markdown("### Team Members")
        
        team_members = [
            {"name": "Demo User", "email": "demo@example.com", "role": "Admin"},
            {"name": "John Smith", "email": "john@example.com", "role": "Editor"},
            {"name": "Jane Doe", "email": "jane@example.com", "role": "Viewer"}
        ]
        
        for member in team_members:
            col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
            
            with col1:
                st.write(member["name"])
            
            with col2:
                st.write(member["email"])
            
            with col3:
                st.write(member["role"])
            
            with col4:
                st.button("✏️", key=f"edit_{member['email']}")
        
        st.markdown("### Invite Team Member")
        
        col1, col2, col3 = st.columns([3, 3, 2])
        
        with col1:
            st.text_input("Email Address")
        
        with col2:
            st.selectbox("Role", ["Admin", "Editor", "Viewer"])
        
        with col3:
            st.button("Send Invite")

elif page == "Samples":
    st.markdown('<div class="title">Sample Policies</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Explore sample policies and their analysis results to see how PolicyEdgeAI works.
    """)
    
    sample_tabs = st.tabs(["Privacy Policy", "Terms of Service", "Cookie Policy"])
    
    with sample_tabs[0]:
        st.markdown("### Sample Privacy Policy")
        
        with st.expander("View Privacy Policy", expanded=False):
            st.markdown("""
            # PRIVACY POLICY
            
            **Last Updated: April 1, 2025**
            
            ## 1. INTRODUCTION
            
            Welcome to our Privacy Policy. This policy explains how we collect, use, and protect your personal information when you use our services.
            
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
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Analyze Sample Privacy Policy", type="primary", use_container_width=True):
                with st.spinner("Analyzing privacy policy..."):
                    # Simulate processing delay
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)  # Simulate processing time
                        progress_bar.progress(i + 1)
                    
                    # Sample analysis results
                    results = {
                        "compliance": {
                            "GDPR": 87,
                            "CCPA": 92,
                            "HIPAA": 65
                        },
                        "readability": {
                            "grade_level": 12,
                            "clarity_score": 78
                        },
                        "issues": [
                            "Data retention periods not clearly specified",
                            "Missing details on international data transfers",
                            "Vague description of third-party sharing",
                            "Unclear consent mechanisms for cookies"
                        ],
                        "recommendations": [
                            "Add specific retention periods for each data category",
                            "Include details on data transfer safeguards",
                            "List specific third parties with whom data is shared",
                            "Clarify how users can withdraw consent"
                        ]
                    }
                
                # Display results
                st.success("Analysis complete\!")
                
                # Compliance scores
                st.markdown("#### Compliance Scores")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("GDPR", f"{results['compliance']['GDPR']}%")
                
                with col2:
                    st.metric("CCPA", f"{results['compliance']['CCPA']}%")
                
                with col3:
                    st.metric("HIPAA", f"{results['compliance']['HIPAA']}%")
                
                # Readability
                st.markdown("#### Readability")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Grade Level", f"{results['readability']['grade_level']}th")
                    
                    if results['readability']['grade_level'] > 12:
                        st.warning("Your policy may be too complex for the average reader.")
                    else:
                        st.success("Your policy's reading level is appropriate for most users.")
                
                with col2:
                    st.metric("Clarity Score", f"{results['readability']['clarity_score']}%")
                    
                    if results['readability']['clarity_score'] < 70:
                        st.warning("Consider improving clarity with simpler language and structure.")
                    else:
                        st.success("Your policy is clearly written and well-structured.")
                
                # Issues and recommendations
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Issues Identified")
                    
                    for issue in results["issues"]:
                        st.markdown(f"- {issue}")
                
                with col2:
                    st.markdown("#### Recommendations")
                    
                    for i, rec in enumerate(results["recommendations"]):
                        st.markdown(f"{i+1}. {rec}")
                
                # Actions
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("See Full Report Sample"):
                        st.markdown("This would download a full report in the real application.")
                
                with col2:
                    if st.button("Try with Your Own Policy"):
                        st.session_state.logged_in = True
                        st.session_state.current_page = "Upload Policy"
                        st.experimental_rerun()
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### What You'll See")
            st.markdown("""
            Our AI analysis will identify:
            
            - Compliance with GDPR, CCPA, HIPAA
            - Readability metrics
            - Missing or unclear sections
            - Specific recommendations
            - Industry benchmarking
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with sample_tabs[1]:
        st.markdown("### Sample Terms of Service")
        st.markdown("View and analyze our sample Terms of Service document.")
        
        with st.expander("View Terms of Service", expanded=False):
            st.markdown("""
            # TERMS OF SERVICE
            
            **Last Updated: March 15, 2025**
            
            ## 1. INTRODUCTION
            
            These Terms of Service govern your use of our platform and services.
            
            ## 2. ACCEPTANCE OF TERMS
            
            By accessing or using our services, you agree to be bound by these Terms.
            
            ## 3. SERVICES DESCRIPTION
            
            Our platform provides [description of services].
            
            ## 4. USER ACCOUNTS
            
            You are responsible for maintaining the security of your account.
            
            ## 5. USER CONDUCT
            
            You agree not to:
            - Violate any laws
            - Infringe on intellectual property rights
            - Harass or harm others
            - Distribute malicious content
            
            ## 6. INTELLECTUAL PROPERTY
            
            All content and materials available through our services are protected by intellectual property rights.
            
            ## 7. LIMITATION OF LIABILITY
            
            To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages.
            
            ## 8. TERM AND TERMINATION
            
            We reserve the right to suspend or terminate your access to our services for violations of these Terms.
            
            ## 9. CHANGES TO TERMS
            
            We may modify these Terms at any time. Your continued use constitutes acceptance of the updated Terms.
            
            ## 10. GOVERNING LAW
            
            These Terms shall be governed by the laws of [jurisdiction].
            
            ## 11. CONTACT INFORMATION
            
            If you have any questions about these Terms, please contact us at legal@example.com.
            """)
        
        if st.button("Analyze Sample Terms of Service", type="primary"):
            st.info("This would show an analysis similar to the Privacy Policy example.")
    
    with sample_tabs[2]:
        st.markdown("### Sample Cookie Policy")
        st.markdown("View and analyze our sample Cookie Policy document.")
        
        with st.expander("View Cookie Policy", expanded=False):
            st.markdown("""
            # COOKIE POLICY
            
            **Last Updated: February 28, 2025**
            
            ## 1. INTRODUCTION
            
            This Cookie Policy explains how we use cookies and similar technologies.
            
            ## 2. WHAT ARE COOKIES
            
            Cookies are small text files placed on your device when you visit a website.
            
            ## 3. HOW WE USE COOKIES
            
            We use cookies for:
            - Essential website functionality
            - Performance and analytics
            - Personalization
            - Advertising and targeting
            
            ## 4. TYPES OF COOKIES WE USE
            
            - Essential cookies
            - Performance cookies
            - Functional cookies
            - Targeting cookies
            
            ## 5. MANAGING COOKIES
            
            You can manage cookies through your browser settings.
            
            ## 6. UPDATES TO THIS POLICY
            
            We may update this policy from time to time.
            
            ## 7. CONTACT US
            
            If you have questions about our use of cookies, please contact us at cookies@example.com.
            """)
        
        if st.button("Analyze Sample Cookie Policy", type="primary"):
            st.info("This would show an analysis similar to the Privacy Policy example.")
    
    # Try it yourself section
    st.markdown("---")
    st.markdown("### Ready to analyze your own policies?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Register Now", type="primary", use_container_width=True):
            st.session_state.current_page = "Register"
            st.experimental_rerun()
    
    with col2:
        if st.button("Login", type="secondary", use_container_width=True):
            st.session_state.current_page = "Login"
            st.experimental_rerun()

elif page == "Logout" and st.session_state.logged_in:
    # Log out the user
    st.session_state.logged_in = False
    st.session_state.username = None
    
    st.success("You have been logged out successfully.")
    
    if st.button("Return to Home"):
        st.session_state.current_page = "Home"
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;font-size:0.8em;'>© 2025 PolicyEdgeAI. All rights reserved.</div>", unsafe_allow_html=True)
