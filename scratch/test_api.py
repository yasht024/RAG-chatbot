import urllib.request
import json
import urllib.error

url = "http://localhost:8000/v1/questions"
payload = {
    "query": "What is the riskometer classification?",
    "conversation_id": "test_conv",
    "history": [],
}
data = json.dumps(payload).encode("utf-8")
headers = {"Content-Type": "application/json", "Origin": "http://localhost:3000"}
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Headers: {response.headers}")
        print(f"Body: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Headers: {e.headers}")
    print(f"Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Exception: {e}")
