import json
import uuid
import os
from datetime import datetime

DATA_FILE = "anonymized_records.json"

def anonymize_data(candidate_info):
    """
    Creates an anonymized copy of the candidate info.
    Removes direct PII (Name, Email, Phone) and generates a UUID.
    """
    if not candidate_info:
        return None

    # explicit copy to avoid modifying the session state object if passed directly
    data = candidate_info.copy()
    
    # Generate a unique ID for this record
    record_id = str(uuid.uuid4())
    
    anonymized_record = {
        "record_id": record_id,
        "timestamp": datetime.now().isoformat(),
        # Keep technical/professional info
        "experience": data.get("Experience"),
        "position": data.get("Position"),
        "location": data.get("Location"), # Location can be semi-sensitive, but usually city-level is okay for aggregation. 
                                          # For strict GDPR, we might generalize or remove this too. Keeping for now.
        "tech_stack": data.get("Tech Stack"),
        # We explicitly DO NOT include Name, Email, Phone
        "pii_removed": True
    }
    
    return anonymized_record

def save_session_data(candidate_info, messages):
    """
    Saves the anonymized candidate data and the conversation transcript.
    The transcript itself might contain PII if the user typed it, 
    so in a real system we would run a PII scrubber on the text too.
    For this 'Simulated' requirement, we will just save the structured anonymized info
    and a flag that transcript is stored (or store it if needed for the 'technical responses').
    """
    anonymized_record = anonymize_data(candidate_info)
    if not anonymized_record:
        return

    # Extract Q&A pairs might be redundant if we just dump the chat, 
    # but let's try to extract technical content if possible. 
    # For now, we save the full conversation history attached to the anonymized ID.
    # Note: In a PROD GDPR environment, we'd scrub the 'messages' text too.
    
    conversation_log = []
    for msg in messages:
        role = "unknown"
        if hasattr(msg, "type"):
            role = msg.type
        elif hasattr(msg, "role"):
            role = msg.role
            
        content = msg.content
        conversation_log.append({"role": role, "content": content})

    anonymized_record["conversation_history"] = conversation_log

    # Atomic-ish write to JSON file
    records = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                records = json.load(f)
        except json.JSONDecodeError:
            records = []
    
    records.append(anonymized_record)
    
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

    return anonymized_record["record_id"]
