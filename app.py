#AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0e1117"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {st.session_state.bg_color};
    }}
    input, textarea {{
        background-color: #1c1f26 !important;
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

genai.configure(api_key="API_KEY")
model = genai.GenerativeModel("models/gemini-2.5-flash")

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture questions.
- Use simple English.
- Limit answers to 3–5 lines.
- If not farming related, reply:
"I can help only with farming and agriculture questions."
"""

st.markdown("## 🌾 AGRONOVA")
st.markdown("**Farming AI assistant (Text · Voice · Image)**")

with st.popover("🎨 Change background"):
    color = st.color_picker(
        "Select background colour",
        st.session_state.bg_color
    )
    if color:
        st.session_state.bg_color = color
        st.rerun()

text_query = st.text_input("", placeholder="Ask a farming question")

uploaded_image = st.file_uploader(
    "Drag and drop a plant / leaf image here",
    type=["jpg", "jpeg", "png"]
)

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
margin-top:10px;
padding:10px 16px;
border-radius:8px;
border:none;
background:#4f6cff;
color:white;
font-size:16px;
cursor:pointer;
">🎤 Speak</button>
""", height=90)

ask = st.button("Ask")

if ask:
    if uploaded_image:
        image = Image.open(uploaded_image)
        prompt = text_query or "Identify the plant disease and suggest treatment"
        response = model.generate_content(
            [SYSTEM_PROMPT + prompt, image]
        )
        st.markdown("### 🌱 Result")
        st.write(response.text)

    elif text_query:
        response = model.generate_content(
            SYSTEM_PROMPT + text_query
        )
        st.markdown("### 🌱 Result")
        st.write(response.text)

    else:
        st.warning("Please ask a farming question or upload an image")
