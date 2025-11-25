#genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")

import streamlit as st
import requests
import google.generativeai as genai
import json
import time

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"
SESSION_NODE = "active_session"

WEATHER_API = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude={lat}&longitude={lon}&current_weather=true"
)

# SET YOUR GEMINI API KEY
genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------------------------------------------------------
# Firebase helpers
# -------------------------------------------------------------------
def fb_set(path, data):
    requests.put(f"{FIREBASE_URL}/{path}.json", data=json.dumps(data))


def fb_push(path, data):
    requests.post(f"{FIREBASE_URL}/{path}.json", data=json.dumps(data))


def fb_delete(path):
    requests.delete(f"{FIREBASE_URL}/{path}.json")


# -------------------------------------------------------------------
# Weather logic
# -------------------------------------------------------------------
def get_weather(lat, lon):
    url = WEATHER_API.format(lat=lat, lon=lon)
    r = requests.get(url)

    if r.status_code != 200:
        return "Unable to reach weather service."

    data = r.json()
    if "current_weather" not in data:
        return "Weather data not available."

    w = data["current_weather"]
    return (
        f"Temperature: {w['temperature']} °C\n"
        f"Windspeed: {w['windspeed']} km/h\n"
        f"Weather Code: {w['weathercode']}"
    )


# -------------------------------------------------------------------
# AgroNova Brain (Gemini + manual logic)
# -------------------------------------------------------------------
def agronova_brain(user_message):

    user_lower = user_message.lower()

    # Recognize monsoon question for Madurai
    if "monsoon" in user_lower and "madurai" in user_lower:
        return (
            "Madurai mainly gets rain from the Northeast Monsoon, "
            "which comes from October to December."
        )

    # Recognize weather request
    if "weather" in user_lower:
        return "Please give latitude and longitude like: lat 9.9 lon 78.1"

    # General Gemini reply
    response = model.generate_content(
        "You are AgroNova, a simple farming helper for Tamil Nadu. "
        "Understand wrong spelling and Tamil-English mix. "
        f"Always answer in 3–4 short lines, very easy English, with steps + safety. Question: {user_message}"
    )

    return response.text



# -------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------
def main():

    st.set_page_config(page_title="AgroNova", page_icon="🌱")

    st.title("🌱 AgroNova – Smart Farming Assistant")
    st.caption("Weather, monsoon, and farming questions")

    # Initialize session storage in Firebase
    if "started" not in st.session_state:
        st.session_state.started = True
        fb_set(SESSION_NODE, [])

    # Chat UI
    user_input = st.text_input("Ask your question:")

    if st.button("Ask"):
        if user_input.strip():

            # Store question in Firebase
            fb_push(SESSION_NODE, {"question": user_input, "time": time.time()})

            # Weather special case
            if "lat" in user_input.lower() and "lon" in user_input.lower():
                try:
                    parts = user_input.replace(",", " ").split()
                    lat = float(parts[parts.index("lat") + 1])
                    lon = float(parts[parts.index("lon") + 1])
                    reply = get_weather(lat, lon)
                except:
                    reply = "Invalid format. Use: lat 9.9 lon 78.1"
            else:
                reply = agronova_brain(user_input)

            st.success(f"AgroNova: {reply}")

    # End session button
    if st.button("End Session"):
        fb_delete(SESSION_NODE)
        st.session_state.clear()
        st.warning("Session cleared from Firebase.")
        st.stop()


# -------------------------------------------------------------------
# RUN STREAMLIT
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
