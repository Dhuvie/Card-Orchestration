from app.agent.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import json
import uuid
import os
import base64
from app.services.google_sheets import find_duplicate, append_row, update_row_audio
from app.services.whatsapp import send_whatsapp_notification
from app.core.config import settings

class ContactInfo(BaseModel):
    full_name: str = Field(description="Full name of the person")
    company: str = Field(description="Company name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Primary phone number")

class VoiceNoteInfo(BaseModel):
    transcript: str = Field(description="The transcript of the voice note")
    summary: str = Field(description="A brief summary of the voice note")

class EnrichmentInfo(BaseModel):
    website: str = Field(description="Company website URL")
    linkedin: str = Field(description="Company LinkedIn URL")

def get_extractor(schema):
    primary = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=settings.GOOGLE_API_KEY).with_structured_output(schema)
    fallback_1 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY).with_structured_output(schema)
    # Note: gemini-3.0-flash is a hypothetical future model fallback as requested
    fallback_2 = ChatGoogleGenerativeAI(model="gemini-3.0-flash", google_api_key=settings.GOOGLE_API_KEY).with_structured_output(schema)
    
    return primary.with_fallbacks([fallback_1, fallback_2])

async def process_input(state: AgentState) -> AgentState:
    last_message = state['messages'][-1]
    content = last_message.content
    
    # Simple router based on message prefix (set by the frontend)
    if content.startswith("image:"):
        state["current_step"] = "extracting"
        state["uploaded_card_url"] = content.split("image:")[-1].strip()
    elif content.startswith("audio:"):
        state["current_step"] = "processing_audio"
        state["voice_note"] = content.split("audio:")[-1].strip()
    elif state.get("confirmation_status") == "pending":
        if "approve" in content.lower() or "yes" in content.lower():
            state["confirmation_status"] = "approved"
            state["current_step"] = "saving"
        else:
            state["confirmation_status"] = "rejected"
            state["current_step"] = "none"
            state["messages"].append(AIMessage(content="Data discarded. You can upload another card."))
    else:
        state["current_step"] = "chatting"
        state["messages"].append(AIMessage(content="CRM System active. Please drop a visiting card image or a voice note for the last contact."))
        
    return state

