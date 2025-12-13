#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import base64
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit.components.v1 as components

API_KEY = "YOUR_GEMINI_API_KEY"
if not API_KEY or API_KEY.strip() == "":
    st.error("API key missing")
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

st.set_page_config(page_title="AGRONOVA", layout="wide")
st.title("🌾 AGRONOVA")
st.caption("Ask anything about farming using text, voice, or image")

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

pasted_image_base64 = st.text_input("", key="paste_image", label_visibility="collapsed")

components.html(
    """
    <script>
    function startMic() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition not supported in this browser');
            return;
        }
        const rec = new webkitSpeechRecognition();
        rec.lang = 'en-US';
        rec.interimResults = false;
        rec.start();
        rec.onresult = function(e) {
            const text = e.results[0][0].transcript;
            const input = window.parent.document.getElementById("voice_input");
            input.value = text;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        }
    }
    </script>
    <button onclick="startMic()">🎤 Speak</button>
    """,
    height=45,
)

voice_text = st.text_input("", key="voice_input", label_visibility="collapsed")

text = st.text_input(
    "",
    placeholder="Ask anything about farming",
)

st.caption("🖼️ Ask AGRONOVA with image — copy a plant or leaf image and press Ctrl + V")

query = voice_text if voice_text else text

image_bytes = None
if pasted_image_base64:
    try:
        header, encoded = pasted_image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        st.image(image_bytes, caption="Pasted image", use_column_width=True)
    except Exception:
        image_bytes = None

if st.button("Ask"):
    if not query and not image_bytes:
        st.warning("Please type, speak, or paste an image")
    else:
        with st.spinner("Thinking..."):
            try:
                if image_bytes:
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
                st.error("Error while generating response. Check your API key or input.")
