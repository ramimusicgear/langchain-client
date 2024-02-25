from ..utills import verify_jwt_token, db


def get_filtered_predata(selected_db_collection, jwt):
    payload = verify_jwt_token(jwt)
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
    result = db[selected_db_collection].aggregate(pipeline)

    # Extract the results from the aggregation
    data = next(result, {})
    unique_names = data.get("unique_feedback_senders", [])
    unique_backend_versions = data.get("unique_backend_versions", [])
    first_chat_date = data.get("first_chat_date", None)
    last_chat_date = data.get("last_chat_date", None)

    return {
        "db_sender_names": unique_names,
        "db_backend_versions": unique_backend_versions,
        "db_first_last_dates": [first_chat_date, last_chat_date],
    }
