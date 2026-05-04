# db/connection.py
import mysql.connector
from mysql.connector import Error

_db     = None
_cursor = None

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "root007",
    "database": "event_management"
}

def connect():
    global _db, _cursor
    try:
        _db     = mysql.connector.connect(**DB_CONFIG)
        _cursor = _db.cursor()
        return True
    except Error as e:
        print(f"[DB] Connection failed: {e}")
        return False

def get_db():
    global _db
    if _db is None or not _db.is_connected():
        connect()
    return _db

def get_cursor():
    global _cursor, _db
    if _db is None or not _db.is_connected():
        connect()
    _cursor = _db.cursor()
    return _cursor

def close():
    global _db, _cursor
    if _cursor: _cursor.close()
    if _db and _db.is_connected(): _db.close()

connect()
