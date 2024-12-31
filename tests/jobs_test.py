import requests

url = "http://127.0.0.1:5000/jobs"

data = {
    "search_term": "software engineer",
    "location": "San Francisco",
    "results_wanted": 10,
    "site_name": "linkedin",
    "is_remote": True,
    "use_tor": False
}

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Response:")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")
