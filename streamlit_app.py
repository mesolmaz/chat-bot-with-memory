import asyncio
import time
import json
import requests
import uuid
import streamlit as st
from chatbot import chatbot
from langchain_core.messages import HumanMessage

st.title("Simple chat-bot")
url = "http://localhost:8000/invocations/"

async def async_response_generator(placeholder, prompt, config):

    input = {"prompt": prompt, "config": config}
    payload = json.dumps(input)
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        streamed_text = json.loads(resp.content.decode())["text"]
        placeholder.write(streamed_text)
        st.session_state.messages.append({"type": "assistant", "content": streamed_text})
    else:
        placeholder.write("Error: ", resp.status_code)

async def main() -> None:
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id
        st.session_state.config = config

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["type"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"type": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        ai_placeholder = st.chat_message("assistant")
        await async_response_generator(ai_placeholder, prompt, st.session_state.config)

if __name__ == "__main__":
    asyncio.run(main())