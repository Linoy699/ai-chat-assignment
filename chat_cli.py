"""
Command-Line Chat with the IAC Student API
------------------------------------------
This script lets the user have an interactive conversation with the
GPT-5-NANO model exposed by the college Student API.

Two modes are supported:
    0 - Simple chat (Chat Completions endpoint, stateless: full history is sent each turn)
    1 - Agent     (Responses API, stateful via previous_response_id)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IAC_API_KEY")

CHAT_URL = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
AGENT_URL = "https://server.iac.ac.il/api/v1/studentapi/responses"


def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def check_api_key():
    """Validate that the API key is present and has the expected format."""
    if API_KEY is None:
        print("ERROR: API key was not found.")
        print("Check that the .env file exists and contains:")
        print("IAC_API_KEY=your_key_here")
        return False

    if not API_KEY.startswith("sk-std-"):
        print("ERROR: API key format is wrong.")
        print("The key should start with sk-std-")
        return False

    print("API key loaded successfully.")
    return True


def extract_chat_answer(result):
    return result["choices"][0]["message"]["content"]


def extract_agent_answer(result):
    if "output_text" in result and result["output_text"]:
        return result["output_text"]

    if "output" in result and result["output"]:
        texts = []
        for item in result["output"]:
            content = item.get("content")
            if content is None:
                continue
            for content_item in content:
                text = content_item.get("text")
                if text:
                    texts.append(text)
        if texts:
            return "\n".join(texts)

    return "No text answer was found in the agent response."


def print_usage(result):
    """Print token-usage information so the user can monitor the quota."""
    usage = result.get("usage")
    if usage:
        print(
            f"[Tokens used - prompt: {usage.get('prompt_tokens')}, "
            f"completion: {usage.get('completion_tokens')}, "
            f"total: {usage.get('total_tokens')}]"
        )


def simple_chat():
    """Stateless Chat Completions loop. Keeps history client-side."""
    print("Simple Chat mode selected")
    print("Type exit to quit")

    messages = []

    while True:
        prompt = input("please enter your message: ").strip()

        if prompt == "":
            print("Empty message - please type something.")
            continue
        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages,
            "max_completion_tokens": 10000
        }

        try:
            response = requests.post(CHAT_URL, json=payload, headers=get_headers(), timeout=30)
        except requests.exceptions.RequestException as network_error:
            print(f"Network error: {network_error}")
            messages.pop()  # rollback the user message we just appended
            continue

        try:
            result = response.json()
        except ValueError:
            print(f"Could not decode API response. Status code: {response.status_code}")
            messages.pop()
            continue

        if response.status_code != 200:
            print("Error from API:")
            print(result)
            messages.pop()
            continue

        try:
            answer = extract_chat_answer(result)
        except (KeyError, IndexError):
            print(f"Unexpected API response: {result}")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": answer})
        print("Assistant:", answer)
        print_usage(result)


def agent_chat():
    """Stateful Responses-API loop using previous_response_id."""
    print("Agent mode selected")
    print("Type exit to quit")

    previous_response_id = None

    while True:
        prompt = input("please enter your message: ").strip()

        if prompt == "":
            print("Empty message - please type something.")
            continue
        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        payload = {
            "reasoning": {"effort": "low"},
            "instructions": "You are a helpful AI agent. Answer clearly and simply.",
            "input": prompt,
            "max_output_tokens": 1000
        }

        if previous_response_id is not None:
            payload["previous_response_id"] = previous_response_id

        try:
            response = requests.post(AGENT_URL, json=payload, headers=get_headers(), timeout=30)
        except requests.exceptions.RequestException as network_error:
            print(f"Network error: {network_error}")
            continue

        try:
            result = response.json()
        except ValueError:
            print(f"Could not decode API response. Status code: {response.status_code}")
            continue

        if response.status_code != 200:
            print("Error from API:")
            print(result)
            continue

        if result.get("error") is not None:
            print("Agent error:")
            print(result["error"])
            continue

        if "id" in result:
            previous_response_id = result["id"]

        answer = extract_agent_answer(result)
        print("Agent:", answer)
        print_usage(result)


def select_mode():
    """Ask the user which mode to run; validate the input."""
    print("please select mode:")
    print("0 - simple chat")
    print("1 - agent")

    raw = input("please select 0 for simple chat or 1 for agent: ").strip()

    if raw not in ("0", "1"):
        print("Invalid selection. Please choose 0 or 1.")
        return None

    return int(raw)


def main():
    if not check_api_key():
        return

    mode = select_mode()
    if mode is None:
        return

    if mode == 0:
        simple_chat()
    elif mode == 1:
        agent_chat()


if __name__ == "__main__":
    main()
