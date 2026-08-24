import urllib.request
import json
import urllib.error

url = "http://localhost:8000/v1/questions"
headers = {
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "Content-Type"
}
req = urllib.request.Request(url, headers=headers, method="OPTIONS")

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Headers: {response.headers}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Headers: {e.headers}")
except Exception as e:
    print(f"Exception: {e}")
