"""
    This is the main file for the Pyro Webserver.
"""

import os
import json
import sys
import firebase_admin
from dotenv import load_dotenv
from requests import HTTPError
from firebase_admin import credentials, db
from auth import sign_in_with_email_and_password
from serial import Serial, SerialException
import time

load_dotenv()

sensors = {}

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

def get_status_label(status_level: int):
    if status_level == 0:
        return "IDLE"
    elif status_level == 1:
        return "LOW"
    elif status_level == 2:
        return "MODERATE"
    else:
        return "EXTREME"

def run_serial_port(user_id, realtime_db, serial_port, baud_rate):
    try:
        with Serial(serial_port, baud_rate) as port:
            print("Serial Port Opened")
            def callback(event):
                if(event.event_type == "put"):
                    path = event.path.split("/") # ['', '6Ew6I4uY8obQcfVImlxdk4CoPlz2', 'sensors', '3955813598', 'reset']
                    if len(path) > 3:
                        sensor_id = path[3]
                        if path[4] == "reset" and bool(event.data):
                            print(f"Resetting sensor {sensor_id} for user {user_id}")
                            sensors[sensor_id] = False
                            reset_data = {
                                "sensor_id": sensor_id,
                            }
                            port.write(str(f"{reset_data}\n").encode())
                            
                            
            realtime_db.listen(callback=callback)
            
            while port.is_open:
                try:
                    line = port.readline().decode().rstrip()
                    data = json.loads(line)
                    print("Data: ", data)
                    triggered, alert_level, flame_sensor, smoke_sensor = data["sensor_data"].split(",")
                    
                    sensor_id = str(data['from'])
                    sensors[sensor_id] = bool(triggered)
                    
                    total_triggered = sum(sensors.values())
                    
                    realtime_db.child(user_id).update({
                        sensor_id: {
                                "triggered": bool(triggered),
                                "alert_level": int(alert_level),
                                "status":  get_status_label(int(alert_level)),
                                "flame_sensor": bool(flame_sensor),
                                "smoke_sensor": float(smoke_sensor),
                                "reset": False,
                        },
                        "total_sensors": len(sensors),
                        "total_triggered": int(total_triggered),
                        "timestamp": time.time(),
                        "reset": False,
                        "status": get_status_label(int(total_triggered))
                    })
                    
                except json.decoder.JSONDecodeError as json_error:
                    print("JSONDecodeError: ", json_error)
                except UnicodeDecodeError as unicode_error:
                    print("UnicodeDecodeError: ", unicode_error)
                except ValueError as value_error:
                    print("ValueError: ", value_error)
                except KeyboardInterrupt:
                    port.close()
                    print("Exiting...")

    except SerialException as serial_error:
            print("SerialException: ", serial_error)
    except KeyboardInterrupt:
            port.close()
            print("Exiting...")

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
        rt = db.reference()
        
        serial_port = os.getenv("SERIAL_PORT")
        baud_rate = int(os.getenv("BAUD_RATE"))
        
        print(f"Serial Port: {serial_port}")
        print(f"Baud Rate: {baud_rate}")
        
        print("Initializing Serial...")
        
        run_serial_port(user_id, rt, serial_port, baud_rate)
        
        



if __name__ == "__main__":
    main()