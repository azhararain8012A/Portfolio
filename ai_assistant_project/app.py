"""Simple AI Assistant portfolio application using Streamlit.

This project demonstrates an end-to-end AI assistant pattern: user input,
conversation state, prompt construction, model/API integration point, and
clean UI. Set OPENAI_API_KEY in the environment before using a compatible API.
"""
import os
import streamlit as st

st.set_page_config(page_title="Azhar AI Assistant", page_icon="🤖", layout="centered")

st.title("🤖 Azhar AI Assistant")
st.caption("A portfolio demonstration of a conversational AI application")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI assistant. Ask me about Python, data science, machine learning, or automation."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your AI assistant...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = os.getenv("OPENAI_API_KEY")
    with st.chat_message("assistant"):
        if not api_key:
            response = (
                "I received your question: **" + prompt + "**\n\n"
                "The UI and conversation layer are working. Add `OPENAI_API_KEY` "
                "and connect the model call in this file to enable live LLM responses."
            )
        else:
            response = (
                "API key detected. This portfolio demo is ready for the model/API "
                "integration layer."
            )
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:
    st.header("Project Features")
    st.write("• Conversational chat UI")
    st.write("• Session-based chat history")
    st.write("• Environment-variable secrets")
    st.write("• Ready for LLM/API integration")
    st.write("• Streamlit deployment friendly")
