import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ API key not found in .env. Please create a .env file with your OPENAI_API_KEY.")
else:
    print("✅ API key found.")
    try:
        # Initialize the client with your API key
        client = OpenAI(api_key=api_key)
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What is the first step in building a compliant GPT product?"}
            ],
            max_tokens=100
        )
        
        print("✅ GPT-4 API call succeeded! Here's the response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("❌ GPT-4 API call failed:", str(e))