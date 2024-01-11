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
    # print(username)
    # print(ADMIN_USERNAME)
    # print(password)
    # print(ADMIN_PASSWORD)
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

def login_page(log_in):
    st.title("Login")

    # Use session state variable for the text input
    username = st.text_input('Enter Your Username:', key='username_inp', value=st.session_state.username)
    # Update the session state when the text input changes
    st.session_state.username = username

    # Use session state variable for the text input
    password = st.text_input('Enter Your Password:', type="password", key='password_inp', value=st.session_state.password)
    # Update the session state when the text input changes
    st.session_state.password = password

    # Check if the password is not empty to enable the "Login" button
    if st.session_state.password:
        st.button("Login", key='login_btn', on_click=lambda: log_in(st.session_state.username, st.session_state.password))
    else:
        st.button("Login", key='dis_login_btn', on_click=None, disabled=True)

def register_user(username, password):
    """
    Register a new user and return a JWT token upon successful registration.
    """
    # Add logic to securely store the user's credentials (with hashed password)
    # For demonstration, we assume registration is always successful
    token = create_jwt_token(username, password)  # Reuse the JWT creation function from login
    return True, token


def registration_page(register):
    if st.session_state['page'] == 'register':
        st.title("Registration")
         # Use session state variable for the text input
        new_username = st.text_input('Choose Your Username:', key='new_username', value=st.session_state.username)

        # Update the session state when the text input changes
        st.session_state.username = new_username

         # Use session state variable for the text input
        new_password = st.text_input('Choose Your Password:', type="password", key='new_password', value=st.session_state.password)

        # Update the session state when the text input changes
        st.session_state.password = new_password
         # Check if the password is not empty to enable the "Login" button
        if st.session_state.password:
            st.button("Register", key='register_btn', on_click=lambda: register(st.session_state.username, st.session_state.password))
        else:
            st.button("Register", key='dis_register_btn', on_click=None, disabled=True)