import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime

from login_utils import verify_jwt_token, create_jwt_token
from db import get_all_filtered

# functions
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
    cookie_manager.delete("rami-token", key=f"del_selected_token")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")
    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")


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
#     st.session_state.show_filter_popup = False
# Function to change the active tab
def change_active_tab(tab_name):
    st.session_state.active_tab = tab_name


def increase_page_number():
    conversations, total_prices, query, total_count = get_all_filtered(
        st.session_state.filters,
        False,
        st.session_state.page_number + 1,
        st.session_state.page_size,
    )
    print()
    print(query)
    st.session_state.conversations += conversations
    st.session_state.total_prices = total_prices
    st.session_state.conversations_total_count = total_count
    st.session_state.page_number += 1


def change_filtes(filters):
    st.session_state.filters = filters
    conversations, total_prices, query, total_count = get_all_filtered(
        filters, False, 1, 50
    )
    print()
    print(query)

    if len(query["errors"]) == 0:
        st.session_state.conversations = conversations
        st.session_state.conversations_total_count = total_count
        st.session_state.total_prices = total_prices
        st.session_state.filter_errors = []
        st.session_state.show_filter_popup = False
    else:
        st.session_state.conversations = []
        st.session_state.conversations_total_count = 0
        st.session_state.total_prices = []
        st.session_state.filter_errors = query["errors"]

    st.session_state.page_number = 1
    st.session_state.page_size = 50


def show_hide_filters():
    if st.session_state.show_filter_popup == True:
        st.session_state.show_filter_popup = False
    else:
        st.session_state.show_filter_popup = True


def no_filters():
    conversations, total_prices, query, total_count = get_all_filtered({}, False, 1, 50)
    print()
    print(query)
    st.session_state.page_number = 50
    st.session_state.page_size = 50
    st.session_state.conversations = conversations
    st.session_state.conversations_total_count = total_count
    st.session_state.total_prices = total_prices
    st.session_state.show_filter_popup = False


def log_out(cookie_manager):
    st.session_state.page = "chat"
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None
    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
    cookie_manager.delete("rami-token", key=f"del_page_cookie_chat")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")


def log_in(username, password, cookie_manager):
    token = create_jwt_token(username, password)
    cookie_manager.set("rami-token", token, key=f"set_register_jwt_cookie_{token}")
    payload = None
    if token:
        payload = verify_jwt_token(token)
    if payload:
        st.success(f"You are logged in successfully as {username}")
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload["is_admin"]:
            navigate_to("admin")
        else:
            navigate_to("chat")
    else:
        st.error("Log In failed. Please try again.")
    # st.rerun()


def register(username, password, cookie_manager):
    token = create_jwt_token(
        username, password
    )  # Reuse the JWT creation function from login

    cookie_manager.set("rami-token", token, key=f"set_register_jwt_cookie_{token}")

    payload = None
    if token:
        payload = verify_jwt_token(token)
    if payload:
        st.success(f"You are registered successfully as {username}")
        st.session_state.jwt = token  # Store the JWT in session state
        st.session_state.user = username  # Store the JWT in session state
        if payload["is_admin"]:
            navigate_to("admin")
        else:
            navigate_to("chat")
    else:
        st.error("Registration failed. Please try again.")


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey my name is Rami, How may I assist you today?",
        }
    ]
    st.session_state.start_time = datetime.now()
    st.session_state.document_id = ""

