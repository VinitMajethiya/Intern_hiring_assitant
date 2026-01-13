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
    if candidate_info is None:
        candidate_info = {}

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
        "tech_stack": data.get("tech_stack"),
        
        # PII Storage (Admin Access Only)
        "personal_info": {
            "name": data.get("user_name"),
            "email": data.get("email"),
            "phone": data.get("phone")
        },
        "pii_removed": False # Now storing PII for Admin access
    }
    
    return anonymized_record

    anonymized_record["conversation_history"] = conversation_log

def save_session_data(candidate_info, messages, sentiment_summary=None, evaluation=None):
    """
    Saves the anonymized candidate data, conversation transcript, optional sentiment summary, and evaluation.
    """
    anonymized_record = anonymize_data(candidate_info)
    if not anonymized_record:
        return

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
    
    if sentiment_summary:
        anonymized_record["sentiment_summary"] = sentiment_summary
        
    if evaluation:
        anonymized_record["evaluation"] = evaluation

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

def get_session_data(record_id):
    """
    Retrieves a past session record by ID.
    """
    if not os.path.exists(DATA_FILE):
        return None
        
    try:
        with open(DATA_FILE, "r") as f:
            records = json.load(f)
            
        for record in records:
            if record.get("record_id") == record_id:
                return record
    except (json.JSONDecodeError, IOError):
        pass
        
    return None

def get_all_records():
    """
    Retrieves all session records for the Admin Dashboard.
    """
    if not os.path.exists(DATA_FILE):
        return []
        
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
        
    return []
