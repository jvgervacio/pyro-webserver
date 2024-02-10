import firebase_admin
from firebase_admin import credentials, db, firestore
from dotenv import load_dotenv
import os
import sys
import json

load_dotenv()

def load_firebase_config():
    with open('./firebase_config.json', 'r', encoding="utf-8") as f:
        firebase_config = json.load(f)
        
    return firebase_config

cred = credentials.Certificate('./service_account_key.json')
firebase_admin.initialize_app(cred, load_firebase_config())

# Get a database reference to our blog.
db.reference('users').set({
    'alanisawesome': {
        'date_of_birth': 'June 23, 1912',
        'full_name': 'Alan Turing'
    },
    'gracehop': {
        'date_of_birth': 'December 9, 1906',
        'full_name': 'Grace Hopper'
    }
})
