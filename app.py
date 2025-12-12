#AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

API_KEY = "AIzaSyAutjPwiEPhon5I9ZppEDEHVtrEEnFg5Iw"
if not API_KEY or API_KEY.strip() == "":
    st.error("🚨 ERROR: API KEY is missing. Please add your key in the code.")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL = "gemini-2.5-flash"

safety_settings = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
]

try:
    model = genai.GenerativeModel(MODEL, safety_settings=safety_settings)
except Exception as e:
    st.error(f"Failed to initialize model {MODEL}: {e}")
    st.stop()

st.set_page_config(page_title="Smart Farming Assistant", layout="wide")


@st.cache_data(show_spinner="Analyzing image with Gemini...")
def analyze_image(prompt, image_file):
    """Analyzes an image file using the Gemini multimodal model."""
    if image_file is None:
        return "**Please upload an image before clicking 'Analyze'.**"

    image_bytes = image_file.getvalue()
    mime = image_file.type or "image/jpeg"

    content_parts = [
        prompt,
        {
            "mime_type": mime,
            "data": image_bytes
        }
    ]

    try:
        response = model.generate_content(content_parts)
        return response.text
    except Exception as e:
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"


@st.cache_data(show_spinner="Generating response...")
def analyze_text(prompt):
    """Analyzes a text prompt using the Gemini model."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"


st.title("🌾 Smart Farming Assistant (Gemini 2.5 Flash)")
st.caption("AI-powered analysis for plant health, soil conditions, and general farming questions.")


option = st.sidebar.radio(
    "Choose analysis type:",
    [
        "Leaf Disease Analysis",
        "Soil Health Analysis",
        "Plant Disease Detection",
        "General Farming Query"
    ]
)

if option == "Leaf Disease Analysis":
    st.header("🌿 Leaf Disease Analysis")
    st.write("Upload a clear, close-up image of the affected leaf.")
    img = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])

    if st.button("🔬 Analyze Leaf"):
        prompt = """
        Analyze this plant leaf. Provide your answer in a clear Markdown format with bold headings for each section:
        1. **Disease or Pest Detected**
        2. **Symptoms**
        3. **Severity Level**
        4. **Treatment Recommendations**
        5. **Organic/Home Remedies**
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🔍 Analysis Results")
        st.markdown(response)

elif option == "Soil Health Analysis":
    st.header("🌱 Soil Health Analysis")
    st.write("Upload an image of your soil sample.")
    img = st.file_uploader("Upload soil image", type=["jpg", "png", "jpeg"])

    if st.button("🧪 Analyze Soil"):
        prompt = """
        Analyze the soil in this image with Markdown formatting:
        - **Soil Type**
        - **Visible Moisture Level**
        - **Nutrient Indicators**
        - **Organic Matter Estimate**
        - **Best Crops**
        - **Improvement Suggestions**
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🔬 Analysis Results")
        st.markdown(response)

elif option == "Plant Disease Detection":
    st.header("🩺 Plant Disease Detection")
    st.write("Upload an image of the affected plant.")
    img = st.file_uploader("Upload plant image", type=["jpg", "png", "jpeg"])

    if st.button("🚨 Detect Disease"):
        prompt = """
        Detect the plant disease or pest. Provide:
        - **Disease/Pest**
        - **Visible Symptoms**
        - **Spread Prevention**
        - **Treatment Suggestions**
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🚨 Detection Results")
        st.markdown(response)

else:
    st.header("💬 General Farming Query")
    question = st.text_area("Ask your farming question here:")

    if st.button("➡️ Ask Gemini"):
        if question:
            st.info("Thinking...")
            full_prompt = (
                "You are an expert Smart Farming Assistant. Provide a detailed, structured response. "
                f"Query: {question}"
            )
            response = analyze_text(full_prompt)
            st.markdown("## 💡 Answer")
            st.markdown(response)
        else:
            st.warning("Please enter a question to ask.")
