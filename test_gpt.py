import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

try:
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    print(f"API Key starts with: {api_key[:10]}...")
    
    client = OpenAI(api_key=api_key)
    print("\nTesting OpenAI API...")
    
    # Simple test request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Give me one interesting fact about space in one sentence."}
        ],
        max_tokens=100
    )
    
    print("\nGot response from API:")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"\nError occurred: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")