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

def login_page(log_in):
    st.title("Login")
    f = st.form("LoginForm",clear_on_submit=False,border=True)
    username = f.text_input('Enter Your Username:', key='username_inp')

    password = f.text_input('Enter Your Password:', type="password", key='password_inp')

    submit = f.form_submit_button("Login")
    if submit:
        log_in(username, password)
   
def register_user(username, password):
    """
    Register a new user and return a JWT token upon successful registration.
    """
    # Add logic to securely store the user's credentials (with hashed password)
    # For demonstration, we assume registration is always successful
    token = create_jwt_token(username, password)  # Reuse the JWT creation function from login
    return True, token


def registration_page(register):
    st.title("Registration")
    f = st.form("RegistrationForm",clear_on_submit=False,border=True)
    new_username = f.text_input('Choose Your Username:', key='new_username')

    new_password = f.text_input('Choose Your Password:', type="password", key='new_password')

    submit = f.form_submit_button("Register")
    if submit:
        register(new_username, new_password)