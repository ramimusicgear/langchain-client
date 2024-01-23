import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv
load_dotenv()

from state import st, clear_all_cookies, navigate_to, log_in, log_out, register, select

from user_pages_and_functions import login_page, registration_page

from admin import admin_page
from chat import chat_page

TESTING = False

if st.sidebar.button("Reset Cookies", key='reset_btn'):
    clear_all_cookies()

# App Routing
if st.session_state['page'] == 'login':
    login_page(navigate_to, log_in)

elif st.session_state['page'] == 'register':
    registration_page(navigate_to, register)

elif st.session_state['page'] == 'admin':
    admin_page(navigate_to, select)
    
elif st.session_state['page'] == 'chat':
    chat_page(TESTING, clear_all_cookies, log_out, navigate_to)