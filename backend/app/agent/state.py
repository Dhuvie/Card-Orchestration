from typing import TypedDict, List, Optional, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    session_id: str
    messages: List[BaseMessage]
    uploaded_card_url: Optional[str]
    extracted_contact: Optional[dict]
    contact_id: Optional[str]
    voice_note: Optional[str]
    audio_url: Optional[str]
    confirmation_status: str # 'pending', 'approved', 'rejected', 'none'
    current_step: str # 'chatting', 'extracting', 'deduplicating', 'confirming', 'saving', 'processing_audio', 'notifying', 'none'
    duplicate_found: bool
