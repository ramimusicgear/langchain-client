import os
import re
import time
import traceback
import pymongo
import streamlit as st
from bson import ObjectId
from datetime import datetime
from datetime import date as datetime_date

from login_utils import verify_jwt_token


from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB]
chats = db[MONGODB_COLLECTION]


# GET
def get_filtered_predata():
    payload = verify_jwt_token(st.session_state["jwt"], False)
    if not payload or not payload["is_admin"]:
        return {
            "db_sender_names": None,
            "db_backend_versions": None,
            "db_first_last_dates": [],
        }

    # Aggregation pipeline to find unique feedback sender names, backend versions, and chat dates
    pipeline = [
        {
            "$group": {
                "_id": None,  # Group all documents together
                "unique_feedback_senders": {"$addToSet": "$user_actions.name"},
                "unique_backend_versions": {"$addToSet": "$backend_version"},
                "first_chat_date": {"$min": "$start_time"},
                "last_chat_date": {"$max": "$start_time"},
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "unique_feedback_senders": 1,
                "unique_backend_versions": 1,
                "first_chat_date": 1,
                "last_chat_date": 1,
            }
        },
    ]

    # Execute the aggregation pipeline
    result = chats.aggregate(pipeline)

    # Extract the results from the aggregation
    data = next(result, {})
    unique_names = data.get("unique_feedback_senders", [])
    unique_backend_versions = data.get("unique_backend_versions", [])
    first_chat_date = data.get("first_chat_date", None)
    last_chat_date = data.get("last_chat_date", None)
    print(
        {
            "db_sender_names": unique_names,
            "db_backend_versions": unique_backend_versions,
            "db_first_last_dates": [first_chat_date, last_chat_date],
        }
    )
    return {
        "db_sender_names": unique_names,
        "db_backend_versions": unique_backend_versions,
        "db_first_last_dates": [first_chat_date, last_chat_date],
    }


def get_feedback_sender_names():
    payload = verify_jwt_token(st.session_state["jwt"], False)
    if not payload or not payload["is_admin"]:
        return []

    # Aggregation pipeline to find unique feedback sender names
    pipeline = [
        {
            "$group": {
                "_id": None,  # Group all documents together
                "unique_feedback_senders": {"$addToSet": "$user_actions.name"},
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field from the result
                "unique_feedback_senders": 1,  # Include the unique feedback senders
            }
        },
    ]

    # Execute the aggregation pipeline
    result = chats.aggregate(pipeline)

    # Extract the unique names from the aggregation result
    unique_names = next(result, {}).get("unique_feedback_senders", [])

    return unique_names


# def db_backend_versions():

# def get_first_last_chat_date():


