import streamlit as st
import openai
from PIL import Image
import PyPDF2
from io import BytesIO
from streamlit.components.v1 import html

# --- App Config ---
st.set_page_config(page_title="TCU Biology Chatbot", layout="wide")

# --- Session State Setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "model" not in st.session_state:
    st.session_state.model = "gpt-4"
if "answer_style" not in st.session_state:
    st.session_state.answer_style = "standard"

# --- Sidebar ---
st.sidebar.title("Settings")
if st.sidebar.button("🔁 Restart Chat"):
    st.session_state.messages = []
    st.session_state.summary = ""

st.session_state.model = st.sidebar.radio("Model", ["gpt-3.5-turbo", "gpt-4"], index=1)
st.session_state.answer_style = st.sidebar.radio("Answer Style", ["brief", "standard", "detailed"], index=1)

# --- Title ---
st.title("🧬 TCU Biology Chatbot")
st.markdown("Ask me anything about biology — I’m here to help non-majors like you.")

# --- File Upload (PDF, Image) ---
uploaded_file = st.file_uploader("📎 Upload a PDF or image (optional):", type=["pdf", "png", "jpg", "jpeg"])
text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n\n".join([page.extract_text() for page in reader.pages[:2] if page.extract_text()])
    elif uploaded_file.type.startswith("image/"):
        image = Image.open(uploaded_file)
        st.image(image, caption="Image uploaded")
        st.warning("Text extraction from images is not currently supported.")
        text = ""

# --- Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a biology question")

if user_input:
    # --- Append User Input ---
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- Summarize Earlier Messages (after 10 exchanges) ---
    if len(st.session_state.messages) > 10:
        recent = st.session_state.messages[-5:]
        prior = st.session_state.messages[:-5]
        summary_prompt = [
            {"role": "system", "content": "Summarize this biology Q&A thread for context in one paragraph."},
            *prior
        ]
        summary_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=summary_prompt
        )
        st.session_state.summary = summary_response.choices[0].message.content.strip()
        st.session_state.messages = [{"role": "system", "content": st.session_state.summary}] + recent

    # --- Add User Input Again After Summarizing ---
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- Style Prompt ---
    style_instruction = {
        "brief": "Please answer briefly using one paragraph.",
        "standard": "Please answer clearly for college students with examples.",
        "detailed": "Please answer in detail with examples, analogies, and definitions suitable for non-biology majors."
    }

    st.session_state.messages.insert(0, {
        "role": "system",
        "content": f"You are a helpful AI biology tutor. {style_instruction[st.session_state.answer_style]}"
    })

    # --- Append Uploaded Text (if any) ---
    if text:
        st.session_state.messages.append({"role": "user", "content": f"Here is some background text: {text}"})

    # --- Get Response ---
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=st.session_state.model,
        messages=st.session_state.messages
    )
    assistant_reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # --- Show Response ---
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# --- Auto-scroll to bottom using JavaScript ---
html("""
<script>
  window.scrollTo(0, document.body.scrollHeight);
</script>
""")
