#genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
import requests
import json
import time


# ------------------------------------------------------------
# CONFIG (REQUIRED ONLINE)
# ------------------------------------------------------------
genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("gemini-1.5-flash")

FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
SESSION_PATH = "agronova_memory"


# ------------------------------------------------------------
# SAFE GEMINI CALL (ONLINE ONLY)
# ------------------------------------------------------------
def safe_extract(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        return response.candidates[0].content.parts[0].text.strip()
    except:
        return "Error: Could not read model response."


def gemini_call(prompt):
    """Online-only Gemini call. No offline fallback."""
    for _ in range(2):
        try:
            r = model.generate_content(
                prompt,
                generation_config={"temperature": 0.4, "max_output_tokens": 150}
            )
            return safe_extract(r)

        except Exception as e:
            if "429" in str(e):
                time.sleep(2)
                continue
            return f"Error: {e}"
    return "Error: Server overloaded."


# ------------------------------------------------------------
# FIREBASE HELPERS (ONLINE ONLY)
# ------------------------------------------------------------
def fb_put(path, data):
    """Store last turn (online only)."""
    try:
        requests.put(f"{FIREBASE_URL}/{path}.json", json=data)
    except:
        pass


def fb_get(path):
    """Fetch last turn (online only)."""
    try:
        r = requests.get(f"{FIREBASE_URL}/{path}.json")
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


# ------------------------------------------------------------
# FARMING BOT LOGIC
# ------------------------------------------------------------
def agronova(user_msg, uid="farmer1"):

    # Fetch previous turn from Firebase (online)
    prev = fb_get(f"{SESSION_PATH}/{uid}") or {}
    last_user = prev.get("user", "")
    last_bot = prev.get("bot", "")

    system = (
        "You are AgroNova, a simple Tamil Nadu farming assistant. "
        "Use very simple English. Keep answers short: 3–4 lines only."
    )

    prompt = system + "\n\n"

    # Add online memory if exists
    if last_user:
        prompt += (
            f"Previous Farmer Question: {last_user}\n"
            f"Previous AgroNova Answer: {last_bot}\n\n"
        )

    # Add new question
    prompt += f"Farmer: {user_msg}\nAgroNova:"

    # online Gemini call
    reply = gemini_call(prompt)

    # save to Firebase (online memory)
    fb_put(f"{SESSION_PATH}/{uid}", {"user": user_msg, "bot": reply})

    return reply


# ------------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------------
def main():
    st.title("🌾 AgroNova – Online Farming Assistant")

    st.warning("This bot works **only online**. No offline mode. "
               "Every response depends on Gemini + Firebase.")

    user_q = st.text_input("Ask something:")

    if st.button("Send"):
        if user_q.strip():
            reply = agronova(user_q)
            st.write("### Bot:")
            st.write(reply)


if __name__ == "__main__":
    main()

