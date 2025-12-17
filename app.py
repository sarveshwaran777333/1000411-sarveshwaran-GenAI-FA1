#AIzaSyDSzGRDqBpaC5uKc209JOa94xI3vnj8M_E
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyDSzGRDqBpaC5uKc209JOa94xI3vnj8M_E")

text_model = genai.GenerativeModel("models/gemini-1.0-pro")
vision_model = genai.GenerativeModel("models/gemini-1.0-pro-vision")

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture related questions.
- Topics allowed: crops, soil, irrigation, pests, fertilizers, plant diseases, farming tools, and weather for farming.
- Use very simple English.
- Keep answers short (3–5 lines).
- If the question is NOT related to farming, reply ONLY with:
"I can help only with farming and agriculture questions."
"""

st.markdown("## 🌾 AGRONOVA")
st.markdown("Ask anything about farming using text, voice, or image")

text_query = st.text_input("", placeholder="Ask anything about farming")
uploaded_image = st.file_uploader("Ask AGRONOVA with image", type=["jpg", "jpeg", "png"])

components.html("""
<script>
function startDictation() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";
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
background-color:#4f6cff;
color:white;
">🎤 Speak</button>
""", height=90)

ask = st.button("Ask")

if ask:
    if uploaded_image:
        image = Image.open(uploaded_image)
        user_prompt = text_query if text_query else "Identify plant or leaf disease and give treatment"
        final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{user_prompt}"
        response = vision_model.generate_content([final_prompt, image])
        st.markdown("### 🌱 Result")
        st.write(response.text)

    elif text_query:
        final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{text_query}"
        response = text_model.generate_content(final_prompt)
        st.markdown("### 🌱 Result")
        st.write(response.text)

    else:
        st.warning("Please ask a farming question or upload an image")