async def extract_vision(state: AgentState) -> AgentState:
    try:
        base64_data = state.get("uploaded_card_url", "")
        if base64_data.startswith("data:image"):
            base64_data = base64_data.split(",")[1]
            
        extractor = get_extractor(ContactInfo)
        
        result = await extractor.ainvoke([
            HumanMessage(content=[
                {"type": "text", "text": "Extract the contact details from this business card. If any field is missing, return 'N/A'."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
            ])
        ])
        
        state["extracted_contact"] = result.model_dump() if result else {"full_name": "N/A", "company": "N/A", "email": "N/A", "phone": "N/A"}
        state["contact_id"] = str(uuid.uuid4())
        state["current_step"] = "deduplicating"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        state["current_step"] = "none"
        state["messages"].append(AIMessage(content=f"Error during Gemini extraction: {str(e)}"))
        
    return state

async def deduplicate_contact(state: AgentState) -> AgentState:
    contact = state.get("extracted_contact", {})
    email = contact.get("email", "")
    phone = contact.get("phone", "")
    
    is_duplicate = await find_duplicate(email, phone)
    state["duplicate_found"] = is_duplicate
    
    if is_duplicate:
        state["current_step"] = "none"
        state["confirmation_status"] = "none"
        state["messages"].append(AIMessage(content="This contact already exists in the system based on email/phone match."))
    else:
        state["current_step"] = "enriching"
        
    return state

async def enrich_contact(state: AgentState) -> AgentState:
    contact = state.get("extracted_contact", {})
    company = contact.get("company", "")
    
    if company and company != "N/A" and company.strip() != "":
        extractor = get_extractor(EnrichmentInfo)
        try:
            result = await extractor.ainvoke([
                HumanMessage(content=f"Find or guess the official website and LinkedIn profile for the company: {company}. Return N/A if completely unknown.")
            ])
            contact["website"] = result.website if result else "N/A"
            contact["linkedin"] = result.linkedin if result else "N/A"
        except Exception:
            contact["website"] = "N/A"
            contact["linkedin"] = "N/A"
    else:
        contact["website"] = "N/A"
        contact["linkedin"] = "N/A"
        
    state["extracted_contact"] = contact
    state["current_step"] = "confirming"
    state["confirmation_status"] = "pending"
    
    msg = f"Extracted & Enriched Details:\n" \
          f"- Name: {contact.get('full_name')}\n" \
          f"- Company: {company}\n" \
          f"- Email: {contact.get('email')}\n" \
          f"- Phone: {contact.get('phone')}\n" \
          f"- Website: {contact.get('website')}\n" \
          f"- LinkedIn: {contact.get('linkedin')}\n\n" \
          f"Please review and approve these details before saving."
          
    state["messages"].append(AIMessage(content=msg))
    return state

async def save_to_sheets(state: AgentState) -> AgentState:
    try:
        contact = state.get("extracted_contact", {})
        data = {
            "contact_id": state.get("contact_id", ""),
            "full_name": contact.get("full_name", ""),
            "company": contact.get("company", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "website": contact.get("website", ""),
            "linkedin": contact.get("linkedin", ""),
            "audio_url": state.get("audio_url", "")
        }
        await append_row(data)
        state["current_step"] = "notifying"
    except Exception as e:
        state["current_step"] = "none"
        state["messages"].append(AIMessage(content=f"Error saving to Sheets: {str(e)}"))
    return state

async def process_audio(state: AgentState) -> AgentState:
    try:
        # Assuming voice_note contains base64 string "data:audio/webm;base64,..."
        base64_audio = state.get("voice_note", "")
        if base64_audio.startswith("data:audio"):
            mime_type = base64_audio.split(";")[0].split(":")[1]
            base64_data = base64_audio.split(",")[1]
            
            extractor = get_extractor(VoiceNoteInfo)
            
            result = await extractor.ainvoke([
                HumanMessage(content=[
                    {"type": "text", "text": "Please transcribe this voice note exactly as spoken, and provide a brief summary."},
                    # LangChain Google GenAI supports media type for audio base64 data
                    {"type": "media", "mime_type": mime_type, "data": base64_data}
                ])
            ])
            
            transcript = result.transcript if result else "Failed to transcribe."
            summary = result.summary if result else "Failed to summarize."
            full_text = f"Transcript: {transcript} | Summary: {summary}"
            
            contact_id = state.get("contact_id")
            if contact_id:
                success = await update_row_audio(contact_id, full_text)
                if success:
                    state["messages"].append(AIMessage(content=f"Voice note transcribed and attached to contact: {transcript}"))
                else:
                    state["messages"].append(AIMessage(content="Failed to attach voice note to sheet."))
            else:
                state["messages"].append(AIMessage(content="No active contact to attach the voice note to."))
        
        state["current_step"] = "none"
    except Exception as e:
        state["current_step"] = "none"
        state["messages"].append(AIMessage(content=f"Error processing audio: {str(e)}"))
        
    return state

async def send_whatsapp(state: AgentState) -> AgentState:
    try:
        contact = state.get("extracted_contact", {})
        phone = contact.get("phone", "")
        # Here you would typically use an alert number, but we'll try the contact phone or a hardcoded manager phone.
        manager_phone = settings.WHATSAPP_MANAGER_PHONE or phone
        
        await send_whatsapp_notification(manager_phone, contact)
        
        state["current_step"] = "none"
        state["confirmation_status"] = "none"
        state["messages"].append(AIMessage(content="Contact saved successfully and manager notified via WhatsApp!"))
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error sending WhatsApp: {str(e)}"))
    return state
