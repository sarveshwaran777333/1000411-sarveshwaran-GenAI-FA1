import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AGRONOVA", layout="wide")

# ---------------- SESSION STATE ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#a2d5ab"

# ---------------- COLOR CONTRAST LOGIC ----------------
def get_text_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (0.299*r + 0.587*g + 0.114*b)
    return "#000000" if brightness > 186 else "#FFFFFF"

# ---------------- BACKGROUND STYLE ----------------
def set_background(color):
    text_color = get_text_color(color)

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
            color: {text_color};
        }}

        h1, h2, h3, h4, h5, h6,
        p, span, label, div {{
            color: {text_color} !important;
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

# ---------------- GEMINI CONFIG ----------------
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

# ---------------- UI ----------------
st.markdown("## 🌾 AGRONOVA")
st.markdown("**Farming AI assistant (Text · Image)**")

# ---------------- BACKGROUND PICKER ----------------
st.markdown("### 🎨 Change background")

new_color = st.color_picker(
    "Pick a background colour",
    st.session_state.bg_color
)

if st.button("Apply Background Color"):
    st.session_state.bg_color = new_color
    set_background(new_color)

# ---------------- INPUTS ----------------
question = st.text_input(
    "",
    placeholder="Ask a farming question"
)

image_file = st.file_uploader(
    "Upload a plant / leaf image",
    type=["jpg", "jpeg", "png"]
)

ask = st.button("Ask", disabled=not (question or image_file))

# ---------------- RESPONSE ----------------
if ask:
    with st.spinner("Analyzing..."):
        try:
            content = []

            user_prompt = question or "Identify the plant disease and suggest treatment."
            content.append(SYSTEM_PROMPT + "\n" + user_prompt)

            if image_file:
                image = Image.open(image_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

                img_bytes = io.BytesIO()
                image.save(img_bytes, format=image.format)
                img_bytes = img_bytes.getvalue()

                content.append({
                    "mime_type": "image/png",
                    "data": img_bytes
                })

            response = model.generate_content(content)

            if response.text:
                st.markdown("### 🌱 Result")
                st.write(response.text)
            else:
                st.error("No response received from AI.")

        except Exception as e:
            st.error(f"Something went wrong. Please try again.\n\n{e}")
