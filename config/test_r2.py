import requests
import datetime

print("Starting test at:", datetime.datetime.now())
for i in range(25):
    r = requests.post("https://climbing.hariviggy.com/api/get_upload_url",
                      json={"filename": "test.jpg", "content_type": "image/jpeg", "tracker_id": "test"})
    print(f"Request {i+1}: {r.status_code}")
    print("Test completed at:", datetime.datetime.now())