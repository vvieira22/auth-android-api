from google.oauth2 import id_token
from google.auth.transport import requests
import os

def get_google_data(id_token_str: str):
    """
    Verifies the Google token and returns the user data.
    """
    try:
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), google_client_id)
        return idinfo
    except ValueError as e:
        return None