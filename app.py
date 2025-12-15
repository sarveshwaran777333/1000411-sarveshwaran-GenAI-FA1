#AIzaSyCUohRCUvFm5789mXmDfun8qbgFiIbXct8
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyCUohRCUvFm5789mXmDfun8qbgFiIbXct8")

available_models = [
    m.name for m in genai.list_models()
    if "generateContent" in getattr(m, "supported_generation_methods", [])
]
if not available_models:
    st.error("No models supporting generateContent are available for this API key.")
    st.stop()

MODEL_NAME = available_models[0]

st.markdown("""
<style>
body { background-color: #0e1117; }
.bigbox {
    border: 2px dashed #4f6cff;
    border-radius: 14px;
    padding: 40px;
    text-align: center;
    color: #cfd3ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌾 AGRONOVA")
st.markdown("Ask anything about farming using text, voice, or image")

text_query = st.text_input(label="", placeholder="Ask anything about farming")
uploaded_image = st.file_uploader(label="", type=["jpg", "jpeg", "png"])

# Mic overlay HTML (position fixed, separate from Streamlit layout)
components.html("""
<div id="overlay" style="
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    backdrop-filter: blur(6px);
    background-color: rgba(0,0,0,0.5);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 9999;
">
  <button id="micButton" style="
    padding: 30px;
    border-radius: 50%;
    border: none;
    background-color: #4f6cff;
    color: white;
    font-size: 30px;
    cursor: pointer;
  ">🎤</button>
</div>

<script>
let recognition;
const overlay = document.getElementById("overlay");
const micButton = document.getElementById("micButton");

function startDictation() {
    overlay.style.display = "flex";
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported");
        overlay.style.display = "none";
        return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        const input = window.parent.document.querySelector('input[type="text"]');
        input.value = text;
        input.dispatchEvent(new Event('input', { bubbles: true }));
    };

    recognition.onend = function() {
        overlay.style.display = "none";
    };

    recognition.start();
}

micButton.onclick = () => {
    startDictation();
};
</script>

<button onclick="startDictation()" style="
padding:10px 16px;
border-radius:8px;
border:none;
cursor:pointer;
font-size:16px;
background-color:#4f6cff;
color:white;
">🎤 Speak</button>
""", height=120)  # small height so it doesn't hide other elements

# Streamlit Ask button
ask = st.button("Ask")

if ask:
    model = genai.GenerativeModel(MODEL_NAME)

    if uploaded_image:
        image = Image.open(uploaded_image)
        prompt = text_query if text_query else "Identify plant or leaf disease and give treatment"
        concise_prompt = f"{prompt}\n\nAnswer concisely in 3-5 lines."
        response = model.generate_content([concise_prompt, image])
        st.markdown("### 🌱 Result")
        st.write(response.text)

    elif text_query:
        concise_prompt = f"{text_query}\n\nAnswer concisely in 3-5 lines."
        response = model.generate_content(concise_prompt)
        st.markdown("### 🌱 Result")
        st.write(response.text)

    else:
        st.warning("Please ask a question or upload an image")
