import json
import requests
from requests.exceptions import HTTPError

FIREBASE_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"


def sign_in_with_email_and_password(api_key: str,
                                    email: str, password: str) -> dict:
    """_summary_
    Args:
        api_key (str): Firebase API key
        email (str): user email address
        password (str): user password

    Raises:
        HTTPError: raises an exception if the request fails

    Returns:
        dict: a dictionary containing the user's id, email, and refresh token
    """

    request_url = f"{FIREBASE_REST_API}:signInWithPassword?key={api_key}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password,
                      "returnSecureToken": True})

    try:
        req = requests.post(request_url, headers=headers,
                            data=data, timeout=10)
        req.raise_for_status()
    except HTTPError as http_error:
        raise HTTPError(http_error, req.text) from http_error

    return req.json()
