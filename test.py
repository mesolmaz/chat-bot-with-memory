
import time
import uuid
import asyncio
import json
import requests
from chatbot import chatbot
# from vllm.utils import random_uuid

url = "http://localhost:8000/invocations/"

def test1():
    # The thread id is a unique key that identifies
    # this particular conversation.
    # We'll just generate a random uuid here.
    # This enables a single application to manage conversations among multiple users.

    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    inputs = {"messages": [("human", "Hi I am Sam.")]}
    async def main(inputs):
        async for chunk in chatbot.astream(inputs, config):
            print(chunk["model"]["messages"][-1])
            time.sleep(0.5)

    asyncio.run(main(inputs))

def test2():
    # The thread id is a unique key that identifies
    # this particular conversation.
    # We'll just generate a random uuid here.
    # This enables a single application to manage conversations among multiple users.

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    prompt = "Hi I am Sam."
    input = {'prompt': prompt, 'config': config}
    payload = json.dumps(input)
    resp = requests.post(url, data=payload)
    print(resp)

if __name__ == "__main__":
    # test1()
    test2()