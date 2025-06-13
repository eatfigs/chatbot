import streamlit as st
import openai

st.set_page_config(page_title="Biology Chatbot")

st.title("🤖 Biology Chatbot")
st.markdown("Ask me anything related to biology!")

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# User input
prompt = st.text_input("Your question:")

if prompt:
    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful biology tutor for college-level non-biology majors."},
                {"role": "user", "content": prompt}
            ]
        )
        st.markdown("**Answer:**")
        st.write(response["choices"][0]["message"]["content"])
