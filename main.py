"""
    docstring
"""

import json
from google.oauth2.credentials import Credentials
from google.cloud.firestore import Client
from requests import HTTPError
from serial import Serial, SerialException
from config_manager import ConfigManager
from auth import sign_in_with_email_and_password


# FIREBASE_API_KEY = "AIzaSyAe3eITzBRrvrifZa5iuL__pM4KYCwXGSE"
ALERT_STATUS = [""]


def main():
    """_summary_
    """
    response = None
    config_manager = ConfigManager("config.json")

    if config_manager.get_firebase_api_key() is None:
        config_manager.set_firebase_api_key(
            input("Enter your Firebase API key: "))

    while not response:
        email, password = config_manager.get_login_credentials().values()
        if email is None:
            email = input("Enter your email address: ")
        if password is None:
            password = input("Enter your password: ")

        try:
            response = sign_in_with_email_and_password(
                config_manager.get_firebase_api_key(),
                email,
                password)

            config_manager.set_login_credentials(email, password)
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

    creds = Credentials(response['idToken'], response['refreshToken'])
    firestore = Client("my-pyro-webapp", creds)
    docRef = firestore.collection("user_data").document(response["localId"])
    try:
        with Serial('COM1', 115200) as port:
            while port.is_open:
                # decode the bytes into a string
                try:
                    line = port.readline().decode().rstrip()
                    data = json.loads(line)
                    print(data)
                    triggered, alert_level, flame_sensor, smoke_sensor = [
                        int(x) for x in data["data"].split(",")
                    ]
                    if triggered:
                        docRef.set({"triggered": bool(triggered)}, merge=True)
                    docRef.set(
                        {
                            "sensors": {
                                data["from"]: {
                                    "triggered": bool(triggered),
                                    "alert_level": alert_level,
                                    "flame_sensor": bool(flame_sensor),
                                    "smoke_sensor": smoke_sensor
                                }
                            },
                        },
                        merge=True
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
