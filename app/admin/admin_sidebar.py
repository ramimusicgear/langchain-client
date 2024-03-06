import streamlit as st
from datetime import datetime
from db import get_filtered_predata
from states.state_functions import (
    navigate_to,
    select,
    show_hide_filters,
    show_hide_collection,
    no_filters,
    change_filtes,
    increase_page_number,
    change_collection,
    set_tab,
)

def get_help_from_color(color, selected=False):
    if color == "red":
        return f"{'selected chat - ' if selected else ''}Bad Feedback"
    elif color == "orange":
        return f"{'selected chat - ' if selected else ''}Okay Feedback"
    elif color == "green":
        return f"{'selected chat - ' if selected else ''}Good Feedback"
    else:
        return f"{'selected chat - ' if selected else ''}No Feedback"

def get_card_color(user_actions):
    price = user_actions.get("price", {"rating": "", "reason": ""})
    product = user_actions.get("product", {"rating": "", "reason": ""})
    demands = user_actions.get("demands", {"rating": "", "reason": ""})
    phraise = user_actions.get("phraise", {"rating": "", "reason": ""})

    if (
        price["rating"] == "Bad"
        or product["rating"] == "Bad"
        or demands["rating"] == "Bad"
        or phraise["rating"] == "Bad"
    ):
        return "red"
    elif (
        price["rating"] == "Good"
        or product["rating"] == "Good"
        or demands["rating"] == "Good"
        or phraise["rating"] == "Good"
    ):
        return "green"
    elif (
        price["rating"] == "Okay"
        or product["rating"] == "Okay"
        or demands["rating"] == "Okay"
        or phraise["rating"] == "Okay"
    ):
        return "orange"
    else:
        return "gray"

def show_filtered_converstaions(cookie_manager):
    with st.sidebar:
        conversations = st.session_state.get("conversations", [])
        total_prices = st.session_state.get("total_prices", [])
        conversations_total_count = st.session_state.get("conversations_total_count", 0)

        last_id = ""
        dates = []
        
        st.markdown(
            f"<p>Total Conversations: {conversations_total_count}</p>",
            unsafe_allow_html=True,
        )
        
        # show conversations
        for conv in conversations:
            conversation_id = conv["_id"]
            first_message_text = (
                conv["messages"][0]["text"] if conv["messages"] else "No messages"
            )
            card_color = get_card_color(conv.get("user_actions", {}))

            if last_id == "":
                last_id = conversation_id

            id = (
                st.session_state.selected_conversation
                if st.session_state.selected_conversation
                else last_id
            )

            # print(f"selected: {str(
            #     st.session_state.selected_conversation
            #     if st.session_state.selected_conversation
            #     else last_id
            # )}")

            # print(f"{str(conversation_id)} - {first_message_text}")
            d = str(conv["start_time"]).split()[0]

            if d not in dates:
                # show the total price of all chats on the date
                total_price = total_prices.get(d, 0)  # Get total price for the date
                if total_price == 0:
                    st.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
                else:
                    formatted_number = "{:.2f}".format(total_price)
                    st.markdown(
                        f"<p>Date: {d}, Total Price: {formatted_number} $</p>",
                        unsafe_allow_html=True,
                    )
                dates.append(d)

            if str(conversation_id) == str(id):
                st.markdown(
                    f'<span key="{conversation_id}_btn_label" class="button-after-{card_color} selected"></span>',
                    unsafe_allow_html=True,
                )
                st.button(
                    first_message_text,
                    help=get_help_from_color(card_color, True),
                    key=f"{conversation_id}_btn",
                )
            else:
                st.markdown(
                    f'<span key="{conversation_id}_btn_label" class="button-after-{card_color}"></span>',
                    unsafe_allow_html=True,
                )
                st.button(
                    first_message_text,
                    help=get_help_from_color(card_color),
                    key=f"{conversation_id}_btn",
                    on_click=lambda cid=conversation_id: select(str(cid), cookie_manager),
                )

        # Check if the user has scrolled to the bottom then Add a "Load More" button at the end
        st.markdown(
            f'<span key="load_more_btn_label" class="button-after-load-more"></span>',
            unsafe_allow_html=True,
        )
        if len(conversations) != conversations_total_count:
            st.button("Load More", on_click=increase_page_number)

