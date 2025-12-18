#AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="AGRONOVA", layout="wide")

genai.configure(api_key="AIzaSyC-bojZZZiNEkF8nLcvaPfsSPGyQh0HCmM")

model = genai.GenerativeModel("models/gemini-2.5-flash")

SYSTEM_PROMPT = """
You are AgroNova, a farming-only AI assistant.

Rules:
- Answer ONLY farming and agriculture related questions.
- Allowed topics: crops, soil, irrigation, pests, fertilizers, plant diseases, farming tools, weather for farming.
- Use very simple English.
- Keep answers short (3–5 lines).
- If the question is NOT related to farming, reply ONLY with:
"I can help only with farming and agriculture questions."
"""

components.html(
"""
<div style="display:flex;align-items:center;gap:10px;">
  <input type="color" id="bgPicker" value="#0e1117"
  style="width:60px;height:40px;border:none;cursor:pointer;"
  oninput="
    document.body.style.backgroundColor = this.value;
    document.querySelector('.stApp').style.backgroundColor = this.value;
  ">
  <span style="color:white;font-size:14px;">Change background</span>
</div>
""",
height=60
)

st.markdown("""
<style>
.bigbox {
    border: 2px dashed #4f6cff;
    border-radius: 14px;
    padding: 30px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌾 AGRONOVA")
st.markdown("Farming AI assistant (Text • Voice • Image)")

text_query = st.text_input("", placeholder="Ask a farming question")
uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])
components.html(
"""
<style>
#colorBtn {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  border: 2px solid white;
  cursor: pointer;
  background: #4f6cff;
}
#colorInput {
  opacity: 0;
  width: 42px;
  height: 42px;
  position: absolute;
  cursor: pointer;
}
</style>

<div style="position:relative;display:inline-block;">
  <div id="colorBtn"></div>
  <input type="color" id="colorInput" value="#0e1117"
    onchange="
      document.body.style.backgroundColor=this.value;
      document.querySelector('.stApp').style.backgroundColor=this.value;
    ">
</div>
""",
height=60
)


ask = st.button("Ask")

if ask:
    try:
        if uploaded_image:
            image = Image.open(uploaded_image)
            user_prompt = text_query if text_query else "Identify plant or leaf disease and give treatment"
            final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{user_prompt}"
            response = model.generate_content([final_prompt, image])

        elif text_query:
            final_prompt = f"{SYSTEM_PROMPT}\nUser question:\n{text_query}"
            response = model.generate_content(final_prompt)

        else:
            st.warning("Please ask a farming question or upload an image")
            st.stop()

        st.markdown("### 🌱 Result")
        st.write(response.text)

    except Exception:
        st.error("Something went wrong. Check your API key and model access.")
