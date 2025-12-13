#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components

API_KEY = "AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"
if not API_KEY or API_KEY.strip() == "":
    st.error("API key missing")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL = "gemini-1.5-flash"

safety_settings = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
]

try:
    model = genai.GenerativeModel(MODEL, safety_settings=safety_settings)
except Exception as e:
    st.error(e)
    st.stop()

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")

st.title("🌾 Smart Farming Assistant")
st.caption("Type, speak, or upload a plant image")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

components.html(
    """
    <script>
    function startDictation() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition not supported');
            return;
        }
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.start();
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            const input = window.parent.document.getElementById("voice_input");
            input.value = text;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        };
    }
    </script>
    <button onclick="startDictation()">🎤 Speak</button>
    """,
    height=50,
)

voice_input = st.text_input(
    "Voice text",
    key="voice_input",
    label_visibility="collapsed",
)

text_input = st.text_input("Type your question")

image = st.file_uploader(
    "Upload leaf or plant image (optional)",
    type=["jpg", "jpeg", "png"],
)

final_query = voice_input if voice_input else text_input

if st.button("Ask"):
    if not final_query and not image:
        st.warning("Please type, speak, or upload an image")
    else:
        with st.spinner("Thinking..."):
            try:
                if image:
                    content = [
                        "Answer in very simple English for farmers. Detect disease and give short treatment.",
                        {
                            "mime_type": image.type,
                            "data": image.getvalue(),
                        },
                    ]
                    response = model.generate_content(content)
                    st.markdown("### 💡 Answer")
                    st.markdown(response.text)
                else:
                    prompt = (
                        "Answer in very simple English for farmers. Keep it short. "
                        + final_query
                    )
                    response = model.generate_content(prompt)
                    st.markdown("### 💡 Answer")
                    st.markdown(response.text)
            except Exception:
                st.error("Error while generating response. Check your API key or input.")
