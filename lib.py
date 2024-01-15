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
        conversations = chats.find({}) 
        return conversations
    return []

def get_selected(selected_conversation):
    payload = verify_jwt_token(st.session_state['jwt'])
    if payload and payload['is_admin']:
        conversation = db.chats.find_one({'_id': selected_conversation})
        return conversation
    return None