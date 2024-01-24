import os
import jwt
import time
import hashlib
import datetime
import streamlit as st

SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Function to validate login (implement proper validation here)
def validate_login(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def create_jwt_token(username, password):
    """
    Create a JWT token for the given username and password.
    The password is hashed before being included in the token.
    """
    # Hash the password (consider a more secure hash method for production)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Token expiration time
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    # Payload with hashed password
    payload = {
        "user": username,
        "password": hashed_password,  # Storing hashed password (be cautious)
        "exp": expiration_time,
        "is_admin": validate_login(username, password)
    }

    # Create JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt_token(token, triggered=True):
    """ Verify the given JWT token """
    if triggered:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            st.error("The token has expired. Please log in again.")
            return None
        except jwt.InvalidTokenError:
            st.error("Invalid token. Please log in again.")
            return None
    else:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None

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