#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import re
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components
import speech_recognition as sr
import tempfile

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

    st.subheader("Or upload audio")
    st.markdown("**Step 1:** Upload MP3 file and convert to WAV in-browser for free")
    mp3_file = st.file_uploader("Upload MP3 file:", type="mp3")
    if mp3_file:
        audio_bytes = mp3_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        html_code = f"""
        <audio id="audio" src="data:audio/mp3;base64,{audio_base64}" controls></audio>
        <button onclick="convertAudio()">Convert to WAV</button>
        <script>
        async function convertAudio() {{
            const audio = document.getElementById('audio');
            const arrayBuffer = await fetch(audio.src).then(r => r.arrayBuffer());
            const context = new (window.AudioContext || window.webkitAudioContext)();
            const decoded = await context.decodeAudioData(arrayBuffer);
            const wavBuffer = audioBufferToWav(decoded);
            const blob = new Blob([wavBuffer], {{type: 'audio/wav'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.wav';
            a.click();
        }}
        function audioBufferToWav(buffer) {{
            const numOfChan = buffer.numberOfChannels,
                  length = buffer.length * numOfChan * 2 + 44,
                  bufferArray = new ArrayBuffer(length),
                  view = new DataView(bufferArray),
                  channels = [], i, sample, offset = 0, pos = 0;
            function writeString(view, offset, string){{
                for (let i = 0; i < string.length; i++) {{
                    view.setUint8(offset + i, string.charCodeAt(i));
                }}
            }}
            writeString(view, 0, 'RIFF'); view.setUint32(4, length - 8, true); writeString(view, 8, 'WAVE');
            writeString(view, 12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, numOfChan, true);
            view.setUint32(24, buffer.sampleRate, true); view.setUint32(28, buffer.sampleRate * 2 * numOfChan, true);
            view.setUint16(32, numOfChan * 2, true); view.setUint16(34, 16, true); writeString(view, 36, 'data'); view.setUint32(40, length - 44, true);
            for(i=0; i<numOfChan; i++) channels.push(buffer.getChannelData(i));
            while(pos < buffer.length){{
                for(i=0;i<numOfChan;i++){{
                    sample = Math.max(-1, Math.min(1, channels[i][offset]));
                    view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                    pos += 2;
                }}
                offset++
            }}
            return view.buffer;
        }}
        </script>
        """
        st.components.v1.html(html_code, height=150)

    st.subheader("Or upload WAV directly")
    wav_file = st.file_uploader("Upload WAV file:", type="wav")
    if wav_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio_path = temp_audio.name
            temp_audio.write(wav_file.read())
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
                st.session_state.voice_text = recognizer.recognize_google(audio_data)
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
    img = st.file_uploader("Upload leaf image:", type=["jpg", "png", "jpeg"])
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
    img = st.file_uploader("Upload plant image:", type=["jpg", "png", "jpeg"])
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
