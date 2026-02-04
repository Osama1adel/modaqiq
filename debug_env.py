import os
from dotenv import load_dotenv

# Force reload
os.environ.pop("GEMINI_API_KEY", None)

print("--- Debugging Environment ---")
loaded = load_dotenv()
print(f"load_dotenv() returned: {loaded}")

key = os.getenv("GEMINI_API_KEY")
print(f"Key value: '{key}'")
print(f"Type: {type(key)}")

if key:
    print(f"Length: {len(key)}")
    print(f"Matches 'ضع_المفتاح_هنا': {key == 'ضع_المفتاح_هنا'}")
    condition = key and key != "ضع_المفتاح_هنا"
    print(f"Active Condition (key and key != 'ضع_المفتاح_هنا'): {condition}")
else:
    print("Key is None or Empty")

print("---------------------------")
