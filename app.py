#AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ
import streamlit as st
import google.generativeai as genai
from PIL import Image

GEMINI_API_KEY = "AIzaSyBp3WN0Q1ww9-XCOaKYen9zKZrUU0COqnQ"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="AGRONOVA", layout="centered")

st.markdown("""
<style>
body { background:#0e1117; }
.response { background:#1f2937; padding:16px; border-radius:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌱 AGRONOVA")
st.markdown("Ask anything about farming using text or voice")

# ---------- STATE ----------
if "query" not in st.session_state:
    st.session_state.query = ""

# ---------- INPUT (TEXT + MIC) ----------
spoken_text = st.components.html("""
<style>
.input-box {
  display:flex;
  align-items:center;
  background:#1f2937;
  border-radius:30px;
  padding:14px 18px;
}
.input-box input {
  flex:1;
  background:transparent;
  border:none;
  color:white;
  font-size:16px;
  outline:none;
}
.mic {
  cursor:pointer;
  font-size:18px;
  margin-left:10px;
}
</style>

<div class="input-box">
  <input id="q" placeholder="Ask anything about farming" />
  <span class="mic" onclick="speak()">🎤</span>
</div>

<script>
function speak(){
  if(!('webkitSpeechRecognition' in window)){
    alert("Speech not supported");
    return;
  }

  var rec = new webkitSpeechRecognition();
  rec.lang = "en-IN";
  rec.onresult = function(e){
    let text = e.results[0][0].transcript;
    document.getElementById("q").value = text;

    // send text to Streamlit
    window.parent.postMessage(
      {type:"voice", value:text},
      "*"
    );
  };
  rec.start();
}
</script>
""", height=90)

# ---------- RECEIVE VOICE TEXT ----------
st.markdown("""
<script>
window.addEventListener("message", (e) => {
  if(e.data.type === "voice"){
    const input = document.querySelector('input');
    input.value = e.data.value;
  }
});
</script>
""", unsafe_allow_html=True)

text_query = st.text_input(
    label="",
    placeholder="Ask anything about farming",
    key="query"
)

image = st.file_uploader(
    "Add image (optional)",
    type=["jpg","jpeg","png"]
)

# ---------- AUTO SUBMIT ----------
if st.button("Ask") or st.session_state.query:
    if not st.session_state.query and not image:
        st.warning("Ask a question or use the mic")
    else:
        with st.spinner("Thinking..."):
            if image:
                img = Image.open(image)
                res = model.generate_content(
                    [st.session_state.query or "Analyze this image", img]
                )
            else:
                res = model.generate_content(st.session_state.query)

        st.markdown("### Response")
        st.markdown(f"<div class='response'>{res.text}</div>", unsafe_allow_html=True)
