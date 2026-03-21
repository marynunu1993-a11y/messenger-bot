"""
Facebook Messenger AI Auto Reply Bot
=====================================
ဒီ Bot က Facebook Page Messenger ကနေ လာတဲ့ message တွေကို
OpenAI GPT Model သုံးပြီး အလိုအလျောက် ဖြေပေးပါတယ်။

Requirements:
- Python 3.8+
- Flask
- requests
- openai
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# ===== Configuration =====
# .env file ထဲမှာ ထည့်ထားတဲ့ environment variables တွေကို ဖတ်ပါတယ်
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_verify_token_123")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# OpenAI Model ရွေးချယ်ခြင်း (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4.1-mini")

# System Prompt - Bot ရဲ့ အပြုအမူကို သတ်မှတ်ပေးတာ
# ဒီနေရာမှာ သင့် business အတွက် customize လုပ်နိုင်ပါတယ်
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", """
သင်သည် Facebook Page ၏ Customer Service Assistant ဖြစ်ပါသည်။
ယဉ်ကျေးစွာ၊ အကူအညီပေးနိုင်စွာ ဖြေကြားပေးပါ။
မြန်မာဘာသာနဲ့ မေးရင် မြန်မာဘာသာနဲ့ ဖြေပါ။
English နဲ့ မေးရင် English နဲ့ ဖြေပါ။
တိုတိုရှင်းရှင်း ဖြေပေးပါ။
""".strip())

# Facebook Graph API version
GRAPH_API_VERSION = "v21.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# ===== Logging Setup =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ===== Flask App =====
app = Flask(__name__)

# ===== OpenAI Client =====
client = None
if OPENAI_API_KEY:
    client = OpenAI()
    logger.info("OpenAI client initialized successfully.")
else:
    logger.warning("OPENAI_API_KEY not set. AI replies will not work.")

# ===== Conversation History (In-Memory) =====
# Production မှာ Redis သို့မဟုတ် Database သုံးသင့်ပါတယ်
conversation_history = {}
MAX_HISTORY = 10  # conversation history ဘယ်နှစ်ခု သိမ်းမလဲ


# ===== Helper Functions =====

def get_ai_response(sender_id: str, user_message: str) -> str:
    """
    OpenAI API ကို သုံးပြီး AI response ရယူပါတယ်။
    Conversation history ကိုလည်း ထည့်သွင်းစဉ်းစားပါတယ်။
    """
    if not client:
        return "⚠️ AI service is not configured. Please contact the page admin."

    try:
        # Conversation history ရယူ
        if sender_id not in conversation_history:
            conversation_history[sender_id] = []

        history = conversation_history[sender_id]

        # User message ကို history ထဲ ထည့်
        history.append({"role": "user", "content": user_message})

        # History limit ထိန်းသိမ်း
        if len(history) > MAX_HISTORY * 2:
            history = history[-(MAX_HISTORY * 2):]
            conversation_history[sender_id] = history

        # OpenAI API call
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        ai_reply = response.choices[0].message.content.strip()

        # AI reply ကို history ထဲ ထည့်
        history.append({"role": "assistant", "content": ai_reply})
        conversation_history[sender_id] = history

        logger.info(f"AI Response for {sender_id}: {ai_reply[:100]}...")
        return ai_reply

    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return "ခဏလေး စောင့်ပေးပါ။ Technical issue ရှိနေပါတယ်။ နောက်မှ ထပ်စမ်းကြည့်ပေးပါ။"


def send_message(recipient_id: str, message_text: str) -> bool:
    """
    Facebook Send API ကို သုံးပြီး message ပြန်ပို့ပါတယ်။
    Message ရှည်ရင် 2000 character စီ ခွဲပြီး ပို့ပါတယ်။
    """
    import requests

    if not PAGE_ACCESS_TOKEN:
        logger.error("PAGE_ACCESS_TOKEN is not set!")
        return False

    url = f"{GRAPH_API_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    # Facebook Messenger message limit: 2000 characters
    max_length = 2000
    messages = [message_text[i:i + max_length]
                for i in range(0, len(message_text), max_length)]

    success = True
    for msg in messages:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": msg},
            "messaging_type": "RESPONSE"
        }

        try:
            response = requests.post(url, params=params, json=payload)
            if response.status_code == 200:
                logger.info(f"Message sent to {recipient_id}")
            else:
                logger.error(
                    f"Failed to send message: {response.status_code} - {response.text}")
                success = False
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            success = False

    return success


def send_typing_indicator(recipient_id: str, action: str = "typing_on"):
    """
    Typing indicator ပြပါတယ် (typing_on / typing_off)
    """
    import requests

    if not PAGE_ACCESS_TOKEN:
        return

    url = f"{GRAPH_API_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": action
    }

    try:
        requests.post(url, params=params, json=payload)
    except Exception as e:
        logger.error(f"Error sending typing indicator: {str(e)}")


# ===== Webhook Routes =====

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "bot": "Facebook Messenger AI Auto Reply Bot",
        "version": "1.0.0"
    })


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Meta Webhook Verification
    Meta က webhook URL ကို verify လုပ်တဲ့အခါ GET request ပို့ပါတယ်။
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully!")
        return challenge, 200
    else:
        logger.warning(f"Webhook verification failed. Token: {token}")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Meta Webhook Event Handler
    Messenger ကနေ message လာတိုင်း ဒီ endpoint ကို POST request ပို့ပါတယ်။
    """
    body = request.get_json()

    if not body or body.get("object") != "page":
        return "Not Found", 404

    # Process each entry
    for entry in body.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")

            if not sender_id:
                continue

            # Handle different event types
            if "message" in messaging_event:
                handle_message(sender_id, messaging_event["message"])
            elif "postback" in messaging_event:
                handle_postback(sender_id, messaging_event["postback"])

    return "EVENT_RECEIVED", 200


