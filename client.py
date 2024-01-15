import json
import streamlit as st
import os
import requests

SERVER_URL = 'http://127.0.0.1:5000'  # Replace with your server's URL
# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

placeholder_sidebar = st.sidebar.empty()
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

st.sidebar.write("enter Feedback")
user_input = st.sidebar.text_input('Enter your message:')

if st.sidebar.button("Give FeedBack"):
    data = {"feedback":user_input,"chats":st.session_state.messages}
    with open("feedback.json","w") as f:
        json.dump(data,f)

def generate_response(prompt_input):
    messages = st.session_state.messages
    data = {"history":messages,"user_input":prompt_input}
    response = requests.post(f'{SERVER_URL}/process', json=data)
    result = response.json()
    return result.get('response', '')

# User-provided prompt
if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.write(full_response)
            placeholder.write(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
