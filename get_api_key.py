import requests
#ask user whether he wants to chat with simpale LLM or an agent?
#if user wants chat complecettion

headers = {"Authorization": "Bearer sk-std-YOUR-KEY"}
payload = {
    "messages": [
        {
            "role": "user",
            "content": "what is better a cat or a dog? give a short, up to 50 words answer."
        }
    ],
    "max_completion_tokens": 500
}

r = requests.post("https://server.iac.ac.il/api/v1/studentapi/chat/completions",
                  json=payload, headers=headers)
print(r.json())
