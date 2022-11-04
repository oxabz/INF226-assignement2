from typing import List
from flask import Flask
import sys
import apsw
from apsw import Error
from dotenv import load_dotenv
import os

load_dotenv()

conn :List[apsw.Connection] = [None]

# Set up app
app = Flask(__name__)

# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
app.secret_key = os.environ.get('SECRET_KEY') or 'mY s3kritz'
app.config['MAX_MESSAGES'] = int(os.environ.get('MAX_MESSAGES') or 100)

import src.coffee
import src.static
import src.messages
import src.user

try:
    conn[0] = apsw.Connection('./tiny.db')
    c = conn[0].cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL);''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id integer PRIMARY KEY,
        sender TEXT NOT NULL,
        sender_deleted INTEGER NOT NULL DEFAULT 0,
        message TEXT NOT NULL,
        datetime integet NOT NULL,
        FOREIGN KEY(sender) REFERENCES users(username)
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS message_to_user (
        id integer PRIMARY KEY,
        user TEXT NOT NULL,
        message_id integer NOT NULL,
        deleted integer NOT NULL DEFAULT 0,
        FOREIGN KEY(user) REFERENCES users(username) ON DELETE CASCADE,
        FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE CASCADE
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id integer PRIMARY KEY, 
        author TEXT NOT NULL,
        text TEXT NOT NULL);''')
except Error as e:
    print(e)
    sys.exit(1)

