import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# App title
st.set_page_config(
    page_title="Rami Chatbot", page_icon="https://ramimusic.io/svg/IconLogo.svg"
)

# Inject custom CSS to remove form borders using data-testid attribute
st.markdown(
    f"""
        <style>
       
        .stApp {{
            background-image: url("https://ramimusic.io/shop/wp-content/uploads/2024/01/background.png");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        header {{
            display: none !important;
        }}
        .stChatFloatingInputContainer {{
            background-color: transparent !important;
        }}
        .stChatMessage {{
            background-color: transparent !important;
        }}
        .stChatMessage * {{
            color: white !important;
        }}
        button *{{
            color: black !important;
        }}
        .main p {{
            color: white;
        }}
        # .row-widget {{
        #     color: white !important;
        # }}
        .main h1{{
            color: white !important;
        }}
        .main span{{
            color: white !important;
        }}
        </style>
        """,
    unsafe_allow_html=True,
)

from login_utils import verify_jwt_token, create_jwt_token

# states
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

if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = None

if "show_filter_popup" not in st.session_state:
    st.session_state.show_filter_popup = False

if "filters" not in st.session_state:
    st.session_state.filters = {}

# Initialize the active tab state if it doesn't exist
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Filtering"

if "ip" not in st.session_state:
    st.session_state.ip = ""
try:
    response = requests.get("https://api.ipify.org?format=json")
    ip_data = response.json()
    st.session_state.ip = ip_data["ip"]

except requests.RequestException as e:
    st.error("refresh please")

# cookies

if "token_loaded" not in st.session_state:
    st.session_state.token_loaded = False
if "page_loaded" not in st.session_state:
    st.session_state.page_loaded = False
if "selected_conversation_loaded" not in st.session_state:
    st.session_state.selected_conversation_loaded = False


def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()

jwt_cookie = cookie_manager.get(cookie="rami-token")
page_cookie = cookie_manager.get(cookie="page")

selected_conversation_cookie = cookie_manager.get(cookie="selected_conversation")

if selected_conversation_cookie and not st.session_state.selected_conversation_loaded:
    st.session_state.selected_conversation = (
        selected_conversation_cookie  # Store the JWT in session state
    )
    st.session_state.selected_conversation_loaded = True

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


# functions
def clear_all_cookies():
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


def navigate_to(page):
    st.session_state.page = page
    cookie_manager.set("page", page, key=f"set_page_cookie_{page}")


def select(conv_id):
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


def change_filtes(filters):
    st.session_state.filters = filters
    st.session_state.show_filter_popup = False


def show_hide_filters():
    if st.session_state.show_filter_popup == True:
        st.session_state.show_filter_popup = False
    else:
        st.session_state.show_filter_popup = True


def log_out():
    st.session_state.page = "chat"
    st.session_state.jwt = None
    st.session_state.user = None
    st.session_state.selected_conversation = None
    cookie_manager.set("page", "chat", key=f"set_page_cookie_chat")
    cookie_manager.delete("rami-token", key=f"del_page_cookie_chat")
    cookie_manager.delete("selected_conversation", key=f"del_selected_conversation")


def log_in(username, password):
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


def register(username, password):
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


TESTING = False

from admin import admin_page
from chat import chat_page
from login_pages import login_page, registration_page

# App Routing
if st.session_state.page == "login":
    login_page(navigate_to, log_in)

elif st.session_state.page == "register":
    registration_page(navigate_to, register)

elif st.session_state.page == "admin":
    admin_page(navigate_to, select, show_hide_filters, change_filtes, change_active_tab)

elif st.session_state.page == "chat":
    chat_page(TESTING, clear_all_cookies, log_out, navigate_to)
