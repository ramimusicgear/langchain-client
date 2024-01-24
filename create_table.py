import os
import time
import pymongo

from dotenv import load_dotenv
load_dotenv()


MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)

db = client[MONGODB_DB]  

init = True

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
            "price": {"bsonType": "double"},
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
                    "required": ["name", "description", "price", "categories"],
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
	# Check if the MONGODB_COLLECTION collection exists
	collection_names = db.list_collection_names()
	if MONGODB_COLLECTION in collection_names:
		print(f"Collection {MONGODB_COLLECTION} already exists. Deleting it.")
		db[MONGODB_COLLECTION].drop()

	# Create or update the collection with the new validator
	chats = db.create_collection(MONGODB_COLLECTION, validator=chat_schema)

	# Add indexes on 'category' and 'subcategory'
	chats.create_index([("category", pymongo.ASCENDING), ("subcategory", pymongo.ASCENDING)])
else:
	# Retrieve the first document
	# Check if the MONGODB_COLLECTION collection exists
	collection_names = db.list_collection_names()
	if MONGODB_COLLECTION in collection_names:
		chats = db[MONGODB_COLLECTION]
		first_document = chats.find_one()
		# Print the document
		print(first_document)