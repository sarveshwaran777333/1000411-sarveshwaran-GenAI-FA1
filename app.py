#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import streamlit as st
import google.generativeai as genai

API_KEY = "AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"

if not API_KEY or API_KEY.strip() == "":
    st.error("API key missing")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="AGRONOVA", layout="wide")

st.markdown("""
<style>
.image-drop {
    border: 2px dashed #4f46e5;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    font-size: 18px;
    color: #c7c7c7;
    margin-top: 20px;
    margin-bottom: 20px;
}
.image-drop small {
    display: block;
    margin-top: 8px;
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

st.title("🌾 AGRONOVA")
st.caption("Ask anything about farming using text or image")

question = st.text_input(
    "",
    placeholder="Ask anything about farming"
)

st.markdown("""
<div class="image-drop">
📎 Add image
<small>Drag & drop a plant or leaf image here, or click below</small>
</div>
""", unsafe_allow_html=True)

image = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

ask = st.button("Ask")

if ask:
    if not question and not image:
        st.warning("Please ask a question or upload an image")
    else:
        try:
            if image:
                response = model.generate_content([
                    "Answer in simple English so farmers can understand.",
                    {
                        "mime_type": image.type,
                        "data": image.getvalue()
                    },
                    question if question else "Analyze this image and explain clearly"
                ])
            else:
                response = model.generate_content(
                    "Answer in simple English so farmers can understand. " + question
                )

            st.markdown("### 💡 Answer")
            st.write(response.text)

        except Exception:
            st.error("Error while generating response. Check your API key or input.")
