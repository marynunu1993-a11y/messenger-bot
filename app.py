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
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# ===== Configuration =====
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_verify_token_123")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Fix: Read model from MODEL_NAME env var (Render), fallback to llama-3.3-70b-versatile
AI_MODEL = os.environ.get("MODEL_NAME", os.environ.get("AI_MODEL", "llama-3.3-70b-versatile"))

# PAGE_ID — Facebook Page ရဲ့ ID (Render Environment Variables မှာ ထည့်ပေးပါ)
# ဒါကို သုံးပြီး Page ကိုယ်တိုင် ပို့တဲ့ message ကို skip လုပ်ပါတယ်
PAGE_ID = os.environ.get("PAGE_ID", "")

# System Prompt — Bot ရဲ့ အပြုအမူ သတ်မှတ်ပေးတာ
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", """
သင်သည် Facebook Page ၏ Customer Service Assistant ဖြစ်ပါသည်။
ယဉ်ကျေးစွာ၊ အကူအညီပေးနိုင်စွာ ဖြေကြားပေးပါ။
မြန်မာဘာသာနဲ့ မေးရင် မြန်မာဘာသာနဲ့ ဖြေပါ။
English နဲ့ မေးရင် English နဲ့ ဖြေပါ။
တိုတိုရှင်းရှင်း ဖြေပေးပါ။
""".strip())

# Facebook Graph API
GRAPH_API_VERSION = "v21.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# ===== Logging =====
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
conversation_history = {}
MAX_HISTORY = 10


# ===== Helper Functions =====

def get_ai_response(sender_id, user_message):
    """AI response ရယူပါတယ်"""
    if not client:
        return "AI service is not configured. Please contact the page admin."

    try:
        if sender_id not in conversation_history:
            conversation_history[sender_id] = []

        history = conversation_history[sender_id]
        history.append({"role": "user", "content": user_message})

        if len(history) > MAX_HISTORY * 2:
            history = history[-(MAX_HISTORY * 2):]
            conversation_history[sender_id] = history

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        ai_reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": ai_reply})
        conversation_history[sender_id] = history

        logger.info(f"AI Response for {sender_id}: {ai_reply[:100]}...")
        return ai_reply

    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return "ခဏလေး စောင့်ပေးပါ။ Technical issue ရှိနေပါတယ်။ နောက်မှ ထပ်စမ်းကြည့်ပေးပါ။"


def send_message(recipient_id, message_text):
    """Facebook Send API ကို သုံးပြီး message ပြန်ပို့ပါတယ်"""
    import requests as req

    if not PAGE_ACCESS_TOKEN:
        logger.error("PAGE_ACCESS_TOKEN is not set!")
        return False

    url = f"{GRAPH_API_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    max_length = 2000
    chunks = [message_text[i:i + max_length]
              for i in range(0, len(message_text), max_length)]

    success = True
    for chunk in chunks:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": chunk},
            "messaging_type": "RESPONSE"
        }
        try:
            response = req.post(url, params=params, json=payload)
            if response.status_code == 200:
                logger.info(f"Message sent to {recipient_id}")
            else:
                logger.error(f"Failed to send: {response.status_code} - {response.text}")
                success = False
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            success = False

    return success


def send_typing_indicator(recipient_id, action="typing_on"):
    """Typing indicator ပြပါတယ်"""
    import requests as req

    if not PAGE_ACCESS_TOKEN:
        return

    url = f"{GRAPH_API_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": action
    }
    try:
        req.post(url, params=params, json=payload)
    except Exception as e:
        logger.error(f"Error sending typing indicator: {str(e)}")


# ===== Webhook Routes =====

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "bot": "Facebook Messenger AI Auto Reply Bot",
        "version": "1.0.0"
    })


@app.route("/webhook", methods=["GET"])
def verify_webhook():
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
    body = request.get_json()

    if not body or body.get("object") != "page":
        return "Not Found", 404

    for entry in body.get("entry", []):
        # entry ထဲမှ page_id ရယူ — ဒါက Page ကိုယ်တိုင်ရဲ့ ID ဖြစ်ပါတယ်
        entry_page_id = entry.get("id", "")

        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id", "")
            recipient_id = event.get("recipient", {}).get("id", "")

            if not sender_id:
                continue

            # ===== ADMIN FILTER =====
            # Facebook webhook မှာ:
            # - Customer က message ပို့ရင်: sender = customer ID, recipient = page ID
            # - Page/Admin က message ပို့ရင်: sender = page ID, recipient = customer ID
            # ဒါကြောင့် sender_id က page ID နဲ့ တူရင် skip လုပ်ရပါတယ်
            if sender_id == entry_page_id:
                logger.info(f"Skipping message sent BY the page itself (sender={sender_id})")
                continue

            if PAGE_ID and sender_id == PAGE_ID:
                logger.info(f"Skipping message from PAGE_ID admin (sender={sender_id})")
                continue

            # ===== CUSTOMER MESSAGE — AI ဖြေပေးမည် =====
            logger.info(f"Customer message from {sender_id} to page {recipient_id}")

            if "message" in event:
                handle_message(sender_id, event["message"])
            elif "postback" in event:
                handle_postback(sender_id, event["postback"])

    return "EVENT_RECEIVED", 200


def handle_message(sender_id, message):
    # Bot ကိုယ်တိုင် ပို့တဲ့ echo message ကို skip
    if message.get("is_echo"):
        logger.info(f"Skipping echo message for {sender_id}")
        return

    send_typing_indicator(sender_id, "typing_on")

    if "text" in message:
        user_text = message["text"]
        logger.info(f"Received text from customer {sender_id}: {user_text}")

        ai_reply = get_ai_response(sender_id, user_text)
        send_message(sender_id, ai_reply)

    elif "attachments" in message:
        attachment_type = message["attachments"][0].get("type", "unknown")
        logger.info(f"Received {attachment_type} attachment from {sender_id}")
        reply = "ကျေးဇူးတင်ပါတယ်။ Text message နဲ့ မေးခွန်းမေးပေးပါ။"
        send_message(sender_id, reply)

    send_typing_indicator(sender_id, "typing_off")


def handle_postback(sender_id, postback):
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
        ai_reply = get_ai_response(sender_id, f"[Button clicked: {payload}]")
        send_message(sender_id, ai_reply)


# ===== Main =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting bot server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
