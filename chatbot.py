import time
import uuid
import asyncio
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0,\
                   max_tokens=None, timeout=None)

# # Define the function that calls the model
# def call_model(state: MessagesState):
#     system_prompt = (
#         "You are a helpful assistant. "
#         "Answer all questions to the best of your ability."
#     )
#     messages = [SystemMessage(content=system_prompt)] + state["messages"]
#     response = model.invoke(messages)
#     return {"messages": response}

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
 
# The thread id is a unique key that identifies
# this particular conversation.
# We'll just generate a random uuid here.
# This enables a single application to manage conversations among multiple users.
# thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}

# input_message = HumanMessage(content="hi! I'm bob")
# for event in chatbot.stream({"messages": [input_message]}, config, stream_mode="values"):
#     event["messages"][-1].pretty_print()

# # # Here, let's confirm that the AI remembers our name!
# # input_message = HumanMessage(content="what was my name?")
# # for event in chatbot.stream({"messages": [input_message]}, config, stream_mode="values"):
# #     event["messages"][-1].pretty_print()

# thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}
# print(chatbot.invoke(
#     {"messages": [HumanMessage(content="Hi I am Mehmet.")]},
#     config=config))

# print(chatbot.invoke(
#     {"messages": [HumanMessage(content="what was my name?")]},
#     config=config))

# thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# inputs = {"messages": [("human", "Hi I am Mehmet.")]}
# async def main(inputs):
#     chunks = []
#     async for chunk in chatbot.astream(inputs, config):
#         print(chunk["model"]["messages"][-1])
#         time.sleep(0.5)

# asyncio.run(main(inputs))