def filter_by_feedback_expander(filters):
    with st.sidebar:
        with st.container(border=True):
            with_or_without_feedback = st.selectbox(
                "With/Without Feedback",
                [
                    "All Chats",
                    "Only Chats With Feedback",
                    "Only Chats Without Feedback",
                ],
                key="with_or_without_feedback_selectbox",
                default=st.session_state.filters.get("feedback", "All Chats"),
            )

            # Update with actual sender names
            selected_senders = st.multiselect(
                "Select Sender’s Name",
                st.session_state.db_filter_predata["db_sender_names"],
                key="selected_senders_multiselect",
                default=st.session_state.filters.get("reviewer_names", []),
            )
            # Free Text Search in Review
            review_search_text = st.text_input(
                "Search Text in Reviews",
                value=st.session_state.filters.get(
                    "free_text_inside_the_user_actions", None
                ),
                key="review_search_text_input"
            )

            # Rating Selections
            price_match_rating = st.multiselect(
                "Price Match Rating",
                ["Good", "Okay", "Bad"],
                key="price_match_rating_multiselect",
                default=st.session_state.filters.get("price_ratings", None),
            )
            product_match_rating = st.multiselect(
                "Product Match Rating",
                ["Good", "Okay", "Bad"],
                key="product_match_rating_multiselect",
                default=st.session_state.filters.get("product_ratings", None),
            )
            recommendation_match_rating = st.multiselect(
                "Recommendation Match Rating",
                ["Good", "Okay", "Bad"],
                key="recommendation_match_rating_multiselect",
                default=st.session_state.filters.get("demands_ratings", None),
            )
            chat_phrasing_rating = st.multiselect(
                "Chat Phrasing Rating",
                ["Good", "Okay", "Bad"],
                key="chat_phrasing_rating_multiselect",
                default=st.session_state.filters.get("phraise_ratings", None),
            )
            
            # Submit Advanced Filtering Button
            filters = st.session_state.filters
            filters["feedback"] = with_or_without_feedback
            filters["reviewer_names"] = selected_senders
            filters["demands_ratings"] = recommendation_match_rating
            filters["product_ratings"] = product_match_rating
            filters["price_ratings"] = price_match_rating
            filters["phraise_ratings"] = chat_phrasing_rating
            filters["free_text_inside_the_user_actions"] = review_search_text
            print(filters)
            print()
            print(st.session_state.filters)
            print()
            print()
            st.button(
                "Submit",
                key="submit_feedback_filters_btn",
                on_click=lambda: change_filtes(filters),
            )
            st.button(
                "Basic Filtering",
                key="back_to_basic_filters_btn",
                on_click=lambda: set_tab("Basic"),
            )

