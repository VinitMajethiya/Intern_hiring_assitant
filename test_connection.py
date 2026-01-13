import socket
import os
import sys

hostname = "api.groq.com"

print(f"Testing connectivity to {hostname}...")
try:
    # Check DNS resolution
    ip = socket.gethostbyname(hostname)
    print(f"DNS Resolution successful: {hostname} -> {ip}")
    
    # Check TCP connection (port 443 for HTTPS)
    try:
        sock = socket.create_connection((hostname, 443), timeout=5)
        print("TCP Connection to port 443 successful.")
        sock.close()
    except Exception as e:
        print(f"TCP Connection failed: {e}")

except Exception as e:
    print(f"DNS Resolution failed: {e}")
    
# Also check if we have the API key
from dotenv import load_dotenv
load_dotenv()
if os.getenv("GROQ_API_KEY"):
    print("GROQ_API_KEY is present in environment.")
else:
    print("WARNING: GROQ_API_KEY is missing from environment.")