def handle_message(sender_id: str, message: dict):
    """
    Message event handler
    Text message ရော attachment ရော handle လုပ်ပါတယ်။
    """
    # Echo message (bot ကိုယ်တိုင် ပို့တဲ့ message) ကို skip
    if message.get("is_echo"):
        return

    # Typing indicator ပြ
    send_typing_indicator(sender_id, "typing_on")

    if "text" in message:
        user_text = message["text"]
        logger.info(f"Received text from {sender_id}: {user_text}")

        # AI response ရယူ
        ai_reply = get_ai_response(sender_id, user_text)

        # Reply ပို့
        send_message(sender_id, ai_reply)

    elif "attachments" in message:
        # Attachment (ပုံ၊ video၊ file) လာရင်
        attachment_type = message["attachments"][0].get("type", "unknown")
        logger.info(
            f"Received {attachment_type} attachment from {sender_id}")

        reply = f"ကျေးဇူးတင်ပါတယ်။ {attachment_type} ကို လက်ခံရရှိပါပြီ။ Text message နဲ့ မေးခွန်းမေးပေးပါ။"
        send_message(sender_id, reply)

    # Typing off
    send_typing_indicator(sender_id, "typing_off")


def handle_postback(sender_id: str, postback: dict):
    """
    Postback event handler (button click events)
    """
    payload = postback.get("payload", "")
    logger.info(f"Received postback from {sender_id}: {payload}")

    if payload == "GET_STARTED":
        welcome_msg = (
            "မင်္ဂလာပါ! 👋\n\n"
            "ကျွန်တော်/ကျွန်မ က AI Assistant ဖြစ်ပါတယ်။\n"
            "ဘာမဆို မေးချင်တာ မေးနိုင်ပါတယ်။\n\n"
            "Hello! I'm an AI Assistant.\n"
            "Feel free to ask me anything!"
        )
        send_message(sender_id, welcome_msg)
    else:
        # Other postbacks
        ai_reply = get_ai_response(sender_id, f"[Button clicked: {payload}]")
        send_message(sender_id, ai_reply)


# ===== Main =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting bot server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
