import os
import re
import time
import json
import requests
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime

from user_pages_and_functions import create_jwt_token, verify_jwt_token

# App title
st.set_page_config(page_title="Rami Chatbot")
  
# states
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]

if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()

if 'document_id' not in st.session_state:
    st.session_state.document_id = ''
    
# Initialize log in and admin dashboard
if 'jwt' not in st.session_state:
    st.session_state['jwt'] = None
if 'user' not in st.session_state:
    st.session_state['user'] = None

if 'selected_conversation' not in st.session_state:
    st.session_state['selected_conversation']= None

# Initialize page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'chat'
    
if 'ip' not in st.session_state:
    st.session_state.ip = ''
try:
    response = requests.get('https://api.ipify.org?format=json')
    ip_data = response.json()
    st.session_state.ip = ip_data['ip']

except requests.RequestException as e:
    st.error("refresh please")

# cookies
    
st.session_state.token_loaded = False
st.session_state.page_loaded = False
st.session_state.selected_conversation_loaded = False


def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

page_cookie = cookie_manager.get(cookie="page")
if page_cookie and not st.session_state.page_loaded:
    st.session_state['page'] = page_cookie  # Store the JWT in session state
    st.session_state.page_loaded = True

selected_conversation_cookie = cookie_manager.get(cookie="selected_conversation")
if selected_conversation_cookie and not st.session_state.selected_conversation_loaded:
    st.session_state['selected_conversation'] = selected_conversation_cookie  # Store the JWT in session state
    st.session_state.selected_conversation_loaded = True

jwt_cookie = cookie_manager.get(cookie="jwt-token")
if jwt_cookie and not st.session_state.token_loaded:
    st.session_state.token_loaded = True
    payload = None
    token = st.session_state['jwt']
    if token:
        payload = verify_jwt_token(jwt_cookie)
    if payload:
        st.session_state['jwt'] = jwt_cookie  # Store the JWT in session state
        st.session_state['user'] = payload['user']


if jwt_cookie and not st.session_state.token_loaded:
    st.session_state.jwt = jwt_cookie
    st.session_state.token_loaded = True
    payload = None
    token = st.session_state['jwt']
    if token:
        payload = verify_jwt_token(jwt_cookie)
    if payload:
        st.session_state['jwt'] = jwt_cookie  # Store the JWT in session state
        st.session_state['user'] = payload['user']


# functions
        
def clear_all_cookies():
    st.session_state.messages = [{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]
    st.session_state.start_time = datetime.now()
    st.session_state.document_id = ''
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None
    st.session_state.page = "chat"
    # cookie_manager.set("messages",json.dumps([{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]), key=f"set_messages_cookie_first")
    cookie_manager.delete("jwt-token", key=f"del_selected_token")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")
    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
  
def navigate_to(page):
    st.session_state.page = page
    cookie_manager.set("page", page, key=f"set_page_cookie_{page}")

def select(conv_id):
    st.session_state.selected_conversation = conv_id
    cookie_manager.set("selected_conversation", conv_id, key=f"set_selected_conversation_cookie_{conv_id}")

def log_out():
    st.session_state.page = "chat"
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None

    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
    cookie_manager.delete("jwt-token", key=f"del_page_cookie_chat")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")
    
def log_in(username, password):
    token = create_jwt_token(username, password)
    cookie_manager.set("jwt-token", token, key=f"set_register_jwt_cookie_{token}")
    payload = None
    if token:
        payload = verify_jwt_token(token)
    if payload:
        st.success(f"You are logged in successfully as {username}")
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload['is_admin']:
            navigate_to('admin')
        else:
            navigate_to('chat')
    else:
        st.error("Log In failed. Please try again.")
    print(payload)
    print(st.session_state['user'])
    print()
    # st.rerun()

def register(username, password):
    token = create_jwt_token(username, password)  # Reuse the JWT creation function from login
    cookie_manager.set("jwt-token", token, key=f"set_register_jwt_cookie_{token}")

    payload = None
    if token:
        payload = verify_jwt_token(token)    
    if payload:
        st.success(f"You are registered successfully as {username}")
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload['is_admin']:
            navigate_to('admin')
        else:
            navigate_to('chat')
    else:
        st.error("Registration failed. Please try again.")

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]
    st.session_state.start_time = datetime.now()
    st.session_state.document_id = ''
    