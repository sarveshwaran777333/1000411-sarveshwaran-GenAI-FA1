#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import streamlit as st
from PIL import Image
import google.generativeai as genai

GEMINI_API_KEY = "IzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="AGRONOVA", layout="centered")

st.markdown("""
<style>
body {
    background-color: #0e1117;
}
div[data-testid="stTextInput"] input {
    font-size: 18px;
    padding: 14px;
}
div[data-testid="stFileUploader"] {
    border: 2px dashed #4f6ef7;
    border-radius: 16px;
    padding: 60px 20px;
    background: #0e1117;
    text-align: center;
}
div[data-testid="stFileUploader"] label {
    display: none;
}
div[data-testid="stFileUploader"] section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
div[data-testid="stFileUploader"] small {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌱 AGRONOVA")
st.markdown("Ask anything about farming using text or image")

text_query = st.text_input("", placeholder="Ask anything about farming")

image = st.file_uploader(
    "Add image\nDrag & drop a plant or leaf image here, or click to browse",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False
)

ask = st.button("Ask")

if ask:
    if not text_query and not image:
        st.warning("Please ask a question or upload an image.")
    else:
        with st.spinner("Analyzing..."):
            if image and text_query:
                img = Image.open(image)
                response = model.generate_content([text_query, img])
            elif image:
                img = Image.open(image)
                response = model.generate_content(["Analyze this plant or leaf image and explain any disease or issue.", img])
            else:
                response = model.generate_content(text_query)

        st.markdown("### Response")
        st.write(response.text)
