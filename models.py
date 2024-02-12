import os
import time
from pymongo import MongoClient, TEXT

from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = MongoClient(MONGODB_URL)

db = client[MONGODB_DB]


# Schema for the 'messages' collection
messages_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "text", "timestamp", "sender"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "text": {"bsonType": "string"},
            "timestamp": {"bsonType": "date"},
            "sender": {"bsonType": "string"},
            # Add other message-specific fields here
        },
    }
}

# Schema for the 'user_actions' collection
user_actions_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "overall_rate"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "name": {"bsonType": "string"},
            "overall_rate": {"bsonType": "string"},
            "feedback": {"bsonType": "string"},
            "feedback_text": {"bsonType": "string"},
            # Add other user_action-specific fields here
        },
    }
}

# Schema for the 'chats' collection (as you provided)
chats_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "_id",
            "start_time",
            "end_time",
            "message_ids",
            "user_action_ids",
            "prompts",
        ],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "start_time": {"bsonType": "date"},
            "end_time": {"bsonType": "date"},
            "message_ids": {"bsonType": "array", "items": {"bsonType": "objectId"}},
            "user_action_ids": {"bsonType": "array", "items": {"bsonType": "objectId"}},
            "prompts": {
                "bsonType": "object",
                # Define the properties of 'prompts' as per your requirement
            },
            # Include any other fields that are part of the 'chats' collection
        },
    }
}

# Create collections with the schemas
db.create_collection("messages", validator={"$jsonSchema": messages_schema})
db.create_collection("user_actions", validator={"$jsonSchema": user_actions_schema})
db.create_collection("chats", validator={"$jsonSchema": chats_schema})

# Create text indexes
db.messages.create_index([("text", TEXT)])
db.user_actions.create_index([("feedback_text", TEXT), ("name", TEXT)])
# Add any other indexes as needed

print("Collections and indexes created successfully.")
