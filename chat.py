import os
import json
import time
import pymongo
import requests
import streamlit as st
from bson import ObjectId
from datetime import datetime

from login_utils import verify_jwt_token

from db import update_feedback, insert_first_message, insert_message

SERVER_URL = os.environ.get("SERVER_URL")

from functions import clear_chat_history, log_out, navigate_to


def chat_page(TESTING, cookie_manager):
    # Navigation buttons

    for message in st.session_state.messages:
        if (
            message["role"] == "assistant"
        ):  # Assuming 'assistant' is the role for the bot
            with st.chat_message(
                message["role"], avatar="https://ramimusic.io/svg/IconLogo.svg"
            ):
                st.markdown(f"<p>{message['content']}</p>", unsafe_allow_html=True)
        else:
            # Default styling for other roles
            with st.chat_message(message["role"]):
                st.markdown(f"<p>{message['content']}</p>", unsafe_allow_html=True)

    # sidebar
    st.sidebar.button("New chat", on_click=clear_chat_history)
    if st.session_state.user:
        if st.sidebar.button("Logout", key="to_logout_btn"):
            log_out(cookie_manager)
        if st.session_state.user:
            st.sidebar.write(f"# Welcome, {st.session_state.user}!")

        payload = None
        token = st.session_state["jwt"]
        if token:
            payload = verify_jwt_token(token, False)
        if payload and payload["is_admin"]:
            st.sidebar.button(
                "Go To Admin Dashboard",
                key="admin_dashboard",
                on_click=lambda: navigate_to("admin", cookie_manager),
            )
    else:
        st.sidebar.write("# Login/Register")
        st.sidebar.button(
            "Login",
            key="to_login_btn",
            on_click=lambda: navigate_to("login", cookie_manager),
        )
        st.sidebar.button(
            "Register",
            key="to_register_btn",
            on_click=lambda: navigate_to("register", cookie_manager),
        )

    # sidebar feedback
    feedback_sender = ""
    price_reasoning = ""
    product_reasoning = ""
    demands_reasoning = ""
    phraise_reasoning = ""
    feedback = ""

    st.sidebar.write("# Feedback")
    with st.sidebar:
        f = st.form("Feedback", clear_on_submit=True, border=True)
    feedback_sender = f.text_input("Name (Not Required)", key="feedback_sender")

    price = f.radio(
        "Rate pricing match", ["Good", "Okay", "Bad"], index=None, horizontal=True
    )

    price_reasoning = f.text_input("Why? (Not Required)", key="price_reason")

    product = f.radio(
        "Rate product match", ["Good", "Okay", "Bad"], index=None, horizontal=True
    )

    product_reasoning = f.text_input("Why? (Not Required)", key="produt_reason")

    demands = f.radio(
        "Rate demands match", ["Good", "Okay", "Bad"], index=None, horizontal=True
    )

    demands_reasoning = f.text_input("Why? (Not Required)", key="demands_reason")

    phraise = f.radio(
        "Rate phrasing", ["Good", "Okay", "Bad"], index=None, horizontal=True
    )

    phraise_reasoning = f.text_input("Why? (Not Required)", key="phraise_reason")

    feedback = f.text_area(
        "Do you have anything else you would like to add?", key="extra feedback"
    )

    submit = f.form_submit_button("Submit")
    # submit the feedback
    if submit:
        if not TESTING:
            if st.session_state.document_id != "":
                new_values = {
                    "user_actions": {
                        "name": feedback_sender,
                        "price": {"rating": price, "reason": price_reasoning},
                        "product": {"rating": product, "reason": product_reasoning},
                        "demands": {"rating": demands, "reason": demands_reasoning},
                        "phraise": {"rating": phraise, "reason": phraise_reasoning},
                        "other": feedback,
                    }
                }
                update_feedback(st.session_state.document_id, new_values)
        st.rerun()

    # Chat

    # User-provided prompt
    if prompt := st.chat_input(disabled=False):
        if len(st.session_state.messages) == 1:
            chat_document = {
                "_id": ObjectId(),  # Generates a unique Object ID
                "user_ip": st.session_state.ip,  # Example IP address
                "user_device": "Desktop",  # Example device type
                # "category": category,
                # "subcategory": subcategory,
                "price": 0.0,
                "start_time": st.session_state.start_time,
                "end_time": datetime.now(),
                "messages": [
                    {
                        "timestamp": datetime.now(),
                        "sender": f"user - {str(st.session_state.ip)}",
                        "text": prompt,
                    }
                ],
                "prompts": {
                    "template_prompt": """Given a conversation (between Human and Assistant) and a follow up question from the user
    You are an assistant you help customers choose products using the given context (use only what is relevent) 
    your output should be nicely phrased
    ask the customer questions to figure out what he needs
    in your questions behave a little bit like a salesman and try and figure out exactly what the customer is looking for
    in your questions lead the customer to the right product for him""",
                    "search_prompt": """you are a spec analiyzer you use the given chat history and question and give out the 
    techincal specs that the product the customer is describing should have 
    don't write anything other than the specs, do not explain why
    the specs should be only technical
    always follow the instructions""",
                },
                # "product_references": references
            }

            if TESTING:
                st.session_state.document_id = "inserted_id"
            else:
                insert_first_message(chat_document)
        else:
            new_message = {
                "timestamp": datetime.now(),
                "sender": f"user - {str(st.session_state.ip)}",
                "text": prompt,
            }
            if not TESTING:
                insert_message(st.session_state.document_id, new_message)

        st.session_state.messages.append({"role": "user", "content": prompt})
        # cookie_manager.set("messages", json.dumps(st.session_state.messages), key=f"set_messages_cookie_{prompt}")

        # show user message added to the chat when he submited the message
        with st.chat_message("user"):
            st.markdown(
                f"""
                <p>{prompt}</p>
                """,
                unsafe_allow_html=True,
            )

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message(
            "assistant", avatar="https://ramimusic.io/svg/IconLogo.svg"
        ):
            with st.spinner("Thinking..."):
                messages = st.session_state.messages
                data = {"history": messages, "user_input": prompt}
                res = requests.post(f"{SERVER_URL}/process", json=data)
                result = res.json()
                response = result.get("response", "")
                placeholder = st.empty()
                full_response = ""
                for item in response:
                    full_response += item
                    placeholder.markdown(
                        f"""
                        <p>{full_response}</p>
                        """,
                        unsafe_allow_html=True,
                    )
                placeholder.markdown(
                    f"""
                        <p>{full_response}</p>
                        """,
                    unsafe_allow_html=True,
                )

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        # cookie_manager.set("messages", json.dumps(st.session_state.messages), key=f"set_messages_cookie_{message}")

        # Fetch the price; default to '0.0' if not found
        price_str = result.get("price", "0.0")
        category = result.get("category", "")
        if category == "":
            category = "backend didn't provide the catgories"
        subcategory = result.get("sub category", "")
        backend_version = result.get("version", "")

        try:
            price = float(price_str)  # Attempt to convert the price to a float
        except ValueError:
            price = 0.0  # Set to a default value

        new_message = {
            "timestamp": datetime.now(),
            "sender": "bot",
            "text": full_response,
        }
        if not TESTING:
            insert_message(
                st.session_state.document_id,
                new_message,
                category,
                subcategory,
                backend_version,
                price,
            )
