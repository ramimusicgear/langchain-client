import streamlit as st

from states.state_functions import navigate_to, log_in, register
from login.login_utils import verify_jwt_token, create_jwt_token

def login_page(cookie_manager):
    st.sidebar.button(
        "Back to Chat",
        key="login_back_btn",
        on_click=lambda: navigate_to("chat", cookie_manager),
    )
    st.sidebar.button(
        "Back to Register",
        key="login_back_register_btn",
        on_click=lambda: navigate_to("login", cookie_manager),
    )
    st.title("Login")
    st.markdown(
        '<span class="black-background"></span>',
        unsafe_allow_html=True,
    )
    f = st.form("LoginForm", clear_on_submit=False, border=True)
    username = f.text_input("Enter Your Username:", key="username")

    password = f.text_input(
        "Enter Your Password:", type="password", key="password"
    )
    submit = f.form_submit_button("Login")
    if submit:
        log_in(username, password, cookie_manager, verify_jwt_token, create_jwt_token)

def registration_page(cookie_manager):
    st.sidebar.button(
        "Back to Chat",
        key="register_back_btn",
        on_click=lambda: navigate_to("chat", cookie_manager),
    )
    st.sidebar.button(
        "Back to Login",
        key="register_back_login_btn",
        on_click=lambda: navigate_to("login", cookie_manager),
    )
    st.title("Registration")
    st.markdown(
        '<span class="black-background"></span>',
        unsafe_allow_html=True,
    )
    f = st.form("RegistrationForm", clear_on_submit=False, border=True)
    new_username = f.text_input("Choose Your Username:", key="new_username")

    new_password = f.text_input(
        "Choose Your Password:", type="password", key="new_password"
    )

    submit = f.form_submit_button("Register")
    if submit:
        register(new_username, new_password, cookie_manager, verify_jwt_token, create_jwt_token)