import streamlit as st
import openai

# Set up the app UI
st.set_page_config(page_title="Biology Chatbot")
st.title("🤖 Biology Chatbot")
st.markdown("Ask me anything about biology!")

# Sidebar model selection
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio(
    "Choose a model:",
    options=["gpt-3.5-turbo", "gpt-4"],
    index=1,
    key="model"
)

# Restart button
if st.button("🔄 Restart Conversation"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly biology tutor helping college-level non-majors understand science clearly."}
    ]
    st.session_state.summary = None
    st.rerun()

# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly biology tutor helping college-level non-majors understand science clearly."}
    ]
if "summary" not in st.session_state:
    st.session_state.summary = None

# Function to summarize older parts of the chat
def summarize_chat():
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    summary_prompt = [
        {"role": "system", "content": "Summarize this biology conversation in 1-2 sentences."},
        *st.session_state.messages[1:-5]  # exclude system and last 5
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=summary_prompt
        )
        summary = response.choices[0].message.content.strip()
        return summary if summary else "Conversation summary not available."
    except Exception as e:
        return "Summary failed."

# Handle user input
if prompt := st.chat_input("Ask a biology question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Summarize if too many messages
    if len(st.session_state.messages) > 12:
        summary = summarize_chat()
        st.session_state.summary = summary
        st.session_state.messages = [
            {"role": "system", "content": f"You are a friendly biology tutor. Previous conversation summary: {summary}"},
            *st.session_state.messages[-5:]
        ]

    # Build client and send request
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Validate message structure
    valid_messages = [
        msg for msg in st.session_state.messages
        if isinstance(msg, dict) and msg.get("role") and msg.get("content")
    ]

    try:
        response = client.chat.completions.create(
            model=st.session_state.model,
            messages=valid_messages
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    # Show and store reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)

# Show full history (excluding initial system message)
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).markdown(msg["content"])
