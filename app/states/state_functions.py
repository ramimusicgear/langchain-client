import streamlit as st
import json
from datetime import datetime

from db import get_all_filtered, get_filtered_predata



# Function to set the current tab
def set_tab(tab_name):
    st.session_state.current_tab = tab_name


def clear_all_cookies(cookie_manager):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey my name is Rami, How may I assist you today?",
        }
    ]
    st.session_state.start_time = datetime.now()
    st.session_state.document_id = ""
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None
    st.session_state.page = "chat"
    # cookie_manager.set("messages",json.dumps([{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]), key=f"set_messages_cookie_first")
    try:
        cookie_manager.delete("t", key=f"del_selected_token")
        cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")
        cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
    except Exception as e:
        pass

def add_message(message, cookie_manager):
    st.session_state.messages.append(message)
    # cookie_manager.set("messages", json.dumps(st.session_state.messages), key=f"set_messages_cookie_{message}")

def set_document_id(document_id, cookie_manager):
    st.session_state.document_id = document_id

def navigate_to(page, cookie_manager):
    st.session_state.page = page
    cookie_manager.set("page", page, key=f"set_page_cookie_{page}")


def select(conv_id, cookie_manager):
    st.session_state.selected_conversation = conv_id
    cookie_manager.set(
        "selected_conversation",
        conv_id,
        key=f"set_selected_conversation_cookie_{conv_id}",
    )


# def no_filtes():
#     st.session_state.show_filter_expander = False
# Function to change the active tab
def change_active_tab(tab_name):
    st.session_state.active_tab = tab_name


def change_collection(collection):
    if collection == "Test":
        st.session_state.selected_db_collection = "chats-test"
    if collection == "Development":
        st.session_state.selected_db_collection = "chats-dev"
    if collection == "Production":
        st.session_state.selected_db_collection = "chats"
    
    st.sidebar.success(f"Show chats from the collection - {collection}")
    
    st.session_state.db_filter_predata = get_filtered_predata(
        st.session_state.selected_db_collection, st.session_state.jwt
    )
    change_filtes(st.session_state.filters)


def increase_page_number():
    conversations, total_prices, query, total_count = get_all_filtered(
        st.session_state.filters,
        False,
        st.session_state.page_number + 1,
        st.session_state.page_size,
        st.session_state.selected_db_collection,
        st.session_state.jwt,
    )
    st.session_state.conversations += conversations
    st.session_state.total_prices = total_prices
    st.session_state.conversations_total_count = total_count
    st.session_state.page_number += 1


def change_filtes(filters):
    st.session_state.filters = filters
    conversations, total_prices, query, total_count = get_all_filtered(
        filters,
        False,
        1,
        50,
        st.session_state.selected_db_collection,
        st.session_state.jwt
    )

    if len(query["errors"]) == 0:
        st.session_state.conversations = conversations
        st.session_state.conversations_total_count = total_count
        st.session_state.total_prices = total_prices
        st.session_state.filter_errors = []
        st.session_state.show_filter_expander = False
    else:
        st.session_state.conversations = []
        st.session_state.conversations_total_count = 0
        st.session_state.total_prices = []
        st.session_state.filter_errors = query["errors"]

    st.session_state.page_number = 1
    st.session_state.page_size = 50
    

    # Check if 'conversations' is a non-empty list
    if conversations and isinstance(conversations, list):
        # Check if the first item exists and is a dict
        first_conversation = conversations[0]
        if isinstance(first_conversation, dict):
            # Return the '_id' if it exists, else return None
            st.session_state.selected_conversation = first_conversation.get("_id", None)
            print(first_conversation.get("_id", None))
    st.rerun()

def show_hide_collection():
    if st.session_state.show_collection_expander == True:
        st.session_state.show_collection_expander = False
    else:
        st.session_state.show_collection_expander = True


def show_hide_filters():
    if st.session_state.show_filter_expander == True:
        st.session_state.show_filter_expander = False
    else:
        st.session_state.show_filter_expander = True


def no_filters():
    conversations, total_prices, query, total_count = get_all_filtered(
        {}, False, 1, 50, st.session_state.selected_db_collection, st.session_state.jwt
    )
    st.session_state.page_number = 50
    st.session_state.page_size = 50
    st.session_state.conversations = conversations
    st.session_state.conversations_total_count = total_count
    st.session_state.total_prices = total_prices
    st.session_state.show_filter_expander = False
    st.session_state.filters = {}


def log_out(cookie_manager):
    st.session_state.page = "chat"
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None
    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
    cookie_manager.delete("t", key=f"del_page_cookie_chat")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")


def log_in(username, password, cookie_manager, verify_jwt_token, create_jwt_token):
    token = create_jwt_token(username, password)
    cookie_manager.set("t", token, key=f"set_register_jwt_cookie_{token}")
    payload = None
    if token:
        payload = verify_jwt_token(token)
    if payload:
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload["is_admin"]:
            st.success(f"You are logged in successfully as The Admin! \n Navigate to the admin dashboard")
            page = "admin"
            st.session_state.page = page
            change_filtes({})
            st.session_state.db_filter_predata = get_filtered_predata(
                st.session_state.selected_db_collection, st.session_state.jwt
            )
            cookie_manager.set("page", page, key=f"set_page_cookie_{page}")
        else:
            st.success(f"You are logged in successfully as {username}")
            page = "chat"
            st.session_state.page = page
            cookie_manager.set("page", page, key=f"set_page_cookie_{page}")
    else:
        st.error("Log In failed. Please try again.")
    st.rerun()


def register(username, password, cookie_manager, verify_jwt_token, create_jwt_token):
    token = create_jwt_token(
        username, password
    )  # Reuse the JWT creation function from login

    cookie_manager.set("t", token, key=f"set_register_jwt_cookie_{token}")

    payload = None
    if token:
        payload = verify_jwt_token(token)
    if payload:
        st.success(f"You are registered successfully as {username}")
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload["is_admin"]:
            navigate_to("admin", cookie_manager)
        else:
            navigate_to("chat", cookie_manager)
    else:
        st.error("Registration failed. Please try again.")


def clear_chat_history(cookie_manager):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey my name is Rami, How may I assist you today?",
        }
    ]
    # cookie_manager.set("messages",json.dumps([{"role": "assistant", "content": "Hey my name is Rami, How may I assist you today?"}]), key=f"set_messages_cookie_new_chat")
    st.session_state.start_time = datetime.now()
    st.session_state.document_id = ""
