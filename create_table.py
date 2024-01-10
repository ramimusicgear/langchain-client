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
        "required": ["_id", "start_time","end_time", "messages","prompts"],
        "properties": {
            "_id": {"bsonType": "objectId"},

			# user	
            "user_ip": {"bsonType": "string"},
            "user_device": {"bsonType": "string"},

            "category": {"bsonType": "string"},
            "subcategory": {"bsonType": "string"},
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
            "prompts": {
                "bsonType": "object",
				"properties": {
					"template_prompt": {"bsonType": "string"},
					"search_prompt": {"bsonType": "string"},
					"response_query": {"bsonType": "string"}
				}
            },
			"user_actions": {
                "bsonType": "object",
                "properties": {
                    "feedback": {"bsonType": "string"},
                    "feedback_text": {"bsonType": "string"},
                    "actions": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["action"],
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
                        "categories": {"bsonType": "string"}
                    }
                }
            }
        }
    }
}


if init:
	# Check if the "chats" collection exists
	collection_names = db.list_collection_names()
	if "chats" in collection_names:
		print("Collection 'chats' already exists. Deleting it.")
		db["chats"].drop()

	# Create or update the collection with the new validator
	chats = db.create_collection("chats", validator=chat_schema)

	# Add indexes on 'category' and 'subcategory'
	chats.create_index([("category", pymongo.ASCENDING), ("subcategory", pymongo.ASCENDING)])
else:
	# Retrieve the first document
	# Check if the "chats" collection exists
	collection_names = db.list_collection_names()
	if "chats" in collection_names:
		first_document = db["chats"].find_one()
		# Print the document
		print(first_document)