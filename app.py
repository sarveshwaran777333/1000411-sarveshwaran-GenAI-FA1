#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import streamlit as st
import base64
import google.generativeai as genai
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

API_KEY = "AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🌾 AGRONOVA")
st.caption("Ask anything about farming using text, voice, or image")

if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None

components.html(
    """
    <script>
    function startMic() {
        if (!('webkitSpeechRecognition' in window)) {
            alert("Browser does not support speech recognition");
            return;
        }
        const rec = new webkitSpeechRecognition();
        rec.lang = 'en-US';
        rec.start();
        rec.onresult = function(e) {
            const text = e.results[0][0].transcript;
            const input = window.parent.document.querySelector('input[type="text"]');
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    document.addEventListener('paste', function (event) {
        const items = event.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                reader.onload = function (e) {
                    window.parent.postMessage({
                        type: "IMAGE_PASTE",
                        data: e.target.result
                    }, "*");
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>

    <button onclick="startMic()" style="
        margin-bottom:12px;
        padding:6px 12px;
        border-radius:6px;
        border:none;
        cursor:pointer;
    ">🎤 Speak</button>
    """,
    height=60,
)

st.markdown(
    "<small>🖼️ <b>Ask AGRONOVA with image</b> — copy a plant or leaf image and press <b>Ctrl + V</b></small>",
    unsafe_allow_html=True,
)

query = st.text_input(
    "",
    placeholder="Ask anything about farming",
)

components.html(
    """
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "IMAGE_PASTE") {
            const streamlitDoc = window.parent.document;
            const input = streamlitDoc.getElementById("image_data");
            input.value = event.data.data;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        }
    });
    </script>
    """,
    height=0,
)

image_data = st.text_input("", key="image_data", label_visibility="collapsed")

if image_data:
    try:
        header, encoded = image_data.split(",", 1)
        st.session_state.image_bytes = base64.b64decode(encoded)
        st.image(st.session_state.image_bytes, caption="Pasted image", use_column_width=True)
    except:
        st.session_state.image_bytes = None

if st.button("Ask"):
    if not query and not st.session_state.image_bytes:
        st.warning("Please type, speak, or paste an image")
    else:
        with st.spinner("Thinking..."):
            try:
                if st.session_state.image_bytes:
                    response = model.generate_content([
                        "Identify the plant disease and give simple treatment.",
                        {
                            "mime_type": "image/png",
                            "data": st.session_state.image_bytes
                        }
                    ])
                else:
                    response = model.generate_content(
                        "Answer in simple English for farmers: " + query
                    )

                st.markdown("### 💡 Answer")
                st.write(response.text)

            except:
                st.error("Error while generating response. Check API key or input.")
