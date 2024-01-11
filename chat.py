import os
import json
import time
import pymongo
import requests
import streamlit as st
from bson import ObjectId
from datetime import datetime

SERVER_URL = os.environ.get('SERVER_URL')
MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client['llamaindex']  # Replace with your database name
chats = db['chats']

def chat_page(navigate_to):
    if st.session_state['user']:
        st.sidebar.write(f"# Welcome, {st.session_state['user']}!")
    else:
        st.sidebar.write("## Login/Register")
        st.sidebar.button("Login",key='to_login_btn', on_click=lambda: navigate_to('login'))
        st.sidebar.button("Register",key='to_register_btn', on_click=lambda: navigate_to('register'))
        
    if st.session_state.new_chat:
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

    st.sidebar.write("### Chat Instruction")
    st.sidebar.write("## Template")
    st.sidebar.write(st.session_state.template)
    st.sidebar.write("## Search Prompt")
    st.sidebar.write(st.session_state.search_prompt)
    if st.sidebar.button('Change Propmts', key='change_propmpts_button'):
        st.session_state.change_instruction = True
        
    # Model Instruction
    if st.session_state.change_instruction:
        st.title('Model Instruction')
        st.text_area('Enter Model Instruction For Template: ', 
                                key='template', 
                                value=st.session_state.template, 
                                height=50)
        st.text_area('Enter Model Instruction For Prompt Refinement: ', 
                                    key='search_prompt', 
                                    value=st.session_state.search_prompt, 
                                    height=125)
        
    # Chat Interface
    st.title('Chat Interface')
    st.text_area('Enter your message:', 
                            key='user_input', 
                            value=st.session_state.user_input, 
                            height=35)


    if st.button('Send', key='send_button'):
        start_time = datetime.now()
        data = {
            'template': st.session_state.template, 
            'user_input': st.session_state.user_input,
            'search_prompt': st.session_state.search_prompt
        }
        res = requests.post(f'{SERVER_URL}/process', json=data, verify=False)

        if res.status_code != 200:
            st.error('Failed to get a response from the server.')

        result = res.json()
        context = result.get("context","")
        st.session_state.context = context
        
        response = result.get('response', '')
        st.session_state.response = response
        response_query = result.get('response_query', '')
        st.session_state.response_query = response_query

        query_time = result.get('query_time', '')
        st.session_state.query_time = query_time

        st.session_state.message_submitted = True


    if st.session_state.message_submitted:	
        st.write("### response")
        st.write(st.session_state.response)
        st.write("### Gpt Generated search")
        st.write(st.session_state.response_query)
        st.write("### time took to generate")
        st.write(f"{round(st.session_state.query_time)} seconds")

        inserted_id = ''
        references = []
        category = ''
        subcategory = ''
        
        # Join the list into a single string (if it's not already)
        context_string = ' '.join(st.session_state.context)
        if not context_string.startswith("{"):
            context_string = "{" + context_string
        if not context_string.endswith("}"):
            context_string += "}"
        
        def extract_json_strings(s):
            json_strings = []
            brace_count = 0
            current_json = ''

            for char in s:
                if char == '{':
                    brace_count += 1
                    current_json += char
                elif char == '}':
                    brace_count -= 1
                    current_json += char
                    if brace_count == 0:
                        json_strings.append(current_json)
                        current_json = ''
                elif brace_count > 0:
                    current_json += char

            return json_strings

        json_strings = extract_json_strings(context_string)

        # Parsing each JSON string
        for json_str in json_strings:
            try:
                p = json.loads(json_str)
                category = p["categories"][2]
                subcategory = p["categories"][3]
                references.append({
                    "name": p["name"],
                    "description": p["description"] ,
                    "price": float(p["price"].replace(",","")),
                    "categories": json.dumps(p["categories"])
                })
            except json.JSONDecodeError:
                print(f"Invalid JSON object: {json_str}")

        while True:
            try:
                chat_document = {
                    "_id": ObjectId(),  # Generates a unique Object ID
                    "user_ip": st.session_state.ip,  # Example IP address
                    "user_device": "Desktop",  # Example device type
                    "category": category,
                    "subcategory": subcategory,
                    "start_time": start_time,
                    "end_time": datetime.now(),
                    "messages": [
                        {
                            "timestamp": datetime.now(),
                            "sender": f"user - {str(st.session_state.ip)}",
                            "text": st.session_state.user_input
                        },
                        {
                            "timestamp": datetime.now(),
                            "sender": "bot",
                            "text": st.session_state.response
                        }
                    ],
                    "prompts": {
                        "template_prompt": st.session_state.template,
                        "search_prompt": st.session_state.search_prompt,
                        "response_query": st.session_state.response_query
                    },
                    "product_references": references
                }

                # Insert the document into the 'chats' collection
                insert_result = chats.insert_one(chat_document)
                # Get the _id of the inserted document
                inserted_id = insert_result.inserted_id
                st.session_state.document_id = inserted_id


                break
            except Exception as e:
                st.error(str(e))
                time.sleep(10)

        st.session_state.ready_for_feedback = True
    if st.session_state.ready_for_feedback:

        st.write("## Feedback")

        # Use session state variable for the text input
        new_feedback_text = st.text_input('Enter Your Feedback:', key='feedback_text', value=st.session_state.feedback)

        # Update the session state when the text input changes
        st.session_state.feedback = new_feedback_text

        # Use session state variable for the text input
        sender = st.text_input('Enter Your Name:', key='feedback_name_text', value=st.session_state.sender)

        # Update the session state when the text input changes
        st.session_state.sender = sender

        if st.button('Send Feedback', key='send_feedback_button'):
            try:
                # Create 'user_actions' with 'feedback_text'
                new_values = {"user_actions": {"feedback_text": new_feedback_text, "sender": sender}}
                # Perform the update
                update_result = chats.update_one({"_id": st.session_state.document_id}, {"$set": new_values})

                # Check if the update was successful
                if update_result.modified_count > 0:
                    st.write("thank you very much!")
                else:
                    st.write("try feedback again, sorry")

                    
            except Exception as e:
                st.error(str(e))

        if st.button('New Chat', key='new_chat_btn'):
            st.session_state.new_chat = True
