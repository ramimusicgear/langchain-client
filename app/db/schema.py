import os
import time
import pymongo
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)

db = client[MONGODB_DB]

# Updated schema definition
chat_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "version", "start_time", "messages"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            # user
            "user_ip": {"bsonType": "string"},
            "user_device": {"bsonType": "string"},
            "version": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "subcategory": {"bsonType": "string"},
            "start_time": {"bsonType": "date"},
            "price": {"bsonType": "double"},
            "messages": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["timestamp", "sender", "text"],
                    "properties": {
                        "timestamp": {"bsonType": "date"},
                        "sender": {"bsonType": "string"},
                        "text": {"bsonType": "string"},
                    },
                },
            },
            "prompts": {
                "bsonType": "object",
                "properties": {
                    "template_prompt": {"bsonType": "string"},
                    "search_prompt": {"bsonType": "string"},
                    "response_query": {"bsonType": "string"},
                },
            },
            "user_actions": {
                "bsonType": "object",
                "properties": {
                    "name": {"bsonType": "string"},
                    "overall_rate": {"bsonType": "string"},
                    "price": {
                        "bsonType": "object",
                        "properties": {
                            "rating": {"bsonType": "string"},
                            "reason": {"bsonType": "string"},
                        },
                    },
                    "product": {
                        "bsonType": "object",
                        "properties": {
                            "rating": {"bsonType": "string"},
                            "reason": {"bsonType": "string"},
                        },
                    },
                    "demands": {
                        "bsonType": "object",
                        "properties": {
                            "rating": {"bsonType": "string"},
                            "reason": {"bsonType": "string"},
                        },
                    },
                    "phraise": {
                        "bsonType": "object",
                        "properties": {
                            "rating": {"bsonType": "string"},
                            "reason": {"bsonType": "string"},
                        },
                    },
                    "other": {"bsonType": "string"},
                    "feedback": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "actions": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["action"],
                            "properties": {
                                "product_id": {"bsonType": "string"},
                                "action": {"bsonType": "string"},
                            },
                        },
                    },
                },
            },
            "product_references": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["name", "description", "price", "categories"],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "description": {"bsonType": "string"},
                        "price": {"bsonType": "double"},
                        "categories": {"bsonType": "string"},
                    },
                },
            },
        },
    }
}


# Check if the MONGODB_COLLECTION collection exists
collection_names = db.list_collection_names()
if MONGODB_COLLECTION in collection_names:
    print(f"Collection {MONGODB_COLLECTION} already exists.no way im Deleting it.")
    # db[MONGODB_COLLECTION].drop()
else:
    # Create or update the collection with the new validator
    chats = db.create_collection(MONGODB_COLLECTION, validator=chat_schema)

    # Add indexes on 'category' and 'subcategory'
    chats.create_index(
        [("category", pymongo.ASCENDING), ("subcategory", pymongo.ASCENDING)]
    )
