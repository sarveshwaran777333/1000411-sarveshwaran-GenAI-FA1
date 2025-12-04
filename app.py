#genai.configure(api_key="AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg")
#FIREBASE_URL = "https://agronova-weather-default-rtdb.firebaseio.com"

import os
from flask import Flask, request, jsonify
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

# Configure Gemini
genai.configure(api_key=os.getenv("AIzaSyAq-ZfkANIx7dsOQ4keAwlqVt2S3hmevyg"))
MODEL = "gemini-2.5-flash"


def save_image(file):
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    return path


def gemini_image_query(prompt, image_path):
    response = genai.generate(
        model=MODEL,
        prompt=prompt,
        images=[image_path]
    )
    return response.text


def gemini_text_query(prompt):
    response = genai.generate(
        model=MODEL,
        prompt=prompt
    )
    return response.text


# ------------------ ROUTES ------------------

@app.route("/analyze-leaf", methods=["POST"])
def analyze_leaf():
    if "image" not in request.files:
        return jsonify({"error": "image required"}), 400

    file = request.files["image"]
    img_path = save_image(file)

    prompt = """Analyze this plant leaf. Identify:
    1. Disease or pest (if any)
    2. Cause
    3. Severity (Low/Medium/High)
    4. Recommended solution
    5. Organic/home-based treatment options"""

    result = gemini_image_query(prompt, img_path)
    return jsonify({"analysis": result})


@app.route("/detect-disease", methods=["POST"])
def detect_disease():
    if "image" not in request.files:
        return jsonify({"error": "image required"}), 400

    file = request.files["image"]
    img_path = save_image(file)

    prompt = """Identify any plant disease from this image.
    Provide:
    - Disease name
    - Symptoms visible in the photo
    - Immediate steps to prevent spread
    - Suggested pesticides or treatments"""

    result = gemini_image_query(prompt, img_path)
    return jsonify({"disease_detection": result})


@app.route("/soil-analysis", methods=["POST"])
def soil_analysis():
    if "image" not in request.files:
        return jsonify({"error": "image required"}), 400

    file = request.files["image"]
    img_path = save_image(file)

    prompt = """Analyze the soil in this image. Estimate:
    - Soil type (sandy, clay, loam, etc.)
    - Moisture condition
    - Fertility and organic matter level
    - Possible nutrient deficiencies
    - Crops best suited for this soil
    - Suggestions to improve soil health"""

    result = gemini_image_query(prompt, img_path)
    return jsonify({"soil_report": result})


@app.route("/general-query", methods=["POST"])
def general_query():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "question required"}), 400

    result = gemini_text_query(question)
    return jsonify({"answer": result})


# Run API
if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

