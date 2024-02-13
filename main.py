import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from db import get_all_filtered, get_filtered_predata

# App title
st.set_page_config(
    page_title="Rami Chatbot", page_icon="https://ramimusic.io/svg/IconLogo.svg"
)

# Inject custom CSS to remove form borders using data-testid attribute
st.markdown(
    f"""
        <style>
            .filter-errors {{
                color: red !important;
            }}
            .element-container:has(.btn-selected) + div button{{
                border: 1.5px black solid !important;
            }}
            .element-container:has(.selected) + div button {{
                border: 1.5px black solid !important;
            }}
            .element-container:has(.black-background) + div{{
                border-color: black !important; /* New border color on hover */
            }}
            .st-g1:focus {{
                color: black !important; /* New border color on hover */
            }}
            [data-baseweb="tab-list"] p {{
                color: white !important; /* New border color on hover */
            }}
            [data-baseweb="tab-highlight"] {{
                background-color: white !important; /* New border color on hover */
            }}
            button:focus {{
                border-color: black !important; /* New border color on hover */
            }}
            button:hover {{
                border-color: black !important; /* New border color on hover */
            }}
            [data-testid="stSidebar"] {{
                background-color: rgba(128, 0, 128, 0.66) !important; /* #800080a8 with 50% transparency */
            }}
            .element-container:has(.selected) + div p{{
                font-weight: 600;
            }}
            .element-container:has(.button-after-red) + div button{{
                background-color: #f15454 !important;
            }}
            .element-container:has(.button-after-green) + div button{{
                background-color: #90ee90 !important;
            }}            
            .element-container:has(.button-after-orange) + div button{{
                background-color: #ffcc99 !important;
            }}
            .element-container:has(.button-after-gray) + div button{{
                background-color: #d3d3d3 !important;
            }}
            .element-container:has(.800080a8) + div button{{
                background-color: #800080a8 !important;
            }}
            .stApp {{
                background-image: url("https://ramimusic.io/shop/wp-content/uploads/2024/01/background.png");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            header {{
                display: none !important;
            }}
            [data-testid="stBottom"]>div{{
                background-color: transparent !important;
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
            [data-testid="stSidebar"] p {{
                color: white;
            }}
            [data-testid="stSidebar"] h1 {{
                color: white;
            }}
            [data-testid="stSidebar"] span {{
                color: white;
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

if "filter_errors" not in st.session_state:
    st.session_state.filter_errors = []

if "db_filter_predata" not in st.session_state:
    st.session_state.db_filter_predata = {}

# Initialize or update the current tab based on user interaction
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Basic'

if "page_size" not in st.session_state:
    st.session_state.page_size = 50

if "page_number" not in st.session_state:
    st.session_state.page_number = 1

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
        if (
            "conversations" not in st.session_state
            or "total_prices" not in st.session_state
            or "conversations_total_count" not in st.session_state
            or not "db_filter_predata" in st.session_state
            or not "filter_errors" in st.session_state
        ):
            st.session_state.db_filter_predata = get_filtered_predata()
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
                st.session_state.conversations_total_count = total_count
                st.session_state.total_prices = total_prices
                st.session_state.filter_errors = []
            else:
                st.session_state.conversations = []
                st.session_state.conversations_total_count = 0
                st.session_state.total_prices = []
                st.session_state.filter_errors = query["errors"]



TESTING = False

from admin import admin_page
from chat import chat_page
from login_pages import login_page, registration_page

# App Routing
if st.session_state.page == "login":
    login_page(cookie_manager)

elif st.session_state.page == "register":
    registration_page(cookie_manager)

elif st.session_state.page == "admin":
    admin_page(cookie_manager)

elif st.session_state.page == "chat":
    chat_page(TESTING, cookie_manager)
