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

placeholder_sidebar = st.sidebar.empty()
st.sidebar.button('New chat', on_click=clear_chat_history)

st.sidebar.write("# Enter Your Feedback")
feedback_text = st.sidebar.text_input('Enter your message:')
feedback_sender = st.sidebar.text_input('Enter your name:')

if st.sidebar.button("Send Feedback"):
    if not TESTING:
        if st.session_state.document_id != '':
             while True:
                try:
                    # Create 'user_actions' with 'feedback_text'
                    new_values = {"user_actions": {"feedback_text": feedback_text, "sender": feedback_sender}}
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
              
         
def generate_response(prompt_input):
    messages = st.session_state.messages
    data = {"history":messages,"user_input":prompt_input}
    response = requests.post(f'{SERVER_URL}/process', json=data, verify=False)
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
