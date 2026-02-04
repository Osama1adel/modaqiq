import google.generativeai as genai

API_KEY = "AIzaSyAogh5Th2Ir3zrdS7G_WQJDsPuWUEtqh-c"

print(f"Listing models with Key: {API_KEY}")

try:
    genai.configure(api_key=API_KEY)
    for m in genai.list_models():
        print(f"Model: {m.name}, Supported Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Failed to list models! Error: {e}")
