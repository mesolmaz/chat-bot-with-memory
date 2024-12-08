import time
import uuid
import asyncio
import json
import uvicorn
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from langchain_core.messages import SystemMessage, HumanMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0,\
                   max_tokens=None, timeout=None)

app = FastAPI()

async def call_model(state: MessagesState):
    system_prompt = (
        "You are a helpful assistant. "
        "Answer all questions to the best of your ability."
    )
    state["messages"] = [SystemMessage(content=system_prompt)] + state["messages"]
    selected_messages = trim_messages(
        state["messages"],
        token_counter=len,  # <-- len will simply count the number of messages rather than tokens
        max_tokens=5,  # <-- allow up to 5 messages.
        strategy="last",
        # Most chat models expect that chat history starts with either:
        # (1) a HumanMessage or
        # (2) a SystemMessage followed by a HumanMessage
        # start_on="human" makes sure we produce a valid chat history
        start_on="human",
        # Usually, we want to keep the SystemMessage
        # if it's present in the original history.
        # The SystemMessage has special instructions for the model.
        include_system=True,
        allow_partial=False,
    )
    response = await model.ainvoke(selected_messages)
    return {"messages": [response]}

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)
# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
chatbot = workflow.compile(
    checkpointer=MemorySaver()
)

@app.get('/ping')
async def ping():
    return {"message": "ok"}

@app.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)

@app.post("/invocations")
async def generate(request: Request) -> Response:

    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    config = request_dict.pop("config")

    async def stream_results() -> AsyncGenerator[bytes, None]:
        streamed_text = ""
        async for chunk in chatbot.astream({"messages": [HumanMessage(content=prompt)]}, config=config):
            streamed_text = streamed_text + chunk["model"]["messages"][-1].content
            ret = {"text": streamed_text}
            yield (json.dumps(ret)).encode("utf-8")

    return StreamingResponse(stream_results())

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)