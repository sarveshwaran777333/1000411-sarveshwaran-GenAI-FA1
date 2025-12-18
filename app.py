import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AGRONOVA", layout="wide")

# ---------------- SESSION STATE ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#a2d5ab"  # softer default green

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
st.markdown(
    """
    <style>
    /* Strong black outline for color picker */
    input[type=color] {
        border: 3px solid black !important;
        border-radius: 8px !important;
        box-shadow: 0 0 0 2px black inset;
        height: 50px !important;
        width: 50px !important;
        cursor: pointer;
        margin-bottom: 10px;
    }

    /* Black outline when focused */
    input[type=color]:focus {
        outline: 2px solid black !important;
    }

    /* Apply Background button styling */
    .apply-bg-btn button {
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #111;
        color: white;
        border-radius: 8px;
        border: 2px solid black;
        cursor: pointer;
        font-weight: bold;
    }

    .apply-bg-btn button:hover {
        background-color: #222;
    }
    </style>
    """,
    unsafe_allow_html=True
)

new_color = st.color_picker(
    "Pick a background colour",
    st.session_state.bg_color
)

st.markdown('<div class="apply-bg-btn">', unsafe_allow_html=True)
if st.button("Apply Background Color"):
    st.session_state.bg_color = new_color
    set_background(st.session_state.bg_color)
st.markdown('</div>', unsafe_allow_html=True)

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
