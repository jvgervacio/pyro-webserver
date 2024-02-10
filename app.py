"""
    This is the main file for the Pyro Webserver.
"""

import os
import json
import sys
import firebase_admin
from dotenv import load_dotenv
from requests import HTTPError
from firebase_admin import credentials, db, firestore
from auth import sign_in_with_email_and_password
from serial import Serial, SerialException

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
        sys.exit(1)


def main():
    account_email = os.getenv("ACCOUNT_EMAIL")
    account_password = os.getenv("ACCOUNT_PASSWORD")
    
    if account_email is None or account_password is None:
        print("Please set your account email and password in .env")
        sys.exit(1)
    else:
        print(f"Signing in with {account_email}...")
        config = load_firebase_config()
        (_, _, user_id)= sign_in(account_email, account_password, config["apiKey"])
        print(f"Signed in with {account_email}!")
        print(f"User ID: {user_id}")
        
        print("Initializing Firebase...")
        cred = credentials.Certificate('./service_account_key.json')
        firebase_admin.initialize_app(cred, config)
        
        print("Initializing Firestore and Realtime Database...")
        fs = firestore.client()
        rt = db.reference()
        
        serial_port = os.getenv("SERIAL_PORT")
        baud_rate = int(os.getenv("BAUD_RATE"))
        
        print(f"Serial Port: {serial_port}")
        print(f"Baud Rate: {baud_rate}")
        
        print("Initializing Serial...")
        try:
            with Serial(serial_port, baud_rate) as port:
                while port.is_open:
                    # decode the bytes into a string
                    try:
                        line = port.readline().decode().rstrip()
                        data = json.loads(line)
                        print(data)
                        triggered, alert_level, flame_sensor, smoke_sensor = data[
                            "sensor_data"].split(",")
                        
                        rt.child(str(data['from'])).update(
                            {
                                "triggered": bool(int(triggered)),
                                "alert_level": int(alert_level),
                                "flame_sensor": bool(int(flame_sensor)),
                                "smoke_sensor": int(smoke_sensor)
                            }
                        )
                    except json.decoder.JSONDecodeError as json_error:
                        print("JSONDecodeError: ", json_error)
                    except UnicodeDecodeError as unicode_error:
                        print("UnicodeDecodeError: ", unicode_error)

        except SerialException as serial_error:
            print("SerialException: ", serial_error)
        except KeyboardInterrupt:
            port.close()
            print("Exiting...")
    

if __name__ == "__main__":
    main()