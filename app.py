#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="FarmAssist Bot", layout="wide")

genai.configure(api_key="AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw")
model = genai.GenerativeModel("gemini-1.5-flash")

def detect_language_preference(text):
    t = text.lower()
    if "in tamil" in t or "tamil la" in t:
        return "tamil"
    if "in english" in t:
        return "english"
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    if tamil_chars > 3:
        return "tamil"
    return "english"

def generate_response(text, image=None):
    lang = detect_language_preference(text)

    system_rules = {
        "english": "Answer clearly in English. Keep it simple for farmers.",
        "tamil": "எளிமையான தமிழில் விவசாயிகளுக்குப் புரியும் வகையில் பதில் எழுதவும்."
    }

    if image:
        prompt = f"{system_rules[lang]}\nUser question: {text}\nExplain based on the uploaded image."
        return model.generate_content([prompt, image]).text
    else:
        prompt = f"{system_rules[lang]}\nUser question: {text}"
        return model.generate_content(prompt).text

st.title("FarmAssist – All-in-One Smart Farming Bot")

query = st.text_input("Ask anything (English or Tamil):")

uploaded_image = st.file_uploader("Upload leaf/plant image (optional)", type=["jpg","jpeg","png"])

mic_audio = st.audio_input("Use microphone to ask (optional)")

if st.button("Ask"):
    user_text = query

    if mic_audio and not query:
        try:
            audio_bytes = mic_audio.read()
            user_text = model.generate_content(
                [{"mime_type": "audio/wav", "data": audio_bytes}],
                request_options={"timeout": 300}
            ).text
        except:
            st.error("Could not process microphone input.")
            st.stop()

    if not user_text:
        st.error("Please type or speak a question.")
        st.stop()

    image_obj = None
    if uploaded_image:
        try:
            image_obj = Image.open(uploaded_image)
        except:
            st.error("Invalid image.")
            st.stop()

    output = generate_response(user_text, image_obj)
    st.markdown("### Response")
    st.write(output)
