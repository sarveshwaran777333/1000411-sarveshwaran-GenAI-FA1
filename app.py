#genai.configure(api_key="AIzaSyDP8Llyi9Rd9d2s7r5SVbm4iOSXCZK-wyo")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import requests
import json
import google.generativeai as genai

# --------------------------------------------
# CONFIG
# --------------------------------------------
genai.configure(api_key="AIzaSyDP8Llyi9Rd9d2s7r5SVbm4iOSXCZK-wyo")
model = genai.GenerativeModel("gemini-2.0-flash")

FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
MEMORY_NODE = "agronova_memory"


# --------------------------------------------
# FIREBASE HELPERS
# --------------------------------------------
def load_memory():
    try:
        r = requests.get(f"{FIREBASE_URL}/{MEMORY_NODE}.json")
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return {"last_user": "", "last_bot": ""}


def save_memory(data):
    try:
        requests.put(f"{FIREBASE_URL}/{MEMORY_NODE}.json", json=data)
    except:
        pass


# --------------------------------------------
# AGRO NOVA (very small Gemini prompt)
# --------------------------------------------
def agronova(user_msg):

    mem = load_memory()

    prompt = (
        "You are AgroNova, a simple farming helper for Tamil Nadu. "
        "Use very easy English and reply in 3–4 short lines only.\n\n"
        f"Earlier farmer question: {mem['last_user']}\n"
        f"Earlier answer: {mem['last_bot']}\n\n"
        f"Farmer: {user_msg}\nAgroNova:"
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 80,   # very small
                "temperature": 0.3
            }
        )
        reply = response.text.strip()
    except Exception as e:
        reply = f"Error: {str(e)}"

    # Save new memory
    save_memory({
        "last_user": user_msg,
        "last_bot": reply
    })

    return reply


# --------------------------------------------
# STREAMLIT UI
# --------------------------------------------
def main():
    st.title("🌾 AgroNova – Smart Farming Assistant")

    user_input = st.text_input("Ask something:")

    if st.button("Send"):
        if user_input.strip():
            reply = agronova(user_input)
            st.write("### Bot:")
            st.write(reply)


if __name__ == "__main__":
    main()
