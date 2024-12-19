import json

import requests

url = "http://localhost:9600/delete_message"

payload = {"client_id": "test", "id": 283}

headers = {"accept": "application/json", "Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print(response.text)
