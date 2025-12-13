#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import base64
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components

API_KEY = "AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"
if not API_KEY:
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    safety_settings=[
        {
            "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
            "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    ],
)

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")
st.title("🌾 Smart Farming Assistant")
st.caption("Type, speak, or paste an image (Ctrl+V)")

if "pasted_image" not in st.session_state:
    st.session_state.pasted_image = None

components.html(
    """
    <script>
    document.addEventListener('paste', function (event) {
        const items = event.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                reader.onload = function (e) {
                    const base64Image = e.target.result;
                    const input = window.parent.document.getElementById("paste_image");
                    input.value = base64Image;
                    input.dispatchEvent(new Event("change", { bubbles: true }));
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>
    """,
    height=0,
)

pasted_image_base64 = st.text_input(
    "Paste image here",
    key="paste_image",
    label_visibility="collapsed",
)

components.html(
    """
    <script>
    function startMic() {
        const rec = new webkitSpeechRecognition();
        rec.lang = 'en-US';
        rec.start();
        rec.onresult = function(e) {
            const text = e.results[0][0].transcript;
            const input = window.parent.document.getElementById("voice");
            input.value = text;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        }
    }
    </script>
    <button onclick="startMic()">🎤 Speak</button>
    """,
    height=40,
)

voice_text = st.text_input("voice", key="voice", label_visibility="collapsed")
text = st.text_input("Type your question")

query = voice_text if voice_text else text

if pasted_image_base64:
    header, encoded = pasted_image_base64.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    st.image(image_bytes, caption="Pasted image")

if st.button("Ask"):
    if not query and not pasted_image_base64:
        st.warning("Type, speak, or paste an image")
    else:
        with st.spinner("Thinking..."):
            try:
                if pasted_image_base64:
                    content = [
                        "Detect plant or leaf disease. Answer in very simple English. Give short treatment.",
                        {
                            "mime_type": "image/png",
                            "data": image_bytes,
                        },
                    ]
                    response = model.generate_content(content)
                else:
                    prompt = "Answer in very simple English for farmers. Keep it short. " + query
                    response = model.generate_content(prompt)

                st.markdown("### 💡 Answer")
                st.markdown(response.text)

            except Exception:
                st.error("Error while generating response. Check API key or input.")
