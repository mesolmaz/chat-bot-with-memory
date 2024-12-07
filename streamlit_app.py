import asyncio
import time
import uuid
from pydantic import BaseModel, Field
from typing import AsyncGenerator
import streamlit as st
from chatbot import chatbot
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

st.title("Simple chat-bot")

def response_generator(prompt, config):
    response = chatbot.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
    for word in response['messages'][-1].content.split():
        yield word + " "
        time.sleep(0.05)

async def async_response_generator(prompt, config):
    response = await chatbot.ainvoke({"messages": [HumanMessage(content=prompt)]}, config=config)
    for word in response['messages'][-1].content.split():
        yield word + " "
        time.sleep(0.05)

async def main() -> None:
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = uuid.uuid4()
            config = {"configurable": {"thread_id": thread_id}}
            messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id
        st.session_state.config = config
        # print(st.session_state.thread_id)
        # print(st.session_state.config)


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

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # response = st.write_stream(response_generator(prompt, st.session_state.config))
            result = []
            async for item in async_response_generator(prompt, st.session_state.config):
                result.append(item)
            response = st.write("".join(result))
        # Add assistant response to chat history
        st.session_state.messages.append({"type": "assistant", "content": response})


if __name__ == "__main__":
    asyncio.run(main())
    # main() 