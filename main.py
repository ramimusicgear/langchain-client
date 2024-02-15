import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import streamlit as st
import extra_streamlit_components as stx

from dotenv import load_dotenv

load_dotenv()

from state_functions import clear_all_cookies

# App title
st.set_page_config(
    page_title="Rami Chatbot", page_icon="https://ramimusic.io/svg/IconLogo.svg"
)
from css import add_css
from init_state import init
add_css()

def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
init(cookie_manager)

if st.sidebar.button("Reset Cookies", key="reset_btn"):
    clear_all_cookies(cookie_manager)

try:
    response = requests.get("https://api.ipify.org?format=json")
    ip_data = response.json()
    st.session_state.ip = ip_data["ip"]

except requests.RequestException as e:
    st.error("refresh please")

from admin_page import admin_page
from chat_page import chat_page
from login_pages import login_page, registration_page

TESTING = False

# App Routing
if st.session_state.page == "login":
    login_page(cookie_manager)
elif st.session_state.page == "register":
    registration_page(cookie_manager)
elif st.session_state.page == "admin":
    admin_page(cookie_manager)
elif st.session_state.page == "chat":
    chat_page(TESTING, cookie_manager)
