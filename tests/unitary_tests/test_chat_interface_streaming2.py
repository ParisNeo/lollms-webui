import json

import requests

url = "http://localhost:1234/lollms_generate"

payload = {"prompt": "Once apon a time, ", "temperature": 0.1, "stream": True}

headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)

if response.status_code == 200:
    for response_chunk in response.iter_lines():
        if response_chunk:
            rc = response_chunk.decode()
            print(rc, end="", flush=True)
else:
    print("Error:", response.status_code)
