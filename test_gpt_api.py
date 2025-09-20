import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set base URL for the API
BASE_URL = "http://localhost:8000"  # Update this if your server is running elsewhere

def test_simple_chat():
    """Test the simple chat endpoint"""
    endpoint = f"{BASE_URL}/gpt/simple-chat"
    
    payload = {
        "prompt": "What is the first step in building a compliant GPT product?",
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== Simple Chat Success ===")
            print(f"Model: {data.get('model', 'unknown')}")
            print("\nResponse:")
            print(data.get('text', 'No text returned'))
        else:
            print(f"\n=== Simple Chat Error ({response.status_code}) ===")
            print(response.text)
    except Exception as e:
        print(f"Error calling API: {str(e)}")

def test_gpt_providers():
    """Test the providers endpoint to check available models"""
    endpoint = f"{BASE_URL}/gpt/providers"
    
    try:
        # This endpoint requires authentication
        # For testing purposes, you might need to disable auth in the API or add proper auth
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== Available Providers ===")
            print(json.dumps(data, indent=2))
        else:
            print(f"\n=== Providers Error ({response.status_code}) ===")
            print(response.text)
    except Exception as e:
        print(f"Error calling API: {str(e)}")

if __name__ == "__main__":
    print("Testing GPT API endpoints...")
    
    # Check if API key is configured
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key and not anthropic_api_key:
        print("\n⚠️ Warning: No API keys configured. Tests will likely fail.")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
    
    # Run tests
    test_simple_chat()
    test_gpt_providers()