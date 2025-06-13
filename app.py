import streamlit as st
import openai
import PyPDF2
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Biology Chatbot")
st.title("🤖 Biology Chatbot")

# --- SIDEBAR SETTINGS ---
st.sidebar.title("⚙️ Settings")

# Model toggle
t_model = st.sidebar.radio("Choose a model:", ["gpt-3.5-turbo", "gpt-4"], index=1, key="model")

# Answer style toggle
answer_style = st.sidebar.radio("Answer Style:", ["Brief", "Standard", "Detailed"], index=1, key="style")

import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# Upload block (PDF and image support)
uploaded_file = st.sidebar.file_uploader("Upload PDF or image", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    text = ""
    if uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc[:2]:  # limit to 2 pages
                text += page.get_text()
    else:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)

    st.session_state.pdf_text = text.strip()
    if text:
        st.success("File uploaded and processed. I’ll consider it when answering.")
    else:
        st.warning("File uploaded but no readable text was extracted.")

# --- HEADER WITH MODEL INFO ---
st.markdown(f"<p style='color: gray;'>🧠 Model in use: <b>{t_model}</b></p>", unsafe_allow_html=True)

# --- CHAT DISPLAY ---
for msg in st.session_state.messages[1:]:  # skip initial system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.code(msg["content"], language=None)
            st.button("📋 Copy", key=f"copy_{hash(msg['content'])}", on_click=st.session_state.update, kwargs={})

# --- CHAT INPUT ---
prompt = st.chat_input("Ask a biology question...")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Adjust for answer style
    style_instructions = {
        "Brief": "Keep the answer short and focused.",
        "Standard": "Answer as a clear, friendly tutor would.",
        "Detailed": "Provide an in-depth and thorough explanation suitable for curious learners."
    }

    # Append answer style to system prompt
    custom_context = style_instructions[answer_style]
    if st.session_state.pdf_text:
        custom_context += f" Also refer to the following uploaded document if it helps: {st.session_state.pdf_text[:1500]}"

    st.session_state.messages[0]["content"] = f"You are a helpful biology tutor for college-level non-majors. {custom_context}"

    # Call OpenAI
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=t_model,
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content.strip()

    # Show assistant reply
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
