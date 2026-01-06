import os
from fastapi import FastAPI, Request, HTTPException
import requests
import json

# --- Configuration (TEMPORARY HARDCODED FOR DEBUGGING) ---
# NOTE: This is temporary. We will revert this after testing.
INFOBIP_API_KEY = "7ee559bf97db52e37dea0789c647bc29-260f73b9-3e3a-4afd-ac17-c2eeb8f0a37a"
INFOBIP_BASE_URL = "https://api.infobip.com"
WHATSAPP_SENDER_ID = "0316B1A51F2E9C89ABFB2744DDCC3319"

app = FastAPI()

def send_whatsapp_message(to_number: str, message_text: str):
    """Sends a text message using the Infobip WhatsApp API."""
    url = f"{INFOBIP_BASE_URL}/whatsapp/1/message/text"
    
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "from": WHATSAPP_SENDER_ID,
                "to": to_number,
                "message": {
                    "text": message_text
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Message sent successfully to {to_number}. Status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {to_number}: {e}")
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Synapse Digital WhatsApp Bot Engine is running."}

@app.post("/webhook")
async def webhook(request: Request):
    """Handles incoming messages from Infobip."""
    try:
        data = await request.json()
        print(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # Infobip webhook structure is complex. We look for the first message text.
        for result in data.get("results", []):
            if result.get("message", {}).get("type") == "TEXT":
                from_number = result.get("from")
                text = result.get("message", {}).get("text")
                
                # Simple Welcome Flow Logic (Day 1)
                if text.lower() == "hi":
                    response_text = (
                        "👋 Welcome to Synapse Digital's 'Ignite' Demo!\n\n"
                        "I am your fully automated ordering bot.\n\n"
                        "How can I help you today?\n"
                        "1. View Menu\n"
                        "2. Place Order\n"
                        "3. Talk to Staff"
                    )
                    send_whatsapp_message(from_number, response_text)
                else:
                    # Default response for unhandled messages
                    send_whatsapp_message(from_number, "I'm sorry, I didn't understand that. Please type 'Hi' to see the main menu.")
                
                # We only process the first message in the batch for simplicity
                return {"status": "success", "message": "Message processed"}

        # Handle cases where no text message was found (e.g., status updates, media)
        return {"status": "ignored", "message": "No text message found in payload"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Return 200 OK to Infobip even on internal error to prevent retries, 
        # but log the error for debugging.
        return {"status": "error", "message": str(e)}
