import google.generativeai as genai
import os

# The key from the screenshot and user message
API_KEY = 

print(f"Testing Key: {API_KEY}")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro-latest')
    response = model.generate_content("Hello, are you working?")
    print("Success! Response from Gemini:")
    print(response.text)
except Exception as e:
    print(f"Failed! Error: {e}")
