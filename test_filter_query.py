import unittest
from unittest.mock import patch
from datetime import datetime
from db import (
    get_all_filtered,
)  # replace "db" with the actual module where your function is define


class TestGetAllFiltered(unittest.TestCase):
    # categories test
    def test_filter_by_categories(self):
        filter = {"categories": ["Guitars & Basses"]}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(chat["category"] == "Guitars & Basses" for chat in conversations)
        )

    def test_filter_by_subcategories(self):
        filter = {"subcategories": ["Electric Guitars"]}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(chat["subcategory"] == "Electric Guitars" for chat in conversations)
        )

    def test_filter_by_categories_and_subcategories(self):
        filter = {
            "categories": ["Guitars & Basses"],
            "subcategories": ["Electric Guitars"],
        }
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(chat["subcategory"] == "Electric Guitars" for chat in conversations)
        )

        filter = {
            "categories": ["Guitars & Basses", "Keys"],
            "subcategories": ["Electric Guitars"],
        }
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(
                (
                    chat["subcategory"] == "Electric Guitars"
                    and chat["category"] != "Keys"
                )
                for chat in conversations
            )
        )

    # date ranges test
    def test_filter_by_date_range(self):
        start_date = datetime(2024, 1, 25, 0, 0, 0)
        end_date = datetime(2024, 2, 10, 0, 0, 0)
        filter = {"date_range": [start_date, end_date]}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(start_date <= chat["start_time"] <= end_date for chat in conversations)
        )

    def test_filter_by_date_range_and_more_filters(self):
        start_date = datetime(2024, 1, 25, 0, 0, 0)
        end_date = datetime(2024, 2, 10, 0, 0, 0)
        filter = {
            "date_range": [start_date, end_date],
            "categories": ["Guitars & Basses"],
            "subcategories": ["Electric Guitars"],
        }
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(
                chat["subcategory"] == "Electric Guitars"
                and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
        )

        filter = {
            "date_range": [start_date, end_date],
            "categories": ["Guitars & Basses", "Keys"],
            "subcategories": ["Electric Guitars"],
        }
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(
                chat["subcategory"] == "Electric Guitars"
                and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
        )

        filter = {"date_range": [start_date, end_date], "categories": ["Keys"]}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(
                chat["category"] == "Keys"
                and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
        )

        filter = {
            "date_range": [start_date, end_date],
            "feedback": "Only Chats With Feedback",
        }
        conversations, total_prices, query = get_all_filtered(filter, True)

        self.assertTrue(
            all(
                "user_actions" in chat and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
        )

        filter = {
            "date_range": [start_date, end_date],
            "feedback": "Only Chats Without Feedback",
        }
        conversations, total_prices, query = get_all_filtered(filter, True)

        self.assertTrue(
            all(
                "user_actions" not in chat
                and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
        )

        word = "2"
        filter = {
            "date_range": [start_date, end_date],
            "feedback": "Only Chats Without Feedback",
            "free_text_inside_the_messages": word,
        }
        conversations, total_prices, query = get_all_filtered(filter, True)

        self.assertTrue(
            all(
                "user_actions" not in chat
                and start_date <= chat["start_time"] <= end_date
                for chat in conversations
            )
            and any(
                word.lower() in message["text"].lower()
                for chat in conversations
                for message in chat["messages"]
            )
        )

    def test_filter_by_free_text_inside_messages(self):
        word = "6"
        filter = {"free_text_inside_the_messages": word}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            any(
                word.lower() in message["text"].lower()
                for chat in conversations
                for message in chat["messages"]
            )
        )

    # with and without check
    def test_filter_by_feedback_only_with_feedback(self):
        filter = {"feedback": "Only Chats With Feedback"}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(all("user_actions" in chat for chat in conversations))

    def test_filter_by_feedback_only_without_feedback(self):
        filter = {"feedback": "Only Chats Without Feedback"}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(all("user_actions" not in chat for chat in conversations))

    def test_filter_by_user_actions_criteria(self):
        filter = {"price_rating": "Okay", "product_rating": "Okay"}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(
            all(
                (
                    "user_actions" in chat
                    and chat["user_actions"]["price"]["rating"] == "Okay"
                    and chat["user_actions"]["product"]["rating"] == "Okay"
                )
                or ("user_actions" not in chat)
                for chat in conversations
            )
        )

    def test_filter_by_empty_categories(self):
        # Test with an empty list of categories
        filter = {"categories": []}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(all("category" in chat for chat in conversations))

    def test_filter_by_null_categories(self):
        # Test with null value for categories
        filter = {"categories": None}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertTrue(all("category" in chat for chat in conversations))

    def test_filter_by_categories(self):
        filter = {"categories": ["Nonexistent Category"]}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertEqual(len(conversations), 0)

    # Add similar tests for other filters
    def test_no_results_found(self):
        # Test with a combination of filters that should yield no results
        filter = {
            "categories": ["Nonexistent Category"],
            "subcategories": ["Nonexistent Subcategory"],
        }
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertEqual(len(conversations), 0)

    def test_invalid_input_types(self):
        # Test with invalid input types for filters
        invalid_filters = [
            {"categories": "Invalid Type"},  # Invalid type for categories
            {"categories": 1},  # Invalid type for categories
            {"categories": [1]},  # Invalid type for categories
            {"subcategories": "Invalid Type"},  # Invalid type for subcategories
            {"date_range": "Invalid Type"},  # Invalid type for date_range
            {
                "free_text_inside_the_messages": 123
            },  # Invalid type for free_text_inside_the_messages
            {
                "free_text_inside_the_messages": [123]
            },  # Invalid type for free_text_inside_the_messages
            {"feedback": 123},  # Invalid type for feedback
            {"feedback": [123]},  # Invalid type for feedback
            {"feedback": ["123"]},  # Invalid type for feedback
            {"price_rating": 123},  # Invalid type for price_rating
            {"price_rating": [123]},  # Invalid type for price_rating
            {"price_rating": ["123"]},  # Invalid type for price_rating
            {"product_rating": 123},  # Invalid type for product_rating
            {"demands_rating": 123},  # Invalid type for demands_rating
            {"phraise_rating": 123},  # Invalid type for phraise_rating
            {"reviewer_name": 123},  # Invalid type for reviewer_name
            {
                "free_text_inside_the_user_actions": 123
            },  # Invalid type for free_text_inside_the_messages
            {
                "categories": "Invalid Type",
                "subcategories": "Invalid Type",
            },  # Invalid type for categories
            {"categories": ["Keys"], "subcategories": 1},  # Invalid type for categories
            {
                "categories": ["Keys"],
                "subcategories": 1,
                "feedback": 123,
                "reviewer_name": 123,
                "free_text_inside_the_user_actions": ["11"],
            },  # Invalid type for mix filters
            {
                "categories": ["Keys"],
                "subcategories": 1,
                "feedback": 123,
                "reviewer_name": 123,
                "free_text_inside_the_user_actions": ["11"],
                "date_range": "Invalid Type",
            },  # Invalid type for more mix filters
            {"date_range": [datetime(2025, 1, 1), datetime(2024, 1, 1)]},
        ]

        for invalid_filter in invalid_filters:
            with self.subTest(invalid_filter=invalid_filter):
                conversations, total_prices, query = get_all_filtered(
                    invalid_filter, True
                )
                self.assertEqual(len(conversations), 0)

    def test_edge_cases(self):
        # Test with empty string for free_text_inside_the_messages
        filter = {"free_text_inside_the_messages": ""}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertEqual(len(conversations), 0)

        # Test with empty string for free_text_inside_the_user_actions
        filter = {"free_text_inside_the_user_actions": ""}
        conversations, total_prices, query = get_all_filtered(filter, True)
        self.assertEqual(len(conversations), 0)

        # Test with an date range that represent all
        start_date = datetime(1900, 1, 1, 0, 0, 0)
        end_date = datetime(3000, 1, 1, 0, 0, 0)
        filter = {"date_range": [start_date, end_date]}
        all_conversations, total_prices, query = get_all_filtered({}, True)
        conversations, total_prices, query = get_all_filtered(filter, True)

        self.assertEqual(len(conversations), len(all_conversations))

    # test aggregate
    @patch("db.chats.aggregate")
    @patch("db.chats.find")
    def test_aggregate_function(self, mock_find, mock_aggregate):
        # Mock the conversations data
        mock_conversations = [
            {"_id": 1, "start_time": datetime(2024, 1, 1), "price": 100},
            {"_id": 2, "start_time": datetime(2024, 1, 1), "price": 150},
            {"_id": 3, "start_time": datetime(2024, 1, 2), "price": 200},
            # Add more mock data as needed
        ]

        # Mock the find method to return conversations
        mock_find.return_value = mock_conversations

        # Mock the aggregate method to return the aggregation result
        mock_aggregate_result = [
            {"_id": "2024-01-01", "total_price": 250},
            {"_id": "2024-01-02", "total_price": 200},
            # Add more aggregation results as needed
        ]
        mock_aggregate.return_value = mock_aggregate_result

        # Define a filter (you can customize this based on your test scenario)
        filter = {"categories": ["Guitars & Basses"]}

        # Call the function
        conversations, total_prices, query = get_all_filtered(filter, True)

        # Assertions
        # Verify that the aggregation pipeline is constructed correctly
        self.assertIn({"$match": query}, mock_aggregate.call_args[0][0])
        self.assertIn(
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}
                    },
                    "total_price": {"$sum": "$price"},
                }
            },
            mock_aggregate.call_args[0][0],
        )

        # Verify that the conversations match the mocked data
        self.assertEqual(conversations, mock_conversations)

        # Verify that the total_prices match the mocked aggregation result
        expected_total_prices = {"2024-01-01": 250, "2024-01-02": 200}
        self.assertEqual(total_prices, expected_total_prices)


if __name__ == "__main__":
    unittest.main()