def basic_filter_expander(filters):
    with st.sidebar:
        with st.container(border=True):
            # Category Selection
            if st.session_state.db_filter_predata.get("db_backend_versions", None):
                # Define the categories and sub-categories
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
                # Multi-select widget for categories
                selected_categories = st.multiselect(
                    "Select Categories",
                    options=list(categories.keys()),
                    key="categories_multiselect",
                    default=st.session_state.filters.get("categories", []),
                )

                # Add filter options here

                # Display subcategories based on the selected categories
                subcategories_options = [
                    subcategory
                    for category in selected_categories
                    for subcategory in categories[category]
                ]
                selected_subcategories = st.multiselect(
                    "Select Subcategories:",
                    options=subcategories_options,
                    key="subcategories_multiselect",
                    default=st.session_state.filters.get("subcategories", []),
                )

                # backend version Selection
                backend_versions = ["0.1.1", "0.1.2"]

                # Update with actual backend version
                selected_backend_version = st.multiselect(
                    "Select backend version",
                    st.session_state.db_filter_predata["db_backend_versions"],
                    key="versions_multiselect",
                    default=st.session_state.filters.get("backend_versions", []),
                )
                # Free Text Search
                search_text = st.text_input(
                    "Search Text In Messages",
                    value=st.session_state.filters.get(
                        "free_text_inside_the_messages", None
                    ),
                    key="search_text_input"

                )
                # Date Range Selection

                # Simplified access to 'date_range' with fallback
                date_range = st.session_state.filters.get("date_range", False)
                now = datetime.now()
                if date_range and len(date_range) > 1:
                    start_value = date_range[0]
                    end_value = date_range[1]
                else:
                    start_value = st.session_state.db_filter_predata.get(
                        "db_first_last_dates", [datetime(2023, 12, 1)]
                    )[0]
                    end_value = st.session_state.db_filter_predata.get(
                        "db_first_last_dates",
                        [datetime(2023, 12, 1), now],
                    )[1]
                start_date = st.date_input(
                    "Select Start Date",
                    value=start_value,
                    format="DD/MM/YYYY",
                    min_value=st.session_state.db_filter_predata[
                        "db_first_last_dates"
                    ][0],
                    max_value=st.session_state.db_filter_predata[
                        "db_first_last_dates"
                    ][1],
                    key="start_date_input"

                )
                end_date = st.date_input(
                    "Select End Date",
                    value=end_value,
                    format="DD/MM/YYYY",
                    min_value=st.session_state.db_filter_predata[
                        "db_first_last_dates"
                    ][0]
                    if start_date is None
                    else start_date,
                    max_value=st.session_state.db_filter_predata[
                        "db_first_last_dates"
                    ][1],
                    key="end_date_input"

                )
                filters = st.session_state.filters
                filters["free_text_inside_the_messages"] = search_text
                filters["backend_versions"] = selected_backend_version
                filters["date_range"] = [start_date, end_date]
                filters["categories"] = selected_categories
                filters["subcategories"] = selected_subcategories
                errors = st.session_state.get("filter_errors", [])
                if len(errors):
                    for error in errors:
                        st.markdown(
                            f'<p class="filter-errors">{error}</p>',
                            unsafe_allow_html=True,
                        )
                st.markdown(
                    f'<p style="margin:5px"></p>',
                    unsafe_allow_html=True,
                )
                col1, col2 = st.columns(2)

                with col1:
                    st.button(
                        "Submit",
                        key="submit_basic_filters_btn",
                        on_click=lambda: change_filtes(filters),
                    )

                with col2:
                    st.button(
                        "No Filters",
                        key="no_filters_btn",
                        on_click=no_filters,
                    )
                st.button(
                    "Filter By Feedback",
                    key="go_to_feedback_filters_btn",
                    on_click=lambda: set_tab("By Feedback"),
                )

def admin_sidebar(cookie_manager):
    st.sidebar.button(
        "Back to Chat",
        key="back_btn",
        on_click=lambda: navigate_to("chat", cookie_manager),
    )
    st.sidebar.write("# Conversations")

    st.sidebar.button("Change Database Collection", key="change_database_collection_btn", on_click=show_hide_collection)

    if st.session_state.get("show_collection_expander", False):
        with st.sidebar:
            with st.container(border=True):
                collection = st.selectbox(
                    "Select Database Collection",
                    [
                        "Development",
                        "Production",
                        "Test"
                    ],
                    key="change_database_collection_selectbox"
                )
                st.button("Submit", key="submit_collection_btn", on_click=lambda: change_collection(collection))

    # Filter Button
    st.sidebar.button("Filter Conversations", key="filter_conversations_btn", on_click=show_hide_filters)
    show_filter_expander = st.session_state.get("show_filter_expander", False)
    # Popup for Filtering
    if show_filter_expander:
        filters = {}
        st.markdown(
            '<span class="black-background"></span>',
            unsafe_allow_html=True,
        )
        if st.session_state.current_tab == "Basic":
            basic_filter_expander(filters)
            
        if st.session_state.current_tab == "By Feedback":
            filter_by_feedback_expander(filters)
            
    show_filtered_converstaions(cookie_manager)