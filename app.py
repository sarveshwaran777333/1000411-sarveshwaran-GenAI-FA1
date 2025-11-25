#genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
import requests
import json
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
SESSION_NODE = "active_session"

WEATHER_API = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude={lat}&longitude={lon}&current_weather=true"
)

# GEMINI SETUP
genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("gemini-2.5-flash")


# --------------------------------------------------
# Firebase functions
# --------------------------------------------------

def fb_push(message):
    """Save chat message to Firebase."""
    data = {"role": message["role"], "text": message["text"], "time": time.time()}
    requests.post(f"{FIREBASE_URL}/{SESSION_NODE}.json", json=data)

def fb_load(limit=12):
    """Load last N messages."""
    r = requests.get(f"{FIREBASE_URL}/{SESSION_NODE}.json")
    if r.status_code != 200 or r.json() is None:
        return []
    messages = list(r.json().values())
    messages.sort(key=lambda x: x["time"])
    return messages[-limit:]

def fb_clear():
    """Clear chat session."""
    requests.delete(f"{FIREBASE_URL}/{SESSION_NODE}.json")


# --------------------------------------------------
# Weather system
# --------------------------------------------------

def get_weather(lat, lon):
    url = WEATHER_API.format(lat=lat, lon=lon)
    r = requests.get(url)

    if r.status_code != 200:
        return "Weather service unreachable."

    data = r.json()
    if "current_weather" not in data:
        return "Weather data not available."

    w = data["current_weather"]
    return (
        f"Temperature: {w['temperature']}°C\n"
        f"Windspeed: {w['windspeed']} km/h\n"
        f"Weather Code: {w['weathercode']}"
    )


# --------------------------------------------------
# AgroNova Brain
# --------------------------------------------------

def agronova_brain(user_text, history):
    """Answer using Gemini + chat memory."""

    # Special case: monsoon question for Madurai
    if "monsoon" in user_text.lower() and "madurai" in user_text.lower():
        return (
            "Madurai mainly gets rain from the Northeast Monsoon.\n"
            "It happens from October to December.\n"
            "Farmers should prepare fields before first rains.\n"
            "Store seeds in dry place to avoid damage."
        )

    # Special case: weather request
    if "lat" in user_text.lower() and "lon" in user_text.lower():
        try:
            parts = user_text.replace(",", " ").split()
            lat = float(parts[parts.index("lat") + 1])
            lon = float(parts[parts.index("lon") + 1])
            return get_weather(lat, lon)
        except:
            return "Use correct format: lat 9.9 lon 78.1"

    # Simple 3–4 line helper prompt
    system_prompt = (
        "You are AgroNova, a simple farming helper for Tamil Nadu. "
        "Understand wrong spelling and Tamil-English mix. "
        "Always answer in 3–4 very simple lines."
    )

    # Construct full prompt with history
    msg_list = [{"role": "user", "text": system_prompt}]
    for m in history:
        msg_list.append({"role": m["role"], "text": m["text"]})
    msg_list.append({"role": "user", "text": user_text})

    response = model.generate_content(msg_list)
    return response.text


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------

def main():

    st.title("🌱 AgroNova – Smart Farming Assistant")
    st.caption("Farming, weather and monsoon support for Tamil Nadu")

    # Load chat memory
    history = fb_load(limit=12)

    # Display chat
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"**Farmer:** {msg['text']}")
        else:
            st.markdown(f"**AgroNova:** {msg['text']}")

    # User input
    user_input = st.text_input("Ask your question:")

    if st.button("Ask"):
        if user_input.strip() == "":
            st.warning("Type something.")
            return

        # Save user message
        fb_push({"role": "user", "text": user_input})

        # Process
        reply = agronova_brain(user_input, history)

        # Save bot reply
        fb_push({"role": "assistant", "text": reply})

        st.success(f"AgroNova: {reply}")

    # Clear session button
    if st.button("Clear Chat"):
        fb_clear()
        st.warning("Chat history cleared.")
        st.stop()


if __name__ == "__main__":
    main()
