import os
import jwt
import time
import hashlib
import datetime
import streamlit as st

def login_page(navigate_to, log_in):
    st.sidebar.button("Back to Chat", key='login_back_btn', on_click=lambda: navigate_to('chat'))
    st.sidebar.button("Back to Register", key='login_back_register_btn', on_click=lambda: navigate_to('login'))
    st.title("Login")
    f = st.form("LoginForm",clear_on_submit=False,border=True)
    username = f.text_input('Enter Your Username:', key='username_inp')

    password = f.text_input('Enter Your Password:', type="password", key='password_inp')

    submit = f.form_submit_button("Login")
    if submit:
        log_in(username, password)

def registration_page(navigate_to, register):
    st.sidebar.button("Back to Chat", key='register_back_btn', on_click=lambda: navigate_to('chat'))
    st.sidebar.button("Back to Login", key='register_back_login_btn', on_click=lambda: navigate_to('login'))
    st.title("Registration")
    f = st.form("RegistrationForm",clear_on_submit=False,border=True)
    new_username = f.text_input('Choose Your Username:', key='new_username')

    new_password = f.text_input('Choose Your Password:', type="password", key='new_password')

    submit = f.form_submit_button("Register")
    if submit:
        register(new_username, new_password)