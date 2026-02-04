import google.generativeai as genai

API_KEY = "AIzaSyAogh5Th2Ir3zrdS7G_WQJDsPuWUEtqh-c"

print(f"Listing models with Key: {API_KEY}")

try:
    genai.configure(api_key=API_KEY)
    # Filter for models that supports generateContent
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for m in models:
        print(f"Model: {m.name}")
        
    print("\nAttempting a single small request with 'models/gemini-1.5-flash'...")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("hi")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
