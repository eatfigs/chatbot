import streamlit as st
import openai

st.set_page_config(page_title="Biology Chatbot")
st.title("🤖 Biology Chatbot")
st.markdown("Ask me anything about biology!")

# New-style OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

question = st.text_input("Your question:")

if question:
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful biology tutor for college-level non-biology majors."},
                {"role": "user", "content": question}
            ]
        )
        st.write("**Answer:**")
        st.markdown(response.choices[0].message.content)
