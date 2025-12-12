#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import re
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import tempfile

AudioSegment.converter = which("ffmpeg")

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

SHORT_INSTRUCTION = "Always answer in simple, easy English that any farmer can understand. Use 1–2 short sentences only."

def shortify(text: str, max_sentences: int = 2) -> str:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(parts) <= max_sentences:
        return text.strip()
    short = " ".join(parts[:max_sentences]).strip()
    if not re.search(r'[.!?]$', short):
        short += "."
    return short

@st.cache_data(show_spinner="Analyzing image with Gemini...")
def analyze_image(prompt, image_file):
    if image_file is None:
        return "**Please upload an image before clicking 'Analyze'.**"
    image_bytes = image_file.getvalue()
    mime = image_file.type or "image/jpeg"
    full_prompt = f"{SHORT_INSTRUCTION} {prompt}"
    content_parts = [full_prompt, {"mime_type": mime, "data": image_bytes}]
    try:
        response = model.generate_content(content_parts)
        return response.text
    except Exception as e:
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"

@st.cache_data(show_spinner="Generating response...")
def analyze_text(prompt):
    full_prompt = f"{SHORT_INSTRUCTION} {prompt}"
    try:
        response = model.generate_content(full_prompt)
        return shortify(response.text, max_sentences=2)
    except Exception as e:
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"

st.title("🌾 Smart Farming Assistant")
st.caption("AI-powered simple English answers for everyday farming questions.")

option = st.sidebar.radio(
    "Choose analysis type:",
    ["General Farming Query", "Leaf Disease Analysis", "Plant Disease Detection"]
)

if option == "General Farming Query":
    st.header("💬 General Farming Query")
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""
    if st.button("🎤 Start Speaking"):
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
    text_input = st.text_input("Or type your question:", value="")
    audio_file = st.file_uploader("Or upload an audio file (.wav/.mp3):", type=["wav", "mp3"])
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio_path = temp_audio.name
            uploaded_temp_path = temp_audio_path + "_upload"
            with open(uploaded_temp_path, "wb") as f:
                f.write(audio_file.read())
            if audio_file.type == "audio/mpeg":
                sound = AudioSegment.from_file(uploaded_temp_path, format="mp3")
                sound.export(temp_audio_path, format="wav")
            else:
                sound = AudioSegment.from_file(uploaded_temp_path, format="wav")
                sound.export(temp_audio_path, format="wav")
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
                audio_text = recognizer.recognize_google(audio_data)
                st.session_state.voice_text = audio_text
        except Exception as e:
            st.warning(f"Could not process audio file: {e}")
    user_input = st.session_state.voice_text or text_input
    if st.button("➡️ Ask Gemini"):
        if user_input.strip():
            full_prompt = f"Question: {user_input}"
            with st.spinner("Thinking..."):
                response = analyze_text(full_prompt)
            st.markdown("## 💡 Answer")
            st.markdown(response)
        else:
            st.warning("Please speak, type, or upload an audio file to ask a question.")

elif option == "Leaf Disease Analysis":
    st.header("🌿 Leaf Disease Analysis")
    st.write("Upload a clear, close-up image of the affected leaf.")
    img = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])
    if st.button("🔬 Analyze Leaf"):
        prompt = """
Provide very short answers (one sentence per heading). Use Markdown with bold headings:
1. **Disease or Pest Detected**
2. **Symptoms**
3. **Severity Level**
4. **Treatment Recommendations**
5. **Organic/Home Remedies**
"""
        with st.spinner("Analyzing leaf image..."):
            response = analyze_image(prompt, img)
        st.markdown("## 🔍 Analysis Results")
        st.markdown(response)

elif option == "Plant Disease Detection":
    st.header("🩺 Plant Disease Detection")
    st.write("Upload an image of the affected plant.")
    img = st.file_uploader("Upload plant image", type=["jpg", "png", "jpeg"])
    if st.button("🚨 Detect Disease"):
        prompt = """
Provide very short answers (one sentence per bullet). Use Markdown:
- **Disease/Pest**
- **Visible Symptoms**
- **Spread Prevention**
- **Treatment Suggestions**
"""
        with st.spinner("Detecting disease..."):
            response = analyze_image(prompt, img)
        st.markdown("## 🚨 Detection Results")
        st.markdown(response)