def get_all_filtered(filter, test=False, page_number=1, page_size=50):
    if not test:
        payload = verify_jwt_token(st.session_state["jwt"], False)
        if not payload or not payload["is_admin"]:
            return [], {}, {"errors": ["not admin"]}, 0

    backend_versions = filter.get("backend_versions", None)
    categories = filter.get("categories", None)
    subcategories = filter.get("subcategories", None)
    free_text_inside_the_messages = filter.get("free_text_inside_the_messages", None)
    date_range = filter.get("date_range", None)

    # feedbacks
    feedback = filter.get("feedback", None)
    reviewer_names = filter.get("reviewer_names", None)
    free_text_inside_the_user_actions = filter.get(
        "free_text_inside_the_user_actions", None
    )
    price_ratings = filter.get("price_ratings", None)
    product_ratings = filter.get("product_ratings", None)
    demands_ratings = filter.get("demands_ratings", None)
    phraise_ratings = filter.get("phraise_ratings", None)

    try:
        valid_messages = []
        # Ensure backend_versions, categories, and subcategories, reviewer_names are lists
        backend_versions = (
            backend_versions
            if isinstance(backend_versions, list)
            else [backend_versions]
            if backend_versions
            else None
        )
        categories = (
            categories
            if isinstance(categories, list)
            else [categories]
            if categories
            else None
        )
        subcategories = (
            subcategories
            if isinstance(subcategories, list)
            else [subcategories]
            if subcategories
            else None
        )
        reviewer_names = (
            reviewer_names
            if isinstance(reviewer_names, list)
            else [reviewer_names]
            if reviewer_names
            else None
        )

        # Ensure free_text_inside_the_messages, free_text_inside_the_user_actions are strings
        if free_text_inside_the_messages is not None and not isinstance(
            free_text_inside_the_messages, str
        ):
            valid_messages.append("the Search Text in the messages is invalid")
        if free_text_inside_the_user_actions is not None and not isinstance(
            free_text_inside_the_user_actions, str
        ):
            valid_messages.append("the Search Text in the feedback section is invalid")

        # Ensure feedback is a valid string
        valid_feedback_values = [
            None,
            "All Chats",
            "Only Chats With Feedback",
            "Only Chats Without Feedback",
        ]
        if feedback == "":
            feedback = None
        feedback = feedback if feedback in valid_feedback_values else "not valid"
        if feedback == "not valid":
            valid_messages.append("the with or without feedback answer is invalid")

        # Ensure price_ratings, product_ratings, demands_ratings, and phraise_ratings are valid strings
        valid_rating_values = [None, "", "Good", "Okay", "Bad"]

        if price_ratings and len(price_ratings) != 0:
            for rating in price_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("price ratings is invalid")
        else:
            price_ratings = None

        if product_ratings and len(product_ratings) != 0:
            for rating in product_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("product recommendation ratings is invalid")
        else:
            product_ratings = None

        if demands_ratings and len(demands_ratings) != 0:
            for rating in demands_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("demands ratings is invalid")
        else:
            demands_ratings = None

        if phraise_ratings and len(phraise_ratings) != 0:
            for rating in phraise_ratings:
                if rating not in valid_rating_values:
                    phraise_ratings = "not valid"
                    valid_messages.append("phraise ratings is invalid")
        else:
            phraise_ratings = None

        query = {"errors": []}

        # Ensure date_range is a list of two dates
        if date_range:
            if (
                isinstance(date_range, list)
                and len(date_range) == 2
                and all(isinstance(date, datetime_date) for date in date_range)
            ):
                start_date, end_date = date_range

                if start_date > end_date:
                    valid_messages.append("date range is invalid")

                start_date = datetime(start_date.year, start_date.month, start_date.day)
                end_date = datetime(end_date.year, end_date.month, end_date.day)

                query["start_time"] = {"$gte": start_date, "$lte": end_date}
            else:
                valid_messages.append("date range is invalid")

        if len(valid_messages) != 0:
            return [], {}, {"errors": valid_messages}, 0

        if categories:
            query["category"] = {"$in": categories}

        if subcategories:
            query["subcategory"] = {"$in": subcategories}

        if backend_versions:
            query["backend_version"] = {"$in": backend_versions}

        if free_text_inside_the_messages:
            regex = re.compile(free_text_inside_the_messages, re.IGNORECASE)
            query["messages.text"] = {"$regex": regex}

        if feedback == "Only Chats With Feedback":
            query["user_actions"] = {"$exists": True}

        elif feedback == "Only Chats Without Feedback":
            query["user_actions"] = {"$exists": False}
        else:
            if reviewer_names:
                query["user_actions.name"] = {"$in": reviewer_names}

            if free_text_inside_the_user_actions:
                regex = re.compile(free_text_inside_the_user_actions, re.IGNORECASE)
                query["user_actions.feedback"] = {"$regex": regex}

            if price_ratings is not None:
                query["user_actions.price.rating"] = price_ratings

            if product_ratings is not None:
                query["user_actions.product.rating"] = product_ratings

            if demands_ratings is not None:
                query["user_actions.demands.rating"] = demands_ratings

            if phraise_ratings is not None:
                query["user_actions.phraise.rating"] = phraise_ratings

        # Pagination logic
        skip_count = (page_number - 1) * page_size
        limit_count = page_size
        query_db = {key: value for key, value in query.items() if key != "errors"}

        pipeline = [
            {
                "$match": query_db  # Ensure this matches the filter criteria you want to apply before aggregation
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}
                    },
                    "total_price": {"$sum": "$price"},
                }
            },
            {"$sort": {"_id": -1}},  # Sorting by the grouped date in descending order
            {"$skip": skip_count},  # Skip documents based on the calculated skip_count
            {
                "$limit": page_size
            },  # Limit the number of documents in the result  # Sorting by the grouped date in descending order
        ]

        # Execute the aggregation pipeline
        total_prices_by_date = chats.aggregate(pipeline)
        total_prices = {}
        for result in total_prices_by_date:
            date = result["_id"]
            total_price = result["total_price"]
            total_prices[date] = total_price
            # print(f"Date: {date}, Total Price: {total_price}")

        conversations = list(chats.find(query_db).skip(skip_count).limit(limit_count))
        total_count = chats.count_documents(query_db)

        return conversations, total_prices, query, total_count

    except ValueError as ve:
        traceback.print_exc()
        # Log or handle the ValueError as needed
        print(f"ValueError in get_all_filtered: {ve}")
        return [], {}, {"errors": [f"ValueError in get_all_filtered: {ve}"]}, 0
    except Exception as e:
        traceback.print_exc()
        # Log or handle other exceptions as needed
        print(f"Exception in get_all_filtered: {e}")
        return [], {}, {"errors": [f"ValueError in get_all_filtered: {e}"]}, 0


