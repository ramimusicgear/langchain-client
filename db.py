import os
import time
import pymongo
import streamlit as st
from bson import ObjectId
from datetime import datetime

from user_pages_and_functions import verify_jwt_token

MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client['llamaindex']  
chats = db['chats']

# GET
def get_all():
    payload = verify_jwt_token(st.session_state['jwt'])
    if payload and payload['is_admin']:
        conversations = chats.find({}).sort("start_time", -1)
        return conversations
    return []

def get_selected(selected_conversation):
    try:
        # Convert string to ObjectId
        selected_conversation_id = ObjectId(selected_conversation)
    except Exception as e:
        # Handle invalid ObjectId string
        return None

    payload = verify_jwt_token(st.session_state['jwt'])
    if payload and payload['is_admin']:
        # Query the database with ObjectId
        conversation = db.chats.find_one({'_id': selected_conversation_id})
        return conversation

    return None

# POST, UPDATE
def update_feedback(id, new_values):
    retry = 0
    while True:
        try:
            update_result = chats.update_one({"_id": id}, {"$set": new_values})
            # Check if the update was successful
            if update_result.modified_count > 0:
                break
            else:
                if retry > 3:
                    st.error("error, refresh to fix")
                    time.sleep(10)
                retry += 1
                time.sleep(1)
        except Exception as e:
            print(str(e))
            if retry > 3:
                st.error("error, refresh to fix")
                time.sleep(10)
            retry += 1
            time.sleep(1)

def insert_first_message(chat_document):
    retry = 0
    while True:
        try:
            # Insert the document into the 'chats' collection
            insert_result = chats.insert_one(chat_document)
            # Get the _id of the inserted document
            inserted_id = insert_result.inserted_id
            st.session_state.document_id = inserted_id
            break
        except Exception as e:
            if retry > 3:
                st.error("error, to fix click on reset button")
                st.error(str(e))
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)

def insert_message(document_id, new_message):
    retry = 0
    while True:
        try:
            update_result = chats.update_one(
                {"_id": document_id},
                {"$push": {"messages": new_message}}
            )
            # Check if the update was successful
            if update_result.modified_count > 0:
                break
            else:
                if retry > 3:
                    st.error("error, to fix click on reset button")
                    time.sleep(10)
                retry += 1
                time.sleep(1)
        except Exception as e:
            if retry > 3:
                st.error("error, to fix click on reset button")
                st.error(str(e))
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)