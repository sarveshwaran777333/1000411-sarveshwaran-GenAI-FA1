#genai.configure(api_key="AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


try:
    API_KEY = st.secrets["AIzaSyBRxR6B_cF_-2DKtqU01O_3rtc9R56o17I"]
except KeyError:
    st.error("🚨 Configuration Error: Gemini API key not found.")
    st.markdown(
        "Please ensure you have set `gemini_api_key` in your "
        "`.streamlit/secrets.toml` file or as an environment variable."
    )
    st.stop()

# --- CONFIGURATION ---
genai.configure(api_key=API_KEY)

# Using 'flash' for better speed/cost balance for image analysis and general chat.
MODEL = "gemini-2.5-flash" 

# Configure safety settings to potentially allow more agricultural content
# which might involve discussions of pests/diseases, if needed.
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


# --- ENHANCED ANALYSIS FUNCTIONS with Error Handling ---

@st.cache_data(show_spinner="Analyzing image with Gemini...")
def analyze_image(prompt, image_file):
    """Analyzes an image file using the Gemini multimodal model."""
    if image_file is None:
        return "**Please upload an image before clicking 'Analyze'.**"

    # Get data and MIME type
    image_bytes = image_file.getvalue()
    mime = image_file.type or "image/jpeg"

    # Prepare content parts
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
        # CRITICAL FIX 2: Better API error handling
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"


@st.cache_data(show_spinner="Generating response...")
def analyze_text(prompt):
    """Analyzes a text prompt using the Gemini model."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # CRITICAL FIX 2: Better API error handling
        return f"🚨 **API Error:** Could not complete the analysis. Details: {e}"


# --- UI LAYOUT ---

st.title("🌾 Smart Farming Assistant (Gemini 2.5 Flash)")
st.caption("AI-powered analysis for plant health, soil conditions, and general farming questions.")

# Sidebar for analysis option
option = st.sidebar.radio(
    "Choose analysis type:",
    [
        "Leaf Disease Analysis",
        "Soil Health Analysis",
        "Plant Disease Detection",
        "General Farming Query"
    ]
)

# ---------------------------------------------------
# LEAF DISEASE ANALYSIS
# ---------------------------------------------------
if option == "Leaf Disease Analysis":
    st.header("🌿 Leaf Disease Analysis")
    st.write("Upload a clear, close-up image of the affected leaf.")
    img = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])

    if st.button("🔬 Analyze Leaf"):
        prompt = """
        Analyze this plant leaf. Provide your answer in a clear Markdown format with bold headings for each section:
        1. **Disease or Pest Detected**: The most likely issue.
        2. **Symptoms**: Detailed visible characteristics.
        3. **Severity Level**: Low, Medium, or High.
        4. **Treatment Recommendations**: Specific actions, including chemical or biological controls.
        5. **Organic/Home Remedies**: Safe, eco-friendly alternatives.
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🔍 Analysis Results")
        st.markdown(response)

# ---------------------------------------------------
# SOIL HEALTH ANALYSIS
# ---------------------------------------------------
elif option == "Soil Health Analysis":
    st.header("🌱 Soil Health Analysis")
    st.write("Upload an image of your soil sample.")
    img = st.file_uploader("Upload soil image", type=["jpg", "png", "jpeg"])

    if st.button("🧪 Analyze Soil"):
        prompt = """
        Analyze the soil in this image. Provide your analysis in a clear Markdown format:
        - **Soil Type**: (e.g., Sandy, Clay, Loam)
        - **Visible Moisture Level**: (e.g., Dry, Moist, Saturated)
        - **Visual Fertility & Nutrient Indicators**: Observations on color, aggregation, etc.
        - **Organic Matter Level Estimate**: Based on visual appearance.
        - **Best Crops for This Soil**: Suggestions based on the analysis.
        - **Improvement Suggestions**: Steps to enhance soil health (e.g., adding compost, adjusting pH).
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🔬 Analysis Results")
        st.markdown(response)

# ---------------------------------------------------
# PLANT DISEASE DETECTION
# ---------------------------------------------------
elif option == "Plant Disease Detection":
    st.header("🩺 Plant Disease Detection")
    st.write("Upload an image of the entire affected plant or a section showing damage.")
    img = st.file_uploader("Upload plant image", type=["jpg", "png", "jpeg"])

    if st.button("🚨 Detect Disease"):
        prompt = """
        Detect the plant disease or pest from the image. Provide your answer in a clear Markdown format:
        - **Disease Name/Pest**: Identification of the problem.
        - **Visible Symptoms**: Detailed description of what is visible.
        - **Spread Prevention Steps**: How to stop it from infecting other plants.
        - **Treatment Suggestions**: Recommended actions and products.
        """
        st.info("Analysis in progress...")
        response = analyze_image(prompt, img)
        st.markdown("## 🚨 Detection Results")
        st.markdown(response)

# ---------------------------------------------------
# GENERAL FARMING QUERY
# ---------------------------------------------------
else:
    st.header("💬 General Farming Query")
    st.write("Ask any question about crops, irrigation, fertilization, weather, or techniques.")
    
    question = st.text_area("Ask your farming question here:")

    if st.button("➡️ Ask Gemini"):
        if question:
            st.info("Thinking...")
            # Enhanced prompt for general queries
            full_prompt = (
                "You are an expert Smart Farming Assistant. Answer the following query "
                "in a detailed, helpful, and organized Markdown format. Query: "
                f"{question}"
            )
            response = analyze_text(full_prompt)
            st.markdown("## 💡 Answer")
            st.markdown(response)
        else:
            st.warning("Please enter a question to ask.")
