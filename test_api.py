import requests
import json
import datetime

# Setup Data
BASE_URL = "http://127.0.0.1:8000/api/cases/submit_and_validate/"

# Dates: Incident 30 days ago (Should be VALID)
incident_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

payload = {
    "title": "Unjust Termination",
    "description": "I was terminated from my job without a valid reason and without notice.",
    "incident_date": incident_date,
    "grievance_date": incident_date, # Same day
    "court_type": "Administrative",
    "claim_amount": "50000.00",
    "plaintiff": {
        "name": "Ahmed Al-Muwadhaf",
        "party_type": "INDIVIDUAL",
        "role": "PLAINTIFF",
        "national_id": "1010101010"
    },
    "defendant": {
        "name": "Ministry of X",
        "party_type": "GOVERNMENT",
        "role": "DEFENDANT"
    },
    "documents": []
}

print("Sending Request to:", BASE_URL)
print(json.dumps(payload, indent=2))

try:
    response = requests.post(BASE_URL, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 201:
        print("\nSuccess! API Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("\nFailed!")
        print(response.text)

except Exception as e:
    print(f"\nError: {e}")
