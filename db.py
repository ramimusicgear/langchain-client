import os
import time
import pymongo
import streamlit as st
from bson import ObjectId
from datetime import datetime

from login_utils import verify_jwt_token

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB]  
chats = db[MONGODB_COLLECTION]

# GET
def get_all():
    payload = verify_jwt_token(st.session_state['jwt'], False)


    if payload and payload['is_admin']:
        # Fetch all conversations and sort by start_time with total price of the day
        conversations = chats.find({}).sort("start_time", -1)

        total_prices = {}  # Dictionary to cache total prices by date

        # Aggregate total prices by date
        pipeline = [
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}},
                    "total_price": {"$sum": "$price"}
                }
            }
        ]
        for group in chats.aggregate(pipeline):
            total_prices[group["_id"]] = group["total_price"]

        return conversations, total_prices
    return [], {}

def get_selected(selected_conversation):
    try:
        # Convert string to ObjectId
        selected_conversation_id = ObjectId(selected_conversation)
    except Exception as e:
        # Handle invalid ObjectId string
        return None

    payload = verify_jwt_token(st.session_state.jwt, False)
    if payload and payload['is_admin']:
        # Query the database with ObjectId
        conversation = chats.find_one({'_id': selected_conversation_id})
        return conversation

    return None

def get_requests_overall_average_time():
    # Check if the MONGODB_COLLECTION collection exists
    collection_names = db.list_collection_names()
    if MONGODB_COLLECTION in collection_names:
        chats = db[MONGODB_COLLECTION]

       # Initialize variables to calculate the total average time difference
        total_time_difference = 0
        total_message_count = 0
        # Define the start_date as a datetime object
        start_date = datetime(2024, 1, 21)

        # Query for messages before the start_date
        query = {"messages.timestamp": {"$lt": start_date}}

        # Iterate through all chat documents that match the query
        for chat_document in chats.find(query):
            # Access the "messages" array within the chat document
            messages = chat_document.get("messages", [])

            # Initialize variables to calculate the average time difference for this chat
            chat_time_difference = 0
            chat_message_count = len(messages)

            # Iterate through messages to calculate time differences
            for i in range(1, chat_message_count):
                current_message = messages[i]
                previous_message = messages[i - 1]

                # Extract timestamp from the messages
                current_timestamp = current_message.get("timestamp")
                previous_timestamp = previous_message.get("timestamp")

                if current_timestamp and previous_timestamp:
                    # Calculate the time difference between messages
                    time_difference = (current_timestamp - previous_timestamp).total_seconds()

                    # Add the time difference to the chat total
                    chat_time_difference += time_difference

            # Add the chat's time difference and message count to the total
            total_time_difference += chat_time_difference
            total_message_count += chat_message_count

        # Calculate the overall average time difference
        average_time_difference = total_time_difference / (total_message_count - len(chats.distinct("_id")))

        # Print the overall average time difference
        print(f"Overall Average Time Between Messages: {average_time_difference} seconds")



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
            print(inserted_id)
            break
        except Exception as e:
            if retry > 3:
                st.error("error, to fix click on reset button")
                st.error(str(e))
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)

def insert_message(document_id, new_message, price=0):
    retry = 0
    while True:
        try:
            update_result = chats.update_one(
                {"_id": document_id},
                {
                    "$push": {"messages": new_message},
                    "$inc": {"price": price}
                }
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