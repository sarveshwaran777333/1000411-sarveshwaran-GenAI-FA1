#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import re
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components

API_KEY = "AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw"
if not API_KEY or API_KEY.strip() == "":
    st.error("🚨 ERROR: API KEY is missing. Please add your key in the code.")
    st.stop()

genai.configure(api_key=API_KEY)
MODEL = "gemini-2.5-flash"
safety_settings = [
    {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
]

try:
    model = genai.GenerativeModel(MODEL, safety_settings=safety_settings)
except Exception as e:
    st.error(f"Failed to initialize model {MODEL}: {e}")
    st.stop()

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")
SHORT_INSTRUCTION = "Answer in simple English, short sentences, understandable by any farmer."

def shortify(text: str, max_sentences: int = 2) -> str:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(parts) <= max_sentences:
        return text.strip()
    short = " ".join(parts[:max_sentences]).strip()
    if not re.search(r'[.!?]$', short):
        short += "."
    return short

@st.cache_data(show_spinner="Generating text response...")
def analyze_text(prompt):
    full_prompt = f"{SHORT_INSTRUCTION} {prompt}"
    try:
        response = model.generate_content(full_prompt)
        return shortify(response.text, max_sentences=2)
    except Exception as e:
        return f"🚨 API Error: {e}"

@st.cache_data(show_spinner="Analyzing image...")
def analyze_image(image_file):
    prompt = """
Detect disease or pest in the plant/leaf image. Provide short answers using Markdown:
- **Disease/Pest**
- **Visible Symptoms**
- **Treatment Recommendations**
"""
    image_bytes = image_file.getvalue()
    mime = image_file.type or "image/jpeg"
    content_parts = [f"{SHORT_INSTRUCTION} {prompt}", {"mime_type": mime, "data": image_bytes}]
    try:
        response = model.generate_content(content_parts)
        return response.text
    except Exception as e:
        return f"🚨 API Error: {e}"

st.title("🌾 Smart Farming Assistant")
st.caption("Type, speak, or upload an image. The bot will respond below.")

st.header("💬 Your Message")

if st.button("🎤 Speak"):
    components.html("""
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.start();
    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        window.parent.document.getElementById('voice_input').value = text;
    };
    </script>
    <input type="hidden" id="voice_input" />
    """, height=0)
    st.info("Speak now...")

text_input = st.text_input("Type your question here:", value="")
image_input = st.file_uploader("Optional: upload a leaf/plant image", type=["jpg","png","jpeg"])

user_message = st.session_state.get("voice_text", "") or text_input

if st.button("➡️ Ask"):
    if not user_message and not image_input:
        st.warning("Please type a question, speak, or upload an image.")
    else:
        with st.spinner("Thinking..."):
            response_text = ""
            if user_message:
                response_text += analyze_text(f"Question: {user_message}") + "\n\n"
            if image_input:
                response_text += analyze_image(image_input)
        st.markdown("## 💡 Answer")
        st.markdown(response_text)
