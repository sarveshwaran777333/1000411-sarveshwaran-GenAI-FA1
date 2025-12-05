#genai.configure(api_key="AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
import os

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
genai.configure(api_key=os.getenv("AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg"))   # Make sure your API key variable is correct
MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")


# ---------------------------------------------------
# IMAGE ANALYSIS FUNCTION (FIXED)
# ---------------------------------------------------
def analyze_image(prompt, image_file):
    if image_file is None:
        return "Please upload an image."

    # Read image bytes directly
    image_bytes = image_file.read()

    model = genai.GenerativeModel(MODEL)

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": image_file.type,
                "data": image_bytes
            }
        ]
    )

    return response.text


# ---------------------------------------------------
# TEXT ANALYSIS FUNCTION (WORKING)
# ---------------------------------------------------
def analyze_text(prompt):
    model = genai.GenerativeModel(MODEL)
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
        prompt = """Analyze this plant leaf. Provide:
        1. Disease or pest detected
        2. Symptoms
        3. Severity level
        4. Treatment recommendations
        5. Organic/home remedies
        """
        response = analyze_image(prompt, img)
        st.write(response)


# ---------------------------------------------------
# SOIL HEALTH ANALYSIS
# ---------------------------------------------------
elif option == "Soil Health Analysis":
    st.header("🌱 Soil Health Analysis")
    img = st.file_uploader("Upload soil image", type=["jpg", "png", "jpeg"])

    if st.button("Analyze Soil"):
        prompt = """Analyze the soil in this image. Provide:
        - Soil type
        - Moisture level
        - Fertility & nutrients
        - Organic matter level
        - Best crops for this soil
        - Improvement suggestions
        """
        response = analyze_image(prompt, img)
        st.write(response)


# ---------------------------------------------------
# PLANT DISEASE DETECTION
# ---------------------------------------------------
elif option == "Plant Disease Detection":
    st.header("🩺 Plant Disease Detection")
    img = st.file_uploader("Upload plant image", type=["jpg", "png", "jpeg"])

    if st.button("Detect Disease"):
        prompt = """Detect plant disease from the image. Provide:
        - Disease name
        - Visible symptoms
        - Spread prevention steps
        - Treatment suggestions
        """
        response = analyze_image(prompt, img)
        st.write(response)


# ---------------------------------------------------
# GENERAL FARMING QUESTION
# ---------------------------------------------------
else:
    st.header("💬 General Farming Query")

question = st.text_input("Ask any farming question:")

if st.button("Ask"):
    response = analyze_text(question)
    st.write(response)
