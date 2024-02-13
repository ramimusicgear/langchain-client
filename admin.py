import streamlit as st
from datetime import datetime

from functions import (
    navigate_to,
    select,
    show_hide_filters,
    show_hide_collection,
    no_filters,
    change_filtes,
    increase_page_number,
    change_collection
)
from db import get_selected

# Function to set the current tab
def set_tab(tab_name):
    st.session_state.current_tab = tab_name

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


def admin_page(cookie_manager):
    st.sidebar.button(
        "Back to Chat",
        key="back_btn",
        on_click=lambda: navigate_to("chat", cookie_manager),
    )
    st.sidebar.write("# Conversations")

    st.sidebar.button("Change Database Collection", on_click=show_hide_collection)

    if st.session_state.get("show_collection_expander", False):
        with st.sidebar:
            with st.container(border=True):
                collection = st.selectbox(
                    "Select Database Collection",
                    [
                        "Development",
                        "Production",
                        "Test",
                    ]
                )
                st.button("Submit", on_click=lambda: change_collection(collection))


    # Filter Button
    st.sidebar.button("Filter Conversations", on_click=show_hide_filters)

    # Popup for Filtering
    if st.session_state.get("show_filter_expander", False):
        with st.sidebar:
            filters = {}
            st.markdown(
                '<span  class="black-background"></span>',
                unsafe_allow_html=True,
            )
            if st.session_state.current_tab == "Basic":
                with st.container(border=True):
                    # Category Selection

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
                        key="categories_select",
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
                        key="subcategories_select_in_form",
                        default=st.session_state.filters.get("subcategories", []),
                    )

                    # backend version Selection
                    backend_versions = ["0.1.1", "0.1.2"]

                    # Update with actual backend version
                    selected_backend_version = st.multiselect(
                        "Select backend version",
                        st.session_state.db_filter_predata["db_backend_versions"],
                        default=st.session_state.filters.get(
                            "backend_versions", []
                        ),
                    )
                    # Free Text Search
                    search_text = st.text_input(
                        "Search Text In Messages",
                        value=st.session_state.filters.get(
                            "free_text_inside_the_messages", None
                        ),
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
                    )

                    # date_range = st.slider('Select Date Range', value=(datetime(2023, 12, 1), datetime.now()))
                    # # Print the selected date range
                    # Submit Filtering Button
                    # if f.form_submit_button("No Filters"):
                    #     st.session_state.show_filter_expander = False
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
                            key="submit_filters_btn",
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
                        key="By Feedback",
                        on_click=lambda: set_tab("By Feedback"),
                    )

            if st.session_state.current_tab == "By Feedback":
                with st.container(border=True):
                    with_or_without = st.selectbox(
                        "With/Without Feedback",
                        [
                            "All Chats",
                            "Only Chats With Feedback",
                            "Only Chats Without Feedback",
                        ],
                    )

                    # Update with actual sender names
                    selected_senders = st.multiselect(
                        "Select Sender’s Name",
                        st.session_state.db_filter_predata["db_sender_names"],
                        default=st.session_state.filters.get("reviewer_names", []),
                    )
                    # Free Text Search in Review
                    review_search_text = st.text_input(
                        "Search Text in Reviews",
                        value=st.session_state.filters.get(
                            "free_text_inside_the_user_actions", None
                        ),
                    )

                    # Rating Selections
                    price_match_rating = st.multiselect(
                        "Price Match Rating",
                        ["Good", "Okay", "Bad"],
                        default=st.session_state.filters.get("price_ratings", None),
                    )
                    product_match_rating = st.multiselect(
                        "Product Match Rating",
                        ["Good", "Okay", "Bad"],
                        default=st.session_state.filters.get(
                            "product_ratings", None
                        ),
                    )
                    recommendation_match_rating = st.multiselect(
                        "Recommendation Match Rating",
                        ["Good", "Okay", "Bad"],
                        default=st.session_state.filters.get(
                            "demands_ratings", None
                        ),
                    )
                    chat_phrasing_rating = st.multiselect(
                        "Chat Phrasing Rating",
                        ["Good", "Okay", "Bad"],
                        default=st.session_state.filters.get(
                            "phraise_ratings", None
                        ),
                    )
                    # Submit Advanced Filtering Button
                    filters["feedback"] = with_or_without
                    filters["reviewer_names"] = selected_senders
                    filters["demands_ratings"] = recommendation_match_rating
                    filters["product_ratings"] = product_match_rating
                    filters["price_ratings"] = price_match_rating
                    filters["phraise_ratings"] = chat_phrasing_rating
                    filters[
                        "free_text_inside_the_user_actions"
                    ] = review_search_text
                    filters["reviewer_name"] = selected_senders
                    st.button(
                        "Submit",
                        key="feedback_submit_filters_btn",
                        on_click=lambda: change_filtes(filters),
                    )
                    st.button(
                        "Basic Filtering",
                        key="By Feedback",
                        on_click=lambda: set_tab("Basic"),
                    )

    conversations = st.session_state.get("conversations", [])
    total_prices = st.session_state.get("total_prices", [])
    conversations_total_count = st.session_state.get("conversations_total_count", 0)

    last_id = ""
    dates = []
    if st.session_state.filters != None:
        st.sidebar.markdown(
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
                st.sidebar.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
            else:
                formatted_number = "{:.2f}".format(total_price)
                st.sidebar.markdown(
                    f"<p>Date: {d}, Total Price: {formatted_number} $</p>",
                    unsafe_allow_html=True,
                )
            dates.append(d)

        if str(conversation_id) == str(id):
            st.sidebar.markdown(
                f'<span key="{conversation_id}_btn_label" class="button-after-{card_color} selected"></span>',
                unsafe_allow_html=True,
            )
            st.sidebar.button(
                first_message_text,
                help=get_help_from_color(card_color, True),
                key=f"{conversation_id}_btn",
            )
        else:
            st.sidebar.markdown(
                f'<span key="{conversation_id}_btn_label" class="button-after-{card_color}"></span>',
                unsafe_allow_html=True,
            )
            st.sidebar.button(
                first_message_text,
                help=get_help_from_color(card_color),
                key=f"{conversation_id}_btn",
                on_click=lambda cid=conversation_id: select(str(cid), cookie_manager),
            )

    # Check if the user has scrolled to the bottom then Add a "Load More" button at the end
    st.sidebar.markdown(
        f'<span key="load_more_btn_label" class="button-after-load-more"></span>',
        unsafe_allow_html=True,
    )
    if len(conversations) != conversations_total_count:
        st.sidebar.button("Load More", on_click=increase_page_number)

    conv = get_selected(
        st.session_state.selected_conversation
        if st.session_state.selected_conversation
        else last_id,
        st.session_state.selected_db_collection
    )
    if conv is None:
        st.write("### Please select a conversation")
    else:
        toggle_button = st.checkbox("Show Model Instruction")
        if toggle_button:
            # Model Instruction
            st.write("### Model Instruction")
            st.write("#### Template:")
            st.markdown(
                f"<p>{conv['prompts']['template_prompt']}</p>", unsafe_allow_html=True
            )

            st.write("#### Prompt Refinement:")
            st.markdown(
                f"<p>{conv['prompts']['search_prompt']}</p>", unsafe_allow_html=True
            )

        # Chat Interface
        st.title("Chat Interface")
        for idx, msg in enumerate(conv["messages"]):
            # st.markdown(f'<p><strong>{"client: " if idx % 2 == 0 else "bot: "}</strong>{msg['text']}</p>', unsafe_allow_html=True)
            st.markdown(
                f"<p><strong>{'client: ' if idx % 2 == 0 else 'bot: '}</strong>{msg['text']}</p>",
                unsafe_allow_html=True,
            )
        try:
            print(conv["category"])
            conv["category"]
            st.write("## categories")
            st.markdown(
                f"<p><strong>{conv['category']} - {conv['subcategory']}</strong></p>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            print(e)
            pass

        try:
            conv["price"]
            formatted_number = "{:.2f}".format(conv["price"])
            st.write("## Price")
            st.markdown(
                f"<p><strong>{formatted_number} $</strong></p>", unsafe_allow_html=True
            )
        except Exception as e:
            pass

        with_feedback = False
        try:
            conv["user_actions"]
            st.write("## Feedback")
            with_feedback = True
        except Exception as e:
            st.write("## No Feedback")
            with_feedback = False
        if with_feedback:
            try:
                conv["user_actions"]["price"]
                st.write("##### Rate pricing match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['price']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['price']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate product match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['product']['rating']}</p>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"<p>{conv['user_actions']['product']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate demands match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['demands']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['demands']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate phrasing")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['phraise']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['phraise']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Do you have anything else you would like to add?")
                st.markdown(
                    f"<p>{conv['user_actions']['other']}</p>", unsafe_allow_html=True
                )

                st.write(f"### The Feedback Is From - {conv['user_actions']['name']}")
            except Exception as e:
                try:
                    conv["user_actions"]["feedback_text"]
                    st.write("##### Feedback Text")
                    st.markdown(
                        f"<p>{conv['user_actions']['feedback_text']}</p>",
                        unsafe_allow_html=True,
                    )

                    st.write(
                        f"### The Feedback Is From - {conv['user_actions']['sender']}"
                    )
                except Exception as e:
                    pass
