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
            "content": "What are some popular AI frameworks for robotics?",
        },
    ],
    "max_tokens": 100,
    "temperature": 0.5,
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
    completion = data["choices"][0]["message"]["content"]
    print(completion)
else:
    print("Error:", response.status_code)
