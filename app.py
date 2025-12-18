#AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM")

MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture related questions.
- Allowed topics: crops, soil, irrigation, pests, fertilizers, plant diseases, tools, farming weather.
- Use simple English.
- Answer in 3–5 short lines.
- If NOT farming related, reply ONLY:
"I can help only with farming and agriculture questions."
"""

st.markdown("""
<style>
body {
    background-color: #0e1117;
}
input, textarea {
    background-color: #1c1f26 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌾 AGRONOVA")
st.markdown("**Farming AI assistant (Text • Voice • Image)**")

components.html(
"""
<style>
.bg-control {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0 20px 0;
  color: #cfd3ff;
  font-size: 14px;
}
</style>

<div class="bg-control">
  <span>Change background</span>
  <input type="color" value="#0e1117"
    style="width:28px;height:28px;border:none;background:none;cursor:pointer"
    onchange="document.querySelector('.stApp').style.backgroundColor=this.value">
</div>
""",
height=60
)

text_query = st.text_input("", placeholder="Ask a farming question")

uploaded_image = st.file_uploader(
    "Drag and drop a plant / leaf image here",
    type=["jpg", "jpeg", "png"]
)

components.html("""
<script>
function startDictation() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";
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
margin-top:10px;
padding:10px 16px;
border-radius:8px;
border:none;
cursor:pointer;
font-size:16px;
background-color:#4f6cff;
color:white;
">🎤 Speak</button>
""", height=90)

ask = st.button("Ask")

if ask:
    if uploaded_image:
        image = Image.open(uploaded_image)
        user_prompt = text_query if text_query else "Identify the plant disease and suggest treatment"
        final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{user_prompt}"

        response = model.generate_content([final_prompt, image])
        st.markdown("### 🌱 Result")
        st.write(response.text)

    elif text_query:
        final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{text_query}"
        response = model.generate_content(final_prompt)

        st.markdown("### 🌱 Result")
        st.write(response.text)

    else:
        st.warning("Please ask a farming question or upload an image")
