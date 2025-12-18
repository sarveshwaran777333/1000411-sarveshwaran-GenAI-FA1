import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AGRONOVA", layout="wide")

# ---------------- SESSION STATE ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0e1117"

# ---------------- BACKGROUND STYLE ----------------
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
        /* Color picker outline in black */
        input[type=color] {{
            border: 2px solid black !important;
            height: 35px;
            width: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply current background
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

# Button to apply the background color
if st.button("Apply Background Color"):
    st.session_state.bg_color = new_color
    set_background(st.session_state.bg_color)

# ---------------- INPUTS ----------------
question = st.text_input(
    "",
    placeholder="Ask a farming question"
)

image_file = st.file_uploader(
    "Upload a plant / leaf image",
    type=["jpg", "jpeg", "png"]
)

# Disable button if no input
ask = st.button("Ask", disabled=not (question or image_file))

# ---------------- RESPONSE ----------------
if ask:
    if not question and not image_file:
        st.warning("Please ask a farming question or upload an image")
    else:
        with st.spinner("Analyzing..."):
            try:
                # If an image is uploaded
                if image_file:
                    image = Image.open(image_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    
                    # Convert image to bytes for Gemini API
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

                # Safely display response text
                result_text = getattr(response, "text", None)
                if result_text:
                    st.markdown("### 🌱 Result")
                    st.write(result_text)
                else:
                    st.error("No response received from AI.")

            except Exception as e:
                st.error(f"Something went wrong. Please try again. ({e})")
