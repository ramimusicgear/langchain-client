import os
import sys
import random
import pymongo
from faker import Faker
from bson import ObjectId
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_DB = os.environ.get("MONGODB_DB")
MONGODB_COLLECTION = "chats-test"

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB]
chats = db[MONGODB_COLLECTION]

fake = Faker()

categories = {
    "Guitars & Basses": [
        "Electric Guitars",
        "Acoustic Guitars",
        "Classical Guitars",
        "Electric Basses",
        "Acoustic & Semi-Acoustic Basses",
        "Ukuleles",
        "Guitar/Bass Accessories",
        "Bluegrass Instruments",
        "Strings",
        "Guitar & Bass Spare Parts",
        "Pickups",
        "Travel Guitars",
        "Misc. Stringed Instruments",
        "Electric Guitar Amps",
        "Bass Amps",
        "Guitar & Bass Effects",
        "Acoustic Guitar Amps",
    ],
    "Keys": [
        "Keyboards",
        "Keyboard Amps",
        "Synthesizers",
        "Piano Accessories",
        "MIDI Master Keyboards",
        "Stage Pianos",
        "Digital Pianos",
        "Electric Organs",
        "Classical Organs",
    ],
}

user_action_ratings = ["Good", "Okay", "Bad"]


def fake_category_subcategory():
    category = random.choice(list(categories.keys()))
    subcategory = random.choice(categories[category])
    return category, subcategory


def fake_user_actions():
    feedback_sender_names = [
        "Ori Brosh",
        "Yaron Kaplan",
        "Yoav Lustman",
        "Roy Barak",
        "Kanye West",
        "Boris Gorlik",
        "Kfir Ben Yakov",
    ]
    feedback_sender_name = random.choice(feedback_sender_names)
    price_reason = fake.sentence()
    product_reason = fake.sentence()
    demands_reason = fake.sentence()
    phraise_reason = fake.sentence()
    other = fake.sentence()
    return {
        "name": "guest",
        "price": {"rating": random.choice(user_action_ratings), "reason": price_reason},
        "product": {
            "rating": random.choice(user_action_ratings),
            "reason": product_reason,
        },
        "demands": {
            "rating": random.choice(user_action_ratings),
            "reason": demands_reason,
        },
        "phraise": {
            "rating": random.choice(user_action_ratings),
            "reason": phraise_reason,
        },
        "other": other,
        "feedback": f"{other} {product_reason} {price_reason} {demands_reason} {phraise_reason}",
    }


def generate_fake_data(num_records=1000):
    data = []

    for _ in range(num_records):
        category, subcategory = fake_category_subcategory()
        user_actions = fake_user_actions()

        # Generate multiple messages for each record
        num_messages = random.randint(1, 10)
        start_time = fake.date_time_this_decade()
        messages = [
            {
                "timestamp": start_time + timedelta(minutes=i),
                "sender": random.choice(["user", "bot"]),
                "text": f"Message {i + 1} - {fake.sentence()}",
            }
            for i in range(num_messages)
        ]
        id = ObjectId()
        record = {
            "_id": id,
            "user_ip": fake.ipv4(),
            "user_device": random.choice(["Desktop", "Mobile"]),
            "price": round(random.uniform(0, 500), 2),
            "start_time": start_time,
            "backend_version": random.choice(
                ["0.0.1", "0.0.2", "0.0.3", "0.0.4", "0.0.5"]
            ),
            "category": category,
            "subcategory": subcategory,
            "messages": messages,
            "user_actions": user_actions,
            "summary": fake.sentence(),
            "product_references": [
                {
                    "name": fake.word(),
                    "description": fake.sentence(),
                    "price": round(random.uniform(10, 200), 2),
                    "categories": fake.word(),
                }
                for _ in range(random.randint(1, 3))
            ],
        }

        data.append(record)

    return data


if __name__ == "__main__":
    # for c in chats.find({}).limit(50):
    #     print(c["_id"])
    fake_data = generate_fake_data(25000)  # Adjust the number of records as needed

    # Insert the fake data into the MongoDB collection
    result = chats.insert_many(fake_data)
    print(f"Inserted {len(result.inserted_ids)} records into the 'chats' collection.")
