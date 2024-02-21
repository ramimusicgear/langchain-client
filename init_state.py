import os
import streamlit as st
from datetime import datetime

from login_utils import verify_jwt_token
from db import get_all_filtered, get_filtered_predata

def init(cookie_manager):
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hey my name is Rami, How may I assist you today?",
            }
        ]

    if "start_time" not in st.session_state:
        st.session_state.start_time = datetime.now()

    if "document_id" not in st.session_state:
        st.session_state.document_id = ""

    # Initialize page navigation
    if "page" not in st.session_state:
        st.session_state.page = "chat"

    # Initialize log in and admin dashboard
    if "jwt" not in st.session_state:
        st.session_state.jwt = None
    if "user" not in st.session_state:
        st.session_state.user = None

    if "selected_db_collection" not in st.session_state:
        st.session_state.selected_db_collection = os.environ.get("MONGODB_COLLECTION")

    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None

    if "show_filter_expander" not in st.session_state:
        st.session_state.show_filter_expander = False

    if "show_collection_expander" not in st.session_state:
        st.session_state.show_collection_expander = False

    if "filters" not in st.session_state:
        st.session_state.filters = {}

    if "filter_errors" not in st.session_state:
        st.session_state.filter_errors = []

    if "db_filter_predata" not in st.session_state:
        st.session_state.db_filter_predata = {}

    # Initialize or update the current tab based on user interaction
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Basic"

    if "page_size" not in st.session_state:
        st.session_state.page_size = 50

    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # Initialize the active tab state if it doesn't exist
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Filtering"

    if "ip" not in st.session_state:
        st.session_state.ip = ""




    # cookies

    if "token_loaded" not in st.session_state:
        st.session_state.token_loaded = False
    if "page_loaded" not in st.session_state:
        st.session_state.page_loaded = False
    if "selected_conversation_loaded" not in st.session_state:
        st.session_state.selected_conversation_loaded = False
    # if "messages_loaded" not in st.session_state:
    #     st.session_state.messages_loaded = False


    jwt_cookie = cookie_manager.get(cookie="t")
    page_cookie = cookie_manager.get(cookie="page")
    # messages_cookie = cookie_manager.get(cookie="messages")

    # if messages_cookie and not st.session_state.messages_loaded:
    #     st.session_state.messages = messages_cookie
    #     st.session_state.messages_loaded = True


    selected_conversation_cookie = cookie_manager.get(cookie="selected_conversation")

    if selected_conversation_cookie and not st.session_state.selected_conversation_loaded:
        st.session_state.selected_conversation = (
            selected_conversation_cookie  
        )
        st.session_state.selected_conversation_loaded = True

    if page_cookie and not st.session_state.page_loaded:
        if page_cookie != "admin":
            st.session_state.page = (
                page_cookie  
            )
            st.session_state.page_loaded = True

    if jwt_cookie and not st.session_state.token_loaded:
        payload = None
        if jwt_cookie:
            payload = verify_jwt_token(jwt_cookie, False)
        if payload:
            if page_cookie and not st.session_state.page_loaded:
                if not payload["is_admin"] and page_cookie == "admin":
                    page_cookie == "chat"
                st.session_state.page = page_cookie  # Store the JWT in session state
                st.session_state.page_loaded = True
            st.session_state.user = payload["user"]
            st.session_state.jwt = jwt_cookie
            st.session_state.token_loaded = True
            if (
                "conversations" not in st.session_state
                or "total_prices" not in st.session_state
                or "conversations_total_count" not in st.session_state
                or not "db_filter_predata" in st.session_state
                or not "filter_errors" in st.session_state
            ):
                st.session_state.db_filter_predata = get_filtered_predata(
                    st.session_state.selected_db_collection, st.session_state.jwt
                )
                conversations, total_prices, query, total_count = get_all_filtered(
                    st.session_state.filters if "filters" in st.session_state else {},
                    False,
                    st.session_state.page_number
                    if "page_number" in st.session_state
                    else 1,
                    st.session_state.page_size if "page_size" in st.session_state else 50,
                )
                if len(query["errors"]) == 0:
                    st.session_state.conversations = conversations
                    if st.session_state.selected_conversation == None:
                        st.session_state.selected_conversation =  conversations[0].get("_id", None)
                    st.session_state.conversations_total_count = total_count
                    st.session_state.total_prices = total_prices
                    st.session_state.filter_errors = []
                else:
                    st.session_state.conversations = []
                    st.session_state.conversations_total_count = 0
                    st.session_state.total_prices = []
                    st.session_state.filter_errors = query["errors"]
