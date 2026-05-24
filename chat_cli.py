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


def simple_chat():
    print("Simple Chat mode selected")
    print("Type exit to quit")

    messages = []

    while True:
        prompt = input("please enter your message: ")

        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "messages": messages,
            "max_completion_tokens": 1000
        }

        try:
            response = requests.post(
                CHAT_URL,
                json=payload,
                headers=get_headers()
            )

            result = response.json()

            if response.status_code != 200:
                print("Error from API:")
                print(result)
                continue

            answer = extract_chat_answer(result)

            messages.append({
                "role": "assistant",
                "content": answer
            })

            print("Assistant:", answer)

        except Exception as error:
            print("General error:")
            print(error)


def agent_chat():
    print("Agent mode selected")
    print("Type exit to quit")

    previous_response_id = None

    while True:
        prompt = input("please enter your message: ")

        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        payload = {
            "reasoning": {
                "effort": "low"
            },
            "instructions": "You are a helpful AI agent. Answer clearly and simply.",
            "input": prompt,
            "max_output_tokens": 1000
        }

        if previous_response_id is not None:
            payload["previous_response_id"] = previous_response_id

        try:
            response = requests.post(
                AGENT_URL,
                json=payload,
                headers=get_headers()
            )

            result = response.json()

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

        except Exception as error:
            print("General error:")
            print(error)


if not check_api_key():
    exit()

print("please select mode:")
print("0 - simple chat")
print("1 - agent")

state = int(input("please select 0 for simple chat or 1 for agent: "))

if state == 0:
    simple_chat()

elif state == 1:
    agent_chat()

else:
    print("Invalid selection. Please choose 0 or 1.")