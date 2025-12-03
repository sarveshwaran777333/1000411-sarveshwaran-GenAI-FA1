#genai.configure(api_key="AIzaSyDP8Llyi9Rd9d2s7r5SVbm4iOSXCZK-wyo")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import requests
import google.genai as genai
from google.genai.types import Content, Part

# ---------------------------------------------------
# 1. CONFIG
# ---------------------------------------------------

API_KEY = "AIzaSyDP8Llyi9Rd9d2s7r5SVbm4iOSXCZK-wyo"
FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
SESSION_NODE = "active_session"

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"

SYSTEM_TEXT = """
You are SmartFarm Buddy.
You help Tamil Nadu farmers with simple, clear answers.
"""


# ---------------------------------------------------
# 2. Firebase: Save chat history
# ---------------------------------------------------
def save_message(role, text):
    data = {"role": role, "text": text}
    requests.post(f"{FIREBASE_URL}/{SESSION_NODE}.json", json=data)


# ---------------------------------------------------
# 3. Firebase: Load entire chat history
# ---------------------------------------------------
def load_history():
    r = requests.get(f"{FIREBASE_URL}/{SESSION_NODE}.json")
    if r.status_code != 200 or r.json() is None:
        return []

    raw = r.json()
    history = []

    for key in raw:
        history.append(raw[key])

    return history


# ---------------------------------------------------
# 4. Build conversation for Gemini
# ---------------------------------------------------
def build_conversation(user_text):
    conversation = []

    # Add system instruction
    conversation.append(
        Content(role="user", parts=[Part.from_text(SYSTEM_TEXT)])
    )

    # Load previous messages
    history = load_history()

    for msg in history:
        conversation.append(
            Content(
                role=msg["role"],
                parts=[Part.from_text(msg["text"])]
            )
        )

    # Add latest user message
    conversation.append(
        Content(
            role="user",
            parts=[Part.from_text(user_text)]
        )
    )

    return conversation


# ---------------------------------------------------
# 5. Ask Gemini with memory
# ---------------------------------------------------
def ask_bot(user_text):
    try:
        conversation = build_conversation(user_text)

        res = client.models.generate_content(
            model=MODEL,
            contents=conversation
        )

        reply = res.text.strip()
        save_message("user", user_text)
        save_message("assistant", reply)

        return reply

    except Exception as e:
        err = str(e)
        if "429" in err:
            return "Error: Rate limit reached. Try again later."
        if "503" in err:
            return "Error: Server overloaded."
        if "404" in err:
            return "Error: Model not found. Use gemini-1.5-flash."

        return "Error: " + err


# ---------------------------------------------------
# 6. CLI bot loop (optional)
# ---------------------------------------------------
if __name__ == "__main__":
    print("SmartFarm Buddy is online.")
    while True:
        q = input("You: ")
        print("Bot:", ask_bot(q))
