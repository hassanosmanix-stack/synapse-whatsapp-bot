from fastapi import FastAPI, Request
import requests
import json

INFOBIP_API_KEY = "7ee559bf97db52e37dea0789c647bc29-260f73b9-3e3a-4afd-ac17-c2eeb8f0a37a"
INFOBIP_BASE_URL = "https://api.infobip.com"
WHATSAPP_SENDER_ID = "254768846446"

app = FastAPI()

def send_whatsapp_message(to_number: str, message_text: str):
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

    response = requests.post(url, headers=headers, json=payload)
    print("Outbound status:", response.status_code)
    print("Outbound response:", response.text)
    return response.json()

@app.get("/")
async def root():
    return {"status": "Bot running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("INBOUND WEBHOOK:", json.dumps(data, indent=2))

    for result in data.get("results", []):
        from_number = result.get("from")
        message = result.get("message", {})
        text = message.get("text")

        if not text:
            continue

        if text.lower() == "hi":
            send_whatsapp_message(
                from_number,
                "Bot is LIVE ✅\nReply 1 to test menu."
            )
        else:
            send_whatsapp_message(
                from_number,
                "Type HI to start."
            )

        return {"status": "processed"}

    return {"status": "ignored"}

