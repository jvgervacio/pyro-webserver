"""
    This is the main file for the Pyro Webserver.
"""

import os
import json
import sys
import firebase_admin
from firebase_admin import credentials, firestore, db
from dotenv import load_dotenv
from requests import HTTPError
from serial import Serial, SerialException
from auth import sign_in_with_email_and_password

load_dotenv()

def load_firebase_config():
    with open('./firebase_config.json', 'r', encoding="utf-8") as f:
        firebase_config = json.load(f)
        
    return firebase_config

def sign_in(email, password, api_key):
    try:
        response = sign_in_with_email_and_password(
            api_key,
            email,
            password)
        return (response['idToken'], response['refreshToken'], response['localId'])
    except HTTPError as http_error:
        error_msg = json.loads(
        http_error.args[1])['error']['message']
        match error_msg:
            case "EMAIL_NOT_FOUND":
                print("The email address was not found")
            case "INVALID_PASSWORD":
                print("The password is invalid")
            case "USER_DISABLED":
                print("The user account has been \
                    disabled by an administrator")
            case _:
                print("An unknown error occurred:", error_msg)

def main():
    ACCOUNT_EMAIL = os.getenv("ACCOUNT_EMAIL")
    ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")
    
    if ACCOUNT_EMAIL is None or ACCOUNT_PASSWORD is None:
        print("Please set your account email and password in .env")
        sys.exit(1)
    else:
        config = load_firebase_config()
        (_, _, user_id)= sign_in(ACCOUNT_EMAIL, ACCOUNT_PASSWORD, config["apiKey"])
        print(user_id)
        # Use a service account
        cred = credentials.Certificate('./service_account_key.json')
        firebase_admin.initialize_app(cred, config)

        rt = db.reference()
        print(rt.child(user_id).get())

if __name__ == "__main__":
    main()