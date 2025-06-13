import streamlit as st
import openai

st.set_page_config(page_title="Biology Chatbot")
st.title("🤖 Biology Chatbot")
st.markdown("Ask me anything about biology!")

# ✅ Sidebar model selector
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio(
    "Choose a model:",
    options=["gpt-3.5-turbo (faster)", "gpt-4 (more detailed)"],
    index=1,
    key="model"
)

# 🔁 Restart conversation button
if st.button("🔄 Restart Conversation"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly biology tutor helping college-level non-majors understand science clearly."}
    ]
    st.session_state.summary = None
    st.rerun()

# ✅ Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly biology tutor helping college-level non-majors understand science clearly."}
    ]
if "summary" not in st.session_state:
    st.session_state.summary = None

# 🧹 Summarize and prune older messages
def summarize_chat():
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    summary_prompt = [
        {"role": "system", "content": "Summarize this conversation in 1-2 sentences for future reference."},
        *st.session_state.messages[1:-5]  # Skip system, keep recent
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use cheap model for summarizing
        messages=summary_prompt
    )
    return response.choices[0].message.content

# ✏️ Handle user input
if prompt := st.chat_input("Ask a biology question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Summarize if conversation is too long
    if len(st.session_state.messages) > 12:
        summary_text = summarize_chat()
        st.session_state.summary = summary_text
        st.session_state.messages = [
            {"role": "system", "content": f"You are a friendly biology tutor. Previous conversation summary: {summary_text}"},
            *st.session_state.messages[-5:]
        ]

    # Send to OpenAI
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=st.session_state.model,
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)

# 💬 Show chat history
for msg in st.session_state.messages[1:]:  # Skip system
    st.chat_message(msg["role"]).markdown(msg["content"])
