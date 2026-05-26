"""
API Connection Test Script
--------------------------
This script performs a sanity check on the IAC Student API.
It loads the personal API key from the .env file (so the key is never
written in code or pushed to Git) and sends a minimal request in order
to verify that the key is valid and that the server responds.

Usage:
    python get_api_key.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IAC_API_KEY")
CHAT_URL = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"


def test_api_connection():
    """Send a minimal request and report whether the API responds correctly."""
    if API_KEY is None:
        print("ERROR: IAC_API_KEY was not found in the environment.")
        print("Make sure a .env file exists and contains: IAC_API_KEY=your_key_here")
        return

    if not API_KEY.startswith("sk-std-"):
        print("ERROR: API key format is invalid (it should start with sk-std-).")
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": "Reply with the single word: OK."}
        ],
        "max_completion_tokens": 10
    }

    try:
        response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=15)
    except requests.exceptions.RequestException as network_error:
        print(f"Network error while contacting the API: {network_error}")
        return

    if response.status_code != 200:
        print(f"API returned an error. Status code: {response.status_code}")
        print(f"Response body: {response.text}")
        return

    result = response.json()
    answer = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})

    print("API connection successful.")
    print(f"Model reply: {answer}")
    if usage:
        print(
            "Tokens used in this test - "
            f"prompt: {usage.get('prompt_tokens')}, "
            f"completion: {usage.get('completion_tokens')}, "
            f"total: {usage.get('total_tokens')}"
        )


if __name__ == "__main__":
    test_api_connection()
