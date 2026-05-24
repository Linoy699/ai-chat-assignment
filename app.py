import os
import requests
import streamlit as st
from dotenv import load_dotenv

# -------------------------------------------------
# Load API key from .env file
# -------------------------------------------------
load_dotenv()

API_KEY = os.getenv("IAC_API_KEY")

CHAT_URL = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"


# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="LLM Chat",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Chat with an LLM")
st.caption("Streamlit frontend for user ↔ LLM chat")


# -------------------------------------------------
# Check API key
# -------------------------------------------------
if API_KEY is None:
    st.error("API key was not found. Please check that your .env file exists.")
    st.stop()

if not API_KEY.startswith("sk-std-"):
    st.error("API key format is wrong. The key should start with sk-std-")
    st.stop()


# -------------------------------------------------
# Headers for API request
# -------------------------------------------------
def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


# -------------------------------------------------
# Session state - chat history
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "If the user writes in Hebrew, answer in Hebrew. "
                "If the user writes in English, answer in English. "
                "Keep answers clear, simple, and helpful."
            )
        }
    ]


# -------------------------------------------------
# Sidebar settings
# -------------------------------------------------
with st.sidebar:
    st.header("Settings")

    max_tokens = st.slider(
        "Max completion tokens",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )

    st.write("Model: GPT-5-NANO")

    if st.button("Clear chat"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "If the user writes in Hebrew, answer in Hebrew. "
                    "If the user writes in English, answer in English. "
                    "Keep answers clear, simple, and helpful."
                )
            }
        ]
        st.rerun()


# -------------------------------------------------
# Function to call the LLM API
# -------------------------------------------------
def get_llm_response(messages, max_tokens):
    payload = {
        "messages": messages,
        "max_completion_tokens": max_tokens
    }

    response = requests.post(
        CHAT_URL,
        json=payload,
        headers=get_headers()
    )

    try:
        result = response.json()
    except Exception:
        return f"Error: could not read API response. Status code: {response.status_code}"

    if response.status_code != 200:
        return f"Error from API: {result}"

    if "choices" not in result:
        return f"Unexpected response from API: {result}"

    answer = result["choices"][0]["message"]["content"]

    if answer is None or answer.strip() == "":
        return f"המודל החזיר תשובה ריקה. תשובת השרת המלאה: {result}"

    return answer


# -------------------------------------------------
# Display chat history
# -------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# -------------------------------------------------
# Chat input
# -------------------------------------------------
user_prompt = st.chat_input("Type your message...")

if user_prompt:
    # Add user message to history
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("Thinking...")

        try:
            assistant_reply = get_llm_response(
                messages=st.session_state.messages,
                max_tokens=max_tokens
            )

            response_placeholder.markdown(assistant_reply)

        except Exception as error:
            assistant_reply = f"General error: {str(error)}"
            response_placeholder.error(assistant_reply)

    # Save assistant response to history
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )