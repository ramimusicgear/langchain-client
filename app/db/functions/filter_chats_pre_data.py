from ..utills import verify_jwt_token, db

def get_filtered_predata(selected_db_collection, jwt):
    """
    Retrieves unique feedback sender names, backend versions, and the range of chat dates from a specified database collection.

    This function is designed to support an administrative interface where insights into the data are necessary for further filtering or analysis. Access to this data requires admin privileges, verified through a JWT token.

    Parameters:
    - selected_db_collection (str): The name of the MongoDB collection from which to retrieve the data.
    - jwt (str): A JWT token used for verifying if the caller has admin privileges.

    Returns:
    dict: A dictionary containing three keys:
          - db_sender_names: A list of unique names who sent feedback.
          - db_backend_versions: A list of unique backend versions present in the data.
          - db_first_last_dates: A list containing the earliest and latest chat dates.

    If the JWT token does not validate or the user is not an admin, returns a dictionary with None or empty values as appropriate.
    """
    # Verify the JWT token and ensure the user is an admin
    payload = verify_jwt_token(jwt)
    if not payload or not payload["is_admin"]:
        # If not valid or not admin, return empty data structure
        return {
            "db_sender_names": None,
            "db_backend_versions": None,
            "db_first_last_dates": [],
        }

    # Define an aggregation pipeline for MongoDB to extract the needed information
    pipeline = [
        {
            "$group": {
                "_id": None,  # Group all documents together to aggregate the data
                "unique_feedback_senders": {"$addToSet": "$user_actions.name"},  # Unique sender names
                "unique_backend_versions": {"$addToSet": "$backend_version"},  # Unique backend versions
                "first_chat_date": {"$min": "$start_time"},  # Earliest chat date
                "last_chat_date": {"$max": "$start_time"},  # Latest chat date
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field from results
                "unique_feedback_senders": 1,  # Include unique sender names
                "unique_backend_versions": 1,  # Include unique backend versions
                "first_chat_date": 1,  # Include the earliest chat date
                "last_chat_date": 1,  # Include the latest chat date
            }
        },
    ]

    # Execute the aggregation pipeline on the selected database collection
    result = db[selected_db_collection].aggregate(pipeline)

    # Extract and format the results from the aggregation operation
    data = next(result, {})  # Use next to get the first item from the iterator or return an empty dict if none
    unique_names = data.get("unique_feedback_senders", [])
    unique_backend_versions = data.get("unique_backend_versions", [])
    first_chat_date = data.get("first_chat_date", None)
    last_chat_date = data.get("last_chat_date", None)

    # Return the formatted data
    return {
        "db_sender_names": unique_names,
        "db_backend_versions": unique_backend_versions,
        "db_first_last_dates": [first_chat_date, last_chat_date],
    }
