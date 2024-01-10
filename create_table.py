import os
import time
import pymongo

from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)

db = client['llamaindex']  

init = False

# Updated schema definition
chat_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "start_time","end_time", "messages"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "category": {"bsonType": "string"},
            "subcategory": {"bsonType": "string"},  # Added subcategory field
            "start_time": {"bsonType": "date"},
            "end_time": {"bsonType": "date"},
            "messages": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["timestamp", "sender", "text"],
                    "properties": {
                        "timestamp": {"bsonType": "date"},
                        "sender": {"bsonType": "string"},
                        "text": {"bsonType": "string"}
                    }
                }
            },
            "user_actions": {
                "bsonType": "object",
                "properties": {
                    "feedback": {"bsonType": "string"},
                    "product_interactions": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["product_id", "action"],
                            "properties": {
                                "product_id": {"bsonType": "string"},
                                "action": {"bsonType": "string"}
                            }
                        }
                    }
                }
            },
            "product_references": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["name", "description", "price", "category"],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "description": {"bsonType": "string"},
                        "price": {"bsonType": "double"},
                        "category": {"bsonType": "string"}
                    }
                }
            }
        }
    }
}


if init:
	# Create or update the collection with the new validator
	chats = db.create_collection("chats", validator=chat_schema)

	# Add indexes on 'category' and 'subcategory'
	chats.create_index([("category", pymongo.ASCENDING), ("subcategory", pymongo.ASCENDING)])