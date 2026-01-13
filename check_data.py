import json
import os

DATA_FILE = "anonymized_records.json"

if not os.path.exists(DATA_FILE):
    print("File does not exist.")
else:
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if not content:
                print("File is empty.")
            else:
                data = json.loads(content)
                print(f"JSON is valid. Found {len(data)} records.")
                for i, r in enumerate(data):
                    print(f"Record {i}: ID={r.get('record_id')}, Name={r.get('personal_info', {}).get('name')}")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        # Print the last few chars to see if it was cut off
        print(f"Last 100 chars: {content[-100:]}")
