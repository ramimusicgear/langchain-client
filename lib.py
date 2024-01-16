import os
import pymongo
from bson import ObjectId

from datetime import datetime
import streamlit as st
from login import verify_jwt_token

MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client['llamaindex']  
chats = db['chats']

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
