import time
import uuid
import asyncio
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0,\
                   max_tokens=None, timeout=None)


## Define the function that calls the model
async def call_model(state: MessagesState):
    system_prompt = (
        "You are a helpful assistant. "
        "Answer all questions to the best of your ability."
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": [response]}

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)
# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

chatbot = workflow.compile(
    checkpointer=MemorySaver()
)


def test():
    # The thread id is a unique key that identifies
    # this particular conversation.
    # We'll just generate a random uuid here.
    # This enables a single application to manage conversations among multiple users.

    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    inputs = {"messages": [("human", "Hi I am Mehmet.")]}
    async def main(inputs):
        async for chunk in chatbot.astream(inputs, config):
            print(chunk["model"]["messages"][-1])
            time.sleep(0.5)

    asyncio.run(main(inputs))
