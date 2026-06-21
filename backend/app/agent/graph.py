from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import process_input, extract_vision, deduplicate_contact, enrich_contact, save_to_sheets, send_whatsapp, process_audio
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient
import os

def route_after_process(state: AgentState) -> str:
    step = state.get("current_step")
    if step == "extracting":
        return "extract_vision"
    elif step == "saving":
        return "save_to_sheets"
    elif step == "processing_audio":
        return "process_audio"
    return END

def route_after_extract(state: AgentState) -> str:
    step = state.get("current_step")
    if step == "deduplicating":
        return "deduplicate_contact"
    return END

def route_after_dedup(state: AgentState) -> str:
    if state.get("duplicate_found"):
        return END
    return "enrich_contact"

def route_after_enrich(state: AgentState) -> str:
    return END

def route_after_save(state: AgentState) -> str:
    return "send_whatsapp"

workflow = StateGraph(AgentState)

workflow.add_node("process_input", process_input)
workflow.add_node("extract_vision", extract_vision)
workflow.add_node("deduplicate_contact", deduplicate_contact)
workflow.add_node("enrich_contact", enrich_contact)
workflow.add_node("save_to_sheets", save_to_sheets)
workflow.add_node("send_whatsapp", send_whatsapp)
workflow.add_node("process_audio", process_audio)

workflow.set_entry_point("process_input")

workflow.add_conditional_edges("process_input", route_after_process, {
    "extract_vision": "extract_vision",
    "save_to_sheets": "save_to_sheets",
    "process_audio": "process_audio",
    END: END
})

workflow.add_conditional_edges("extract_vision", route_after_extract, {
    "deduplicate_contact": "deduplicate_contact",
    END: END
})

workflow.add_conditional_edges("deduplicate_contact", route_after_dedup, {
    "enrich_contact": "enrich_contact",
    END: END
})

workflow.add_conditional_edges("enrich_contact", route_after_enrich, {
    END: END
})

workflow.add_conditional_edges("save_to_sheets", route_after_save, {
    "send_whatsapp": "send_whatsapp"
})

workflow.add_edge("send_whatsapp", END)
workflow.add_edge("process_audio", END)

# Production Checkpointer Setup
mongo_uri = os.getenv("MONGODB_URL")
if mongo_uri:
    client = AsyncIOMotorClient(mongo_uri)
    checkpointer = AsyncMongoDBSaver(client)
    app = workflow.compile(checkpointer=checkpointer)
else:
    # Fallback for mock local testing without DB
    from langgraph.checkpoint.memory import MemorySaver
    app = workflow.compile(checkpointer=MemorySaver())
