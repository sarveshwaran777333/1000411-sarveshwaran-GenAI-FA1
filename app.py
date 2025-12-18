import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="AGRONOVA", layout="wide")

if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0e1117"

def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        input, textarea {{
            background-color: #1c1f26 !important;
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(st.session_state.bg_color)

genai.configure(api_key=st.secrets["GENAI_API_KEY"])
model = genai.GenerativeModel("models/gemini-2.5-flash")

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture questions
- Use simple English
- Maximum 5 lines
- If question is not about farming, reply:
"I can help only with farming and agriculture questions."
"""

st.markdown("## 🌾 AGRONOVA")
st.markdown("**Farming AI assistant (Text · Image)**")

st.markdown("### 🎨 Change background")
new_color = st.color_picker(
    "Pick a background colour",
    st.session_state.bg_color
)

if st.button("Apply Background Color"):
    st.session_state.bg_color = new_color
    st.experimental_rerun()

question = st.text_input(
    "",
    placeholder="Ask a farming question"
)

image_file = st.file_uploader(
    "Upload a plant / leaf image",
    type=["jpg", "jpeg", "png"]
)

ask = st.button("Ask", disabled=not (question or image_file))

if ask:
    if not question and not image_file:
        st.warning("Please ask a farming question or upload an image")
    else:
        with st.spinner("Analyzing..."):
            try:
                if image_file:
                    image = Image.open(image_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format=image.format)
                    img_bytes = img_bytes.getvalue()

                    prompt = question or "Identify plant disease and suggest treatment"
                    response = model.generate_content(
                        input=[SYSTEM_PROMPT + prompt],
                        images=[img_bytes]
                    )
                else:
                    response = model.generate_content(
                        input=SYSTEM_PROMPT + question
                    )
                    
                    result_text = getattr(response, "text", None)
                if result_text:
                    st.markdown("### 🌱 Result")
                    st.write(result_text)
                else:
                    st.error("No response received from AI.")

            except Exception as e:
                st.error(f"Something went wrong. Please try again. ({e})")
