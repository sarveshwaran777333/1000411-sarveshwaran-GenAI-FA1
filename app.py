#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import streamlit as st
import google.generativeai as genai
import tempfile
from PIL import Image

genai.configure(api_key="AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw")

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("Smart Farm Assistant – Tamil Nadu Farmers Support")

st.write("Ask about crops, soil, fertilizers, weather, pest control, or upload a plant/leaf image.")

user_text = st.text_input("Type your question (English or Tamil)")
uploaded_image = st.file_uploader("Upload image (optional)", type=["jpg", "jpeg", "png"])

if st.button("Ask"):
    inputs = []

    if user_text:
        inputs.append({"text": user_text})

    if uploaded_image:
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(uploaded_image.read())
        temp.close()
        img = Image.open(temp.name)
        inputs.append({"image": img})

    if not inputs:
        st.error("Please type a question or upload an image.")
    else:
        try:
            response = model.generate_content(inputs)
            answer = response.text
            st.success(answer)
        except Exception as e:
            st.error("Error while generating response. Check your API key or input.")
