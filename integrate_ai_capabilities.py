import streamlit as st
import os
import time
import random
import json

# Configuration
st.set_page_config(
    page_title="PolicyEdgeAI",
    page_icon="🔍",
    layout="wide"
)

# Initialize session states
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "home"
if 'api_providers' not in st.session_state:
    st.session_state.api_providers = {
        "openai": {"configured": False, "model": "gpt-4-turbo"},
        "anthropic": {"configured": False, "model": "claude-3-opus-20240229"}
    }
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem;}
    .section-header {font-size: 1.5rem; font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem;}
    .model-box {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4263eb;
    }
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    .stButton button {width: 100%;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80?text=PolicyEdgeAI", width=200)
    st.markdown("## PolicyEdgeAI")
    
    if st.session_state.authenticated:
        st.markdown("### Main Navigation")
        selected_view = st.radio(
            "Select View",
            ["Dashboard", "Document Analysis", "Compliance Q&A", "Implementation Guidance", "Provider Comparison", "Settings", "Logout"]
        )
        if selected_view \!= st.session_state.current_view:
            st.session_state.current_view = selected_view
            st.experimental_rerun()
    else:
        st.markdown("### Welcome")
        selected_view = st.radio(
            "Select View",
            ["Home", "Login", "About Us"]
        )
        if selected_view \!= st.session_state.current_view:
            st.session_state.current_view = selected_view
            st.experimental_rerun()
    
    # Quick demo access
    if not st.session_state.authenticated:
        st.markdown("---")
        if st.button("✨ Demo Access", use_container_width=True, type="primary"):
            st.session_state.authenticated = True
            st.session_state.current_view = "Dashboard"
            # Mock configuration of API providers
            st.session_state.api_providers["openai"]["configured"] = True
            st.session_state.api_providers["anthropic"]["configured"] = True
            st.experimental_rerun()
    
    # Status indicator for API providers
    st.markdown("---")
    st.markdown("### API Status")
    
    openai_status = "✅ Configured" if st.session_state.api_providers["openai"]["configured"] else "❌ Not Configured"
    anthropic_status = "✅ Configured" if st.session_state.api_providers["anthropic"]["configured"] else "❌ Not Configured"
    
    st.markdown(f"**OpenAI**: {openai_status}")
    st.markdown(f"**Anthropic**: {anthropic_status}")

# Mock functions
def analyze_document(text, analysis_type="standard"):
    """Simulate document analysis"""
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    
    return {
        "compliance": {
            "gdpr": random.randint(70, 95),
            "ccpa": random.randint(70, 95),
            "hipaa": random.randint(70, 95),
        },
        "readability": {
            "score": random.randint(60, 90),
            "grade_level": random.randint(8, 14)
        },
        "gaps": [
            "Data retention periods not clearly specified",
            "Missing details about international data transfers",
            "Unclear consent mechanism for cookies",
            "Insufficient description of user rights"
        ],
        "recommendations": [
            "Add specific retention periods for each data category",
            "Include safeguards for international transfers",
            "Add a detailed cookie consent mechanism",
            "Expand the description of user rights with examples"
        ]
    }

def mock_gpt_query(query, provider="openai"):
    """Simulate GPT/Claude query"""
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    
    if "gdpr" in query.lower():
        return """
        # GDPR Compliance Requirements
        
        The General Data Protection Regulation (GDPR) requires organizations to:
        
        1. **Lawful Basis**: Process data only with a lawful basis (consent, contract, legitimate interest, etc.)
        2. **Transparency**: Provide clear information about data collection and processing
        3. **Purpose Limitation**: Collect data for specified, explicit, and legitimate purposes
        4. **Data Minimization**: Process only data that is necessary for the stated purposes
        5. **Accuracy**: Ensure personal data is accurate and kept up to date
        6. **Storage Limitation**: Keep data only as long as necessary
        7. **Security**: Implement appropriate technical and organizational measures
        8. **Accountability**: Demonstrate compliance with GDPR principles
        
        ## Key Rights for Individuals
        - Right to access their data
        - Right to rectification of inaccurate data
        - Right to erasure ("right to be forgotten")
        - Right to restrict processing
        - Right to data portability
        - Right to object to processing
        - Rights related to automated decision making and profiling
        
        ## Documentation Requirements
        Organizations must maintain records of processing activities including:
        - Purposes of processing
        - Categories of data subjects and personal data
        - Recipients of personal data
        - Transfers to third countries
        - Time limits for erasure
        - Security measures
        """
    elif "ccpa" in query.lower():
        return """
        # CCPA Compliance Requirements
        
        The California Consumer Privacy Act (CCPA) requires businesses to:
        
        1. **Disclosure**: Inform consumers about personal information collected and purposes
        2. **Deletion**: Honor consumer requests to delete personal information
        3. **Opt-Out**: Allow consumers to opt-out of the sale of their personal information
        4. **Non-Discrimination**: Not discriminate against consumers exercising their rights
        5. **Privacy Policy**: Maintain a comprehensive privacy policy
        
        ## Key Rights for Consumers
        - Right to know what personal information is collected
        - Right to know if personal information is sold or disclosed
        - Right to say no to the sale of personal information
        - Right to access personal information
        - Right to equal service and price
        
        ## Documentation Requirements
        Businesses must:
        - Update privacy policies with required disclosures
        - Implement methods for consumers to submit requests
        - Train employees handling consumer inquiries
        - Maintain records of consumer requests and responses
        """
    else:
        return """
        I'll need more specific information about which regulation or compliance area you're interested in. 
        
        Some common areas I can provide information about include:
        
        - GDPR (General Data Protection Regulation)
        - CCPA (California Consumer Privacy Act)
        - HIPAA (Health Insurance Portability and Accountability Act)
        - PCI DSS (Payment Card Industry Data Security Standard)
        - SOC 2 (Service Organization Control 2)
        - ISO 27001 (Information Security Management)
        
        Please specify which area you'd like information about, or ask a more specific compliance question.
        """

def generate_implementation_guidance(requirement, level="detailed"):
    """Generate implementation guidance for compliance requirements"""
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    
    if "consent" in requirement.lower():
        return """
        # Implementation Guide: Obtaining Valid Consent
        
        ## 1. Key Requirements
        
        For consent to be valid under GDPR, it must be:
        - **Freely given**: No coercion or significant imbalance of power
        - **Specific**: For particular, explicit purposes
        - **Informed**: Clear information about what the user is consenting to
        - **Unambiguous**: Clear affirmative action (no pre-ticked boxes)
        - **Withdrawable**: As easy to withdraw as to give consent
        
        ## 2. Technical Implementation
        
        ### Cookie Consent
        ```javascript
        // Sample implementation with Cookie Consent library
        window.cookieconsent.initialise({
          palette: {
            popup: { background: "#000" },
            button: { background: "#f1d600" },
          },
          type: "opt-in", // Important: default to opt-out
          content: {
            message: "This website uses cookies to ensure you get the best experience.",
            dismiss: "Got it",
            deny: "Decline",
            link: "Learn more",
            href: "/privacy-policy#cookies",
            policy: "Cookie Policy"
          },
          onInitialise: function(status) {
            if (status === cookieconsent.status.allow) {
              // Enable cookies
              enableCookies();
            }
          },
          onStatusChange: function(status) {
            if (status === cookieconsent.status.allow) {
              // Enable cookies
              enableCookies();
            } else {
              // Disable cookies
              disableCookies();
            }
          }
        });
        ```
        
        ### Form Consent
        ```html
        <div class="consent-form">
          <div class="consent-section">
            <input type="checkbox" id="marketing" name="marketing" required>
            <label for="marketing">
              I consent to receiving marketing communications about your products and services.
              <a href="/privacy-policy#marketing">Learn more</a>
            </label>
          </div>
          
          <div class="consent-section">
            <input type="checkbox" id="analytics" name="analytics" required>
            <label for="analytics">
              I consent to the use of analytics cookies to understand how you interact with our website.
              <a href="/privacy-policy#analytics">Learn more</a>
            </label>
          </div>
          
          <button type="submit">Submit</button>
        </div>
        ```
        
        ## 3. Backend Storage
        
        ```python
        # Example using Django
        class ConsentRecord(models.Model):
            user = models.ForeignKey(User, on_delete=models.CASCADE)
            consent_type = models.CharField(max_length=50)  # e.g., "marketing", "analytics"
            granted = models.BooleanField(default=False)
            timestamp = models.DateTimeField(auto_now=True)
            ip_address = models.GenericIPAddressField(null=True, blank=True)
            user_agent = models.TextField(null=True, blank=True)
            
            class Meta:
                unique_together = ('user', 'consent_type')
        
        # Recording consent
        def record_consent(request, user_id, consent_type, granted):
            ConsentRecord.objects.update_or_create(
                user_id=user_id,
                consent_type=consent_type,
                defaults={
                    'granted': granted,
                    'ip_address': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
        ```
        
        ## 4. Consent Withdrawal
        
        Create a user dashboard where users can:
        - View their current consent settings
        - Toggle consent on/off
        - Request data deletion
        
        ## 5. Documentation Requirements
        
        For each consent, record:
        - What the user consented to (specific purpose)
        - When they consented (timestamp)
        - How they consented (which form, checkbox, etc.)
        - What information was provided (version of privacy policy)
        - Identity verification method
        - Withdrawal mechanism
        
        ## 6. Audit Trail
        
        Implement audit logging to track:
        - All consent actions (grant, withdraw)
        - Changes to consent forms or processes
        - Access to consent records
        """
    elif "data retention" in requirement.lower():
        return """
        # Implementation Guide: Data Retention Policy
        
        ## 1. Key Requirements
        
        Under GDPR Article 5(1)(e), personal data must be:
        - Kept for no longer than necessary for the purposes
        - Periodically reviewed and erased/anonymized when no longer needed
        - Subject to appropriate security measures during storage
        
        ## 2. Policy Implementation
        
        ### Data Inventory
        Create a data inventory spreadsheet:
        
        | Data Category | Purpose | Legal Basis | Retention Period | Justification |
        |---------------|---------|-------------|------------------|---------------|
        | Account data | Service provision | Contract | 7 years after closure | Tax requirements |
        | Marketing data | Promotional emails | Consent | 2 years from last interaction | Business need |
        | Website logs | Security & performance | Legitimate interest | 90 days | Security monitoring |
        
        ### Technical Implementation
        
        ```python
        # Example data retention scheduler using Python
        import datetime
        
        def schedule_data_deletion(data_type, user_id, created_date):
            retention_periods = {
                'account_data': 365 * 7,  # 7 years
                'marketing_data': 365 * 2,  # 2 years
                'logs': 90  # 90 days
            }
            
            if data_type not in retention_periods:
                raise ValueError(f"Unknown data type: {data_type}")
            
            deletion_date = created_date + datetime.timedelta(days=retention_periods[data_type])
            
            # Schedule the deletion task
            DeletionTask.objects.create(
                user_id=user_id,
                data_type=data_type,
                scheduled_date=deletion_date
            )
            
        # Example deletion task
        def process_deletion_tasks():
            today = datetime.date.today()
            tasks = DeletionTask.objects.filter(scheduled_date__lte=today, completed=False)
            
            for task in tasks:
                try:
                    if task.data_type == 'account_data':
                        anonymize_account(task.user_id)
                    elif task.data_type == 'marketing_data':
                        delete_marketing_data(task.user_id)
                    elif task.data_type == 'logs':
                        delete_old_logs(task.user_id)
                    
                    task.completed = True
                    task.completion_date = today
                    task.save()
                except Exception as e:
                    log_error(f"Failed to process deletion task {task.id}: {str(e)}")
        ```
        
        ## 3. Database Structure
        
        ```sql
        -- Example PostgreSQL table with TTL (Time To Live)
        CREATE TABLE user_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            action VARCHAR(255) NOT NULL,
            ip_address VARCHAR(45),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date TIMESTAMP GENERATED ALWAYS AS (timestamp + INTERVAL '90 day') STORED
        );
        
        -- Create index on expiry date for efficient cleanup
        CREATE INDEX idx_user_logs_expiry ON user_logs(expiry_date);
        
        -- Create scheduled task to periodically clean up expired data
        CREATE OR REPLACE FUNCTION cleanup_expired_logs()
        RETURNS void AS $$
        BEGIN
            DELETE FROM user_logs WHERE expiry_date < CURRENT_TIMESTAMP;
        END;
        $$ LANGUAGE plpgsql;
        ```
        
        ## 4. Automated Cleanup Process
        
        Create a scheduled job (e.g., cron task) to:
        1. Identify records past their retention period
        2. Apply appropriate action (delete, anonymize, or archive)
        3. Log the cleanup action for audit purposes
        
        ## 5. Documentation Requirements
        
        Maintain documentation that includes:
        - Retention schedule for all data categories
        - Justification for each retention period
        - Process for reviewing and updating retention periods
        - Technical controls implementing the policy
        - Audit logs of deletion activities
        
        ## 6. Special Considerations
        
        - **Legal Holds**: Implement process to override deletion when data is subject to legal proceedings
        - **Backups**: Ensure backup retention aligns with data retention policy
        - **Archive Data**: Apply different security controls to archived data
        - **Right to Erasure**: Ability to handle data subject deletion requests that may override normal retention
        """
    else:
        return """
        # Implementation Guide: Generic Compliance Framework
        
        Please provide a more specific compliance requirement for detailed implementation guidance. For example:
        
        - Data subject access requests (DSAR) process
        - Consent management implementation
        - Data retention policy and processes
        - International data transfers
        - Privacy by design framework
        - Breach notification procedures
        - Data minimization techniques
        - Vendor management and assessment
        
        With a specific requirement, I can provide:
        - Technical implementation examples
        - Code samples
        - Database structures
        - Documentation templates
        - Process workflows
        """

def compare_providers(query):
    """Compare responses from different AI providers"""
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    
    return {
        "openai": {
            "response": """GDPR compliance requires organizations to:
1. Establish lawful bases for processing data
2. Implement data protection by design and default
3. Conduct data protection impact assessments
4. Maintain records of processing activities
5. Ensure appropriate security measures
6. Report data breaches within 72 hours
7. Appoint a Data Protection Officer (if required)
8. Honor data subject rights (access, rectification, erasure, etc.)
9. Ensure lawful international data transfers
10. Conduct regular compliance audits""",
            "time": "1.23 seconds",
            "tokens": 128,
            "cost": "$0.0012"
        },
        "anthropic": {
            "response": """# GDPR Compliance Requirements

## Core Principles
- **Lawfulness, fairness and transparency**: Process data lawfully, fairly and in a transparent manner
- **Purpose limitation**: Collect data for specified, explicit and legitimate purposes
- **Data minimization**: Ensure data is adequate, relevant and limited to what is necessary
- **Accuracy**: Keep data accurate and up to date
- **Storage limitation**: Store data for no longer than necessary
- **Integrity and confidentiality**: Ensure appropriate security measures

## Key Implementation Requirements
1. **Lawful basis**: Identify and document your lawful basis for each processing activity
2. **Privacy notices**: Provide clear and comprehensive privacy information
3. **Data subject rights**: Implement procedures for handling rights requests
4. **Data protection impact assessments**: Conduct DPIAs for high-risk processing
5. **Records of processing activities**: Maintain detailed documentation
6. **Security measures**: Implement technical and organizational safeguards
7. **Breach notification**: Procedures to detect, report and investigate breaches
8. **International transfers**: Ensure appropriate safeguards for data leaving the EEA
9. **Data Protection Officer**: Appoint a DPO if required
10. **Accountability**: Demonstrate compliance through policies, procedures and records""",
            "time": "2.45 seconds",
            "tokens": 215,
            "cost": "$0.0032"
        },
        "comparison": {
            "completeness": "Claude provides more comprehensive information with better formatting and organization",
            "accuracy": "Both responses are accurate, but Claude includes more detail on core principles",
            "structure": "Claude's response has better hierarchical structure with clear headings",
            "insights": "Claude's response includes implementation requirements separate from principles",
            "recommendation": "Claude's response would be better for detailed compliance guidance"
        }
    }

# Main content
current_view = st.session_state.current_view

if current_view == "home":
    st.markdown('<h1 class="main-header">PolicyEdgeAI</h1>', unsafe_allow_html=True)
    st.markdown("## AI-powered policy compliance and analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        PolicyEdgeAI uses advanced AI to help organizations:
        
        - **Analyze** policy documents for compliance and readability
        - **Query** advanced language models about compliance requirements
        - **Generate** implementation guidance for compliance controls
        - **Compare** responses from different AI providers
        - **Customize** outputs based on industry and regulatory needs
        """)
        
        st.markdown("### Supported AI Technologies")
        
        tech_col1, tech_col2 = st.columns(2)
        
        with tech_col1:
            st.markdown('<div class="model-box">', unsafe_allow_html=True)
            st.markdown("#### OpenAI GPT Models")
            st.markdown("- GPT-4 Turbo")
            st.markdown("- GPT-4o")
            st.markdown("- GPT-3.5 Turbo")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tech_col2:
            st.markdown('<div class="model-box">', unsafe_allow_html=True)
            st.markdown("#### Anthropic Claude Models")
            st.markdown("- Claude 3 Opus")
            st.markdown("- Claude 3 Sonnet")
            st.markdown("- Claude 3 Haiku")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.image("https://via.placeholder.com/300x200?text=PolicyEdgeAI", width=300)
        
        st.markdown("### Try PolicyEdgeAI Now")
        if st.button("Demo Access", use_container_width=True, type="primary"):
            st.session_state.authenticated = True
            st.session_state.current_view = "Dashboard"
            # Mock configuration of API providers
            st.session_state.api_providers["openai"]["configured"] = True
            st.session_state.api_providers["anthropic"]["configured"] = True
            st.experimental_rerun()
        
        if st.button("Login", use_container_width=True):
            st.session_state.current_view = "Login"
            st.experimental_rerun()
    
    st.markdown("---")
    
    st.markdown("### Key Features")
    
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("#### Document Analysis")
        st.markdown("""
        - Privacy policy assessment
        - Terms of service evaluation
        - Compliance gap identification
        - Readability analysis
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with feature_cols[1]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("#### Compliance Q&A")
        st.markdown("""
        - Regulatory requirement explanations
        - Implementation guidance
        - Best practice recommendations
        - Industry-specific guidance
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with feature_cols[2]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("#### AI Provider Comparison")
        st.markdown("""
        - Compare OpenAI vs Anthropic
        - Assess response quality
        - Identify differences in guidance
        - Choose optimal provider
        """)
        st.markdown("</div>", unsafe_allow_html=True)

elif current_view == "Login":
    st.markdown('<h1 class="main-header">Login</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if email and password:
                    # Simulate successful login
                    st.session_state.authenticated = True
                    st.session_state.current_view = "Dashboard"
                    st.experimental_rerun()
                else:
                    st.error("Please enter email and password")
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Quick Demo")
        st.markdown("Try PolicyEdgeAI without creating an account:")
        
        if st.button("Demo Access", use_container_width=True, type="primary"):
            st.session_state.authenticated = True
            st.session_state.current_view = "Dashboard"
            # Mock configuration of API providers
            st.session_state.api_providers["openai"]["configured"] = True
            st.session_state.api_providers["anthropic"]["configured"] = True
            st.experimental_rerun()
        
        st.markdown("### Enterprise SSO")
        st.markdown("We support:")
        st.markdown("- Google Workspace")
        st.markdown("- Microsoft 365")
        st.markdown("- Okta")
        st.markdown("</div>", unsafe_allow_html=True)

elif current_view == "About Us":
    st.markdown('<h1 class="main-header">About PolicyEdgeAI</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    PolicyEdgeAI combines advanced large language models with compliance expertise to provide
    automated policy analysis, compliance guidance, and implementation recommendations.
    
    ### Our Mission
    
    To simplify compliance through AI-powered tools that make regulations comprehensible,
    actionable, and manageable for organizations of all sizes.
    
    ### Our Technology
    
    We leverage state-of-the-art language models from OpenAI and Anthropic, specifically:
    
    - **OpenAI's GPT-4 Turbo** for comprehensive compliance analysis
    - **Anthropic's Claude 3 Opus** for nuanced regulatory interpretation
    
    Our platform offers:
    
    1. **Policy Document Analysis**: Automatically assess compliance of privacy policies, terms of service, and other documents
    2. **Compliance Q&A**: Get authoritative answers to complex regulatory questions
    3. **Implementation Guidance**: Receive detailed technical guidance for implementing compliance controls
    4. **Provider Comparison**: Compare responses from different AI providers for optimal insights
    """)
    
    st.markdown("### Try PolicyEdgeAI Now")
    
    demo_col1, demo_col2 = st.columns([1, 3])
    
    with demo_col1:
        if st.button("Demo Access", use_container_width=True, type="primary"):
            st.session_state.authenticated = True
            st.session_state.current_view = "Dashboard"
            # Mock configuration of API providers
            st.session_state.api_providers["openai"]["configured"] = True
            st.session_state.api_providers["anthropic"]["configured"] = True
            st.experimental_rerun()

elif current_view == "Dashboard" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    # API Status
    st.markdown("### API Provider Status")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("#### OpenAI")
        if st.session_state.api_providers["openai"]["configured"]:
            st.success("✅ Configured")
            st.markdown(f"Model: **{st.session_state.api_providers['openai']['model']}**")
        else:
            st.error("❌ Not Configured")
            if st.button("Configure OpenAI", key="configure_openai"):
                st.session_state.current_view = "Settings"
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with status_col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("#### Anthropic")
        if st.session_state.api_providers["anthropic"]["configured"]:
            st.success("✅ Configured")
            st.markdown(f"Model: **{st.session_state.api_providers['anthropic']['model']}**")
        else:
            st.error("❌ Not Configured")
            if st.button("Configure Anthropic", key="configure_anthropic"):
                st.session_state.current_view = "Settings"
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Access
    st.markdown("### Quick Access")
    
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("Document Analysis", use_container_width=True):
            st.session_state.current_view = "Document Analysis"
            st.experimental_rerun()
    
    with quick_col2:
        if st.button("Compliance Q&A", use_container_width=True):
            st.session_state.current_view = "Compliance Q&A"
            st.experimental_rerun()
    
    with quick_col3:
        if st.button("Implementation Guidance", use_container_width=True):
            st.session_state.current_view = "Implementation Guidance"
            st.experimental_rerun()
    
    with quick_col4:
        if st.button("Provider Comparison", use_container_width=True):
            st.session_state.current_view = "Provider Comparison"
            st.experimental_rerun()
    
    # Recent Activity
    st.markdown("### Recent Activity")
    
    recent_activities = [
        {"type": "Analysis", "description": "Privacy Policy Analysis", "date": "Today", "status": "Completed"},
        {"type": "Query", "description": "GDPR Compliance Requirements", "date": "Yesterday", "status": "Completed"},
        {"type": "Guidance", "description": "Data Retention Implementation", "date": "3 days ago", "status": "Completed"},
        {"type": "Comparison", "description": "OpenAI vs Anthropic for Cookie Consent", "date": "Last week", "status": "Completed"}
    ]
    
    for activity in recent_activities:
        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
        
        with col1:
            st.write(f"**{activity['type']}**")
        
        with col2:
            st.write(activity['description'])
        
        with col3:
            st.write(activity['date'])
        
        with col4:
            if activity['status'] == "Completed":
                st.success("✅")
            else:
                st.info("⏳")

elif current_view == "Document Analysis" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Document Analysis</h1>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        # Document upload and analysis form
        st.markdown("### Upload Document for Analysis")
        
        document_type = st.selectbox(
            "Document Type",
            ["Privacy Policy", "Terms of Service", "Cookie Policy", "EULA", "Other"]
        )
        
        analysis_type = st.radio(
            "Analysis Type",
            ["Standard", "Comprehensive", "Regulatory Focus"]
        )
        
        if analysis_type == "Regulatory Focus":
            regulations = st.multiselect(
                "Select Regulations",
                ["GDPR", "CCPA", "HIPAA", "CPRA", "LGPD", "PIPEDA"],
                default=["GDPR", "CCPA"]
            )
        
        document_text = st.text_area(
            "Paste document text or upload a file",
            height=300
        )
        
        uploaded_file = st.file_uploader("Or upload a document", type=["txt", "pdf", "docx"])
        
        if uploaded_file is not None:
            # In a real app, process the file
            document_text = "Content from uploaded file would appear here."
            st.success(f"File uploaded: {uploaded_file.name}")
        
        if st.button("Analyze Document", type="primary"):
            if document_text or uploaded_file:
                with st.spinner("Analyzing document..."):
                    # Call mock analysis function
                    results = analyze_document(document_text, analysis_type.lower())
                    st.session_state.analysis_results = results
                st.experimental_rerun()
            else:
                st.error("Please enter document text or upload a file")
    
    else:
        # Display analysis results
        st.markdown("### Analysis Results")
        
        # Compliance scores
        st.markdown("#### Compliance Scores")
        
        score_cols = st.columns(3)
        
        with score_cols[0]:
            gdpr_score = st.session_state.analysis_results["compliance"]["gdpr"]
            st.metric("GDPR Compliance", f"{gdpr_score}%")
            
            # Color-coded progress bar
            color = "green" if gdpr_score >= 90 else "blue" if gdpr_score >= 75 else "orange" if gdpr_score >= 60 else "red"
            st.markdown(f"""
            <div style="width:100%;background-color:#eee;height:10px;border-radius:3px">
              <div style="width:{gdpr_score}%;background-color:{color};height:10px;border-radius:3px"></div>
            </div>
            """, unsafe_allow_html=True)
        
        with score_cols[1]:
            ccpa_score = st.session_state.analysis_results["compliance"]["ccpa"]
            st.metric("CCPA Compliance", f"{ccpa_score}%")
            
            color = "green" if ccpa_score >= 90 else "blue" if ccpa_score >= 75 else "orange" if ccpa_score >= 60 else "red"
            st.markdown(f"""
            <div style="width:100%;background-color:#eee;height:10px;border-radius:3px">
              <div style="width:{ccpa_score}%;background-color:{color};height:10px;border-radius:3px"></div>
            </div>
            """, unsafe_allow_html=True)
        
        with score_cols[2]:
            hipaa_score = st.session_state.analysis_results["compliance"]["hipaa"]
            st.metric("HIPAA Compliance", f"{hipaa_score}%")
            
            color = "green" if hipaa_score >= 90 else "blue" if hipaa_score >= 75 else "orange" if hipaa_score >= 60 else "red"
            st.markdown(f"""
            <div style="width:100%;background-color:#eee;height:10px;border-radius:3px">
              <div style="width:{hipaa_score}%;background-color:{color};height:10px;border-radius:3px"></div>
            </div>
            """, unsafe_allow_html=True)
        
        # Readability
        st.markdown("#### Readability")
        
        read_col1, read_col2 = st.columns(2)
        
        with read_col1:
            read_score = st.session_state.analysis_results["readability"]["score"]
            st.metric("Clarity Score", f"{read_score}%")
            
            color = "green" if read_score >= 80 else "blue" if read_score >= 70 else "orange" if read_score >= 60 else "red"
            st.markdown(f"""
            <div style="width:100%;background-color:#eee;height:10px;border-radius:3px">
              <div style="width:{read_score}%;background-color:{color};height:10px;border-radius:3px"></div>
            </div>
            """, unsafe_allow_html=True)
        
        with read_col2:
            grade_level = st.session_state.analysis_results["readability"]["grade_level"]
            st.metric("Grade Level", f"{grade_level}")
            
            if grade_level <= 8:
                st.success("Easy to understand")
            elif grade_level <= 12:
                st.info("Average complexity")
            else:
                st.warning("Complex - consider simplifying")
        
        # Gaps and Recommendations
        gap_col, rec_col = st.columns(2)
        
        with gap_col:
            st.markdown("#### Compliance Gaps")
            
            for i, gap in enumerate(st.session_state.analysis_results["gaps"]):
                severity = "high" if i < 2 else "medium" if i < 3 else "low"
                color = "red" if severity == "high" else "orange" if severity == "medium" else "blue"
                
                st.markdown(f"""
                <div style="border-left:3px solid {color};padding-left:10px;margin-bottom:10px;">
                  <strong>{gap}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        with rec_col:
            st.markdown("#### Recommendations")
            
            for i, rec in enumerate(st.session_state.analysis_results["recommendations"]):
                st.markdown(f"{i+1}. {rec}")
        
        # Actions
        st.markdown("---")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("Download Report", use_container_width=True):
                st.success("Report downloaded")
        
        with action_col2:
            if st.button("Save Analysis", use_container_width=True):
                st.success("Analysis saved")
        
        with action_col3:
            if st.button("New Analysis", use_container_width=True):
                st.session_state.analysis_results = None
                st.experimental_rerun()

elif current_view == "Compliance Q&A" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Compliance Q&A</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Ask questions about compliance requirements, regulatory obligations, or implementation guidance.
    The system will use large language models to provide detailed, accurate responses.
    """)
    
    # Provider selection
    provider = st.radio(
        "Select AI Provider",
        ["OpenAI GPT-4 Turbo", "Anthropic Claude 3 Opus", "Both (Compare)"],
        horizontal=True
    )
    
    # Query input
    query = st.text_area(
        "Enter your compliance question",
        height=100,
        placeholder="Example: What are the key requirements for GDPR compliance?"
    )
    
    if st.button("Submit Question", type="primary"):
        if query:
            if provider == "Both (Compare)":
                st.session_state.current_view = "Provider Comparison"
                st.session_state.comparison_query = query
                st.experimental_rerun()
            else:
                selected_provider = "openai" if "OpenAI" in provider else "anthropic"
                
                with st.spinner(f"Generating response using {provider}..."):
                    response = mock_gpt_query(query, selected_provider)
                
                st.markdown("### Response")
                st.markdown(response)
                
                # Feedback and actions
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("👍 Helpful", use_container_width=True):
                        st.success("Thank you for your feedback\!")
                
                with col2:
                    if st.button("👎 Not Helpful", use_container_width=True):
                        st.error("Thank you for your feedback\!")
                
                with col3:
                    if st.button("💾 Save Response", use_container_width=True):
                        st.success("Response saved\!")
        else:
            st.error("Please enter a question")
    
    # Example queries
    st.markdown("### Example Questions")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        if st.button("What are the key requirements for GDPR compliance?", use_container_width=True):
            # Set the query
            st.session_state.example_query = "What are the key requirements for GDPR compliance?"
            # Rerun to show the response
            st.experimental_rerun()
    
    with example_col2:
        if st.button("What are the CCPA requirements for businesses?", use_container_width=True):
            # Set the query
            st.session_state.example_query = "What are the CCPA requirements for businesses?"
            # Rerun to show the response
            st.experimental_rerun()
    
    # If an example was clicked, show the response
    if hasattr(st.session_state, 'example_query'):
        query = st.session_state.example_query
        # Remove the attribute to avoid showing it again on next rerun
        delattr(st.session_state, 'example_query')
        
        selected_provider = "openai"
        
        with st.spinner(f"Generating response using OpenAI GPT-4 Turbo..."):
            response = mock_gpt_query(query, selected_provider)
        
        st.markdown("### Response")
        st.markdown(response)

elif current_view == "Implementation Guidance" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Implementation Guidance</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Get detailed technical guidance for implementing specific compliance requirements.
    The system provides code examples, configuration settings, and best practices.
    """)
    
    # Guidance category
    category = st.selectbox(
        "Implementation Category",
        ["Consent Management", "Data Retention", "User Rights / DSARs", "Data Security", "Breach Notification", "Cookie Compliance", "Other"]
    )
    
    # Specific requirement
    if category == "Consent Management":
        requirement = st.selectbox(
            "Specific Requirement",
            ["Obtaining valid consent", "Consent withdrawal mechanisms", "Consent records and documentation", "Consent for children", "Proof of consent"]
        )
    elif category == "Data Retention":
        requirement = st.selectbox(
            "Specific Requirement",
            ["Data retention policy", "Automated deletion workflows", "Retention period justification", "Legal holds process", "Backup retention alignment"]
        )
    elif category == "User Rights / DSARs":
        requirement = st.selectbox(
            "Specific Requirement",
            ["Subject access request workflow", "Right to erasure implementation", "Data portability export", "Objection to processing", "Restriction of processing"]
        )
    else:
        requirement = st.text_input("Enter Specific Requirement")
    
    # Detail level
    detail_level = st.radio(
        "Detail Level",
        ["Basic", "Detailed", "Technical Implementation"],
        horizontal=True
    )
    
    if st.button("Generate Guidance", type="primary"):
        full_requirement = f"{category}: {requirement}"
        
        with st.spinner("Generating implementation guidance..."):
            guidance = generate_implementation_guidance(full_requirement, detail_level.lower())
        
        st.markdown("### Implementation Guidance")
        st.markdown(guidance)
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download as PDF", use_container_width=True):
                st.success("Guidance downloaded as PDF")
        
        with col2:
            if st.button("Save Guidance", use_container_width=True):
                st.success("Guidance saved")

elif current_view == "Provider Comparison" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">AI Provider Comparison</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Compare responses from different AI providers to the same compliance question.
    This helps identify differences in guidance and choose the optimal provider.
    """)
    
    # Query input
    if hasattr(st.session_state, 'comparison_query'):
        # Use the query from Compliance Q&A
        query = st.session_state.comparison_query
        # Remove it to avoid using it again on rerun
        delattr(st.session_state, 'comparison_query')
        st.text_area("Compliance Question", value=query, height=100)
    else:
        query = st.text_area(
            "Enter your compliance question",
            height=100,
            placeholder="Example: What are the key requirements for GDPR compliance?"
        )
    
    if st.button("Compare Providers", type="primary"):
        if query:
            with st.spinner("Comparing responses from OpenAI and Anthropic..."):
                comparison = compare_providers(query)
            
            # Display the comparison
            st.markdown("### Provider Comparison Results")
            
            # Side-by-side responses
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("#### OpenAI GPT-4 Turbo")
                st.markdown(f"**Response Time**: {comparison['openai']['time']}")
                st.markdown(f"**Tokens**: {comparison['openai']['tokens']}")
                st.markdown(f"**Estimated Cost**: {comparison['openai']['cost']}")
                
                st.markdown("**Response:**")
                st.markdown(comparison['openai']['response'])
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("#### Anthropic Claude 3 Opus")
                st.markdown(f"**Response Time**: {comparison['anthropic']['time']}")
                st.markdown(f"**Tokens**: {comparison['anthropic']['tokens']}")
                st.markdown(f"**Estimated Cost**: {comparison['anthropic']['cost']}")
                
                st.markdown("**Response:**")
                st.markdown(comparison['anthropic']['response'])
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Comparison analysis
            st.markdown("### Analysis of Differences")
            
            analysis_items = [
                {"aspect": "Completeness", "analysis": comparison['comparison']['completeness']},
                {"aspect": "Accuracy", "analysis": comparison['comparison']['accuracy']},
                {"aspect": "Structure", "analysis": comparison['comparison']['structure']},
                {"aspect": "Insights", "analysis": comparison['comparison']['insights']}
            ]
            
            for item in analysis_items:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{item['aspect']}**")
                
                with col2:
                    st.markdown(item['analysis'])
            
            st.markdown("### Recommendation")
            st.markdown(f"**{comparison['comparison']['recommendation']}**")
            
            # Actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Download Comparison", use_container_width=True):
                    st.success("Comparison downloaded")
            
            with col2:
                if st.button("Save Comparison", use_container_width=True):
                    st.success("Comparison saved")
        else:
            st.error("Please enter a question")

elif current_view == "Settings" and st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
    
    # Settings tabs
    tabs = st.tabs(["API Configuration", "Models & Customization", "Organization Settings", "User Management"])
    
    with tabs[0]:
        st.markdown("### API Provider Configuration")
        
        # OpenAI configuration
        st.markdown("#### OpenAI")
        
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value="sk-..." if st.session_state.api_providers["openai"]["configured"] else ""
        )
        
        openai_model = st.selectbox(
            "OpenAI Model",
            ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"],
            index=0 if st.session_state.api_providers["openai"]["model"] == "gpt-4-turbo" else
                  1 if st.session_state.api_providers["openai"]["model"] == "gpt-4o" else 2
        )
        
        if st.button("Save OpenAI Settings", use_container_width=True):
            if openai_api_key and not openai_api_key.startswith("sk-"):
                st.error("Invalid OpenAI API key format")
            else:
                st.session_state.api_providers["openai"]["configured"] = True if openai_api_key else False
                st.session_state.api_providers["openai"]["model"] = openai_model
                st.success("OpenAI settings saved successfully\!")
        
        st.markdown("---")
        
        # Anthropic configuration
        st.markdown("#### Anthropic")
        
        anthropic_api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value="sk-ant-..." if st.session_state.api_providers["anthropic"]["configured"] else ""
        )
        
        anthropic_model = st.selectbox(
            "Anthropic Model",
            ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            index=0 if st.session_state.api_providers["anthropic"]["model"] == "claude-3-opus-20240229" else
                  1 if st.session_state.api_providers["anthropic"]["model"] == "claude-3-sonnet-20240229" else 2
        )
        
        if st.button("Save Anthropic Settings", use_container_width=True):
            if anthropic_api_key and not (anthropic_api_key.startswith("sk-ant-") or anthropic_api_key.startswith("sk-")):
                st.error("Invalid Anthropic API key format")
            else:
                st.session_state.api_providers["anthropic"]["configured"] = True if anthropic_api_key else False
                st.session_state.api_providers["anthropic"]["model"] = anthropic_model
                st.success("Anthropic settings saved successfully\!")
    
    with tabs[1]:
        st.markdown("### Model Customization Settings")
        
        # Temperature setting
        temperature = st.slider(
            "Model Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative, lower values make output more deterministic"
        )
        
        # Max tokens
        max_tokens = st.slider(
            "Maximum Response Length",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100,
            help="Maximum number of tokens in the response"
        )
        
        # System prompts for specific tasks
        st.markdown("#### Custom System Prompts")
        
        task_tabs = st.tabs(["Document Analysis", "Compliance Q&A", "Implementation Guidance"])
        
        with task_tabs[0]:
            doc_analysis_prompt = st.text_area(
                "Document Analysis System Prompt",
                value="You are an expert compliance analyst. Your task is to analyze policy documents for regulatory compliance, readability, and comprehensiveness.",
                height=100
            )
        
        with task_tabs[1]:
            qa_prompt = st.text_area(
                "Compliance Q&A System Prompt",
                value="You are a compliance expert with deep knowledge of global privacy and data protection regulations. Provide accurate, comprehensive answers to compliance questions.",
                height=100
            )
        
        with task_tabs[2]:
            implementation_prompt = st.text_area(
                "Implementation Guidance System Prompt",
                value="You are an implementation specialist for compliance requirements. Provide detailed technical guidance including code examples, configurations, and best practices.",
                height=100
            )
        
        if st.button("Save Model Settings", use_container_width=True):
            st.success("Model settings saved successfully\!")
    
    with tabs[2]:
        st.markdown("### Organization Settings")
        
        org_name = st.text_input("Organization Name", value="Demo Organization")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Financial Services", "Education", "Retail", "Other"]
        )
        
        st.markdown("#### Primary Compliance Focus")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("GDPR", value=True)
            st.checkbox("CCPA/CPRA", value=True)
            st.checkbox("HIPAA", value=False)
        
        with col2:
            st.checkbox("PIPEDA", value=False)
            st.checkbox("LGPD", value=False)
            st.checkbox("Industry-specific regulations", value=False)
        
        if st.button("Save Organization Settings", use_container_width=True):
            st.success("Organization settings saved successfully\!")
    
    with tabs[3]:
        st.markdown("### User Management")
        
        # Mock users
        users = [
            {"name": "Admin User", "email": "admin@example.com", "role": "Admin"},
            {"name": "Compliance Officer", "email": "compliance@example.com", "role": "Editor"},
            {"name": "Legal Review", "email": "legal@example.com", "role": "Viewer"}
        ]
        
        # Display users
        for user in users:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            
            with col1:
                st.write(user["name"])
            
            with col2:
                st.write(user["email"])
            
            with col3:
                st.write(user["role"])
            
            with col4:
                st.button("✏️", key=f"edit_{user['email']}")
        
        st.markdown("#### Add New User")
        
        with st.form("add_user_form"):
            new_user_cols = st.columns(3)
            
            with new_user_cols[0]:
                new_name = st.text_input("Name")
            
            with new_user_cols[1]:
                new_email = st.text_input("Email")
            
            with new_user_cols[2]:
                new_role = st.selectbox("Role", ["Admin", "Editor", "Viewer"])
            
            submit = st.form_submit_button("Add User")
            
            if submit:
                if new_name and new_email:
                    st.success(f"User {new_name} added successfully\!")
                else:
                    st.error("Please provide name and email")

elif current_view == "Logout" and st.session_state.authenticated:
    # Log out the user
    st.session_state.authenticated = False
    st.session_state.current_view = "home"
    
    st.success("You have been logged out successfully.")
    
    if st.button("Return to Home"):
        st.experimental_rerun()

scp -i /Users/christina/Desktop/GPTPP.pem integrate_ai_capabilities.py ec2-user@18.224.172.238:~/policyedgeai/dashboard/app.py

ssh -i /Users/christina/Desktop/GPTPP.pem ec2-user@18.224.172.238 "docker restart policyedgeai-dashboard"