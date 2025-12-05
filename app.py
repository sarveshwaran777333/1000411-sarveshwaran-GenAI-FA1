#genai.configure(api_key="AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
import os

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

API_KEY = "AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg"
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")


# ---------------------------------------------------
# IMAGE ANALYSIS FUNCTION
# ---------------------------------------------------
def analyze_image(prompt, image_file):
    if image_file is None:
        return "Please upload an image."

    image_bytes = image_file.getvalue()
    mime = image_file.type or "image/jpeg"

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": mime,
                "data": image_bytes
            }
        ],
        stream=False
    )

    return response.text


# ---------------------------------------------------
# TEXT ANALYSIS FUNCTION
# ---------------------------------------------------
def analyze_text(prompt):
    response = model.generate_content(prompt)
    return response.text


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🌾 Smart Farming Assistant (Gemini 2.5 Flash)")

option = st.sidebar.radio(
    "Choose analysis type:",
    [
        "Leaf Disease Analysis",
        "Soil Health Analysis",
        "Plant Disease Detection",
        "General Farming Query"
    ]
)

# ---------------------------------------------------
# LEAF DISEASE ANALYSIS
# ---------------------------------------------------
if option == "Leaf Disease Analysis":
    st.header("🌿 Leaf Disease Analysis")
    img = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])

    if st.button("Analyze Leaf"):
        prompt = """
        Analyze this plant leaf. Provide:
        1. Disease or pest detected
        2. Symptoms
        3. Severity level
        4. Treatment recommendations
        5. Organic/home remedies
        """
        st.write("Analyzing... please wait.")
        response = analyze_image(prompt, img)
        st.write(response)

# ---------------------------------------------------
# SOIL HEALTH ANALYSIS
# ---------------------------------------------------
elif option == "Soil Health Analysis":
    st.header("🌱 Soil Health Analysis")
    img = st.file_uploader("Upload soil image", type=["jpg", "png", "jpeg"])

    if st.button("Analyze Soil"):
        prompt = """
        Analyze the soil in this image. Provide:
        - Soil type
        - Moisture level
        - Fertility & nutrients
        - Organic matter level
        - Best crops for this soil
        - Improvement suggestions
        """
        st.write("Analyzing...")
        response = analyze_image(prompt, img)
        st.write(response)

# ---------------------------------------------------
# PLANT DISEASE DETECTION
# ---------------------------------------------------
elif option == "Plant Disease Detection":
    st.header("🩺 Plant Disease Detection")
    img = st.file_uploader("Upload plant image", type=["jpg", "png", "jpeg"])

    if st.button("Detect Disease"):
        prompt = """
        Detect plant disease from the image. Provide:
        - Disease name
        - Visible symptoms
        - Spread prevention steps
        - Treatment suggestions
        """
        st.write("Analyzing...")
        response = analyze_image(prompt, img)
        st.write(response)

# ---------------------------------------------------
# GENERAL FARMING QUERY
# ---------------------------------------------------
else:
    st.header("💬 General Farming Query")

question = st.text_input("Ask any farming question:")

if st.button("Ask"):
    st.write("Thinking...")
    response = analyze_text(question)
    st.write(response)
