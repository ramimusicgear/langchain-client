import os
import jwt
import time
import hashlib
from datetime import datetime, timedelta, timezone
import streamlit as st

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


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
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)

    # Payload with hashed password
    payload = {
        "user": username,
        "password": hashed_password,  # Storing hashed password (be cautious)
        "exp": expiration_time,
        "is_admin": validate_login(username, password),
    }

    # Create JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt_token(token, triggered=True):
    """Verify the given JWT token"""
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
