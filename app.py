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

genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("gemini-2.5-flash")


# --------------------------------------------------
# Firebase
# --------------------------------------------------

def fb_push(role, text):
    data = {"role": role, "text": text, "time": time.time()}
    requests.post(f"{FIREBASE_URL}/{SESSION_NODE}.json", json=data)

def fb_load(limit=12):
    r = requests.get(f"{FIREBASE_URL}/{SESSION_NODE}.json")
    if r.status_code != 200 or r.json() is None:
        return []
    data = list(r.json().values())
    data.sort(key=lambda x: x["time"])
    return data[-limit:]

def fb_clear():
    requests.delete(f"{FIREBASE_URL}/{SESSION_NODE}.json")


# --------------------------------------------------
# Weather
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

    # Hardcoded local logic
    if "monsoon" in user_text.lower() and "madurai" in user_text.lower():
        return (
            "Madurai gets Northeast Monsoon rainfall from Oct–Dec.\n"
            "Farmers can prepare land before first showers.\n"
            "Keep seeds stored in dry place.\n"
            "Clean drainage to prevent crop damage."
        )

    if "lat" in user_text.lower() and "lon" in user_text.lower():
        try:
            parts = user_text.replace(",", " ").split()
            lat = float(parts[parts.index("lat") + 1])
            lon = float(parts[parts.index("lon") + 1])
            return get_weather(lat, lon)
        except:
            return "Use this format: lat 9.9 lon 78.1"

    # Build messages for Gemini
    system_prompt = (
        "You are AgroNova, a simple farming helper for Tamil Nadu. "
        "Understand wrong spelling and Tamil-English mix. "
        "Always answer in 3–4 very simple lines."
    )

    messages = [
        {"role": "user", "parts": [system_prompt]}
    ]

    for msg in history:
        messages.append({
            "role": msg["role"],
            "parts": [msg["text"]]
        })

    messages.append({"role": "user", "parts": [user_text]})

    # Generate response
    response = model.generate_content(messages)
    return response.text


# --------------------------------------------------
# Streamlit App
# --------------------------------------------------

def main():

    st.title("🌱 AgroNova – Smart Farming Assistant")
    st.caption("Farming, weather and monsoon support for Tamil Nadu")

    history = fb_load()

    # Show chat history
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"**Farmer:** {msg['text']}")
        else:
            st.markdown(f"**AgroNova:** {msg['text']}")

    user_input = st.text_input("Ask your question:")

    if st.button("Ask"):
        if not user_input.strip():
            st.warning("Please type something.")
            return

        fb_push("user", user_input)

        reply = agronova_brain(user_input, history)

        fb_push("assistant", reply)

        st.success(f"AgroNova: {reply}")

    if st.button("Clear Chat"):
        fb_clear()
        st.warning("Chat cleared.")
        st.stop()


if __name__ == "__main__":
    main()
