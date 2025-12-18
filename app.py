#AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM")

MODEL_NAME = "models/gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture related questions.
- Allowed topics: crops, soil, irrigation, fertilizers, pests, plant diseases, weather for farming.
- Use very simple English.
- Keep answers short (3–5 lines).
- If the question is NOT related to farming, reply ONLY with:
"I can help only with farming and agriculture questions."
"""

st.markdown("""
<style>
.bigbox {
    border: 2px dashed #4f6cff;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌾 AGRONOVA")
st.markdown("Ask anything about farming using **text, voice, or image**")

text_query = st.text_input(
    "",
    placeholder="Ask anything about farming"
)

uploaded_image = st.file_uploader(
    "Ask AGRONOVA with image",
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
padding:10px 18px;
border-radius:10px;
border:none;
cursor:pointer;
font-size:16px;
background-color:#4f6cff;
color:white;
">🎤 Speak</button>
""", height=90)

ask = st.button("Ask")

if ask:
    try:
        if uploaded_image:
            image = Image.open(uploaded_image)

            user_prompt = (
                text_query
                if text_query.strip()
                else "Identify the plant problem and suggest treatment"
            )

            final_prompt = f"""
{SYSTEM_PROMPT}

User question:
{user_prompt}
"""

            response = model.generate_content([final_prompt, image])
            st.markdown("### 🌱 Result")
            st.write(response.text)

        elif text_query.strip():
            final_prompt = f"""
{SYSTEM_PROMPT}

User question:
{text_query}
"""

            response = model.generate_content(final_prompt)
            st.markdown("### 🌱 Result")
            st.write(response.text)

        else:
            st.warning("Please ask a farming question or upload an image")

    except Exception as e:
        st.error("Something went wrong. Check your API key and model access.")
