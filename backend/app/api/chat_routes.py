from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from app.agent.graph import app as agent_app
import base64

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat/{session_id}")
async def chat(session_id: str, message: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    content = ""
    
    if file:
        file_bytes = await file.read()
        mime_type = file.content_type
        base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
        
        if file.content_type.startswith("image/"):
            content = f"image:data:{mime_type};base64,{base64_encoded}"
        elif file.content_type.startswith("audio/"):
            content = f"audio:data:{mime_type};base64,{base64_encoded}"
        else:
            return {"error": "Unsupported file type."}
    elif message:
        content = message
    else:
        return {"error": "No message or file provided."}
        
    config = {"configurable": {"thread_id": session_id}}
    
    # We invoke the graph. It automatically uses MongoDB checkpointer internally
    # to maintain state per session_id (thread_id)
    state_input = {"messages": [HumanMessage(content=content)]}
    
    # Invoke the graph asynchronously
    new_state = await agent_app.ainvoke(state_input, config)
    
    # Retrieve the last AI message
    last_message = new_state["messages"][-1].content
    
    return {
        "response": last_message, 
        "state": {
            "current_step": new_state.get("current_step"),
            "confirmation_status": new_state.get("confirmation_status"),
            "extracted_contact": new_state.get("extracted_contact"),
            "contact_id": new_state.get("contact_id")
        }
    }
