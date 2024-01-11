import os
import re
import time
import json
import requests
import streamlit as st

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import pymongo
from bson import ObjectId
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from chat import chat_page
from login import login_page, registration_page, create_jwt_token, verify_jwt_token
from admin import admin_page

# Initialize session state for feedback
if 'template' not in st.session_state:
	st.session_state.template = "You are an assistant you help customers choose products using the given context (use only what is relevant) your output should be nicely phrased:"

if 'search_prompt' not in st.session_state:
	st.session_state.search_prompt = """
	what technical specs is the product the customer is asking for should have, do not explain why.
	You can change the question to get more suitable products.
	for example in case the customer is looking for a product that is suitable for playing a rock style, you will show the specifications suitable for playing rock on the instrument he is requesting."""

if 'user_input' not in st.session_state:
	st.session_state.user_input = ''

if 'start_time' not in st.session_state:
	st.session_state.start_time = datetime.now()

if 'change_instruction' not in st.session_state:
	st.session_state.change_instruction = False

if 'document_id' not in st.session_state:
	st.session_state.document_id = ''

if 'feedback' not in st.session_state:
	st.session_state.feedback = ''

if 'message_submitted' not in st.session_state:
	st.session_state.message_submitted = False

if 'ready_for_feedback' not in st.session_state:
	st.session_state.ready_for_feedback = False

if 'feedback_submitted' not in st.session_state:
	st.session_state.feedback_submitted = False

if 'new_chat' not in st.session_state:
	st.session_state.new_chat = False

if 'context' not in st.session_state:
	st.session_state.context = ''

if 'response_query' not in st.session_state:
	st.session_state.response_query = ''

if 'response' not in st.session_state:
	st.session_state.response = ''

if 'query_time' not in st.session_state:
	st.session_state.query_time = ''

if 'ip' not in st.session_state:
	st.session_state.ip = ''

if 'lastclicked' not in st.session_state:
	st.session_state.lastclicked = ''
if 'sender' not in st.session_state:
	st.session_state.sender = ''

# Initialize page navigation
if 'page' not in st.session_state:
	st.session_state['page'] = 'chat'

# Initialize log in and admin dashboard
if 'jwt' not in st.session_state:
	st.session_state['jwt'] = None
if 'user' not in st.session_state:
	st.session_state['user'] = None
if 'username' not in st.session_state:
	st.session_state.username = ''
if 'password' not in st.session_state:
	st.session_state.password = ''
if 'selected_conversation' not in st.session_state:
	st.session_state.selected_conversation = None

try:
	response = requests.get('https://api.ipify.org?format=json')
	ip_data = response.json()
	st.session_state.ip = ip_data['ip']

except requests.RequestException as e:
	st.error("refresh please")

# Function to navigate between pages
def navigate_to(page):
	st.session_state['page'] = page

def select(conv_id):
	st.session_state.selected_conversation = conv_id

def reset():
	st.session_state.new_chat = False
	st.session_state.user_input = ''
	st.session_state.message_submitted = False
	st.session_state.ready_for_feedback = False
	st.session_state.feedback = ''
	st.session_state.document_id = ''
	st.session_state.feedback_submitted = False
	st.session_state.context = ''
	st.session_state.response_query = ''
	st.session_state.response = ''
	st.session_state.query_time = ''

def log_in(username, password):
	token = create_jwt_token(username, password)
	payload = verify_jwt_token(token)
	if payload:
		st.success(f"You are logged in successfully as {username}")
		st.session_state['jwt'] = token  # Store the JWT in session state
		st.session_state['user'] = username  # Store the JWT in session state
		if payload['is_admin']:
			navigate_to('admin')
		else:
			navigate_to('chat')
	else:
		st.error("Log In failed. Please try again.")

def register(username, password):
	token = create_jwt_token(username, password)  # Reuse the JWT creation function from login
	payload = verify_jwt_token(token)
	if payload:
		st.success(f"You are registered successfully as {username}")
		st.session_state['jwt'] = token  # Store the JWT in session state
		st.session_state['user'] = username  # Store the JWT in session state
		if payload['is_admin']:
			navigate_to('admin')
		else:
			navigate_to('chat')
	else:
		st.error("Registration failed. Please try again.")

# App Routing
if st.session_state['page'] == 'login':
	st.sidebar.button("Back to Chat", key='login_back_btn', on_click=lambda: navigate_to('chat'))
	st.sidebar.button("Back to Register", key='login_back_register_btn', on_click=lambda: navigate_to('login'))
	login_page(log_in)

elif st.session_state['page'] == 'register':
	st.sidebar.button("Back to Chat", key='register_back_btn', on_click=lambda: navigate_to('chat'))
	st.sidebar.button("Back to Login", key='register_back_login_btn', on_click=lambda: navigate_to('login'))
	registration_page(register)

elif st.session_state['page'] == 'chat':
	# Navigation buttons
	chat_page(navigate_to, reset)

elif st.session_state['page'] == 'admin':
	admin_page(select, navigate_to)