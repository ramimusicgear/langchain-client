import os
import re
import time
import json
import requests
import streamlit as st
import extra_streamlit_components as stx

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import pymongo
from bson import ObjectId
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()
from login import login_page, registration_page, create_jwt_token, verify_jwt_token
from admin import admin_page

TESTING = False
SERVER_URL = os.environ.get('SERVER_URL')
MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client['llamaindex']  # Replace with your database name
chats = db['chats']

# Store LLM generated responses
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
    st.session_state.selected_conversation = None

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
    
# App title
st.set_page_config(page_title="Rami Chatbot")

st.session_state.token_loaded = False
st.session_state.page_loaded = False
st.session_state.selected_conversation_loaded = False

st.session_state.loaded_messages = False

def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

messages_cookie = cookie_manager.get(cookie="messages")
if messages_cookie and not st.session_state.loaded_messages:
    if isinstance(messages_cookie, str):
        # If messages_cookie is a string, parse it as JSON
        st.session_state.messages = json.loads(messages_cookie)
    elif isinstance(messages_cookie, list):
        # If messages_cookie is already a list, use it directly
        st.session_state.messages = messages_cookie

    st.session_state.loaded_messages = True


page_cookie = cookie_manager.get(cookie="page")
if page_cookie and not st.session_state.page_loaded:
    st.session_state['page'] = page_cookie  # Store the JWT in session state
    st.session_state.page_loaded = True

selected_conversation_cookie = cookie_manager.get(cookie="selected_conversation")
if selected_conversation_cookie and not st.session_state.selected_conversation_loaded:
    st.session_state['selected_conversation'] = selected_conversation_cookie  # Store the JWT in session state
    st.session_state.selected_conversation_loaded = True

jwt_cookie = cookie_manager.get(cookie="token")
if jwt_cookie and not st.session_state.token_loaded:
    st.session_state.token_loaded = True
    payload = verify_jwt_token(jwt_cookie)
    if payload:
        st.session_state['jwt'] = jwt_cookie  # Store the JWT in session state
        st.session_state['user'] = payload['user']


if jwt_cookie and not st.session_state.token_loaded:
    st.session_state.jwt = jwt_cookie
    st.session_state.token_loaded = True
    payload = verify_jwt_token(jwt_cookie)
    if payload:
        st.session_state['jwt'] = jwt_cookie  # Store the JWT in session state
        st.session_state['user'] = payload['user']

# Function to navigate between pages
def navigate_to(page):
    st.session_state['page'] = page
    cookie_manager.set("page", page, key=f"set_page_cookie_{page}")

def select(conv_id):
    st.session_state.selected_conversation = conv_id
    cookie_manager.set("selected_conversation", conv_id, key=f"set_selected_conversation_cookie_{conv_id}")

def log_in(username, password):
    token = create_jwt_token(username, password)
    cookie_manager.set("token", token, key=f"set_jwt_cookie_{token}")

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
    cookie_manager.set("token", token, key=f"set_register_jwt_cookie_{token}")

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

elif st.session_state['page'] == 'admin':
    admin_page(select, navigate_to)
    
