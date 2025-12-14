#AIzaSyDhHTS1ix5bcS4yxj_s9satnI8e4l6K08Q 
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyDhHTS1ix5bcS4yxj_s9satnI8e4l6K08Q")

# Automatically select the first valid model that supports generateContent
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

components.html("""
<script>
let recognition;
function startDictation() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Speech recognition not supported");
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
  recognition.start();
}
</script>
<button onclick="startDictation()" style="
padding:10px 16px;
border-radius:8px;
border:none;
cursor:pointer;
font-size:16px;
">🎤 Speak</button>
""", height=70)

ask = st.button("Ask")

if ask:
    model = genai.GenerativeModel(MODEL_NAME)

    if uploaded_image:
        image = Image.open(uploaded_image)
        prompt = text_query if text_query else "Identify plant or leaf disease and give treatment"
        response = model.generate_content([prompt, image])
        st.markdown("### 🌱 Result")
        st.write(response.text)

    elif text_query:
        response = model.generate_content(text_query)
        st.markdown("### 🌱 Result")
        st.write(response.text)

    else:
        st.warning("Please ask a question or upload an image")
