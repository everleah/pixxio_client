import requests
import json

# Credentials and endpoint
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

API_KEY = require_api_key()
BASE_URL = f"https://{test_host()}/api/v1/metadata/standard"

# Example: get all standard metadata fields with responseFields
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

params = {
    # Try with and without responseFields to test error
    "responseFields": ["id", "name", "editType", "selectionOptions"],
}

# Option 1: responseFields as repeated query params
response = requests.get(BASE_URL, headers=headers, params=params)
print("Status code:", response.status_code)
print("Response:", response.text)

# Option 2: responseFields as comma-separated string
params2 = {
    "responseFields": ",".join(["id", "name", "editType", "selectionOptions"]),
}
response2 = requests.get(BASE_URL, headers=headers, params=params2)
print("\nStatus code (comma-separated):", response2.status_code)
print("Response (comma-separated):", response2.text)

# Option 3: no responseFields
response3 = requests.get(BASE_URL, headers=headers)
print("\nStatus code (no responseFields):", response3.status_code)
print("Response (no responseFields):", response3.text)
