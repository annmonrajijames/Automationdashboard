import requests
import json

# Replace with your actual API key from Google Cloud's Gemini API
API_KEY = "Enter your API key"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

# The payload to be sent to the API
data = {
    "contents": [
        {
            "parts": [
                {"text": "AI"}
            ]
        }
    ]
}

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check the response status and print the result
if response.status_code == 200:
    result = response.json()
    print("Response from Gemini API:", json.dumps(result, indent=4))
else:
    print(f"Error: {response.status_code}, {response.text}")
