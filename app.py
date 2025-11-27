#genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import requests
import json
import google.generativeai as genai

# ---------------- CONFIG ----------------
FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
SESSION_NODE = "active_session"

WEATHER_API = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude={lat}&longitude={lon}&current_weather=true"
)

genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("gemini-2.0-flash")


# ---------------- FIREBASE HELPERS ----------------
def load_history():
    try:
        r = requests.get(f"{FIREBASE_URL}/{SESSION_NODE}.json")
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return []


def save_history(history):
    try:
        requests.put(f"{FIREBASE_URL}/{SESSION_NODE}.json",
                     data=json.dumps(history))
    except:
        pass


# ---------------- WEATHER TOOL ----------------
def get_weather(lat, lon):
    try:
        url = WEATHER_API.format(lat=lat, lon=lon)
        data = requests.get(url).json()
        w = data["current_weather"]
        return (
            f"Weather now: {w['temperature']}°C, "
            f"Wind {w['windspeed']} km/h, "
            f"Condition Code {w['weathercode']}."
        )
    except:
        return "Weather fetch failed."


# ---------------- MAIN BRAIN ----------------
def agronova_brain(user_text, history):

    # Detect lat lon format
    if "lat" in user_text and "lon" in user_text:
        try:
            parts = user_text.replace(",", " ").split()
            lat = float(parts[parts.index("lat") + 1])
            lon = float(parts[parts.index("lon") + 1])
            return get_weather(lat, lon)
        except:
            return "Use format: lat 10.1 lon 78.3"

    # Short-context retrieval
    last_msg = ""
    for msg in reversed(history):
        if msg["role"] == "user":
            last_msg = msg["text"]
            break

    system_prompt = (
        "You are AgroNova, a simple farming assistant for Tamil Nadu. "
        "Answer in very simple English. "
        "Limit every reply to 3–4 lines only. "
        "If unclear, ask for crop, soil, or season."
    )

    # CORRECT FORMAT → prevents server busy
    messages = [
        {"role": "user", "parts": [{"text": system_prompt}]},
        {"role": "user", "parts": [{"text": last_msg}]},
        {"role": "user", "parts": [{"text": user_text}]}
    ]

    try:
        response = model.generate_content(messages)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- UI ----------------
def main():
    st.title("🌾 AgroNova – Smart Farming Assistant")

    if "history" not in st.session_state:
        st.session_state.history = load_history()

    user_input = st.text_input("Ask something:")

    if st.button("Send"):
        if user_input.strip():

            reply = agronova_brain(user_input, st.session_state.history)

            st.session_state.history.append({"role": "user", "text": user_input})
            st.session_state.history.append({"role": "bot", "text": reply})

            save_history(st.session_state.history)

    st.write("### Chat History")
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.write(f"**You:** {msg['text']}")
        else:
            st.write(f"**Bot:** {msg['text']}")


if __name__ == "__main__":
    main()

