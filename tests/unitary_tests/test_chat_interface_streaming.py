import json

import requests

url = "http://localhost:1234/v1/chat/completions"

payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are a research engineer specialized in the applications of AI in robotics.",
        },
        {
            "role": "user",
            "content": "List a number of libraries I can use for robotics.",
        },
    ],
    "max_tokens": 100,
    "temperature": 0.5,
    "stream": True,
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)

if response.status_code == 200:
    for response_chunk in response.iter_lines():
        if response_chunk:
            rc = response_chunk.decode()
            rc = json.loads(rc)
            print(rc["choices"][0]["delta"]["content"])
else:
    print("Error:", response.status_code)
