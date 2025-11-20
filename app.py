import streamlit as st
import google.generativeai as genai
import time

# ==========================
# CONFIG
# ==========================
genai.configure(api_key="AIzaSyB2M5orKk64-U65TmVUn4uD8_PKR03e7Nc")
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# HELPER FUNCTION: SHORTEN REPLY
# ==========================
def shorten_reply(text):
    words = text.split()
    if len(words) > 40:  # about 2–4 lines
        return " ".join(words[:35]) + "..."
    return text

# ==========================
# HELPER FUNCTION: GET REPLY SAFELY
# ==========================
def get_reply(prompt):
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 2500,
                "temperature": 0.4
            }
        )
        if response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text
        return None
    except Exception as e:
        if "429" in str(e):
            return "429"
        else:
            raise e

# ==========================
# STREAMLIT UI
# ==========================
st.title("🌾 AgroNova – Smart Farming Assistant")
st.write("A simple assistant for Tamil Nadu farmers. Type your question below!")

if "vanakkam_said" not in st.session_state:
    st.session_state.vanakkam_said = False

if not st.session_state.vanakkam_said:
    st.info(
        "Vanakkam! 🙏 I'm AgroNova, your friendly farming helper.\n\n"
        "Before we start, I need two details:\n"
        "1️⃣ Where are you in Tamil Nadu?\n"
        "2️⃣ What help do you want? (rain, crops, soil, pests, etc.)"
    )
    st.session_state.vanakkam_said = True

farmer_input = st.text_input("👩‍🌾 Farmer:", placeholder="Ask your question here...")

if st.button("Ask AgroNova"):
    if farmer_input.strip() == "":
        st.warning("Please type something first!")
    '''else:
        prompt = (
            "You are AgroNova, a friendly Tamil Nadu farming assistant. "
            "Always answer in very simple English. "
            "Use short answers (2–4 short lines). "
            "Avoid scientific words. "
            "Be warm and helpful.\n"
            "When farmer asks about pests, crops, soil, or rain:\n"
            "- Give main reason\n"
            "- Give 2–3 easy steps\n"
            "- Give 1 safety or prevention tip\n"
            "If farmer says 'tell more', explain slightly more but remain simple.\n\n"
            f"Farmer question: {farmer_input}"
        )

        try:
            reply = get_reply(prompt)

            if reply == "429":
                st.warning("AgroNova is resting 🌱. Too many questions at once. Waiting 5 seconds...")
                time.sleep(5)
                reply = get_reply(prompt)

            if reply == "429":
                st.error("AgroNova is still resting 🌱. Please wait a minute and try again.")
            elif not reply:
                st.error("Sorry, I couldn't understand. Please ask again in simple words.")
            else:
                reply = shorten_reply(reply)
                st.success(f"🤖 AgroNova: {reply}")

        except Exception as e:
            st.error(f"Error: {e}")
'''
