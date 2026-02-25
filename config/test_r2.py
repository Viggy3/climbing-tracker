import requests

for i in range(8):
    r = requests.get("https://climbing.hariviggy.com/api/test_rate_limit")
    print(f"Request {i+1}: {r.status_code} - {r.text}")