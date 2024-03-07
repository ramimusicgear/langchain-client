import re
import traceback
from datetime import datetime, timedelta, date as datetime_date

from ..utills import verify_jwt_token, db, MONGODB_COLLECTION


def get_all_filtered(
    filter,
    test=False,
    page_number=1,
    page_size=50,
    selected_db_collection=MONGODB_COLLECTION,
    jwt=None,
):
    if not test and jwt:
        payload = verify_jwt_token(jwt)
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

        # Ensure price_ratings, product_ratings, demands_ratings, and phraise_ratings are valid string arrays
        valid_rating_values = [None, "", "Good", "Okay", "Bad"]

        price_ratings = (
            price_ratings
            if isinstance(price_ratings, list)
            else [price_ratings]
            if price_ratings
            else None
        )

        if price_ratings and len(price_ratings) != 0:
            for rating in price_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("price ratings is invalid")
        else:
            price_ratings = None

        product_ratings = (
            product_ratings
            if isinstance(product_ratings, list)
            else [product_ratings]
            if product_ratings
            else None
        )
        if product_ratings and len(product_ratings) != 0:
            for rating in product_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("product recommendation ratings is invalid")
        else:
            product_ratings = None

        demands_ratings = (
            demands_ratings
            if isinstance(demands_ratings, list)
            else [demands_ratings]
            if demands_ratings
            else None
        )

        if demands_ratings and len(demands_ratings) != 0:
            for rating in demands_ratings:
                if rating not in valid_rating_values:
                    valid_messages.append("demands ratings is invalid")
        else:
            demands_ratings = None

        phraise_ratings = (
            phraise_ratings
            if isinstance(phraise_ratings, list)
            else [phraise_ratings]
            if phraise_ratings
            else None
        )
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
                end_date = end_date + timedelta(days=1)


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

        if feedback == "Only Chats Without Feedback":
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
        total_prices_by_date = db[selected_db_collection].aggregate(pipeline)
        total_prices = {}
        for result in total_prices_by_date:
            date = result["_id"]
            total_price = result["total_price"]
            total_prices[date] = total_price
            # print(f"Date: {date}, Total Price: {total_price}")

        conversations = list(
            db[selected_db_collection]
            .find(query_db)
            .sort("start_time", -1)
            .skip(skip_count)
            .limit(limit_count)
        )
        total_count = db[selected_db_collection].count_documents(query_db)

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
