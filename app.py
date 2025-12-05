#genai.configure(api_key="AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg"))
MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")


def analyze_image(prompt, image_file):
    if image_file is None:
        return "Please upload an image."

    temp_path = "temp_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_file.getbuffer())

    result = genai.generate(
        model=MODEL,
        prompt=prompt,
        images=[temp_path]
    )

    return result.text


def analyze_text(prompt):
    result = genai.generate(
        model=MODEL,
        prompt=prompt
    )
    return result.text


# -----------------------------------------
# UI
# -----------------------------------------

st.title("🌾 Smart Farming Assistant (Gemini 2.5 Flash)")

option = st.sidebar.radio("Choose analysis type:", [
    "Leaf Disease Analysis",
    "Soil Health Analysis",
    "Plant Disease Detection",
    "General Farming Query"
])

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

else:
    st.header("💬 General Farming Query")
    question = st.text_input("Ask any farming question:")

    if st.button("Ask"):
        response = analyze_text(question)
        st.write(response)
