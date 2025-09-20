import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PolicyEdgeAI Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("PolicyEdgeAI Dashboard")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Home", "API Health", "API Keys"])

if page == "Home":
    st.header("Welcome to PolicyEdgeAI Dashboard")
    st.write("This is a placeholder for your PolicyEdgeAI dashboard.")
    
    with st.expander("About PolicyEdgeAI"):
        st.write("""
        PolicyEdgeAI is a platform that helps analyze policy documents using artificial intelligence.
        """)

elif page == "API Health":
    st.header("API Health Status")
    
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            st.success("API is healthy and responding")
            st.json(response.json())
        else:
            st.error(f"API returned status code: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to connect to the API: {str(e)}")
        st.info(f"Attempted to connect to: {API_URL}")

elif page == "API Keys":
    st.header("API Keys Configuration")
    
    try:
        response = requests.get(f"{API_URL}/api-keys")
        if response.status_code == 200:
            data = response.json()
            col1, col2 = st.columns(2)
            
            with col1:
                if data.get("openai") == "Configured":
                    st.success("OpenAI API Key: Configured")
                else:
                    st.error("OpenAI API Key: Not configured")
            
            with col2:
                if data.get("anthropic") == "Configured":
                    st.success("Anthropic API Key: Configured")
                else:
                    st.error("Anthropic API Key: Not configured")
        else:
            st.error(f"API returned status code: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to connect to the API: {str(e)}")