elif st.session_state['page'] == 'chat':
    # Navigation buttons
    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # st.text(message["content"])
            # st.markdown(f"<p>{message["content"]}</p>", unsafe_allow_html=True)
            st.markdown(f"""
                <p>{message["content"]}</p>
                """, unsafe_allow_html=True)

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]
        st.session_state.start_time = datetime.now()
        st.session_state.document_id = ''
        cookie_manager.set("messages",json.dumps([{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]), key=f"set_messages_cookie_first")
        
    placeholder_sidebar = st.sidebar.empty()
    
    st.sidebar.button('New chat', on_click=clear_chat_history)

    if st.session_state['user']:
        st.sidebar.write(f"# Welcome, {st.session_state['user']}!")
        payload = verify_jwt_token(st.session_state['jwt'])
        if payload['is_admin']:
            st.sidebar.button('Go To Admin Dashboard',key="admin_dashboard", on_click=lambda: navigate_to('admin'))
    else:
        st.sidebar.write("# Login/Register")
        st.sidebar.button("Login",key='to_login_btn', on_click=lambda: navigate_to('login'))
        st.sidebar.button("Register",key='to_register_btn', on_click=lambda: navigate_to('register'))
    
    feedback_sender = ""
    price_reasoning = ""
    product_reasoning = ""
    demands_reasoning = ""
    phraise_reasoning = ""
    feedback = ""

    st.sidebar.write("# Feedback")
    with st.sidebar:
        f = st.form("Feedback",clear_on_submit=True,border=True)
    feedback_sender = f.text_input("Name (Not Required)",key="feedback_sender")

    price = f.radio("Rate pricing match",["Good","Okay","Bad"],index=None,horizontal=True)

    price_reasoning = f.text_input("Why? (Not Required)",key="price_reason")

    product = f.radio("Rate product match",["Good","Okay","Bad"],index=None,horizontal=True)

    product_reasoning = f.text_input("Why? (Not Required)",key="produt_reason")

    demands = f.radio("Rate demands match",["Good","Okay","Bad"],index=None,horizontal=True)

    demands_reasoning = f.text_input("Why? (Not Required)",key="demands_reason")

    phraise = f.radio("Rate phrasing",["Good","Okay","Bad"],index=None,horizontal=True)

    phraise_reasoning = f.text_input("Why? (Not Required)",key="phraise_reason")

    feedback = f.text_area("Do you have anything else you would like to add?",key="extra feedback")

    submit = f.form_submit_button("Submit")
    if submit:
        # feedback_d = {"name":feedback_sender,
        #     "price":{"rating":price,"reason":price_reasoning},
        #     "product":{"rating":product,"reason":product_reasoning},
        #     "demands":{"rating":demands,"reason":demands_reasoning},
        #     "phraise":{"rating":phraise,"reason":phraise_reasoning},
        #     "other":feedback}
        if not TESTING:
            if st.session_state.document_id != '':
                while True:
                    try:
                        # Create 'user_actions' with 'feedback_text'
                        new_values = {"user_actions": {"name":feedback_sender,
                            "price":{"rating":price,"reason":price_reasoning},
                            "product":{"rating":product,"reason":product_reasoning},
                            "demands":{"rating":demands,"reason":demands_reasoning},
                            "phraise":{"rating":phraise,"reason":phraise_reasoning},
                            "other":feedback}}
                        # Perform the update
                        update_result = chats.update_one({"_id": st.session_state.document_id}, {"$set": new_values})

                        # Check if the update was successful
                        if update_result.modified_count > 0:
                            st.write(f"thank you very much {feedback_sender}!")
                            break
                        else:
                            st.error("try feedback again, sorry")
                            time.sleep(5)
                        
                    except Exception as e:
                        st.error(str(e))
                        time.sleep(5)
        st.rerun()
                
            
    def generate_response(prompt_input):
        messages = st.session_state.messages
        data = {"history":messages,"user_input":prompt_input}
        response = requests.post(f"{SERVER_URL}/process", json=data, verify=False)
        result = response.json()
        return result.get('response', '')

    # User-provided prompt
    if prompt := st.chat_input(disabled=False):
        if len(st.session_state.messages) == 1:
            while True:
                try:
                    chat_document = {
                        "_id": ObjectId(),  # Generates a unique Object ID
                        "user_ip": st.session_state.ip,  # Example IP address
                        "user_device": "Desktop",  # Example device type
                        # "category": category,
                        # "subcategory": subcategory,
                        "start_time": st.session_state.start_time,
                        "end_time": datetime.now(),
                        "messages": [
                            {
                                "timestamp": datetime.now(),
                                "sender": f"user - {str(st.session_state.ip)}",
                                "text": prompt
                            }
                        ],
                        "prompts": {
                            "template_prompt": """Given a conversation (between Human and Assistant) and a follow up question from the user
    You are an assistant you help customers choose products using the given context (use only what is relevent) 
    your output should be nicely phrased
    ask the customer questions to figure out what he needs
    in your questions behave a little bit like a salesman and try and figure out exactly what the customer is looking for
    in your questions lead the customer to the right product for him""",
                            "search_prompt": """you are a spec analiyzer you use the given chat history and question and give out the 
    techincal specs that the product the customer is describing should have 
    don't write anything other than the specs, do not explain why
    the specs should be only technical
    always follow the instructions""",
                        },
                        # "product_references": references
                    }

                    # Insert the document into the 'chats' collection
                    if not TESTING:
                        insert_result = chats.insert_one(chat_document)
                        # Get the _id of the inserted document
                        inserted_id = insert_result.inserted_id
                        st.session_state.document_id = inserted_id
                    else:
                        st.session_state.document_id = "inserted_id"
                        
                    break
                except Exception as e:
                    st.error(str(e))
                    time.sleep(10)
        else:
            while True:
                try:
                    new_message = {
                        "timestamp": datetime.now(),
                        "sender": f"user - {str(st.session_state.ip)}",
                        "text": prompt
                    }
                    if not TESTING:
                        update_result = chats.update_one(
                            {"_id": st.session_state.document_id},
                            {"$push": {"messages": new_message}}
                        )
                        # Check if the update was successful
                        if update_result.modified_count > 0:
                            break
                        else:
                            st.error("try again, sorry")
                            time.sleep(5)
                    break
                except Exception as e:
                    st.error(str(e))
                    time.sleep(10)
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        cookie_manager.set("messages", json.dumps(st.session_state.messages), key=f"set_messages_cookie_{prompt}")

        with st.chat_message("user"):
            st.markdown(f"""
                <p>{prompt}</p>
                """, unsafe_allow_html=True)
            # st.text(prompt)
            # st.markdown(f"<p>{prompt}</p>", unsafe_allow_html=True)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    # placeholder.text(full_response)
                    placeholder.markdown(f"""
                        <p>{full_response}</p>
                        """, unsafe_allow_html=True)
                    # placeholder.markdown(f"<p>{full_response}</p>", unsafe_allow_html=True)
                # placeholder.text(full_response)
                placeholder.markdown(f"""
                        <p>{full_response}</p>
                        """, unsafe_allow_html=True)
                # placeholder.markdown(f"<p>{full_response}</p>", unsafe_allow_html=True)

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        cookie_manager.set("messages", json.dumps(st.session_state.messages), key=f"set_messages_cookie_{message}")

        while True:
            try:
                new_message = {
                    "timestamp": datetime.now(),
                    "sender": "bot",
                    "text": full_response
                }
                if not TESTING:
                    update_result = chats.update_one(
                        {"_id": st.session_state.document_id},
                        {"$push": {"messages": new_message}}
                    )
                    # Check if the update was successful
                    if update_result.modified_count > 0:
                        break
                    else:
                        st.error("try again, sorry")
                        time.sleep(5)

                break
            except Exception as e:
                st.error(str(e))
                time.sleep(10)
