import os
import re
import jwt
import time
import traceback
import pymongo
import streamlit as st
from bson import ObjectId

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")
# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB]
chats = db[MONGODB_COLLECTION]


def verify_jwt_token(token):
    """Verify the given JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
