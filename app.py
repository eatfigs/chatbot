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

# File uploader (PDF)
uploaded_file = st.sidebar.file_uploader("Upload PDF (e.g. lecture slides)", type=["pdf"])

# --- INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful biology tutor for college-level non-majors."}
    ]
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- PARSE PDF IF UPLOADED ---
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages[:2]:  # Limit to first 2 pages for speed
        text += page.extract_text() or ""
    st.session_state.pdf_text = text.strip()
    if text:
        st.success("PDF uploaded and processed. I’ll consider it when answering.")

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
