import os
import sys
import time
import json
from datetime import datetime

import pymongo
import streamlit as st
from dotenv import load_dotenv
from fuzzywuzzy import process, fuzz

load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB]
chats = db[MONGODB_COLLECTION]

current_dir = os.path.dirname(__file__)

prodcuts_data_path = os.path.join(current_dir, "products_dict.json")


# POST, UPDATE
def update_chat(id, new_values):
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


# Function to find matches for each product in the chat text
def find_best_matches_in_text(text, products, limit=3):
    matches = {}
    for product_name in products:
        # Using fuzz.partial_ratio to find the best match within the text for each product
        match = process.extractOne(product_name, [text], scorer=fuzz.partial_ratio)
        if match and match[1] == 100:  # Considering matches with a score > 60
            matches[product_name] = match

    return matches


try:
    with open(prodcuts_data_path, "r") as f:
        products = json.load(f)

    conversations = chats.find({}).sort("start_time", -1)

    j = 0

    for conv in conversations:
        j += 1

        user_actions = conv.get("user_actions", None)
        if user_actions:
            name = user_actions.get("name", "")
            name = user_actions.get("sender", name)
            other = user_actions.get("feedback_text", "")
            other = user_actions.get("other", other)

            price = user_actions.get("price", {"rating": "", "reason": ""})
            product = user_actions.get("product", {"rating": "", "reason": ""})
            demands = user_actions.get("demands", {"rating": "", "reason": ""})
            phraise = user_actions.get("phraise", {"rating": "", "reason": ""})

            feedback = f'{other} {price["reason"]} {product["reason"]} {demands["reason"]} {phraise["reason"]}'

            new_values = {
                "user_actions": {
                    "name": name,
                    "product": product,
                    "phraise": phraise,
                    "demands": demands,
                    "price": price,
                    "other": other,
                    "feedback": feedback,
                }
            }

            update_chat(conv["_id"], new_values)

        chat_text = " ".join([item["text"] for item in conv["messages"]])

        # Find best matches
        best_matches = find_best_matches_in_text(chat_text, products.keys())
        if best_matches == {}:
            continue

        references = []
        # Display the best matches and their scores
        for product_name, match in best_matches.items():
            # print(f"product_name: {product_name}, Match Score: {match[1]}")
            obj = products[product_name]
            category = obj["category"]
            subcategory = obj["sub_category"]
            references.append(
                {
                    "name": product_name,
                    "description": obj["description"],
                    "price": obj["price"],
                    "categories": f"{category} - {subcategory}",
                }
            )

        new_values = {
            "category": category,
            "subcategory": subcategory,
            "product_references": references,
        }

        update_chat(conv["_id"], new_values)

        print(j)
except Exception as e:
    pass