def get_all():
    payload = verify_jwt_token(st.session_state["jwt"], False)
    if payload and payload["is_admin"]:
        # Fetch all conversations and sort by start_time with total price of the day
        conversations = chats.find({}).sort("start_time", -1)

        total_prices = {}  # Dictionary to cache total prices by date

        # Aggregate total prices by date
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}
                    },
                    "total_price": {"$sum": "$price"},
                }
            }
        ]
        for group in chats.aggregate(pipeline):
            total_prices[group["_id"]] = group["total_price"]

        return conversations, total_prices
    return [], {}


def get_selected(selected_conversation):
    payload = verify_jwt_token(st.session_state.jwt, False)
    if payload and payload["is_admin"]:
        try:
            # Convert string to ObjectId
            ObjectId(selected_conversation)
            # Query the database with ObjectId
            conversation = chats.find_one({"_id": selected_conversation})
            return conversation
        except Exception as e:
            print(e)
            # Handle invalid ObjectId string
            return None

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

        # Define the start_date as January 24, 2024, at 7 PM
        start_date = datetime(2024, 1, 24, 19, 0, 0)

        # Query for messages from the start_date until now
        query = {"messages.timestamp": {"$gte": start_date}}
        j = 0
        # Iterate through all chat documents that match the query
        for chat_document in chats.find({}):
            user_actions = chat_document.get("user_actions", None)
            if user_actions:
                j += 1
            # Access the "messages" array within the chat document
            messages = chat_document.get("messages", [])
            if "0.01904192939400673" in str(messages):
                continue
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
                    time_difference = (
                        current_timestamp - previous_timestamp
                    ).total_seconds()
                    if time_difference < 100:
                        # Add the time difference to the chat total
                        chat_time_difference += time_difference

            # Add the chat's time difference and message count to the total
            total_time_difference += chat_time_difference
            total_message_count += chat_message_count

        # Calculate the overall average time difference
        average_time_difference = total_time_difference / (
            total_message_count - len(chats.distinct("_id"))
        )

        # Print the overall average time difference
        print(
            f"Overall Average Time Between Messages: {average_time_difference} seconds"
        )
    print(f"Messages Amount: {j}")


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


def insert_message(document_id, new_message, category=None, subcategory=None, backend_version=None, price=0):
    retry = 0
    while True:
        try:
            if price == 0:
                update_result = chats.update_one(
                    {"_id": document_id},
                    {"$push": {"messages": new_message}}
                )
            else:
                update_result = chats.update_one(
                    {"_id": document_id},
                    {"$push": {"messages": new_message}, "$inc": {"price": price}, "$set": {"category": category, "subcategory": subcategory, "backend_version": backend_version }}
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
