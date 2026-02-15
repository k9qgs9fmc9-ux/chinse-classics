import asyncio
import json
from typing import Any, AsyncGenerator
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from app.agent.graph import create_graph

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@router.post("/stream")
async def stream_chat(request: ChatRequest, req: Request):
    """
    Stream chat response using SSE (Server-Sent Events)
    """
    app = create_graph()
    
    async def event_generator() -> AsyncGenerator[dict, None]:
        # Initial inputs
        inputs = {"question": request.message, "messages": [], "documents": [], "generation": ""}
        
        # Stream the graph execution
        # Note: app.stream returns a generator of state updates
        try:
            # Real streaming response from LangGraph using astream_events for token-level streaming
            async for event in app.astream_events(inputs, version="v1"):
                kind = event["event"]
                
                # Capture LLM streaming tokens
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "event": "message",
                            "data": json.dumps({"type": "token", "content": content})
                        }
                # Capture Tool outputs (optional status updates)
                elif kind == "on_tool_start":
                    yield {
                        "event": "message",
                        "data": json.dumps({"type": "status", "content": f"Using tool: {event['name']}..."})
                    }
            
            yield {
                "event": "message",
                "data": json.dumps({"type": "done", "content": ""})
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())

@router.post("/")
async def chat(request: ChatRequest):
    """
    Standard chat endpoint (non-streaming)
    """
    app = create_graph()
    inputs = {"question": request.message, "messages": [], "documents": [], "generation": ""}
    
    # Run the graph
    result = await app.ainvoke(inputs)
    
    return {
        "response": result.get("generation", "No response generated"),
        "session_id": request.session_id
    }
